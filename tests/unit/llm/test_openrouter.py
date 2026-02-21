"""Tests for OpenRouter provider with mocked HTTP responses."""

from unittest.mock import MagicMock, patch

from devsync.llm.openrouter import OpenRouterProvider


def _mock_response(status_code: int, json_data: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    mock.text = str(json_data)
    return mock


class TestOpenRouterProvider:
    def test_name(self) -> None:
        provider = OpenRouterProvider(api_key="test-key")
        assert provider.name == "openrouter"

    def test_default_model(self) -> None:
        provider = OpenRouterProvider(api_key="test-key")
        assert "claude" in provider.default_model

    @patch("devsync.llm.openrouter.httpx.Client")
    def test_complete_success(self, mock_client_cls: MagicMock) -> None:
        mock_response = _mock_response(
            200,
            {
                "choices": [{"message": {"content": "Hi"}}],
                "model": "anthropic/claude-sonnet-4-20250514",
                "usage": {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7},
            },
        )
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        provider = OpenRouterProvider(api_key="test-key")
        result = provider.complete("test")

        assert result.content == "Hi"

    @patch("devsync.llm.openrouter.httpx.Client")
    def test_sends_referer_header(self, mock_client_cls: MagicMock) -> None:
        mock_response = _mock_response(
            200,
            {
                "choices": [{"message": {"content": "ok"}}],
                "model": "test",
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            },
        )
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        provider = OpenRouterProvider(api_key="test-key")
        provider.complete("test")

        headers = mock_client.post.call_args[1]["headers"]
        assert "HTTP-Referer" in headers
        assert "X-Title" in headers
