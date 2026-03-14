"""Git diff parsing utilities."""

import re
from pathlib import Path

from codecourt.tools.models import (
    ChangeType,
    DiffFile,
    DiffHunk,
    DiffLine,
    ParsedDiff,
)

# Regex patterns for parsing diffs
DIFF_FILE_HEADER = re.compile(r"^diff --git a/(.*) b/(.*)$")
HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")
OLD_FILE = re.compile(r"^--- (?:a/)?(.*)$")
NEW_FILE = re.compile(r"^\+\+\+ (?:b/)?(.*)$")

# File extension to language mapping
LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".sql": "sql",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
    ".xml": "xml",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".md": "markdown",
}


def detect_language(file_path: str) -> str | None:
    """Detect programming language from file extension."""
    suffix = Path(file_path).suffix.lower()
    return LANGUAGE_MAP.get(suffix)


def parse_diff(diff_text: str) -> ParsedDiff:
    """
    Parse a unified diff into structured data.

    Args:
        diff_text: Raw diff text (e.g., from `git diff` or GitHub API)

    Returns:
        ParsedDiff with all files and their changes.

    Example:
        >>> diff = '''
        ... diff --git a/hello.py b/hello.py
        ... --- a/hello.py
        ... +++ b/hello.py
        ... @@ -1,3 +1,4 @@
        ...  def hello():
        ... -    print("hi")
        ... +    print("hello")
        ... +    print("world")
        ... '''
        >>> result = parse_diff(diff)
        >>> result.files[0].path
        'hello.py'
        >>> result.total_additions
        2
        >>> result.total_deletions
        1
    """
    files: list[DiffFile] = []
    current_file: DiffFile | None = None
    current_hunk: DiffHunk | None = None

    # Track line numbers as we parse
    old_line = 0
    new_line = 0

    lines = diff_text.split("\n")

    for line in lines:
        # Check for new file header: diff --git a/path b/path
        file_match = DIFF_FILE_HEADER.match(line)
        if file_match:
            # Save previous file if exists
            if current_file is not None:
                if current_hunk is not None:
                    current_file.hunks.append(current_hunk)
                files.append(current_file)

            # Start new file
            old_path, new_path = file_match.groups()
            current_file = DiffFile(
                old_path=old_path,
                new_path=new_path,
                language=detect_language(new_path),
            )
            current_hunk = None
            continue

        # Check for --- a/path (old file)
        old_match = OLD_FILE.match(line)
        if old_match and current_file:
            path = old_match.group(1)
            if path == "/dev/null":
                current_file.is_new_file = True
                current_file.old_path = None
            continue

        # Check for +++ b/path (new file)
        new_match = NEW_FILE.match(line)
        if new_match and current_file:
            path = new_match.group(1)
            if path == "/dev/null":
                current_file.is_deleted = True
                current_file.new_path = None
            continue

        # Check for hunk header: @@ -start,count +start,count @@ context
        hunk_match = HUNK_HEADER.match(line)
        if hunk_match and current_file:
            # Save previous hunk
            if current_hunk is not None:
                current_file.hunks.append(current_hunk)

            # Parse hunk header
            old_start = int(hunk_match.group(1))
            old_count = int(hunk_match.group(2) or 1)
            new_start = int(hunk_match.group(3))
            new_count = int(hunk_match.group(4) or 1)
            header = hunk_match.group(5).strip()

            current_hunk = DiffHunk(
                old_start=old_start,
                old_count=old_count,
                new_start=new_start,
                new_count=new_count,
                header=header,
            )

            old_line = old_start
            new_line = new_start
            continue

        # Parse diff content lines
        if current_hunk is not None and len(line) > 0:
            first_char = line[0] if line else " "
            content = line[1:] if len(line) > 1 else ""

            if first_char == "+":
                # Added line
                current_hunk.lines.append(
                    DiffLine(
                        line_number=new_line,
                        old_line_number=None,
                        content=content,
                        change_type=ChangeType.ADDED,
                    )
                )
                new_line += 1

            elif first_char == "-":
                # Removed line
                current_hunk.lines.append(
                    DiffLine(
                        line_number=None,
                        old_line_number=old_line,
                        content=content,
                        change_type=ChangeType.REMOVED,
                    )
                )
                old_line += 1

            elif first_char == " ":
                # Context line (unchanged)
                current_hunk.lines.append(
                    DiffLine(
                        line_number=new_line,
                        old_line_number=old_line,
                        content=content,
                        change_type=ChangeType.CONTEXT,
                    )
                )
                old_line += 1
                new_line += 1

            # Skip lines starting with \ (e.g., "\ No newline at end of file")

    # Don't forget the last file and hunk!
    if current_file is not None:
        if current_hunk is not None:
            current_file.hunks.append(current_hunk)
        files.append(current_file)

    return ParsedDiff(files=files, raw_diff=diff_text)


def format_diff_for_review(parsed: ParsedDiff, include_context: bool = True) -> str:
    """
    Format parsed diff into a clean string for LLM review.

    This creates a readable format that's easier for LLMs to understand
    than raw unified diff format.

    Args:
        parsed: Parsed diff object
        include_context: Whether to include unchanged context lines

    Returns:
        Formatted string suitable for LLM input.
    """
    output = []

    for file in parsed.files:
        # File header
        status = ""
        if file.is_new_file:
            status = " (NEW FILE)"
        elif file.is_deleted:
            status = " (DELETED)"
        elif file.is_renamed:
            status = f" (RENAMED from {file.old_path})"

        output.append(f"## File: {file.path}{status}")
        if file.language:
            output.append(f"Language: {file.language}")
        output.append("")

        # Each hunk
        for hunk in file.hunks:
            if hunk.header:
                output.append(f"### {hunk.header}")

            for line in hunk.lines:
                if line.change_type == ChangeType.ADDED:
                    output.append(f"  + L{line.line_number}: {line.content}")
                elif line.change_type == ChangeType.REMOVED:
                    output.append(f"  - L{line.old_line_number}: {line.content}")
                elif include_context:
                    output.append(f"    L{line.line_number}: {line.content}")

            output.append("")

    return "\n".join(output)
