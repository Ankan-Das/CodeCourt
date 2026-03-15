"""Tests for the Coordinator Agent."""

import pytest

from codecourt.agents import (
    Approval,
    Category,
    CodeReviewAgent,
    CoordinatedReviewResult,
    Coordinator,
    Finding,
    ReviewResult,
    SecurityAgent,
    Severity,
)


class TestCoordinator:
    """Tests for Coordinator initialization."""

    def test_coordinator_initialization(self) -> None:
        """Test coordinator can be created."""
        coordinator = Coordinator(provider_name="ollama")

        assert coordinator.name == "Coordinator"
        assert coordinator.role == "coordinator"
        assert len(coordinator.agents) == 2  # Default agents

    def test_coordinator_with_default_agents(self) -> None:
        """Test coordinator creates default agents."""
        coordinator = Coordinator.with_default_agents(provider_name="ollama")

        assert len(coordinator.agents) == 2
        agent_names = coordinator.agent_names
        assert "CodeReviewer" in agent_names
        assert "SecurityBailiff" in agent_names

    def test_coordinator_custom_agents(self) -> None:
        """Test coordinator with custom agent list."""
        agents = [CodeReviewAgent(provider_name="ollama")]
        coordinator = Coordinator(agents=agents, provider_name="ollama")

        assert len(coordinator.agents) == 1
        assert coordinator.agent_names == ["CodeReviewer"]

    def test_add_agent(self) -> None:
        """Test adding an agent to coordinator."""
        coordinator = Coordinator(agents=[], provider_name="ollama")
        assert len(coordinator.agents) == 0

        coordinator.add_agent(CodeReviewAgent(provider_name="ollama"))
        assert len(coordinator.agents) == 1

    def test_remove_agent(self) -> None:
        """Test removing an agent from coordinator."""
        coordinator = Coordinator.with_default_agents(provider_name="ollama")
        assert len(coordinator.agents) == 2

        coordinator.remove_agent("SecurityBailiff")
        assert len(coordinator.agents) == 1
        assert "SecurityBailiff" not in coordinator.agent_names


class TestCoordinatedReviewResult:
    """Tests for CoordinatedReviewResult."""

    def test_empty_result(self) -> None:
        """Test empty coordinated result."""
        result = CoordinatedReviewResult(
            findings=[],
            summary="No issues",
            approval=Approval.APPROVE,
            total_agents=2,
            agents_approving=2,
            agents_requesting_changes=0,
        )

        assert result.critical_count == 0
        assert result.has_blocking_issues is False

    def test_result_with_findings(self) -> None:
        """Test result with findings from multiple agents."""
        result = CoordinatedReviewResult(
            findings=[
                Finding(file="a.py", severity=Severity.CRITICAL, category=Category.SECURITY, message="SQL injection"),
                Finding(file="b.py", severity=Severity.WARNING, category=Category.STYLE, message="Long line"),
            ],
            summary="Found issues",
            approval=Approval.REQUEST_CHANGES,
            total_agents=2,
            agents_approving=0,
            agents_requesting_changes=2,
        )

        assert result.critical_count == 1
        assert result.error_count == 0
        assert len(result.findings) == 2
        assert result.has_blocking_issues is True


class TestApprovalConsensus:
    """Tests for approval consensus logic."""

    def test_all_approve(self) -> None:
        """Test when all agents approve."""
        coordinator = Coordinator(agents=[], provider_name="ollama")

        results = {
            "Agent1": ReviewResult(findings=[], summary="OK", approval=Approval.APPROVE, agent_name="Agent1"),
            "Agent2": ReviewResult(findings=[], summary="OK", approval=Approval.APPROVE, agent_name="Agent2"),
        }

        approval = coordinator._calculate_approval(results)
        assert approval == Approval.APPROVE

    def test_one_requests_changes(self) -> None:
        """Test when one agent requests changes."""
        coordinator = Coordinator(agents=[], provider_name="ollama")

        results = {
            "Agent1": ReviewResult(findings=[], summary="OK", approval=Approval.APPROVE, agent_name="Agent1"),
            "Agent2": ReviewResult(findings=[], summary="Issues", approval=Approval.REQUEST_CHANGES, agent_name="Agent2"),
        }

        approval = coordinator._calculate_approval(results)
        assert approval == Approval.REQUEST_CHANGES

    def test_mixed_without_changes(self) -> None:
        """Test mixed results without request_changes."""
        coordinator = Coordinator(agents=[], provider_name="ollama")

        results = {
            "Agent1": ReviewResult(findings=[], summary="OK", approval=Approval.APPROVE, agent_name="Agent1"),
            "Agent2": ReviewResult(findings=[], summary="Note", approval=Approval.COMMENT, agent_name="Agent2"),
        }

        approval = coordinator._calculate_approval(results)
        assert approval == Approval.COMMENT


class TestDeduplication:
    """Tests for finding deduplication."""

    def test_removes_duplicates(self) -> None:
        """Test that duplicate findings are removed."""
        coordinator = Coordinator(agents=[], provider_name="ollama")

        findings = [
            Finding(file="a.py", line=10, severity=Severity.WARNING, category=Category.BUG, message="Same issue here"),
            Finding(file="a.py", line=10, severity=Severity.WARNING, category=Category.BUG, message="Same issue here"),
            Finding(file="b.py", line=20, severity=Severity.ERROR, category=Category.BUG, message="Different file"),
        ]

        unique = coordinator._deduplicate_findings(findings)
        assert len(unique) == 2

    def test_keeps_different_lines(self) -> None:
        """Test that findings on different lines are kept."""
        coordinator = Coordinator(agents=[], provider_name="ollama")

        findings = [
            Finding(file="a.py", line=10, severity=Severity.WARNING, category=Category.BUG, message="Issue"),
            Finding(file="a.py", line=20, severity=Severity.WARNING, category=Category.BUG, message="Issue"),
        ]

        unique = coordinator._deduplicate_findings(findings)
        assert len(unique) == 2


class TestSeveritySorting:
    """Tests for severity-based sorting."""

    def test_critical_first(self) -> None:
        """Test that critical findings come first."""
        coordinator = Coordinator(agents=[], provider_name="ollama")

        findings = [
            Finding(file="a.py", severity=Severity.INFO, category=Category.STYLE, message="Info"),
            Finding(file="b.py", severity=Severity.CRITICAL, category=Category.SECURITY, message="Critical"),
            Finding(file="c.py", severity=Severity.WARNING, category=Category.BUG, message="Warning"),
        ]

        sorted_findings = coordinator._sort_by_severity(findings)
        
        assert sorted_findings[0].severity == Severity.CRITICAL
        assert sorted_findings[1].severity == Severity.WARNING
        assert sorted_findings[2].severity == Severity.INFO


class TestParallelExecution:
    """Tests for parallel execution configuration."""

    def test_parallel_mode_enabled(self) -> None:
        """Test parallel mode is enabled by default."""
        coordinator = Coordinator(provider_name="ollama")
        assert coordinator.parallel is True

    def test_sequential_mode(self) -> None:
        """Test sequential mode can be enabled."""
        coordinator = Coordinator(provider_name="ollama", parallel=False)
        assert coordinator.parallel is False
