"""Data models for agent outputs."""

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity level of a finding."""

    CRITICAL = "critical"  # Must fix before merge (security, crashes)
    ERROR = "error"        # Should fix (bugs, broken functionality)
    WARNING = "warning"    # Consider fixing (potential issues)
    INFO = "info"          # Suggestions (style, best practices)
    PRAISE = "praise"      # Positive feedback (good patterns)


class Category(str, Enum):
    """Category of a finding."""

    SECURITY = "security"           # Security vulnerabilities
    BUG = "bug"                     # Logic errors, bugs
    PERFORMANCE = "performance"     # Performance issues
    STYLE = "style"                 # Code style, formatting
    BEST_PRACTICE = "best_practice" # Best practices, patterns
    DOCUMENTATION = "documentation" # Comments, docs
    TESTING = "testing"             # Test coverage, test quality
    ERROR_HANDLING = "error_handling"  # Exception handling
    TYPE_SAFETY = "type_safety"     # Type hints, type issues
    OTHER = "other"                 # Anything else


class Approval(str, Enum):
    """Review approval status."""

    APPROVE = "approve"             # Good to merge
    REQUEST_CHANGES = "request_changes"  # Changes needed
    COMMENT = "comment"             # Just comments, no strong opinion


class Finding(BaseModel):
    """A single review finding."""

    file: str = Field(description="File path where the issue was found")
    line: int | None = Field(default=None, description="Line number (if applicable)")
    severity: Severity = Field(description="How serious is this issue")
    category: Category = Field(description="What type of issue is this")
    message: str = Field(description="Description of the issue")
    suggestion: str | None = Field(default=None, description="How to fix it")
    code_snippet: str | None = Field(default=None, description="Relevant code")


class ReviewResult(BaseModel):
    """Complete review result from an agent."""

    findings: list[Finding] = Field(default_factory=list, description="All findings")
    summary: str = Field(description="Brief summary of the review")
    approval: Approval = Field(description="Overall approval recommendation")
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence in this review (0-1)",
    )
    agent_name: str = Field(default="code_reviewer", description="Name of the reviewing agent")

    @property
    def critical_count(self) -> int:
        """Count of critical findings."""
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def error_count(self) -> int:
        """Count of error findings."""
        return sum(1 for f in self.findings if f.severity == Severity.ERROR)

    @property
    def has_blocking_issues(self) -> bool:
        """Check if there are critical or error findings."""
        return self.critical_count > 0 or self.error_count > 0
