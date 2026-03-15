"""Security Agent - The Bailiff of CodeCourt.

Specialized agent that focuses exclusively on security vulnerabilities.
"""

from typing import Any

from codecourt.agents.base import AgentMessage, AgentResponse, BaseAgent
from codecourt.agents.models import Approval, Category, Finding, ReviewResult, Severity
from codecourt.providers import BaseLLMProvider, get_provider
from codecourt.tools import ParsedDiff, format_diff_for_review

# Security-focused system prompt with OWASP knowledge
SECURITY_SYSTEM_PROMPT = """You are a senior application security engineer performing a security-focused code review.

## Your Role
You are the "Bailiff" of CodeCourt - your job is to identify security vulnerabilities ONLY.
Do NOT comment on code style, performance, or general best practices unless they have security implications.

## What to Look For

### 1. Injection Vulnerabilities (OWASP A03)
- SQL Injection: String concatenation in queries, unsanitized user input in SQL
- Command Injection: User input in shell commands, subprocess calls
- XSS: Unsanitized output in HTML, missing escaping
- LDAP/XML/XPath Injection

### 2. Broken Authentication (OWASP A07)
- Hardcoded credentials, API keys, passwords
- Weak password requirements
- Missing authentication checks
- Session management issues

### 3. Sensitive Data Exposure (OWASP A02)
- Logging sensitive data (passwords, tokens, PII)
- Sensitive data in error messages
- Unencrypted sensitive data
- Debug endpoints exposing data

### 4. Broken Access Control (OWASP A01)
- Missing authorization checks
- IDOR (Insecure Direct Object Reference)
- Privilege escalation possibilities
- Path traversal

### 5. Security Misconfiguration (OWASP A05)
- Debug mode in production code
- Default credentials
- Overly permissive CORS
- Missing security headers

### 6. Cryptographic Failures (OWASP A02)
- Weak hashing algorithms (MD5, SHA1 for passwords)
- Hardcoded encryption keys/IVs
- Insecure random number generation
- Missing encryption for sensitive data

### 7. Secrets in Code
- API keys, tokens, passwords in source code
- Private keys, certificates
- Database connection strings with credentials
- AWS/GCP/Azure credentials

## Severity Guidelines
- CRITICAL: Exploitable vulnerability, immediate risk (SQL injection, RCE, exposed secrets)
- ERROR: Security flaw that needs fixing (missing auth, weak crypto)
- WARNING: Potential security issue (logging PII, debug code)
- INFO: Security improvement suggestion (additional hardening)

## Response Format
Respond with ONLY valid JSON:
{
    "findings": [
        {
            "file": "path/to/file.py",
            "line": 42,
            "severity": "critical",
            "category": "security",
            "vulnerability_type": "sql_injection",
            "message": "SQL query built with string concatenation allows injection",
            "suggestion": "Use parameterized queries instead",
            "cwe_id": "CWE-89"
        }
    ],
    "summary": "Brief security assessment",
    "approval": "approve" | "request_changes" | "comment",
    "confidence": 0.85,
    "security_score": 7.5
}

If no security issues found, return empty findings array with approval: "approve".
"""


class SecurityAgent(BaseAgent):
    """
    Security-focused code review agent (The Bailiff).

    Unlike the general CodeReviewAgent, this agent focuses exclusively
    on security vulnerabilities based on OWASP Top 10 and common
    security anti-patterns.
    """

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
        provider_name: str = "openai",
        model: str | None = None,
    ) -> None:
        """
        Initialize the Security Agent.

        Args:
            provider: LLM provider instance
            provider_name: Name of provider to use if provider not given
            model: Specific model to use
        """
        super().__init__(name="SecurityBailiff", role="security_reviewer")
        self.provider = provider or get_provider(provider_name)
        self.model = model

    async def review(self, diff: ParsedDiff) -> ReviewResult:
        """
        Perform a security-focused review of the diff.

        Args:
            diff: Parsed diff to review

        Returns:
            ReviewResult with security findings only.
        """
        formatted_diff = format_diff_for_review(diff)

        # Build security-focused prompt
        user_message = f"""Perform a SECURITY-ONLY review of these code changes.

## Changed Files
{', '.join(diff.changed_files)}

## File Types
{', '.join(set(f.language or 'unknown' for f in diff.files))}

## Statistics
- Lines added: {diff.total_additions}
- Lines removed: {diff.total_deletions}

## Code Changes
{formatted_diff}

Analyze these changes for security vulnerabilities ONLY. 
Ignore code style, performance, and non-security issues.
Focus on: injection, auth, secrets, access control, crypto, data exposure."""

        messages = [
            {"role": "system", "content": SECURITY_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        try:
            response = await self.provider.complete_json(
                messages=messages,
                schema={
                    "type": "object",
                    "properties": {
                        "findings": {"type": "array"},
                        "summary": {"type": "string"},
                        "approval": {"type": "string"},
                        "confidence": {"type": "number"},
                        "security_score": {"type": "number"},
                    },
                },
                model=self.model,
            )
            return self._parse_response(response)

        except Exception as e:
            return ReviewResult(
                findings=[],
                summary=f"Security review error: {str(e)}",
                approval=Approval.COMMENT,
                confidence=0.0,
                agent_name=self.name,
            )

    def _parse_response(self, response: dict[str, Any]) -> ReviewResult:
        """Parse LLM response into ReviewResult with security findings."""
        findings = []

        for f in response.get("findings", []):
            try:
                # Map vulnerability types to categories
                vuln_type = f.get("vulnerability_type", "")
                
                finding = Finding(
                    file=f.get("file", "unknown"),
                    line=f.get("line"),
                    severity=Severity(f.get("severity", "warning")),
                    category=Category.SECURITY,  # Always security for this agent
                    message=self._format_security_message(f),
                    suggestion=f.get("suggestion"),
                    code_snippet=f.get("code_snippet"),
                )
                findings.append(finding)
            except (ValueError, KeyError):
                continue

        # Parse approval
        approval_str = response.get("approval", "comment").lower()
        try:
            approval = Approval(approval_str)
        except ValueError:
            approval = Approval.COMMENT

        # Force request_changes if critical findings exist
        has_critical = any(f.severity == Severity.CRITICAL for f in findings)
        if has_critical:
            approval = Approval.REQUEST_CHANGES

        return ReviewResult(
            findings=findings,
            summary=response.get("summary", "Security review completed"),
            approval=approval,
            confidence=float(response.get("confidence", 0.8)),
            agent_name=self.name,
        )

    def _format_security_message(self, finding: dict) -> str:
        """Format security finding message with vulnerability details."""
        message = finding.get("message", "Security issue detected")
        vuln_type = finding.get("vulnerability_type", "")
        cwe_id = finding.get("cwe_id", "")

        parts = [message]
        if vuln_type:
            parts.append(f"[Type: {vuln_type}]")
        if cwe_id:
            parts.append(f"[{cwe_id}]")

        return " ".join(parts)

    async def analyze(self, context: dict[str, Any]) -> AgentResponse:
        """Implement BaseAgent interface."""
        diff = context.get("diff")
        if not diff or not isinstance(diff, ParsedDiff):
            return AgentResponse(
                agent_name=self.name,
                verdict="error",
                findings=[{"error": "No valid diff provided"}],
                confidence=0.0,
                reasoning="Cannot perform security review without a diff",
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
        """Respond to messages from other agents."""
        return AgentMessage(
            role=self.role,
            content=f"Security assessment: {message.content[:100]}...",
            metadata={"from": self.name},
        )
