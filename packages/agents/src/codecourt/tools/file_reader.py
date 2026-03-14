"""File reading utilities for code context."""

from pathlib import Path

from pydantic import BaseModel, Field


class FileContext(BaseModel):
    """Context around a specific line in a file."""

    file_path: str
    target_line: int
    start_line: int
    end_line: int
    content: str
    lines: list[str] = Field(default_factory=list)
    language: str | None = None


class FileContent(BaseModel):
    """Full file content with metadata."""

    path: str
    content: str
    lines: list[str] = Field(default_factory=list)
    line_count: int = 0
    language: str | None = None
    exists: bool = True
    error: str | None = None


def read_file(file_path: str | Path) -> FileContent:
    """
    Read a file and return its content with metadata.

    Args:
        file_path: Path to the file

    Returns:
        FileContent with the file's content, or error if not readable.
    """
    path = Path(file_path)

    if not path.exists():
        return FileContent(
            path=str(path),
            content="",
            exists=False,
            error=f"File not found: {path}",
        )

    try:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Detect language from extension
        from codecourt.tools.git_diff import detect_language

        return FileContent(
            path=str(path),
            content=content,
            lines=lines,
            line_count=len(lines),
            language=detect_language(str(path)),
        )
    except Exception as e:
        return FileContent(
            path=str(path),
            content="",
            exists=True,
            error=f"Error reading file: {e}",
        )


def read_file_context(
    file_path: str | Path,
    line_number: int,
    context_lines: int = 5,
) -> FileContext:
    """
    Read a specific line from a file with surrounding context.

    This is useful for understanding changes in context. For example,
    if a line was added, you might want to see what's around it.

    Args:
        file_path: Path to the file
        line_number: The line to center on (1-indexed)
        context_lines: Number of lines to include before and after

    Returns:
        FileContext with the target line and its context.

    Example:
        >>> ctx = read_file_context("src/auth.py", line_number=17, context_lines=3)
        >>> print(ctx.content)
        # Shows lines 14-20 with line 17 highlighted
    """
    file_content = read_file(file_path)

    if file_content.error:
        return FileContext(
            file_path=str(file_path),
            target_line=line_number,
            start_line=line_number,
            end_line=line_number,
            content=f"Error: {file_content.error}",
        )

    # Calculate range (1-indexed to 0-indexed)
    line_idx = line_number - 1
    start_idx = max(0, line_idx - context_lines)
    end_idx = min(len(file_content.lines), line_idx + context_lines + 1)

    # Extract lines
    context_content = file_content.lines[start_idx:end_idx]

    # Format with line numbers
    formatted_lines = []
    for i, line in enumerate(context_content):
        actual_line_num = start_idx + i + 1
        marker = ">>>" if actual_line_num == line_number else "   "
        formatted_lines.append(f"{marker} {actual_line_num:4d} | {line}")

    return FileContext(
        file_path=str(file_path),
        target_line=line_number,
        start_line=start_idx + 1,
        end_line=end_idx,
        content="\n".join(formatted_lines),
        lines=context_content,
        language=file_content.language,
    )


def read_multiple_contexts(
    file_path: str | Path,
    line_numbers: list[int],
    context_lines: int = 3,
) -> list[FileContext]:
    """
    Read multiple line contexts from a file efficiently.

    Useful when reviewing a file with changes in multiple places.

    Args:
        file_path: Path to the file
        line_numbers: List of line numbers to get context for
        context_lines: Number of lines to include around each

    Returns:
        List of FileContext objects, one per line number.
    """
    return [
        read_file_context(file_path, line_num, context_lines)
        for line_num in line_numbers
    ]
