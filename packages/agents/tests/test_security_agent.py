"""Tests for the Security Agent."""

import pytest

from codecourt.agents import (
    Approval,
    Category,
    Finding,
    ReviewResult,
    SecurityAgent,
    Severity,
)


class TestSecurityAgent:
    """Tests for SecurityAgent."""

    def test_agent_initialization(self) -> None:
        """Test agent can be created."""
        agent = SecurityAgent(provider_name="ollama")

        assert agent.name == "SecurityBailiff"
        assert agent.role == "security_reviewer"
        assert agent.provider is not None

    def test_agent_with_custom_model(self) -> None:
        """Test agent with custom model."""
        agent = SecurityAgent(provider_name="openai", model="gpt-4o")

        assert agent.model == "gpt-4o"

    def test_agent_name_reflects_role(self) -> None:
        """Test that agent name reflects its security role."""
        agent = SecurityAgent(provider_name="ollama")

        assert "Security" in agent.name or "Bailiff" in agent.name


class TestSecurityFindings:
    """Tests for security-specific findings."""

    def test_critical_finding_structure(self) -> None:
        """Test creating a critical security finding."""
        finding = Finding(
            file="auth.py",
            line=42,
            severity=Severity.CRITICAL,
            category=Category.SECURITY,
            message="SQL injection vulnerability [Type: sql_injection] [CWE-89]",
            suggestion="Use parameterized queries",
        )

        assert finding.severity == Severity.CRITICAL
        assert finding.category == Category.SECURITY
        assert "SQL injection" in finding.message

    def test_secret_exposure_finding(self) -> None:
        """Test finding for exposed secret."""
        finding = Finding(
            file="config.py",
            line=10,
            severity=Severity.CRITICAL,
            category=Category.SECURITY,
            message="Hardcoded API key detected [Type: secret_exposure] [CWE-798]",
            suggestion="Move to environment variable",
        )

        assert finding.severity == Severity.CRITICAL
        assert "API key" in finding.message


class TestSecurityReviewResult:
    """Tests for security review results."""

    def test_empty_security_review(self) -> None:
        """Test result with no security issues."""
        result = ReviewResult(
            findings=[],
            summary="No security vulnerabilities found",
            approval=Approval.APPROVE,
            agent_name="SecurityBailiff",
        )

        assert result.approval == Approval.APPROVE
        assert len(result.findings) == 0

    def test_critical_security_review(self) -> None:
        """Test result with critical security issue."""
        result = ReviewResult(
            findings=[
                Finding(
                    file="db.py",
                    line=25,
                    severity=Severity.CRITICAL,
                    category=Category.SECURITY,
                    message="SQL injection via user input",
                )
            ],
            summary="Critical: SQL injection vulnerability found",
            approval=Approval.REQUEST_CHANGES,
            agent_name="SecurityBailiff",
        )

        assert result.approval == Approval.REQUEST_CHANGES
        assert result.critical_count == 1
        assert result.has_blocking_issues is True

    def test_all_findings_are_security_category(self) -> None:
        """Test that all findings from security agent are security category."""
        result = ReviewResult(
            findings=[
                Finding(
                    file="a.py",
                    severity=Severity.CRITICAL,
                    category=Category.SECURITY,
                    message="Issue 1",
                ),
                Finding(
                    file="b.py",
                    severity=Severity.WARNING,
                    category=Category.SECURITY,
                    message="Issue 2",
                ),
            ],
            summary="Security review",
            approval=Approval.REQUEST_CHANGES,
            agent_name="SecurityBailiff",
        )

        # All findings should be security category
        for finding in result.findings:
            assert finding.category == Category.SECURITY


class TestSecurityVulnerabilityTypes:
    """Tests for different vulnerability types."""

    @pytest.mark.parametrize(
        "vuln_type,description",
        [
            ("sql_injection", "SQL query with string concatenation"),
            ("xss", "Unsanitized user input in HTML output"),
            ("command_injection", "User input in subprocess call"),
            ("hardcoded_secret", "API key in source code"),
            ("weak_crypto", "MD5 used for password hashing"),
            ("missing_auth", "Endpoint without authentication check"),
            ("path_traversal", "User input in file path without validation"),
        ],
    )
    def test_vulnerability_type_finding(self, vuln_type: str, description: str) -> None:
        """Test creating findings for different vulnerability types."""
        finding = Finding(
            file="vulnerable.py",
            line=1,
            severity=Severity.CRITICAL,
            category=Category.SECURITY,
            message=f"{description} [Type: {vuln_type}]",
        )

        assert vuln_type in finding.message
        assert finding.category == Category.SECURITY
