"""LLM configuration management.

Stores provider and model preferences in ~/.devsync/config.yaml.
API keys are NEVER stored — only env var names for reference.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

_CONFIG_DIR = Path.home() / ".devsync"
_CONFIG_FILE = _CONFIG_DIR / "config.yaml"


@dataclass
class LLMConfig:
    """LLM configuration (no secrets stored).

    Attributes:
        provider: Preferred provider name ('anthropic', 'openai', 'openrouter').
        model: Preferred model ID override.
        env_var: Name of the env var holding the API key (for user reference).
    """

    provider: Optional[str] = None
    model: Optional[str] = None
    env_var: Optional[str] = None

    def to_dict(self) -> dict:
        result: dict = {}
        if self.provider:
            result["provider"] = self.provider
        if self.model:
            result["model"] = self.model
        if self.env_var:
            result["env_var"] = self.env_var
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "LLMConfig":
        return cls(
            provider=data.get("provider"),
            model=data.get("model"),
            env_var=data.get("env_var"),
        )


def load_config(config_path: Optional[Path] = None) -> LLMConfig:
    """Load LLM config from disk.

    Args:
        config_path: Override config file path (for testing).

    Returns:
        LLMConfig instance (empty if file doesn't exist).
    """
    path = config_path or _CONFIG_FILE
    if not path.exists():
        return LLMConfig()

    with open(path) as f:
        data = yaml.safe_load(f) or {}

    llm_data = data.get("llm", {})
    return LLMConfig.from_dict(llm_data)


def save_config(config: LLMConfig, config_path: Optional[Path] = None) -> None:
    """Save LLM config to disk.

    Merges with existing config to preserve other sections.
    API keys are NEVER written to this file.

    Args:
        config: LLMConfig to save.
        config_path: Override config file path (for testing).
    """
    path = config_path or _CONFIG_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict = {}
    if path.exists():
        with open(path) as f:
            existing = yaml.safe_load(f) or {}

    existing["llm"] = config.to_dict()

    with open(path, "w") as f:
        yaml.dump(existing, f, default_flow_style=False, sort_keys=False)
