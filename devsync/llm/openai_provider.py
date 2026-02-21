"""OpenAI provider using HTTP-only calls."""

from typing import Optional

import httpx

from devsync.llm.provider import LLMProvider, LLMProviderError, LLMResponse

_API_URL = "https://api.openai.com/v1/chat/completions"
_DEFAULT_MODEL = "gpt-4o"


class OpenAIProvider(LLMProvider):
    """OpenAI provider via Chat Completions API.

    Uses httpx for HTTP calls — no openai SDK dependency.
    """

    def __init__(self, api_key: str, model: Optional[str] = None):
        self._api_key = api_key
        self._model = model or _DEFAULT_MODEL

    @property
    def name(self) -> str:
        return "openai"

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
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(_API_URL, headers=headers, json=body)
        except httpx.HTTPError as e:
            raise LLMProviderError(f"HTTP error calling OpenAI API: {e}") from e

        raw = response.json()

        if response.status_code != 200:
            error_msg = raw.get("error", {}).get("message", response.text)
            raise LLMProviderError(
                f"OpenAI API error: {error_msg}",
                status_code=response.status_code,
                raw_response=raw,
            )

        content = ""
        choices = raw.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")

        usage_raw = raw.get("usage", {})
        usage = {
            "prompt_tokens": usage_raw.get("prompt_tokens", 0),
            "completion_tokens": usage_raw.get("completion_tokens", 0),
            "total_tokens": usage_raw.get("total_tokens", 0),
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
