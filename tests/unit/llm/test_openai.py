"""Tests for OpenAI provider with mocked HTTP responses."""

from unittest.mock import MagicMock, patch

import pytest

from devsync.llm.openai_provider import OpenAIProvider
from devsync.llm.provider import LLMProviderError


def _mock_response(status_code: int, json_data: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    mock.text = str(json_data)
    return mock


class TestOpenAIProvider:
    def test_name(self) -> None:
        provider = OpenAIProvider(api_key="test-key")
        assert provider.name == "openai"

    def test_default_model(self) -> None:
        provider = OpenAIProvider(api_key="test-key")
        assert provider.default_model == "gpt-4o"

    @patch("devsync.llm.openai_provider.httpx.Client")
    def test_complete_success(self, mock_client_cls: MagicMock) -> None:
        mock_response = _mock_response(
            200,
            {
                "choices": [{"message": {"content": "Hello"}}],
                "model": "gpt-4o",
                "usage": {"prompt_tokens": 8, "completion_tokens": 3, "total_tokens": 11},
            },
        )
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        provider = OpenAIProvider(api_key="test-key")
        result = provider.complete("test")

        assert result.content == "Hello"
        assert result.usage["total_tokens"] == 11

    @patch("devsync.llm.openai_provider.httpx.Client")
    def test_complete_with_system(self, mock_client_cls: MagicMock) -> None:
        mock_response = _mock_response(
            200,
            {
                "choices": [{"message": {"content": "ok"}}],
                "model": "gpt-4o",
                "usage": {"prompt_tokens": 5, "completion_tokens": 1, "total_tokens": 6},
            },
        )
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        provider = OpenAIProvider(api_key="test-key")
        provider.complete("test", system="Be helpful")

        body = mock_client.post.call_args[1]["json"]
        assert body["messages"][0]["role"] == "system"
        assert body["messages"][1]["role"] == "user"

    @patch("devsync.llm.openai_provider.httpx.Client")
    def test_complete_api_error(self, mock_client_cls: MagicMock) -> None:
        mock_response = _mock_response(429, {"error": {"message": "Rate limited"}})
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        provider = OpenAIProvider(api_key="test-key")
        with pytest.raises(LLMProviderError) as exc_info:
            provider.complete("test")
        assert exc_info.value.status_code == 429
