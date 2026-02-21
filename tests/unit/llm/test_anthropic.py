"""Tests for Anthropic provider with mocked HTTP responses."""

from unittest.mock import MagicMock, patch

import pytest

from devsync.llm.anthropic import AnthropicProvider
from devsync.llm.provider import LLMProviderError


def _mock_response(status_code: int, json_data: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    mock.text = str(json_data)
    return mock


class TestAnthropicProvider:
    def test_name(self) -> None:
        provider = AnthropicProvider(api_key="test-key")
        assert provider.name == "anthropic"

    def test_default_model(self) -> None:
        provider = AnthropicProvider(api_key="test-key")
        assert "claude" in provider.default_model

    def test_custom_model(self) -> None:
        provider = AnthropicProvider(api_key="test-key", model="claude-haiku-4-5-20251001")
        assert provider.default_model == "claude-haiku-4-5-20251001"

    @patch("devsync.llm.anthropic.httpx.Client")
    def test_complete_success(self, mock_client_cls: MagicMock) -> None:
        mock_response = _mock_response(
            200,
            {
                "content": [{"type": "text", "text": "Hello world"}],
                "model": "claude-sonnet-4-20250514",
                "usage": {"input_tokens": 10, "output_tokens": 5},
            },
        )
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        provider = AnthropicProvider(api_key="test-key")
        result = provider.complete("Say hello")

        assert result.content == "Hello world"
        assert result.model == "claude-sonnet-4-20250514"
        assert result.usage["prompt_tokens"] == 10
        assert result.usage["completion_tokens"] == 5
        assert result.usage["total_tokens"] == 15

    @patch("devsync.llm.anthropic.httpx.Client")
    def test_complete_with_system_message(self, mock_client_cls: MagicMock) -> None:
        mock_response = _mock_response(
            200,
            {
                "content": [{"type": "text", "text": "ok"}],
                "model": "claude-sonnet-4-20250514",
                "usage": {"input_tokens": 5, "output_tokens": 1},
            },
        )
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        provider = AnthropicProvider(api_key="test-key")
        provider.complete("test", system="You are a helper")

        call_args = mock_client.post.call_args
        body = call_args[1]["json"]
        assert body["system"] == "You are a helper"

    @patch("devsync.llm.anthropic.httpx.Client")
    def test_complete_api_error(self, mock_client_cls: MagicMock) -> None:
        mock_response = _mock_response(
            401,
            {"error": {"message": "Invalid API key"}},
        )
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        provider = AnthropicProvider(api_key="bad-key")
        with pytest.raises(LLMProviderError) as exc_info:
            provider.complete("test")
        assert exc_info.value.status_code == 401

    @patch("devsync.llm.anthropic.httpx.Client")
    def test_validate_api_key_success(self, mock_client_cls: MagicMock) -> None:
        mock_response = _mock_response(
            200,
            {
                "content": [{"type": "text", "text": "ok"}],
                "model": "claude-sonnet-4-20250514",
                "usage": {"input_tokens": 3, "output_tokens": 1},
            },
        )
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        provider = AnthropicProvider(api_key="good-key")
        assert provider.validate_api_key() is True

    @patch("devsync.llm.anthropic.httpx.Client")
    def test_validate_api_key_failure(self, mock_client_cls: MagicMock) -> None:
        mock_response = _mock_response(401, {"error": {"message": "Invalid"}})
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        provider = AnthropicProvider(api_key="bad-key")
        assert provider.validate_api_key() is False
