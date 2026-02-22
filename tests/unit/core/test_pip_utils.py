"""Tests for pip_utils module."""

import importlib.metadata
import subprocess
import sys
from unittest.mock import MagicMock, patch

from devsync.core.pip_utils import (
    _extract_base_name,
    find_pip_executable,
    get_installed_version,
    install_pip_package,
    installed_version_satisfies,
    is_pip_installed,
    resolve_pip_package_for_command,
    validate_pip_spec,
)


class TestValidatePipSpec:
    def test_valid_simple_name(self) -> None:
        assert validate_pip_spec("requests") is True

    def test_valid_hyphenated_name(self) -> None:
        assert validate_pip_spec("mcp-server-github") is True

    def test_valid_version_constraint(self) -> None:
        assert validate_pip_spec("requests>=2.28") is True

    def test_valid_exact_version(self) -> None:
        assert validate_pip_spec("requests==2.28.0") is True

    def test_valid_extras(self) -> None:
        assert validate_pip_spec("requests[security]") is True

    def test_valid_extras_with_version(self) -> None:
        assert validate_pip_spec("mcp-server[all]>=1.0") is True

    def test_reject_empty(self) -> None:
        assert validate_pip_spec("") is False

    def test_reject_whitespace(self) -> None:
        assert validate_pip_spec("   ") is False

    def test_reject_git_url(self) -> None:
        assert validate_pip_spec("git+https://github.com/user/repo") is False

    def test_reject_file_url(self) -> None:
        assert validate_pip_spec("file:///tmp/package.whl") is False

    def test_reject_absolute_path(self) -> None:
        assert validate_pip_spec("/tmp/package.whl") is False

    def test_reject_relative_path(self) -> None:
        assert validate_pip_spec("./package.whl") is False

    def test_reject_shell_semicolon(self) -> None:
        assert validate_pip_spec("requests; rm -rf /") is False

    def test_reject_shell_pipe(self) -> None:
        assert validate_pip_spec("requests|evil") is False

    def test_reject_shell_ampersand(self) -> None:
        assert validate_pip_spec("requests&evil") is False

    def test_reject_shell_dollar(self) -> None:
        assert validate_pip_spec("requests$HOME") is False

    def test_reject_backtick(self) -> None:
        assert validate_pip_spec("requests`whoami`") is False


class TestExtractBaseName:
    def test_simple(self) -> None:
        assert _extract_base_name("requests") == "requests"

    def test_with_version(self) -> None:
        assert _extract_base_name("requests>=2.28") == "requests"

    def test_with_extras(self) -> None:
        assert _extract_base_name("requests[security]") == "requests"


class TestIsPipInstalled:
    @patch("devsync.core.pip_utils.importlib.metadata.version")
    def test_installed(self, mock_version: MagicMock) -> None:
        mock_version.return_value = "2.28.0"
        assert is_pip_installed("requests") is True

    @patch("devsync.core.pip_utils.importlib.metadata.version")
    def test_not_installed(self, mock_version: MagicMock) -> None:
        mock_version.side_effect = importlib.metadata.PackageNotFoundError("nope")
        assert is_pip_installed("nonexistent-pkg") is False

    @patch("devsync.core.pip_utils.importlib.metadata.version")
    def test_strips_version(self, mock_version: MagicMock) -> None:
        mock_version.return_value = "1.0"
        assert is_pip_installed("requests>=2.0") is True
        mock_version.assert_called_once_with("requests")


class TestGetInstalledVersion:
    @patch("devsync.core.pip_utils.importlib.metadata.version")
    def test_found(self, mock_version: MagicMock) -> None:
        mock_version.return_value = "1.2.3"
        assert get_installed_version("requests") == "1.2.3"

    @patch("devsync.core.pip_utils.importlib.metadata.version")
    def test_not_found(self, mock_version: MagicMock) -> None:
        mock_version.side_effect = importlib.metadata.PackageNotFoundError("nope")
        assert get_installed_version("nonexistent") is None


class TestResolvePipPackageForCommand:
    @patch("devsync.core.pip_utils._find_distribution_for_module")
    def test_python_m_pattern(self, mock_find: MagicMock) -> None:
        mock_find.return_value = "mcp-server-fetch"
        result = resolve_pip_package_for_command("python", ["-m", "mcp_server_fetch"])
        assert result == "mcp-server-fetch"
        mock_find.assert_called_once_with("mcp_server_fetch")

    @patch("devsync.core.pip_utils._find_distribution_for_module")
    def test_python3_m_pattern(self, mock_find: MagicMock) -> None:
        mock_find.return_value = "some-package"
        result = resolve_pip_package_for_command("python3", ["-m", "some_module"])
        assert result == "some-package"

    def test_uvx_pattern(self) -> None:
        result = resolve_pip_package_for_command("uvx", ["mcp-server-github"])
        assert result == "mcp-server-github"

    def test_uvx_skips_flags(self) -> None:
        result = resolve_pip_package_for_command("uvx", ["--flag", "value"])
        assert result is None

    @patch("devsync.core.pip_utils._find_distribution_for_script")
    def test_console_script_pattern(self, mock_find: MagicMock) -> None:
        mock_find.return_value = "mcp-server-filesystem"
        result = resolve_pip_package_for_command("mcp-server-filesystem", ["--root", "/tmp"])
        assert result == "mcp-server-filesystem"

    @patch("devsync.core.pip_utils._find_distribution_for_script")
    def test_unknown_command(self, mock_find: MagicMock) -> None:
        mock_find.return_value = None
        result = resolve_pip_package_for_command("npx", ["-y", "some-server"])
        assert result is None

    @patch("devsync.core.pip_utils._resolve_pip_package_for_command_inner")
    def test_exception_returns_none(self, mock_inner: MagicMock) -> None:
        mock_inner.side_effect = RuntimeError("unexpected")
        result = resolve_pip_package_for_command("bad", [])
        assert result is None

    def test_full_path_python(self) -> None:
        with patch("devsync.core.pip_utils._find_distribution_for_module") as mock_find:
            mock_find.return_value = "pkg"
            result = resolve_pip_package_for_command("/usr/bin/python3", ["-m", "mod"])
            assert result == "pkg"


class TestInstalledVersionSatisfies:
    @patch("devsync.core.pip_utils.get_installed_version")
    def test_not_installed(self, mock_ver: MagicMock) -> None:
        mock_ver.return_value = None
        assert installed_version_satisfies("requests>=2.0") is False

    @patch("devsync.core.pip_utils.get_installed_version")
    def test_no_constraint(self, mock_ver: MagicMock) -> None:
        mock_ver.return_value = "1.0.0"
        assert installed_version_satisfies("requests") is True

    @patch("devsync.core.pip_utils.get_installed_version")
    def test_satisfies_constraint(self, mock_ver: MagicMock) -> None:
        mock_ver.return_value = "2.28.0"
        assert installed_version_satisfies("requests>=2.0") is True

    @patch("devsync.core.pip_utils.get_installed_version")
    def test_does_not_satisfy_constraint(self, mock_ver: MagicMock) -> None:
        mock_ver.return_value = "1.5.0"
        assert installed_version_satisfies("requests>=2.0") is False

    @patch("devsync.core.pip_utils.get_installed_version")
    def test_packaging_not_available(self, mock_ver: MagicMock) -> None:
        mock_ver.return_value = "1.0.0"
        with patch.dict("sys.modules", {"packaging.specifiers": None, "packaging.version": None}):
            # When packaging is unavailable, falls back to True (installed = good enough)
            assert installed_version_satisfies("requests>=2.0") is True


class TestFindPipExecutable:
    @patch("devsync.core.pip_utils.subprocess.run")
    def test_sys_executable_works(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0)
        result = find_pip_executable()
        assert result == sys.executable

    @patch("devsync.core.pip_utils.shutil.which")
    @patch("devsync.core.pip_utils.subprocess.run")
    def test_fallback_to_which(self, mock_run: MagicMock, mock_which: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1)
        mock_which.return_value = "/usr/bin/pip"
        result = find_pip_executable()
        assert result == "/usr/bin/pip"

    @patch("devsync.core.pip_utils.shutil.which")
    @patch("devsync.core.pip_utils.subprocess.run")
    def test_none_when_unavailable(self, mock_run: MagicMock, mock_which: MagicMock) -> None:
        mock_run.side_effect = OSError("no python")
        mock_which.return_value = None
        result = find_pip_executable()
        assert result is None


class TestInstallPipPackage:
    def test_invalid_spec(self) -> None:
        success, msg = install_pip_package("git+https://evil.com/repo")
        assert success is False
        assert "Invalid pip package spec" in msg

    @patch("devsync.core.pip_utils.find_pip_executable")
    def test_no_pip(self, mock_find: MagicMock) -> None:
        mock_find.return_value = None
        success, msg = install_pip_package("requests")
        assert success is False
        assert "pip is not available" in msg

    @patch("devsync.core.pip_utils.subprocess.run")
    @patch("devsync.core.pip_utils.find_pip_executable")
    def test_success(self, mock_find: MagicMock, mock_run: MagicMock) -> None:
        mock_find.return_value = sys.executable
        mock_run.return_value = MagicMock(returncode=0)
        success, msg = install_pip_package("requests>=2.0")
        assert success is True
        assert "Successfully installed" in msg

    @patch("devsync.core.pip_utils.subprocess.run")
    @patch("devsync.core.pip_utils.find_pip_executable")
    def test_not_found(self, mock_find: MagicMock, mock_run: MagicMock) -> None:
        mock_find.return_value = sys.executable
        mock_run.return_value = MagicMock(returncode=1, stderr="no matching distribution found")
        success, msg = install_pip_package("nonexistent-pkg")
        assert success is False
        assert "Package not found" in msg

    @patch("devsync.core.pip_utils.subprocess.run")
    @patch("devsync.core.pip_utils.find_pip_executable")
    def test_permission_denied(self, mock_find: MagicMock, mock_run: MagicMock) -> None:
        mock_find.return_value = sys.executable
        mock_run.return_value = MagicMock(returncode=1, stderr="permission denied")
        success, msg = install_pip_package("requests")
        assert success is False
        assert "Permission denied" in msg

    @patch("devsync.core.pip_utils.subprocess.run")
    @patch("devsync.core.pip_utils.find_pip_executable")
    def test_timeout(self, mock_find: MagicMock, mock_run: MagicMock) -> None:
        mock_find.return_value = sys.executable
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pip", timeout=120)
        success, msg = install_pip_package("requests", timeout=120)
        assert success is False
        assert "timed out" in msg

    @patch("devsync.core.pip_utils.subprocess.run")
    @patch("devsync.core.pip_utils.find_pip_executable")
    def test_os_error(self, mock_find: MagicMock, mock_run: MagicMock) -> None:
        mock_find.return_value = sys.executable
        mock_run.side_effect = OSError("broken")
        success, msg = install_pip_package("requests")
        assert success is False
        assert "Failed to run pip" in msg

    @patch("devsync.core.pip_utils.subprocess.run")
    @patch("devsync.core.pip_utils.find_pip_executable")
    def test_no_compatible_version(self, mock_find: MagicMock, mock_run: MagicMock) -> None:
        mock_find.return_value = sys.executable
        mock_run.return_value = MagicMock(returncode=1, stderr="could not find a version that satisfies")
        success, msg = install_pip_package("requests>=999.0")
        assert success is False
        assert "No compatible version" in msg

    @patch("devsync.core.pip_utils.subprocess.run")
    @patch("devsync.core.pip_utils.find_pip_executable")
    def test_generic_failure(self, mock_find: MagicMock, mock_run: MagicMock) -> None:
        mock_find.return_value = sys.executable
        mock_run.return_value = MagicMock(returncode=2, stderr="something unexpected")
        success, msg = install_pip_package("requests")
        assert success is False
        assert "exit code 2" in msg
