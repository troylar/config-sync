"""Tests for AI tool detector."""

import pytest

from aiconfigkit.ai_tools.detector import AIToolDetector, get_detector
from aiconfigkit.core.models import AIToolType


@pytest.fixture
def detector():
    """Create a fresh detector instance."""
    return AIToolDetector()


@pytest.fixture
def mock_all_tools_installed(monkeypatch, temp_dir):
    """Mock all tools as installed."""
    import os

    home_dir = temp_dir / "home"
    home_dir.mkdir(parents=True)

    # Create platform-specific directory structures for all tools
    if os.name == "nt":  # Windows
        (home_dir / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage").mkdir(parents=True)
        (home_dir / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "github.copilot").mkdir(parents=True)
        (home_dir / "AppData" / "Roaming" / "Windsurf" / "User" / "globalStorage").mkdir(parents=True)
        (home_dir / "AppData" / "Roaming" / "Kiro" / "User" / "globalStorage").mkdir(parents=True)
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():  # macOS
            (home_dir / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage").mkdir(parents=True)
            (home_dir / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "github.copilot").mkdir(
                parents=True
            )
            (home_dir / "Library" / "Application Support" / "Windsurf" / "User" / "globalStorage").mkdir(parents=True)
            (home_dir / "Library" / "Application Support" / "Kiro" / "User" / "globalStorage").mkdir(parents=True)
        else:  # Linux
            (home_dir / ".config" / "Cursor" / "User" / "globalStorage").mkdir(parents=True)
            (home_dir / ".config" / "Code" / "User" / "globalStorage" / "github.copilot").mkdir(parents=True)
            (home_dir / ".config" / "Windsurf" / "User" / "globalStorage").mkdir(parents=True)
            (home_dir / ".config" / "Kiro" / "User" / "globalStorage").mkdir(parents=True)
    else:
        raise OSError(f"Unsupported operating system: {os.name}")

    # Claude Code is consistent across platforms
    (home_dir / ".claude" / "rules").mkdir(parents=True)

    monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)


class TestAIToolDetector:
    """Test suite for AIToolDetector."""

    def test_init_creates_all_tools(self, detector):
        """Test that detector initializes with all supported tools."""
        assert len(detector.tools) == 5
        assert AIToolType.CURSOR in detector.tools
        assert AIToolType.COPILOT in detector.tools
        assert AIToolType.WINSURF in detector.tools
        assert AIToolType.CLAUDE in detector.tools
        assert AIToolType.KIRO in detector.tools

    def test_detect_installed_tools_none(self, temp_dir, monkeypatch):
        """Test detect_installed_tools when no tools are installed."""
        home_dir = temp_dir / "empty_home"
        home_dir.mkdir()
        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)

        # Create fresh detector with mocked paths
        detector = AIToolDetector()
        installed = detector.detect_installed_tools()
        assert len(installed) == 0

    def test_detect_installed_tools_all(self, mock_all_tools_installed):
        """Test detect_installed_tools when all tools are installed."""
        # Create fresh detector with mocked paths
        detector = AIToolDetector()
        installed = detector.detect_installed_tools()
        assert len(installed) == 5

    def test_get_tool_by_name_valid(self, detector):
        """Test get_tool_by_name with valid tool name."""
        tool = detector.get_tool_by_name("cursor")
        assert tool is not None
        assert tool.tool_type == AIToolType.CURSOR

    def test_get_tool_by_name_case_insensitive(self, detector):
        """Test get_tool_by_name is case insensitive."""
        tool = detector.get_tool_by_name("CURSOR")
        assert tool is not None
        assert tool.tool_type == AIToolType.CURSOR

    def test_get_tool_by_name_invalid(self, detector):
        """Test get_tool_by_name with invalid tool name."""
        tool = detector.get_tool_by_name("nonexistent")
        assert tool is None

    def test_get_tool_by_type(self, detector):
        """Test get_tool_by_type."""
        tool = detector.get_tool_by_type(AIToolType.CURSOR)
        assert tool is not None
        assert tool.tool_type == AIToolType.CURSOR

    def test_get_tool_by_type_none(self, detector):
        """Test get_tool_by_type with non-existent type."""
        tool = detector.get_tool_by_type(None)
        assert tool is None

    def test_get_primary_tool_cursor_priority(self, temp_dir, monkeypatch):
        """Test get_primary_tool returns Cursor when multiple tools installed."""
        import os

        home_dir = temp_dir / "home"
        home_dir.mkdir(parents=True)

        # Mock Cursor and Winsurf as installed (platform-specific)
        if os.name == "nt":  # Windows
            cursor_dir = home_dir / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage"
            windsurf_dir = home_dir / "AppData" / "Roaming" / "Windsurf" / "User" / "globalStorage"
        elif os.name == "posix":
            if "darwin" in os.uname().sysname.lower():  # macOS
                cursor_dir = home_dir / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage"
                windsurf_dir = home_dir / "Library" / "Application Support" / "Windsurf" / "User" / "globalStorage"
            else:  # Linux
                cursor_dir = home_dir / ".config" / "Cursor" / "User" / "globalStorage"
                windsurf_dir = home_dir / ".config" / "Windsurf" / "User" / "globalStorage"
        else:
            raise OSError(f"Unsupported operating system: {os.name}")

        cursor_dir.mkdir(parents=True)
        windsurf_dir.mkdir(parents=True)

        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)

        # Create fresh detector
        detector = AIToolDetector()
        primary = detector.get_primary_tool()
        assert primary is not None
        assert primary.tool_type == AIToolType.CURSOR

    def test_get_primary_tool_none_installed(self, temp_dir, monkeypatch):
        """Test get_primary_tool returns None when no tools installed."""
        home_dir = temp_dir / "empty_home"
        home_dir.mkdir()
        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)

        detector = AIToolDetector()
        primary = detector.get_primary_tool()
        assert primary is None

    def test_is_any_tool_installed_true(self, mock_all_tools_installed):
        """Test is_any_tool_installed returns True when tools installed."""
        detector = AIToolDetector()
        assert detector.is_any_tool_installed() is True

    def test_is_any_tool_installed_false(self, temp_dir, monkeypatch):
        """Test is_any_tool_installed returns False when no tools installed."""
        home_dir = temp_dir / "empty_home"
        home_dir.mkdir()
        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)

        detector = AIToolDetector()
        assert detector.is_any_tool_installed() is False

    def test_get_tool_names(self, detector):
        """Test get_tool_names returns all tool names."""
        names = detector.get_tool_names()
        assert len(names) == 5
        assert "cursor" in names
        assert "copilot" in names
        assert "winsurf" in names
        assert "claude" in names
        assert "kiro" in names

    def test_validate_tool_name_valid(self, detector):
        """Test validate_tool_name with valid name."""
        assert detector.validate_tool_name("cursor") is True
        assert detector.validate_tool_name("CURSOR") is True

    def test_validate_tool_name_invalid(self, detector):
        """Test validate_tool_name with invalid name."""
        assert detector.validate_tool_name("nonexistent") is False

    def test_get_detection_summary(self, mock_all_tools_installed):
        """Test get_detection_summary."""
        detector = AIToolDetector()
        summary = detector.get_detection_summary()
        assert len(summary) == 5
        assert all(isinstance(v, bool) for v in summary.values())

    def test_format_detection_summary(self, mock_all_tools_installed):
        """Test format_detection_summary."""
        detector = AIToolDetector()
        summary = detector.format_detection_summary()
        assert "AI Coding Tools Detection:" in summary
        assert "✓ Installed" in summary

    def test_get_detector_singleton(self):
        """Test get_detector returns singleton instance."""
        # Reset singleton
        import aiconfigkit.ai_tools.detector

        aiconfigkit.ai_tools.detector._detector_instance = None

        detector1 = get_detector()
        detector2 = get_detector()
        assert detector1 is detector2
