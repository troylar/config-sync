"""Tests for prompt templates."""

from devsync.llm.prompts import (
    ADAPT_PRACTICE_PROMPT,
    EXTRACT_MCP_PROMPT,
    EXTRACT_PRACTICES_PROMPT,
    MERGE_PRACTICES_PROMPT,
    format_files_for_extraction,
)


class TestPromptTemplates:
    def test_extract_practices_has_placeholder(self) -> None:
        assert "{files_content}" in EXTRACT_PRACTICES_PROMPT

    def test_extract_practices_renders(self) -> None:
        result = EXTRACT_PRACTICES_PROMPT.format(files_content="# Rule 1\nBe safe")
        assert "# Rule 1" in result
        assert "practices" in result

    def test_extract_mcp_has_placeholder(self) -> None:
        assert "{mcp_config}" in EXTRACT_MCP_PROMPT

    def test_adapt_practice_renders(self) -> None:
        result = ADAPT_PRACTICE_PROMPT.format(
            practice_json='{"name": "test"}',
            existing_rules="# Existing\nRule 1",
            tool_name="cursor",
        )
        assert "cursor" in result
        assert "test" in result

    def test_merge_practices_renders(self) -> None:
        result = MERGE_PRACTICES_PROMPT.format(
            existing_content="# Old rules",
            incoming_content="# New rules",
        )
        assert "Old rules" in result
        assert "New rules" in result


class TestFormatFilesForExtraction:
    def test_single_file(self) -> None:
        files = {"rules/style.md": "# Style Guide\nUse black."}
        result = format_files_for_extraction(files)
        assert "--- rules/style.md ---" in result
        assert "Use black." in result

    def test_multiple_files(self) -> None:
        files = {
            "rules/style.md": "# Style",
            "rules/testing.md": "# Testing",
        }
        result = format_files_for_extraction(files)
        assert "--- rules/style.md ---" in result
        assert "--- rules/testing.md ---" in result

    def test_empty_files(self) -> None:
        result = format_files_for_extraction({})
        assert result == ""
