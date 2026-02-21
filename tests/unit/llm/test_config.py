"""Tests for LLM configuration management."""

from pathlib import Path

from devsync.llm.config import LLMConfig, load_config, save_config


class TestLLMConfig:
    def test_empty_config(self) -> None:
        config = LLMConfig()
        assert config.provider is None
        assert config.model is None
        assert config.env_var is None

    def test_to_dict_empty(self) -> None:
        config = LLMConfig()
        assert config.to_dict() == {}

    def test_to_dict_full(self) -> None:
        config = LLMConfig(provider="anthropic", model="claude-haiku-4-5-20251001", env_var="ANTHROPIC_API_KEY")
        d = config.to_dict()
        assert d["provider"] == "anthropic"
        assert d["model"] == "claude-haiku-4-5-20251001"
        assert d["env_var"] == "ANTHROPIC_API_KEY"

    def test_from_dict(self) -> None:
        data = {"provider": "openai", "model": "gpt-4o"}
        config = LLMConfig.from_dict(data)
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.env_var is None

    def test_roundtrip(self) -> None:
        original = LLMConfig(provider="anthropic", model="claude-sonnet-4-20250514", env_var="ANTHROPIC_API_KEY")
        restored = LLMConfig.from_dict(original.to_dict())
        assert restored.provider == original.provider
        assert restored.model == original.model
        assert restored.env_var == original.env_var


class TestLoadSaveConfig:
    def test_load_missing_file(self, tmp_path: Path) -> None:
        config = load_config(tmp_path / "nonexistent.yaml")
        assert config.provider is None

    def test_save_and_load(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.yaml"
        config = LLMConfig(provider="anthropic", model="claude-sonnet-4-20250514")
        save_config(config, config_path)

        loaded = load_config(config_path)
        assert loaded.provider == "anthropic"
        assert loaded.model == "claude-sonnet-4-20250514"

    def test_save_preserves_other_sections(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.yaml"
        config_path.write_text("other_section:\n  key: value\n")

        config = LLMConfig(provider="openai")
        save_config(config, config_path)

        loaded_text = config_path.read_text()
        assert "other_section" in loaded_text
        assert "openai" in loaded_text

    def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        config_path = tmp_path / "nested" / "dir" / "config.yaml"
        config = LLMConfig(provider="anthropic")
        save_config(config, config_path)
        assert config_path.exists()

    def test_load_empty_file(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.yaml"
        config_path.write_text("")
        config = load_config(config_path)
        assert config.provider is None
