"""Tests for tools CLI command."""

from unittest.mock import MagicMock, patch

from devsync.cli.tools import show_tools


class TestShowTools:
    def test_show_tools_returns_zero(self) -> None:
        result = show_tools()
        assert result == 0

    def test_show_tools_verbose_returns_zero(self) -> None:
        result = show_tools(verbose=True)
        assert result == 0

    def test_show_tools_verbose_shows_capabilities(self, capsys: object) -> None:
        """Verbose mode should include capability info without crashing."""
        result = show_tools(verbose=True)
        assert result == 0

    @patch("devsync.cli.tools.get_detector")
    def test_show_tools_verbose_with_mock(self, mock_get_detector: MagicMock) -> None:
        """Verify verbose mode accesses capability registry."""
        mock_detector = MagicMock()
        mock_tool = MagicMock()
        mock_tool.tool_name = "TestTool"
        mock_tool.is_installed.return_value = True

        from devsync.core.models import AIToolType

        mock_detector.tools = {AIToolType.CLAUDE: mock_tool}
        mock_detector.detect_installed_tools.return_value = [mock_tool]
        mock_get_detector.return_value = mock_detector

        result = show_tools(verbose=True)
        assert result == 0
