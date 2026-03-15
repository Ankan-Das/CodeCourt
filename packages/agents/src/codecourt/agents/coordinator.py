"""Coordinator Agent - Orchestrates multiple review agents.

The Coordinator is the "Court Clerk" that manages the review process,
running multiple agents and combining their results.
"""

import asyncio
from typing import Any

from pydantic import BaseModel, Field

from codecourt.agents.base import BaseAgent
from codecourt.agents.code_reviewer import CodeReviewAgent
from codecourt.agents.models import Approval, Finding, ReviewResult, Severity
from codecourt.agents.security import SecurityAgent
from codecourt.providers import BaseLLMProvider, get_provider
from codecourt.tools import ParsedDiff


class CoordinatedReviewResult(BaseModel):
    """Result from a coordinated multi-agent review."""

    findings: list[Finding] = Field(default_factory=list)
    summary: str = Field(description="Combined summary from all agents")
    approval: Approval = Field(description="Consensus approval recommendation")
    confidence: float = Field(default=0.0, description="Average confidence")
    
    # Per-agent results
    agent_results: dict[str, ReviewResult] = Field(
        default_factory=dict,
        description="Individual results from each agent",
    )
    
    # Statistics
    total_agents: int = Field(default=0)
    agents_approving: int = Field(default=0)
    agents_requesting_changes: int = Field(default=0)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.ERROR)

    @property
    def has_blocking_issues(self) -> bool:
        return self.critical_count > 0 or self.error_count > 0


class Coordinator(BaseAgent):
    """
    Orchestrates multiple review agents and combines their results.

    The Coordinator can run agents in parallel, deduplicate findings,
    and produce a unified review result.

    Example:
        >>> coordinator = Coordinator.with_default_agents(provider_name="openai")
        >>> result = await coordinator.review(diff)
        >>> print(f"Total findings: {len(result.findings)}")
        >>> print(f"Approval: {result.approval}")
    """

    def __init__(
        self,
        agents: list[BaseAgent] | None = None,
        provider: BaseLLMProvider | None = None,
        provider_name: str = "openai",
        parallel: bool = True,
    ) -> None:
        """
        Initialize the Coordinator.

        Args:
            agents: List of agents to coordinate (creates defaults if None)
            provider: Shared LLM provider for agents
            provider_name: Provider name if creating default agents
            parallel: Whether to run agents in parallel (faster) or sequential
        """
        super().__init__(name="Coordinator", role="coordinator")
        
        self.provider = provider or get_provider(provider_name)
        self.parallel = parallel
        
        # Create default agents if none provided
        if agents is None:
            self.agents = self._create_default_agents()
        else:
            self.agents = agents

    def _create_default_agents(self) -> list[BaseAgent]:
        """Create the default set of review agents."""
        return [
            CodeReviewAgent(provider=self.provider),
            SecurityAgent(provider=self.provider),
        ]

    @classmethod
    def with_default_agents(
        cls,
        provider_name: str = "openai",
        model: str | None = None,
        parallel: bool = True,
    ) -> "Coordinator":
        """
        Create a Coordinator with default agents.

        Args:
            provider_name: LLM provider to use
            model: Specific model (applies to all agents)
            parallel: Run agents in parallel

        Returns:
            Configured Coordinator instance.
        """
        provider = get_provider(provider_name)
        agents = [
            CodeReviewAgent(provider=provider, model=model),
            SecurityAgent(provider=provider, model=model),
        ]
        return cls(agents=agents, provider=provider, parallel=parallel)

    async def review(self, diff: ParsedDiff) -> CoordinatedReviewResult:
        """
        Run all agents and produce a combined review.

        Args:
            diff: Parsed diff to review

        Returns:
            CoordinatedReviewResult with combined findings from all agents.
        """
        if self.parallel:
            results = await self._run_parallel(diff)
        else:
            results = await self._run_sequential(diff)

        return self._combine_results(results)

    async def _run_parallel(self, diff: ParsedDiff) -> dict[str, ReviewResult]:
        """Run all agents in parallel."""
        async def run_agent(agent: BaseAgent) -> tuple[str, ReviewResult]:
            # Type check for agents with review method
            if hasattr(agent, "review"):
                result = await agent.review(diff)  # type: ignore
                return (agent.name, result)
            else:
                # Fallback to analyze method
                response = await agent.analyze({"diff": diff})
                # Convert AgentResponse to ReviewResult
                return (agent.name, ReviewResult(
                    findings=[],
                    summary=response.reasoning,
                    approval=Approval(response.verdict) if response.verdict in ["approve", "request_changes", "comment"] else Approval.COMMENT,
                    confidence=response.confidence,
                    agent_name=agent.name,
                ))

        # Run all agents concurrently
        tasks = [run_agent(agent) for agent in self.agents]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert to dict, handling any exceptions
        results = {}
        for item in results_list:
            if isinstance(item, Exception):
                # Log error but continue with other results
                print(f"Agent error: {item}")
                continue
            name, result = item
            results[name] = result

        return results

    async def _run_sequential(self, diff: ParsedDiff) -> dict[str, ReviewResult]:
        """Run agents one at a time (useful for debugging)."""
        results = {}
        
        for agent in self.agents:
            try:
                if hasattr(agent, "review"):
                    result = await agent.review(diff)  # type: ignore
                    results[agent.name] = result
            except Exception as e:
                print(f"Agent {agent.name} error: {e}")
                continue

        return results

    def _combine_results(
        self, 
        agent_results: dict[str, ReviewResult]
    ) -> CoordinatedReviewResult:
        """Combine results from multiple agents."""
        
        # Collect all findings
        all_findings: list[Finding] = []
        for result in agent_results.values():
            all_findings.extend(result.findings)

        # Deduplicate findings (same file + line + similar message)
        unique_findings = self._deduplicate_findings(all_findings)

        # Sort by severity (critical first)
        sorted_findings = self._sort_by_severity(unique_findings)

        # Calculate consensus approval
        approval = self._calculate_approval(agent_results)

        # Calculate average confidence
        confidences = [r.confidence for r in agent_results.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Count approvals
        approving = sum(
            1 for r in agent_results.values() 
            if r.approval == Approval.APPROVE
        )
        requesting_changes = sum(
            1 for r in agent_results.values() 
            if r.approval == Approval.REQUEST_CHANGES
        )

        # Generate combined summary
        summary = self._generate_summary(agent_results, sorted_findings)

        return CoordinatedReviewResult(
            findings=sorted_findings,
            summary=summary,
            approval=approval,
            confidence=avg_confidence,
            agent_results=agent_results,
            total_agents=len(agent_results),
            agents_approving=approving,
            agents_requesting_changes=requesting_changes,
        )

    def _deduplicate_findings(self, findings: list[Finding]) -> list[Finding]:
        """Remove duplicate findings based on file, line, and message similarity."""
        seen: set[tuple[str, int | None, str]] = set()
        unique: list[Finding] = []

        for finding in findings:
            # Create a key from file, line, and first 50 chars of message
            key = (
                finding.file,
                finding.line,
                finding.message[:50].lower(),
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(finding)

        return unique

    def _sort_by_severity(self, findings: list[Finding]) -> list[Finding]:
        """Sort findings by severity (most severe first)."""
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.ERROR: 1,
            Severity.WARNING: 2,
            Severity.INFO: 3,
            Severity.PRAISE: 4,
        }
        
        return sorted(findings, key=lambda f: severity_order.get(f.severity, 99))

    def _calculate_approval(
        self, 
        results: dict[str, ReviewResult]
    ) -> Approval:
        """
        Calculate consensus approval.

        Rules:
        - If ANY agent requests changes → REQUEST_CHANGES
        - If ALL agents approve → APPROVE
        - Otherwise → COMMENT
        """
        if not results:
            return Approval.COMMENT

        approvals = [r.approval for r in results.values()]

        # Any request for changes means overall request changes
        if Approval.REQUEST_CHANGES in approvals:
            return Approval.REQUEST_CHANGES

        # All approve means approve
        if all(a == Approval.APPROVE for a in approvals):
            return Approval.APPROVE

        return Approval.COMMENT

    def _generate_summary(
        self,
        results: dict[str, ReviewResult],
        findings: list[Finding],
    ) -> str:
        """Generate a combined summary from all agent results."""
        parts = []

        # Overall stats
        critical = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        errors = sum(1 for f in findings if f.severity == Severity.ERROR)
        warnings = sum(1 for f in findings if f.severity == Severity.WARNING)

        if critical > 0:
            parts.append(f"🔴 {critical} critical issue(s)")
        if errors > 0:
            parts.append(f"🟠 {errors} error(s)")
        if warnings > 0:
            parts.append(f"🟡 {warnings} warning(s)")

        if not findings:
            parts.append("✅ No issues found")

        # Add per-agent summaries
        parts.append("\n\nAgent summaries:")
        for name, result in results.items():
            parts.append(f"- {name}: {result.summary}")

        return " | ".join(parts[:3]) + "".join(parts[3:])

    async def analyze(self, context: dict[str, Any]) -> Any:
        """Implement BaseAgent interface."""
        diff = context.get("diff")
        if diff:
            return await self.review(diff)
        return None

    async def respond(self, message: Any) -> Any:
        """Respond to messages (not used by coordinator)."""
        return None

    def add_agent(self, agent: BaseAgent) -> None:
        """Add an agent to the coordination."""
        self.agents.append(agent)

    def remove_agent(self, agent_name: str) -> None:
        """Remove an agent by name."""
        self.agents = [a for a in self.agents if a.name != agent_name]

    @property
    def agent_names(self) -> list[str]:
        """List names of all coordinated agents."""
        return [a.name for a in self.agents]
