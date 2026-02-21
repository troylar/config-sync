"""Tests for the setup command."""

from unittest.mock import MagicMock, patch

from devsync.cli.setup import setup_command
from devsync.llm.config import LLMConfig


class TestSetupCommand:
    @patch("devsync.cli.setup.Confirm.ask", return_value=False)
    @patch("devsync.cli.setup.load_config")
    def test_existing_config_no_reconfigure(self, mock_load: MagicMock, mock_confirm: MagicMock) -> None:
        mock_load.return_value = LLMConfig(provider="anthropic")
        result = setup_command()
        assert result == 0

    @patch("devsync.cli.setup.save_config")
    @patch("devsync.cli.setup.resolve_provider", return_value=None)
    @patch("devsync.cli.setup.Prompt.ask", side_effect=["anthropic", "claude-sonnet-4-20250514"])
    @patch("devsync.cli.setup.load_config", return_value=LLMConfig())
    def test_new_config_no_api_key(
        self,
        mock_load: MagicMock,
        mock_prompt: MagicMock,
        mock_resolve: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        result = setup_command()
        assert result == 0
        mock_save.assert_called_once()
        saved_config = mock_save.call_args[0][0]
        assert saved_config.provider == "anthropic"
        assert saved_config.env_var == "ANTHROPIC_API_KEY"

    @patch("devsync.cli.setup.save_config")
    @patch("devsync.cli.setup.Prompt.ask", side_effect=["openai", "gpt-4o"])
    @patch("devsync.cli.setup.load_config", return_value=LLMConfig())
    def test_openai_provider_selection(
        self,
        mock_load: MagicMock,
        mock_prompt: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        mock_provider = MagicMock()
        mock_provider.validate_api_key.return_value = True
        with patch("devsync.cli.setup.resolve_provider", return_value=mock_provider):
            result = setup_command()
        assert result == 0
        saved_config = mock_save.call_args[0][0]
        assert saved_config.provider == "openai"
        assert saved_config.env_var == "OPENAI_API_KEY"

    @patch("devsync.cli.setup.save_config")
    @patch("devsync.cli.setup.Prompt.ask", side_effect=["anthropic", "claude-sonnet-4-20250514"])
    @patch("devsync.cli.setup.load_config", return_value=LLMConfig())
    def test_valid_api_key(
        self,
        mock_load: MagicMock,
        mock_prompt: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        mock_provider = MagicMock()
        mock_provider.validate_api_key.return_value = True
        with patch("devsync.cli.setup.resolve_provider", return_value=mock_provider):
            result = setup_command()
        assert result == 0

    @patch("devsync.cli.setup.Confirm.ask", return_value=False)
    @patch("devsync.cli.setup.Prompt.ask", side_effect=["anthropic", "claude-sonnet-4-20250514"])
    @patch("devsync.cli.setup.load_config", return_value=LLMConfig())
    def test_invalid_api_key_decline_save(
        self,
        mock_load: MagicMock,
        mock_prompt: MagicMock,
        mock_confirm: MagicMock,
    ) -> None:
        mock_provider = MagicMock()
        mock_provider.validate_api_key.return_value = False
        with patch("devsync.cli.setup.resolve_provider", return_value=mock_provider):
            result = setup_command()
        assert result == 1
