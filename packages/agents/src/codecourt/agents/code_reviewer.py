"""Code Review Agent - Reviews pull request changes."""

from typing import Any

from codecourt.agents.base import AgentMessage, AgentResponse, BaseAgent
from codecourt.agents.models import Approval, Category, Finding, ReviewResult, Severity
from codecourt.providers import BaseLLMProvider, get_provider
from codecourt.tools import ParsedDiff, format_diff_for_review

# System prompt that defines the agent's behavior
SYSTEM_PROMPT = """You are an expert code reviewer. Your job is to review pull request changes and provide constructive feedback.

## Your Review Process

1. **Understand the change**: What is this PR trying to accomplish?
2. **Check for bugs**: Are there logic errors, edge cases, or potential crashes?
3. **Security review**: Are there any security vulnerabilities?
4. **Performance**: Are there obvious performance issues?
5. **Best practices**: Does the code follow good patterns?
6. **Praise good work**: Acknowledge well-written code!

## Guidelines

- Be constructive, not harsh
- Explain WHY something is an issue
- Suggest HOW to fix it when possible
- Focus on important issues, not nitpicks
- Consider the context and trade-offs

## Response Format

You MUST respond with valid JSON matching this exact structure:
{
    "findings": [
        {
            "file": "path/to/file.py",
            "line": 42,
            "severity": "warning",
            "category": "bug",
            "message": "Description of the issue",
            "suggestion": "How to fix it"
        }
    ],
    "summary": "Brief summary of your review",
    "approval": "approve" | "request_changes" | "comment",
    "confidence": 0.85
}

Severity levels: critical, error, warning, info, praise
Categories: security, bug, performance, style, best_practice, documentation, testing, error_handling, type_safety, other
"""


class CodeReviewAgent(BaseAgent):
    """
    Agent that reviews code changes and provides feedback.

    This is the foundational review agent. Other agents (Defender, Prosecutor)
    will extend or use this for specialized review tasks.
    """

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
        provider_name: str = "openai",
        model: str | None = None,
    ) -> None:
        """
        Initialize the Code Review Agent.

        Args:
            provider: LLM provider instance (optional, will create one if not provided)
            provider_name: Name of provider to use if provider not given
            model: Specific model to use (defaults to provider's default)
        """
        super().__init__(name="CodeReviewer", role="code_reviewer")
        self.provider = provider or get_provider(provider_name)
        self.model = model

    async def review(self, diff: ParsedDiff) -> ReviewResult:
        """
        Review a parsed diff and return findings.

        This is the main entry point for code review.

        Args:
            diff: Parsed diff from parse_diff()

        Returns:
            ReviewResult with findings, summary, and approval recommendation.

        Example:
            >>> agent = CodeReviewAgent(provider_name="ollama")
            >>> diff = parse_diff(raw_diff_text)
            >>> result = await agent.review(diff)
            >>> print(result.summary)
            >>> for finding in result.findings:
            ...     print(f"{finding.severity}: {finding.message}")
        """
        # Format the diff for the LLM
        formatted_diff = format_diff_for_review(diff)

        # Build the prompt
        user_message = f"""Please review the following code changes:

## Changed Files
{', '.join(diff.changed_files)}

## Statistics
- Lines added: {diff.total_additions}
- Lines removed: {diff.total_deletions}

## Diff
{formatted_diff}

Review these changes and provide your findings in the specified JSON format."""

        # Call the LLM
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        try:
            # Try to get JSON response
            response = await self.provider.complete_json(
                messages=messages,
                schema={
                    "type": "object",
                    "properties": {
                        "findings": {"type": "array"},
                        "summary": {"type": "string"},
                        "approval": {"type": "string"},
                        "confidence": {"type": "number"},
                    },
                },
                model=self.model,
            )

            # Parse the response into our model
            return self._parse_response(response)

        except Exception as e:
            # Fallback if JSON parsing fails
            return ReviewResult(
                findings=[],
                summary=f"Error during review: {str(e)}",
                approval=Approval.COMMENT,
                confidence=0.0,
                agent_name=self.name,
            )

    def _parse_response(self, response: dict[str, Any]) -> ReviewResult:
        """Parse LLM response into ReviewResult."""
        findings = []

        for f in response.get("findings", []):
            try:
                finding = Finding(
                    file=f.get("file", "unknown"),
                    line=f.get("line"),
                    severity=Severity(f.get("severity", "info")),
                    category=Category(f.get("category", "other")),
                    message=f.get("message", ""),
                    suggestion=f.get("suggestion"),
                    code_snippet=f.get("code_snippet"),
                )
                findings.append(finding)
            except (ValueError, KeyError):
                # Skip malformed findings
                continue

        # Parse approval
        approval_str = response.get("approval", "comment").lower()
        try:
            approval = Approval(approval_str)
        except ValueError:
            approval = Approval.COMMENT

        return ReviewResult(
            findings=findings,
            summary=response.get("summary", "Review completed"),
            approval=approval,
            confidence=float(response.get("confidence", 0.8)),
            agent_name=self.name,
        )

    async def analyze(self, context: dict[str, Any]) -> AgentResponse:
        """
        Implement BaseAgent interface.

        Args:
            context: Must contain 'diff' key with ParsedDiff

        Returns:
            AgentResponse with findings
        """
        diff = context.get("diff")
        if not diff or not isinstance(diff, ParsedDiff):
            return AgentResponse(
                agent_name=self.name,
                verdict="error",
                findings=[{"error": "No valid diff provided"}],
                confidence=0.0,
                reasoning="Cannot review without a diff",
            )

        result = await self.review(diff)

        return AgentResponse(
            agent_name=self.name,
            verdict=result.approval.value,
            findings=[f.model_dump() for f in result.findings],
            confidence=result.confidence,
            reasoning=result.summary,
        )

    async def respond(self, message: AgentMessage) -> AgentMessage:
        """
        Respond to a message from another agent.

        This is used in the debate system when other agents
        challenge or question this agent's findings.
        """
        # For now, just acknowledge the message
        return AgentMessage(
            role=self.role,
            content=f"Acknowledged: {message.content[:100]}...",
            metadata={"from": self.name},
        )
