"""Anthropic Claude provider using HTTP-only calls."""

from typing import Optional

import httpx

from devsync.llm.provider import LLMProvider, LLMProviderError, LLMResponse

_API_URL = "https://api.anthropic.com/v1/messages"
_API_VERSION = "2023-06-01"
_DEFAULT_MODEL = "claude-sonnet-4-20250514"


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider via Messages API.

    Uses httpx for HTTP calls — no anthropic SDK dependency.
    """

    def __init__(self, api_key: str, model: Optional[str] = None):
        self._api_key = api_key
        self._model = model or _DEFAULT_MODEL

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return self._model

    def complete(
        self,
        prompt: str,
        *,
        system: str = "",
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> LLMResponse:
        model_id = model or self._model
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": _API_VERSION,
            "content-type": "application/json",
        }

        body: dict = {
            "model": model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(_API_URL, headers=headers, json=body)
        except httpx.HTTPError as e:
            raise LLMProviderError(f"HTTP error calling Anthropic API: {e}") from e

        raw = response.json()

        if response.status_code != 200:
            error_msg = raw.get("error", {}).get("message", response.text)
            raise LLMProviderError(
                f"Anthropic API error: {error_msg}",
                status_code=response.status_code,
                raw_response=raw,
            )

        content = ""
        for block in raw.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")

        usage_raw = raw.get("usage", {})
        usage = {
            "prompt_tokens": usage_raw.get("input_tokens", 0),
            "completion_tokens": usage_raw.get("output_tokens", 0),
            "total_tokens": usage_raw.get("input_tokens", 0) + usage_raw.get("output_tokens", 0),
        }

        return LLMResponse(
            content=content,
            model=raw.get("model", model_id),
            usage=usage,
            raw_response=raw,
        )

    def validate_api_key(self) -> bool:
        try:
            self.complete("Say 'ok'.", max_tokens=10)
            return True
        except LLMProviderError:
            return False
