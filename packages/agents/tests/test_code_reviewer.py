"""Tests for the Code Review Agent."""

import pytest

from codecourt.agents import (
    Approval,
    Category,
    CodeReviewAgent,
    Finding,
    ReviewResult,
    Severity,
)
from codecourt.tools import parse_diff


class TestFindingModel:
    """Tests for Finding model."""

    def test_create_finding(self) -> None:
        """Test creating a finding."""
        finding = Finding(
            file="src/app.py",
            line=42,
            severity=Severity.WARNING,
            category=Category.BUG,
            message="Potential null pointer",
            suggestion="Add null check",
        )

        assert finding.file == "src/app.py"
        assert finding.line == 42
        assert finding.severity == Severity.WARNING
        assert finding.category == Category.BUG

    def test_finding_without_line(self) -> None:
        """Test finding without specific line."""
        finding = Finding(
            file="README.md",
            severity=Severity.INFO,
            category=Category.DOCUMENTATION,
            message="Consider adding examples",
        )

        assert finding.line is None
        assert finding.suggestion is None


class TestReviewResult:
    """Tests for ReviewResult model."""

    def test_empty_result(self) -> None:
        """Test result with no findings."""
        result = ReviewResult(
            findings=[],
            summary="No issues found",
            approval=Approval.APPROVE,
        )

        assert result.critical_count == 0
        assert result.error_count == 0
        assert result.has_blocking_issues is False

    def test_result_with_critical_finding(self) -> None:
        """Test result with critical finding."""
        result = ReviewResult(
            findings=[
                Finding(
                    file="auth.py",
                    severity=Severity.CRITICAL,
                    category=Category.SECURITY,
                    message="SQL injection vulnerability",
                )
            ],
            summary="Critical security issue found",
            approval=Approval.REQUEST_CHANGES,
        )

        assert result.critical_count == 1
        assert result.has_blocking_issues is True

    def test_result_counts(self) -> None:
        """Test counting different severity levels."""
        result = ReviewResult(
            findings=[
                Finding(file="a.py", severity=Severity.CRITICAL, category=Category.SECURITY, message="Critical"),
                Finding(file="b.py", severity=Severity.ERROR, category=Category.BUG, message="Error 1"),
                Finding(file="c.py", severity=Severity.ERROR, category=Category.BUG, message="Error 2"),
                Finding(file="d.py", severity=Severity.WARNING, category=Category.STYLE, message="Warning"),
                Finding(file="e.py", severity=Severity.INFO, category=Category.STYLE, message="Info"),
            ],
            summary="Multiple issues",
            approval=Approval.REQUEST_CHANGES,
        )

        assert result.critical_count == 1
        assert result.error_count == 2
        assert len(result.findings) == 5


class TestCodeReviewAgent:
    """Tests for CodeReviewAgent."""

    def test_agent_initialization(self) -> None:
        """Test agent can be created."""
        # Using Ollama as it doesn't require API key
        agent = CodeReviewAgent(provider_name="ollama")

        assert agent.name == "CodeReviewer"
        assert agent.role == "code_reviewer"
        assert agent.provider is not None

    def test_agent_with_custom_model(self) -> None:
        """Test agent with custom model."""
        agent = CodeReviewAgent(provider_name="ollama", model="codellama")

        assert agent.model == "codellama"


class TestSeverityEnum:
    """Tests for Severity enum."""

    def test_all_severities_exist(self) -> None:
        """Test all severity levels are defined."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"
        assert Severity.PRAISE.value == "praise"

    def test_severity_from_string(self) -> None:
        """Test creating severity from string."""
        assert Severity("critical") == Severity.CRITICAL
        assert Severity("warning") == Severity.WARNING


class TestCategoryEnum:
    """Tests for Category enum."""

    def test_common_categories(self) -> None:
        """Test common categories exist."""
        assert Category.SECURITY.value == "security"
        assert Category.BUG.value == "bug"
        assert Category.PERFORMANCE.value == "performance"
        assert Category.STYLE.value == "style"


class TestApprovalEnum:
    """Tests for Approval enum."""

    def test_all_approvals_exist(self) -> None:
        """Test all approval states are defined."""
        assert Approval.APPROVE.value == "approve"
        assert Approval.REQUEST_CHANGES.value == "request_changes"
        assert Approval.COMMENT.value == "comment"
