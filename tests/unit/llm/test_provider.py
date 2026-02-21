"""Tests for LLM provider abstraction and resolution."""

import os
from unittest.mock import patch

from devsync.llm.provider import LLMProviderError, LLMResponse, resolve_provider


class TestLLMResponse:
    def test_create_response(self) -> None:
        response = LLMResponse(content="hello", model="test-model")
        assert response.content == "hello"
        assert response.model == "test-model"
        assert response.usage == {}
        assert response.raw_response == {}

    def test_create_response_with_usage(self) -> None:
        usage = {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        response = LLMResponse(content="hi", model="m", usage=usage)
        assert response.usage["total_tokens"] == 15


class TestLLMProviderError:
    def test_error_with_status_code(self) -> None:
        err = LLMProviderError("fail", status_code=401)
        assert str(err) == "fail"
        assert err.status_code == 401

    def test_error_with_raw_response(self) -> None:
        err = LLMProviderError("fail", raw_response={"error": "bad"})
        assert err.raw_response == {"error": "bad"}


class TestResolveProvider:
    def test_no_env_vars_returns_none(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            # Clear any existing keys
            for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY"):
                os.environ.pop(key, None)
            result = resolve_provider()
            assert result is None

    def test_anthropic_key_resolves_first(self) -> None:
        env = {
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "OPENAI_API_KEY": "sk-test",
        }
        with patch.dict(os.environ, env, clear=False):
            provider = resolve_provider()
            assert provider is not None
            assert provider.name == "anthropic"

    def test_openai_key_resolves_when_no_anthropic(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            os.environ.pop("OPENROUTER_API_KEY", None)
            provider = resolve_provider()
            assert provider is not None
            assert provider.name == "openai"

    def test_openrouter_key_resolves_last(self) -> None:
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-test"}, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            os.environ.pop("OPENAI_API_KEY", None)
            provider = resolve_provider()
            assert provider is not None
            assert provider.name == "openrouter"

    def test_preferred_provider_used(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test", "ANTHROPIC_API_KEY": "sk-ant"}, clear=False):
            provider = resolve_provider(preferred_provider="openai")
            assert provider is not None
            assert provider.name == "openai"

    def test_preferred_provider_no_key_returns_none(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)
            result = resolve_provider(preferred_provider="openai")
            assert result is None

    def test_invalid_preferred_provider_returns_none(self) -> None:
        result = resolve_provider(preferred_provider="nonexistent")
        assert result is None

    def test_preferred_model_passed_through(self) -> None:
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test"}, clear=False):
            provider = resolve_provider(preferred_model="claude-haiku-4-5-20251001")
            assert provider is not None
            assert provider.default_model == "claude-haiku-4-5-20251001"
