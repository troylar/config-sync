"""Unit tests for path utilities."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aiconfigkit.utils.paths import (
    ensure_directory_exists,
    get_claude_config_dir,
    get_claude_desktop_config_path,
    get_copilot_config_dir,
    get_cursor_config_dir,
    get_cursor_mcp_config_path,
    get_devsync_data_dir,
    get_home_directory,
    get_installation_tracker_path,
    get_library_dir,
    get_windsurf_mcp_config_path,
    get_winsurf_config_dir,
    resolve_conflict_name,
    safe_file_name,
)


class TestGetHomeDirectory:
    """Test get_home_directory function."""

    def test_returns_path(self) -> None:
        """Test that home directory is returned as Path."""
        home = get_home_directory()
        assert isinstance(home, Path)
        assert home.exists()


class TestGetCursorConfigDir:
    """Test get_cursor_config_dir function."""

    @pytest.mark.skipif(os.name == "nt", reason="os.uname not available on Windows")
    @patch("os.name", "posix")
    @patch("os.uname")
    def test_cursor_config_macos(self, mock_uname: MagicMock) -> None:
        """Test Cursor config directory on macOS."""
        mock_uname.return_value = MagicMock(sysname="Darwin")
        config_dir = get_cursor_config_dir()
        assert "Library/Application Support/Cursor" in str(config_dir)

    @pytest.mark.skipif(os.name == "nt", reason="os.uname not available on Windows")
    @patch("os.name", "posix")
    @patch("os.uname")
    def test_cursor_config_linux(self, mock_uname: MagicMock) -> None:
        """Test Cursor config directory on Linux."""
        mock_uname.return_value = MagicMock(sysname="Linux")
        config_dir = get_cursor_config_dir()
        assert ".config/Cursor" in str(config_dir)

    @pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
    def test_cursor_config_windows_native(self) -> None:
        """Test Cursor config directory on actual Windows."""
        if os.name == "nt":
            config_dir = get_cursor_config_dir()
            assert "AppData" in str(config_dir) and "Cursor" in str(config_dir)


class TestGetCopilotConfigDir:
    """Test get_copilot_config_dir function."""

    @pytest.mark.skipif(os.name == "nt", reason="os.uname not available on Windows")
    @patch("os.name", "posix")
    @patch("os.uname")
    def test_copilot_config_macos(self, mock_uname: MagicMock) -> None:
        """Test Copilot config directory on macOS."""
        mock_uname.return_value = MagicMock(sysname="Darwin")
        config_dir = get_copilot_config_dir()
        assert "Library/Application Support/Code" in str(config_dir)
        assert "github.copilot" in str(config_dir)

    @pytest.mark.skipif(os.name == "nt", reason="os.uname not available on Windows")
    @patch("os.name", "posix")
    @patch("os.uname")
    def test_copilot_config_linux(self, mock_uname: MagicMock) -> None:
        """Test Copilot config directory on Linux."""
        mock_uname.return_value = MagicMock(sysname="Linux")
        config_dir = get_copilot_config_dir()
        assert ".config/Code" in str(config_dir)
        assert "github.copilot" in str(config_dir)

    @pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
    def test_copilot_config_windows_native(self) -> None:
        """Test Copilot config directory on actual Windows."""
        if os.name == "nt":
            config_dir = get_copilot_config_dir()
            assert "AppData" in str(config_dir)
            assert "Code" in str(config_dir)
            assert "github.copilot" in str(config_dir)


class TestGetWinsurfConfigDir:
    """Test get_winsurf_config_dir function."""

    @pytest.mark.skipif(os.name == "nt", reason="os.uname not available on Windows")
    @patch("os.name", "posix")
    @patch("os.uname")
    def test_winsurf_config_macos(self, mock_uname: MagicMock) -> None:
        """Test Windsurf config directory on macOS."""
        mock_uname.return_value = MagicMock(sysname="Darwin")
        config_dir = get_winsurf_config_dir()
        assert "Library/Application Support/Windsurf" in str(config_dir)

    @pytest.mark.skipif(os.name == "nt", reason="os.uname not available on Windows")
    @patch("os.name", "posix")
    @patch("os.uname")
    def test_winsurf_config_linux(self, mock_uname: MagicMock) -> None:
        """Test Windsurf config directory on Linux."""
        mock_uname.return_value = MagicMock(sysname="Linux")
        config_dir = get_winsurf_config_dir()
        assert ".config/Windsurf" in str(config_dir)

    @pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
    def test_winsurf_config_windows_native(self) -> None:
        """Test Windsurf config directory on actual Windows."""
        if os.name == "nt":
            config_dir = get_winsurf_config_dir()
            assert "AppData" in str(config_dir) and "Windsurf" in str(config_dir)


class TestGetClaudeConfigDir:
    """Test get_claude_config_dir function."""

    def test_claude_config_dir(self) -> None:
        """Test Claude config directory (same on all platforms)."""
        config_dir = get_claude_config_dir()
        # Convert to POSIX path for cross-platform comparison
        assert ".claude/rules" in config_dir.as_posix()


class TestGetClaudeDesktopConfigPath:
    """Test get_claude_desktop_config_path function."""

    @pytest.mark.skipif(os.name == "nt", reason="os.uname not available on Windows")
    @patch("os.name", "posix")
    @patch("os.uname")
    def test_claude_desktop_config_macos(self, mock_uname: MagicMock) -> None:
        """Test Claude Desktop config path on macOS."""
        mock_uname.return_value = MagicMock(sysname="Darwin")
        config_path = get_claude_desktop_config_path()
        assert "Library/Application Support/Claude" in str(config_path)
        assert "claude_desktop_config.json" in str(config_path)

    @pytest.mark.skipif(os.name == "nt", reason="os.uname not available on Windows")
    @patch("os.name", "posix")
    @patch("os.uname")
    def test_claude_desktop_config_linux(self, mock_uname: MagicMock) -> None:
        """Test Claude Desktop config path on Linux."""
        mock_uname.return_value = MagicMock(sysname="Linux")
        config_path = get_claude_desktop_config_path()
        assert ".config/Claude" in str(config_path)
        assert "claude_desktop_config.json" in str(config_path)

    @pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
    def test_claude_desktop_config_windows(self) -> None:
        """Test Claude Desktop config path on Windows."""
        config_path = get_claude_desktop_config_path()
        assert "AppData" in str(config_path)
        assert "Claude" in str(config_path)
        assert "claude_desktop_config.json" in str(config_path)

    @pytest.mark.skipif(os.name == "nt", reason="os.name mocking conflicts on Windows")
    @patch("os.name", "unknown")
    def test_claude_desktop_config_unsupported_os(self) -> None:
        """Test that unsupported OS raises error."""
        with pytest.raises(OSError, match="Unsupported operating system"):
            get_claude_desktop_config_path()


class TestGetCursorMcpConfigPath:
    """Test get_cursor_mcp_config_path function."""

    @pytest.mark.skipif(os.name == "nt", reason="os.uname not available on Windows")
    @patch("os.name", "posix")
    @patch("os.uname")
    def test_cursor_mcp_config_path(self, mock_uname: MagicMock) -> None:
        """Test Cursor MCP config path."""
        mock_uname.return_value = MagicMock(sysname="Darwin")
        config_path = get_cursor_mcp_config_path()
        assert "mcp_config.json" in str(config_path)
        assert "Cursor" in str(config_path)


class TestGetWinsurfMcpConfigPath:
    """Test get_windsurf_mcp_config_path function."""

    @pytest.mark.skipif(os.name == "nt", reason="os.uname not available on Windows")
    @patch("os.name", "posix")
    @patch("os.uname")
    def test_windsurf_mcp_config_path(self, mock_uname: MagicMock) -> None:
        """Test Windsurf MCP config path."""
        mock_uname.return_value = MagicMock(sysname="Darwin")
        config_path = get_windsurf_mcp_config_path()
        assert "mcp_config.json" in str(config_path)
        assert "Windsurf" in str(config_path)


class TestGetInstructionkitDataDir:
    """Test get_devsync_data_dir function."""

    def test_creates_data_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that data directory is created."""
        # Use tmp_path as home directory
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

        data_dir = get_devsync_data_dir()
        assert data_dir.exists()
        assert ".instructionkit" in str(data_dir)


class TestGetLibraryDir:
    """Test get_library_dir function."""

    def test_creates_library_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that library directory is created."""
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

        library_dir = get_library_dir()
        assert library_dir.exists()
        assert "library" in str(library_dir)


class TestGetInstallationTrackerPath:
    """Test get_installation_tracker_path function."""

    def test_installation_tracker_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test installation tracker path."""
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

        tracker_path = get_installation_tracker_path()
        assert "installations.json" in str(tracker_path)


class TestEnsureDirectoryExists:
    """Test ensure_directory_exists function."""

    def test_creates_directory(self, tmp_path: Path) -> None:
        """Test creating a new directory."""
        new_dir = tmp_path / "new" / "nested" / "directory"
        ensure_directory_exists(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_existing_directory(self, tmp_path: Path) -> None:
        """Test with existing directory (should not raise error)."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        ensure_directory_exists(existing_dir)
        assert existing_dir.exists()


class TestSafeFileName:
    """Test safe_file_name function."""

    def test_safe_name_no_changes(self) -> None:
        """Test filename that needs no changes."""
        assert safe_file_name("normal-file-name.txt") == "normal-file-name.txt"
        assert safe_file_name("file123.md") == "file123.md"

    def test_replace_unsafe_characters(self) -> None:
        """Test replacing unsafe characters."""
        assert safe_file_name("file<name>.txt") == "file_name_.txt"
        assert safe_file_name('file"name".txt') == "file_name_.txt"
        assert safe_file_name("file:name.txt") == "file_name.txt"
        assert safe_file_name("file/path\\name.txt") == "file_path_name.txt"

    def test_replace_all_unsafe_chars(self) -> None:
        """Test replacing all unsafe characters at once."""
        unsafe = '<>:"/\\|?*'
        result = safe_file_name(f"test{unsafe}file.txt")
        for char in unsafe:
            assert char not in result
        assert "_" in result


class TestResolveConflictName:
    """Test resolve_conflict_name function."""

    def test_with_custom_suffix(self, tmp_path: Path) -> None:
        """Test resolving conflict with custom suffix."""
        original = tmp_path / "file.md"
        result = resolve_conflict_name(original, suffix="backup")
        assert result.name == "file-backup.md"
        assert result.parent == tmp_path

    def test_auto_increment_no_conflicts(self, tmp_path: Path) -> None:
        """Test auto-increment when no conflicts exist."""
        original = tmp_path / "file.md"
        result = resolve_conflict_name(original)
        assert result.name == "file-1.md"

    def test_auto_increment_with_existing(self, tmp_path: Path) -> None:
        """Test auto-increment skips existing files."""
        original = tmp_path / "file.md"
        (tmp_path / "file-1.md").touch()
        (tmp_path / "file-2.md").touch()

        result = resolve_conflict_name(original)
        assert result.name == "file-3.md"

    def test_preserves_extension(self, tmp_path: Path) -> None:
        """Test that file extension is preserved."""
        original = tmp_path / "document.txt"
        result = resolve_conflict_name(original, suffix="v2")
        assert result.suffix == ".txt"
        assert result.stem == "document-v2"

    def test_files_without_extension(self, tmp_path: Path) -> None:
        """Test handling files without extension."""
        original = tmp_path / "README"
        result = resolve_conflict_name(original, suffix="new")
        assert result.name == "README-new"
