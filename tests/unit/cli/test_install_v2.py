"""Tests for install v2 CLI command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from devsync.cli.install_v2 import (
    _get_tool_instruction_path,
    _install_pip_dependencies,
    _resolve_source,
    install_v2_command,
)


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


class TestInstallPipDependencies:
    def _make_server(self, name: str = "test-mcp", pip_package: str | None = None, description: str = "") -> MagicMock:
        server = MagicMock()
        server.name = name
        server.pip_package = pip_package
        server.description = description
        return server

    def test_no_pip_servers_does_nothing(self) -> None:
        servers = [self._make_server(pip_package=None)]
        _install_pip_dependencies(servers, skip_pip=False)

    def test_skip_pip_flag(self) -> None:
        servers = [self._make_server(pip_package="mcp-server>=1.0")]
        _install_pip_dependencies(servers, skip_pip=True)

    @patch("devsync.core.pip_utils.validate_pip_spec", return_value=False)
    def test_invalid_spec_skipped(self, mock_validate: MagicMock) -> None:
        servers = [self._make_server(pip_package="bad-spec")]
        _install_pip_dependencies(servers, skip_pip=False)

    @patch("devsync.core.pip_utils.get_installed_version", return_value="1.2.3")
    @patch("devsync.core.pip_utils.validate_pip_spec", return_value=True)
    def test_already_installed_skipped(self, mock_validate: MagicMock, mock_version: MagicMock) -> None:
        servers = [self._make_server(pip_package="mcp-server>=1.0")]
        _install_pip_dependencies(servers, skip_pip=False)

    @patch("devsync.cli.install_v2.Confirm.ask", return_value=False)
    @patch("devsync.core.pip_utils.get_installed_version", return_value=None)
    @patch("devsync.core.pip_utils.validate_pip_spec", return_value=True)
    def test_user_declines(self, mock_validate: MagicMock, mock_version: MagicMock, mock_ask: MagicMock) -> None:
        servers = [self._make_server(pip_package="mcp-server>=1.0")]
        _install_pip_dependencies(servers, skip_pip=False)

    @patch("devsync.core.pip_utils.install_pip_package", return_value=(True, "Successfully installed mcp-server>=1.0"))
    @patch("devsync.cli.install_v2.Confirm.ask", return_value=True)
    @patch("devsync.core.pip_utils.get_installed_version", return_value=None)
    @patch("devsync.core.pip_utils.validate_pip_spec", return_value=True)
    def test_install_success(
        self, mock_validate: MagicMock, mock_version: MagicMock, mock_ask: MagicMock, mock_install: MagicMock
    ) -> None:
        servers = [self._make_server(pip_package="mcp-server>=1.0")]
        _install_pip_dependencies(servers, skip_pip=False)
        mock_install.assert_called_once_with("mcp-server>=1.0")

    @patch("devsync.core.pip_utils.install_pip_package", return_value=(False, "Package not found: bad-pkg"))
    @patch("devsync.cli.install_v2.Confirm.ask", return_value=True)
    @patch("devsync.core.pip_utils.get_installed_version", return_value=None)
    @patch("devsync.core.pip_utils.validate_pip_spec", return_value=True)
    def test_install_failure(
        self, mock_validate: MagicMock, mock_version: MagicMock, mock_ask: MagicMock, mock_install: MagicMock
    ) -> None:
        servers = [self._make_server(pip_package="bad-pkg")]
        _install_pip_dependencies(servers, skip_pip=False)
        mock_install.assert_called_once_with("bad-pkg")


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
