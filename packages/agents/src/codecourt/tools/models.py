"""Data models for git diff parsing."""

from enum import Enum

from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    """Type of change in a diff."""

    ADDED = "added"
    REMOVED = "removed"
    CONTEXT = "context"  # Unchanged lines shown for context


class DiffLine(BaseModel):
    """A single line in a diff."""

    line_number: int | None = Field(
        description="Line number in the new file (None for removed lines)"
    )
    old_line_number: int | None = Field(
        description="Line number in the old file (None for added lines)"
    )
    content: str = Field(description="The actual line content (without +/- prefix)")
    change_type: ChangeType = Field(description="Whether line was added, removed, or context")


class DiffHunk(BaseModel):
    """
    A 'hunk' is a contiguous block of changes.

    Example hunk header: @@ -15,7 +15,8 @@
    This means: starting at line 15, showing 7 lines from old file, 8 from new.
    """

    old_start: int = Field(description="Starting line in the old file")
    old_count: int = Field(description="Number of lines from old file")
    new_start: int = Field(description="Starting line in the new file")
    new_count: int = Field(description="Number of lines from new file")
    lines: list[DiffLine] = Field(default_factory=list, description="Lines in this hunk")
    header: str = Field(default="", description="Optional function/class context from @@ line")


class DiffFile(BaseModel):
    """A single file's changes in a diff."""

    old_path: str | None = Field(description="Original file path (None if new file)")
    new_path: str | None = Field(description="New file path (None if deleted)")
    hunks: list[DiffHunk] = Field(default_factory=list, description="Change blocks in this file")
    is_new_file: bool = Field(default=False, description="True if file was created")
    is_deleted: bool = Field(default=False, description="True if file was deleted")
    is_renamed: bool = Field(default=False, description="True if file was renamed")
    language: str | None = Field(default=None, description="Detected programming language")

    @property
    def path(self) -> str:
        """Get the most relevant path (new path for existing files, old for deleted)."""
        return self.new_path or self.old_path or "unknown"

    @property
    def added_lines(self) -> list[DiffLine]:
        """Get all added lines across all hunks."""
        lines = []
        for hunk in self.hunks:
            lines.extend(line for line in hunk.lines if line.change_type == ChangeType.ADDED)
        return lines

    @property
    def removed_lines(self) -> list[DiffLine]:
        """Get all removed lines across all hunks."""
        lines = []
        for hunk in self.hunks:
            lines.extend(line for line in hunk.lines if line.change_type == ChangeType.REMOVED)
        return lines


class ParsedDiff(BaseModel):
    """Complete parsed diff containing all file changes."""

    files: list[DiffFile] = Field(default_factory=list, description="All changed files")
    raw_diff: str = Field(default="", description="Original diff text")

    @property
    def total_additions(self) -> int:
        """Count total added lines."""
        return sum(len(f.added_lines) for f in self.files)

    @property
    def total_deletions(self) -> int:
        """Count total removed lines."""
        return sum(len(f.removed_lines) for f in self.files)

    @property
    def changed_files(self) -> list[str]:
        """List all changed file paths."""
        return [f.path for f in self.files]
