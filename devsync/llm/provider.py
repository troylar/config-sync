"""Abstract LLM provider and provider resolution."""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMResponse:
    """Response from an LLM provider.

    Attributes:
        content: The text content of the response.
        model: The model that generated the response.
        usage: Token usage dict with prompt_tokens, completion_tokens, total_tokens.
        raw_response: The raw HTTP response dict for debugging.
    """

    content: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    raw_response: dict = field(default_factory=dict)


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    All providers use HTTP-only calls (no SDK dependencies) via httpx.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'anthropic', 'openai', 'openrouter')."""

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model ID for this provider."""

    @abstractmethod
    def complete(
        self,
        prompt: str,
        *,
        system: str = "",
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> LLMResponse:
        """Send a completion request to the LLM.

        Args:
            prompt: The user message/prompt.
            system: Optional system message.
            model: Model override (uses default_model if None).
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature (0.0 = deterministic).

        Returns:
            LLMResponse with the generated content.

        Raises:
            LLMProviderError: If the API call fails.
        """

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate the API key with a minimal test call.

        Returns:
            True if the key is valid, False otherwise.
        """


class LLMProviderError(Exception):
    """Raised when an LLM API call fails."""

    def __init__(self, message: str, status_code: Optional[int] = None, raw_response: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.raw_response = raw_response


_PROVIDER_ENV_VARS = [
    ("anthropic", "ANTHROPIC_API_KEY"),
    ("openai", "OPENAI_API_KEY"),
    ("openrouter", "OPENROUTER_API_KEY"),
]


def resolve_provider(
    preferred_provider: Optional[str] = None,
    preferred_model: Optional[str] = None,
) -> Optional[LLMProvider]:
    """Resolve the best available LLM provider.

    Checks env vars in priority order: ANTHROPIC_API_KEY → OPENAI_API_KEY → OPENROUTER_API_KEY.
    If preferred_provider is set, only that provider is checked.

    Args:
        preferred_provider: Optional provider name to use ('anthropic', 'openai', 'openrouter').
        preferred_model: Optional model ID override.

    Returns:
        An LLMProvider instance, or None if no API key is found.
    """
    from devsync.llm.anthropic import AnthropicProvider
    from devsync.llm.openai_provider import OpenAIProvider
    from devsync.llm.openrouter import OpenRouterProvider

    provider_map: dict[str, type[LLMProvider]] = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "openrouter": OpenRouterProvider,
    }

    if preferred_provider:
        provider_cls = provider_map.get(preferred_provider)
        if not provider_cls:
            return None
        env_var = next((ev for name, ev in _PROVIDER_ENV_VARS if name == preferred_provider), None)
        if not env_var:
            return None
        api_key = os.environ.get(env_var)
        if not api_key:
            return None
        return provider_cls(api_key=api_key, model=preferred_model)  # type: ignore[call-arg]

    for provider_name, env_var in _PROVIDER_ENV_VARS:
        api_key = os.environ.get(env_var)
        if api_key:
            provider_cls = provider_map[provider_name]
            return provider_cls(api_key=api_key, model=preferred_model)  # type: ignore[call-arg]

    return None
