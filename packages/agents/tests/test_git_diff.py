"""Tests for git diff parsing."""

import pytest

from codecourt.tools import (
    ChangeType,
    detect_language,
    format_diff_for_review,
    parse_diff,
)


class TestDetectLanguage:
    """Tests for language detection."""

    def test_python_file(self) -> None:
        assert detect_language("src/main.py") == "python"

    def test_typescript_file(self) -> None:
        assert detect_language("components/Button.tsx") == "typescript"

    def test_javascript_file(self) -> None:
        assert detect_language("app.js") == "javascript"

    def test_unknown_extension(self) -> None:
        assert detect_language("README.txt") is None

    def test_no_extension(self) -> None:
        assert detect_language("Makefile") is None


class TestParseDiff:
    """Tests for diff parsing."""

    SIMPLE_DIFF = """diff --git a/hello.py b/hello.py
--- a/hello.py
+++ b/hello.py
@@ -1,3 +1,4 @@
 def hello():
-    print("hi")
+    print("hello")
+    print("world")
"""

    def test_parse_simple_diff(self) -> None:
        """Test parsing a simple diff."""
        result = parse_diff(self.SIMPLE_DIFF)

        assert len(result.files) == 1
        assert result.files[0].path == "hello.py"
        assert result.files[0].language == "python"

    def test_count_additions(self) -> None:
        """Test counting added lines."""
        result = parse_diff(self.SIMPLE_DIFF)

        assert result.total_additions == 2

    def test_count_deletions(self) -> None:
        """Test counting removed lines."""
        result = parse_diff(self.SIMPLE_DIFF)

        assert result.total_deletions == 1

    def test_parse_hunks(self) -> None:
        """Test that hunks are parsed correctly."""
        result = parse_diff(self.SIMPLE_DIFF)

        assert len(result.files[0].hunks) == 1
        hunk = result.files[0].hunks[0]
        assert hunk.old_start == 1
        assert hunk.new_start == 1

    def test_parse_line_types(self) -> None:
        """Test that line types are detected correctly."""
        result = parse_diff(self.SIMPLE_DIFF)

        hunk = result.files[0].hunks[0]
        line_types = [line.change_type for line in hunk.lines]

        assert ChangeType.CONTEXT in line_types  # "def hello():"
        assert ChangeType.REMOVED in line_types  # "print("hi")"
        assert ChangeType.ADDED in line_types    # "print("hello")"

    def test_changed_files_property(self) -> None:
        """Test the changed_files property."""
        result = parse_diff(self.SIMPLE_DIFF)

        assert result.changed_files == ["hello.py"]


class TestNewFileDiff:
    """Tests for new file detection."""

    NEW_FILE_DIFF = """diff --git a/new_file.py b/new_file.py
--- /dev/null
+++ b/new_file.py
@@ -0,0 +1,3 @@
+def new_function():
+    pass
+
"""

    def test_detect_new_file(self) -> None:
        """Test detecting a new file."""
        result = parse_diff(self.NEW_FILE_DIFF)

        assert len(result.files) == 1
        assert result.files[0].is_new_file is True
        assert result.files[0].old_path is None


class TestDeletedFileDiff:
    """Tests for deleted file detection."""

    DELETED_FILE_DIFF = """diff --git a/old_file.py b/old_file.py
--- a/old_file.py
+++ /dev/null
@@ -1,3 +0,0 @@
-def old_function():
-    pass
-
"""

    def test_detect_deleted_file(self) -> None:
        """Test detecting a deleted file."""
        result = parse_diff(self.DELETED_FILE_DIFF)

        assert len(result.files) == 1
        assert result.files[0].is_deleted is True
        assert result.files[0].new_path is None


class TestMultiFileDiff:
    """Tests for diffs with multiple files."""

    MULTI_FILE_DIFF = """diff --git a/file1.py b/file1.py
--- a/file1.py
+++ b/file1.py
@@ -1,2 +1,2 @@
-old line
+new line
diff --git a/file2.js b/file2.js
--- a/file2.js
+++ b/file2.js
@@ -5,3 +5,4 @@
 const x = 1;
+const y = 2;
"""

    def test_parse_multiple_files(self) -> None:
        """Test parsing diff with multiple files."""
        result = parse_diff(self.MULTI_FILE_DIFF)

        assert len(result.files) == 2
        assert result.changed_files == ["file1.py", "file2.js"]

    def test_different_languages(self) -> None:
        """Test that different languages are detected."""
        result = parse_diff(self.MULTI_FILE_DIFF)

        assert result.files[0].language == "python"
        assert result.files[1].language == "javascript"


class TestFormatDiffForReview:
    """Tests for formatting diff for LLM review."""

    SIMPLE_DIFF = """diff --git a/hello.py b/hello.py
--- a/hello.py
+++ b/hello.py
@@ -1,3 +1,4 @@
 def hello():
-    print("hi")
+    print("hello")
+    print("world")
"""

    def test_format_includes_file_path(self) -> None:
        """Test that formatted output includes file path."""
        parsed = parse_diff(self.SIMPLE_DIFF)
        formatted = format_diff_for_review(parsed)

        assert "hello.py" in formatted

    def test_format_includes_language(self) -> None:
        """Test that formatted output includes language."""
        parsed = parse_diff(self.SIMPLE_DIFF)
        formatted = format_diff_for_review(parsed)

        assert "python" in formatted.lower()

    def test_format_shows_additions(self) -> None:
        """Test that additions are marked with +."""
        parsed = parse_diff(self.SIMPLE_DIFF)
        formatted = format_diff_for_review(parsed)

        assert "+ L" in formatted  # Added lines show with +
