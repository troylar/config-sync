"""Tests for install v2 CLI command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from devsync.cli.install_v2 import _get_tool_instruction_path, _resolve_source, install_v2_command


class TestResolveSource:
    def test_local_directory(self, tmp_path: Path) -> None:
        result = _resolve_source(str(tmp_path))
        assert result == tmp_path

    def test_nonexistent_path(self) -> None:
        result = _resolve_source("/definitely/not/a/real/path/xyz123")
        assert result is None


class TestGetToolInstructionPath:
    def test_claude_path(self, tmp_path: Path) -> None:
        result = _get_tool_instruction_path("claude", tmp_path, "test-rule")
        assert result is not None
        assert result == tmp_path / ".claude" / "rules" / "test-rule.md"

    def test_cursor_path(self, tmp_path: Path) -> None:
        result = _get_tool_instruction_path("cursor", tmp_path, "test-rule")
        assert result is not None
        assert result == tmp_path / ".cursor" / "rules" / "test-rule.mdc"

    def test_unknown_tool_returns_none(self, tmp_path: Path) -> None:
        result = _get_tool_instruction_path("unknown-tool", tmp_path, "test")
        assert result is None


class TestInstallV2Command:
    def test_install_nonexistent_source(self) -> None:
        result = install_v2_command(source="/nonexistent/package/path")
        assert result == 1

    def test_install_no_manifest(self, tmp_path: Path) -> None:
        result = install_v2_command(source=str(tmp_path))
        assert result == 1

    @patch("devsync.cli.install_v2.find_project_root")
    @patch("devsync.cli.install_v2._resolve_tools", return_value=["claude"])
    @patch("devsync.cli.install_v2.Confirm.ask", return_value=False)
    def test_install_v1_package_file_copy(
        self, mock_confirm: MagicMock, mock_tools: MagicMock, mock_root: MagicMock, tmp_path: Path
    ) -> None:
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        mock_root.return_value = project_dir

        pkg_dir = tmp_path / "package"
        pkg_dir.mkdir()
        instructions_dir = pkg_dir / "instructions"
        instructions_dir.mkdir()
        (instructions_dir / "style.md").write_text("# Style\nUse black.")

        manifest = {
            "name": "test-pkg",
            "version": "1.0.0",
            "description": "Test",
            "author": "Dev",
            "license": "MIT",
            "namespace": "test",
            "components": {
                "instructions": [{"name": "style", "file": "instructions/style.md"}],
            },
        }
        (pkg_dir / "ai-config-kit-package.yaml").write_text(yaml.dump(manifest))

        result = install_v2_command(source=str(pkg_dir), no_ai=True, project_dir=str(project_dir))

        assert result == 0
        installed = project_dir / ".claude" / "rules" / "style.md"
        assert installed.exists()
        assert "Use black" in installed.read_text()
