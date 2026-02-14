"""Unit tests for dotenv utilities."""

from pathlib import Path

import pytest

from aiconfigkit.core.models import EnvironmentConfig, InstallationScope
from aiconfigkit.utils.dotenv import (
    ensure_env_gitignored,
    load_env_config,
    merge_env_configs,
    save_env_config,
    set_env_variable,
)


class TestLoadEnvConfig:
    """Test load_env_config function."""

    def test_load_env_config_basic(self, tmp_path: Path) -> None:
        """Test loading basic .env file."""
        env_path = tmp_path / ".env"
        env_path.write_text('API_KEY="test-key"\nDATABASE_URL="postgresql://localhost"\n')

        config = load_env_config(env_path, InstallationScope.PROJECT)

        assert config.variables["API_KEY"] == "test-key"
        assert config.variables["DATABASE_URL"] == "postgresql://localhost"
        assert config.file_path == str(env_path)
        assert config.scope == InstallationScope.PROJECT

    def test_load_env_config_nonexistent_file(self, tmp_path: Path) -> None:
        """Test loading non-existent .env file returns empty config."""
        env_path = tmp_path / ".env"

        config = load_env_config(env_path, InstallationScope.PROJECT)

        assert config.variables == {}
        assert config.file_path == str(env_path)
        assert config.scope == InstallationScope.PROJECT

    def test_load_env_config_empty_file(self, tmp_path: Path) -> None:
        """Test loading empty .env file."""
        env_path = tmp_path / ".env"
        env_path.write_text("")

        config = load_env_config(env_path, InstallationScope.PROJECT)

        assert config.variables == {}

    def test_load_env_config_with_comments(self, tmp_path: Path) -> None:
        """Test loading .env with comments."""
        env_path = tmp_path / ".env"
        env_path.write_text('# Comment line\nAPI_KEY="value"\n# Another comment\n')

        config = load_env_config(env_path, InstallationScope.PROJECT)

        assert config.variables["API_KEY"] == "value"
        assert len(config.variables) == 1

    def test_load_env_config_with_empty_values(self, tmp_path: Path) -> None:
        """Test loading .env with empty values."""
        env_path = tmp_path / ".env"
        env_path.write_text('VALID_KEY="value"\nEMPTY_KEY=\n')

        config = load_env_config(env_path, InstallationScope.PROJECT)

        assert "VALID_KEY" in config.variables
        # Empty values become empty strings
        assert config.variables.get("EMPTY_KEY") == ""

    def test_load_env_config_global_scope(self, tmp_path: Path) -> None:
        """Test loading with GLOBAL scope."""
        env_path = tmp_path / ".env"
        env_path.write_text('KEY="value"\n')

        config = load_env_config(env_path, InstallationScope.GLOBAL)

        assert config.scope == InstallationScope.GLOBAL

    def test_load_env_config_multiline_values(self, tmp_path: Path) -> None:
        """Test loading .env with multiline values."""
        env_path = tmp_path / ".env"
        env_path.write_text('PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\\nMIIE...\\n-----END RSA PRIVATE KEY-----"\n')

        config = load_env_config(env_path, InstallationScope.PROJECT)

        assert "PRIVATE_KEY" in config.variables
        assert "BEGIN RSA PRIVATE KEY" in config.variables["PRIVATE_KEY"]

    def test_load_env_config_special_characters(self, tmp_path: Path) -> None:
        """Test loading .env with special characters in values."""
        env_path = tmp_path / ".env"
        env_path.write_text('PASSWORD="p@ssw0rd!#$%"\nURL="https://example.com?key=value&foo=bar"\n')

        config = load_env_config(env_path, InstallationScope.PROJECT)

        assert config.variables["PASSWORD"] == "p@ssw0rd!#$%"
        assert config.variables["URL"] == "https://example.com?key=value&foo=bar"


class TestSaveEnvConfig:
    """Test save_env_config function."""

    def test_save_env_config_basic(self, tmp_path: Path) -> None:
        """Test saving basic environment config."""
        env_path = tmp_path / ".env"
        config = EnvironmentConfig(
            variables={"API_KEY": "test-key", "DATABASE_URL": "postgresql://localhost"},
            file_path=str(env_path),
            scope=InstallationScope.PROJECT,
        )

        save_env_config(config)

        assert env_path.exists()
        content = env_path.read_text()
        assert 'API_KEY="test-key"' in content
        assert 'DATABASE_URL="postgresql://localhost"' in content

    def test_save_env_config_creates_directory(self, tmp_path: Path) -> None:
        """Test saving creates parent directories."""
        env_path = tmp_path / "nested" / "dirs" / ".env"
        config = EnvironmentConfig(variables={"KEY": "value"}, file_path=str(env_path), scope=InstallationScope.PROJECT)

        save_env_config(config)

        assert env_path.exists()
        assert env_path.parent.exists()

    def test_save_env_config_no_file_path(self, tmp_path: Path) -> None:
        """Test saving without file_path raises error."""
        config = EnvironmentConfig(variables={"KEY": "value"}, file_path=None, scope=InstallationScope.PROJECT)

        with pytest.raises(ValueError, match="EnvironmentConfig must have file_path set"):
            save_env_config(config)

    def test_save_env_config_includes_header(self, tmp_path: Path) -> None:
        """Test saved file includes header comments."""
        env_path = tmp_path / ".env"
        config = EnvironmentConfig(variables={"KEY": "value"}, file_path=str(env_path), scope=InstallationScope.PROJECT)

        save_env_config(config)

        content = env_path.read_text()
        assert "MCP Server Credentials" in content
        assert "Auto-generated by DevSync" in content
        assert "DO NOT commit this file" in content

    def test_save_env_config_sorted_keys(self, tmp_path: Path) -> None:
        """Test saved file has sorted keys."""
        env_path = tmp_path / ".env"
        config = EnvironmentConfig(
            variables={"ZEBRA": "z", "ALPHA": "a", "MIKE": "m"},
            file_path=str(env_path),
            scope=InstallationScope.PROJECT,
        )

        save_env_config(config)

        content = env_path.read_text()
        # Check that ALPHA comes before MIKE which comes before ZEBRA
        alpha_pos = content.index("ALPHA")
        mike_pos = content.index("MIKE")
        zebra_pos = content.index("ZEBRA")
        assert alpha_pos < mike_pos < zebra_pos

    def test_save_env_config_escapes_special_chars(self, tmp_path: Path) -> None:
        """Test saving escapes special characters."""
        env_path = tmp_path / ".env"
        config = EnvironmentConfig(
            variables={"MULTILINE": "line1\nline2", "QUOTED": 'value with "quotes"', "BACKSLASH": "path\\to\\file"},
            file_path=str(env_path),
            scope=InstallationScope.PROJECT,
        )

        save_env_config(config)

        content = env_path.read_text()
        assert "\\n" in content  # Newline escaped
        assert '\\"' in content  # Quotes escaped
        assert "\\\\" in content  # Backslash escaped

    def test_save_env_config_creates_gitignore(self, tmp_path: Path) -> None:
        """Test saving creates .gitignore."""
        env_path = tmp_path / ".env"
        config = EnvironmentConfig(variables={"KEY": "value"}, file_path=str(env_path), scope=InstallationScope.PROJECT)

        save_env_config(config)

        gitignore_path = tmp_path / ".gitignore"
        assert gitignore_path.exists()
        assert ".env" in gitignore_path.read_text()

    def test_save_env_config_empty_variables(self, tmp_path: Path) -> None:
        """Test saving with empty variables."""
        env_path = tmp_path / ".env"
        config = EnvironmentConfig(variables={}, file_path=str(env_path), scope=InstallationScope.PROJECT)

        save_env_config(config)

        content = env_path.read_text()
        # Should only have header comments
        assert "MCP Server Credentials" in content
        # Should not have any variable assignments
        lines = [line for line in content.split("\n") if "=" in line]
        assert len(lines) == 0

    def test_save_env_config_creates_backup(self, tmp_path: Path) -> None:
        """Test saving creates backup of existing file."""
        env_path = tmp_path / ".env"
        env_path.write_text('OLD_KEY="old_value"\n')

        config = EnvironmentConfig(
            variables={"NEW_KEY": "new_value"}, file_path=str(env_path), scope=InstallationScope.PROJECT
        )

        save_env_config(config)

        # For .env files, backup is .env.bak (suffix is appended, not replaced)
        backup_path = tmp_path / ".env.bak"
        assert backup_path.exists()
        assert 'OLD_KEY="old_value"' in backup_path.read_text()


class TestSetEnvVariable:
    """Test set_env_variable function."""

    def test_set_env_variable_basic(self, tmp_path: Path) -> None:
        """Test setting a basic environment variable."""
        env_path = tmp_path / ".env"

        set_env_variable(env_path, "API_KEY", "test-value")

        assert env_path.exists()
        content = env_path.read_text()
        assert "API_KEY" in content
        assert "test-value" in content

    def test_set_env_variable_creates_directory(self, tmp_path: Path) -> None:
        """Test setting variable creates parent directory."""
        env_path = tmp_path / "nested" / ".env"

        set_env_variable(env_path, "KEY", "value")

        assert env_path.parent.exists()
        assert env_path.exists()

    def test_set_env_variable_invalid_name_lowercase(self, tmp_path: Path) -> None:
        """Test setting variable with lowercase name raises error."""
        env_path = tmp_path / ".env"

        with pytest.raises(ValueError, match="Invalid environment variable name"):
            set_env_variable(env_path, "lowercase_key", "value")

    def test_set_env_variable_invalid_name_starts_with_number(self, tmp_path: Path) -> None:
        """Test setting variable starting with number raises error."""
        env_path = tmp_path / ".env"

        with pytest.raises(ValueError, match="Invalid environment variable name"):
            set_env_variable(env_path, "1INVALID", "value")

    def test_set_env_variable_invalid_name_special_chars(self, tmp_path: Path) -> None:
        """Test setting variable with special characters raises error."""
        env_path = tmp_path / ".env"

        with pytest.raises(ValueError, match="Invalid environment variable name"):
            set_env_variable(env_path, "INVALID-KEY", "value")

    def test_set_env_variable_valid_with_numbers(self, tmp_path: Path) -> None:
        """Test setting variable with numbers is valid."""
        env_path = tmp_path / ".env"

        set_env_variable(env_path, "API_KEY_V2", "value")

        assert env_path.exists()
        assert "API_KEY_V2" in env_path.read_text()

    def test_set_env_variable_valid_with_underscores(self, tmp_path: Path) -> None:
        """Test setting variable with underscores is valid."""
        env_path = tmp_path / ".env"

        set_env_variable(env_path, "DATABASE_CONNECTION_STRING", "value")

        assert env_path.exists()
        assert "DATABASE_CONNECTION_STRING" in env_path.read_text()

    def test_set_env_variable_updates_existing(self, tmp_path: Path) -> None:
        """Test setting variable updates existing value."""
        env_path = tmp_path / ".env"
        env_path.write_text('API_KEY="old-value"\n')

        set_env_variable(env_path, "API_KEY", "new-value")

        content = env_path.read_text()
        assert "new-value" in content
        assert "old-value" not in content

    def test_set_env_variable_creates_gitignore(self, tmp_path: Path) -> None:
        """Test setting variable creates .gitignore."""
        env_path = tmp_path / ".env"

        set_env_variable(env_path, "KEY", "value")

        gitignore_path = tmp_path / ".gitignore"
        assert gitignore_path.exists()
        assert ".env" in gitignore_path.read_text()

    def test_set_env_variable_quoted_value(self, tmp_path: Path) -> None:
        """Test variable value is always quoted."""
        env_path = tmp_path / ".env"

        set_env_variable(env_path, "KEY", "value with spaces")

        content = env_path.read_text()
        # python-dotenv's quote_mode="always" should quote the value
        assert '"value with spaces"' in content or "'value with spaces'" in content


class TestEnsureEnvGitignored:
    """Test ensure_env_gitignored function."""

    def test_ensure_env_gitignored_creates_new(self, tmp_path: Path) -> None:
        """Test creating new .gitignore with .env entry."""
        env_path = tmp_path / ".env"

        ensure_env_gitignored(env_path)

        gitignore_path = tmp_path / ".gitignore"
        assert gitignore_path.exists()
        content = gitignore_path.read_text()
        assert ".env" in content
        assert "MCP Server Credentials" in content

    def test_ensure_env_gitignored_skips_if_exists(self, tmp_path: Path) -> None:
        """Test skipping if .env already in .gitignore."""
        env_path = tmp_path / ".env"
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("# Existing\n.env\nnode_modules/\n")

        ensure_env_gitignored(env_path)

        # Should not modify existing .gitignore
        content = gitignore_path.read_text()
        assert content.count(".env") == 1  # Only original entry
        assert "MCP Server Credentials" not in content  # No new comment added

    def test_ensure_env_gitignored_appends_to_existing(self, tmp_path: Path) -> None:
        """Test appending .env to existing .gitignore without it."""
        env_path = tmp_path / ".env"
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("# Existing content\nnode_modules/\n*.pyc\n")

        ensure_env_gitignored(env_path)

        content = gitignore_path.read_text()
        assert "node_modules/" in content  # Original content preserved
        assert ".env" in content  # New entry added
        assert "MCP Server Credentials" in content

    def test_ensure_env_gitignored_preserves_existing_content(self, tmp_path: Path) -> None:
        """Test existing .gitignore content is preserved."""
        env_path = tmp_path / ".env"
        gitignore_path = tmp_path / ".gitignore"
        original_content = "# Important\n*.log\n__pycache__/\n"
        gitignore_path.write_text(original_content)

        ensure_env_gitignored(env_path)

        content = gitignore_path.read_text()
        assert "*.log" in content
        assert "__pycache__/" in content
        assert ".env" in content


class TestMergeEnvConfigs:
    """Test merge_env_configs function."""

    def test_merge_env_configs_basic(self, tmp_path: Path) -> None:
        """Test basic merge of environment configs."""
        project_config = EnvironmentConfig(
            variables={"PROJECT_KEY": "project_value"},
            file_path=str(tmp_path / ".env"),
            scope=InstallationScope.PROJECT,
        )
        global_config = EnvironmentConfig(
            variables={"GLOBAL_KEY": "global_value"},
            file_path=str(Path.home() / ".env"),
            scope=InstallationScope.GLOBAL,
        )

        merged = merge_env_configs(project_config, global_config)

        assert merged.variables["PROJECT_KEY"] == "project_value"
        assert merged.variables["GLOBAL_KEY"] == "global_value"
        assert merged.scope == InstallationScope.PROJECT

    def test_merge_env_configs_project_overrides_global(self, tmp_path: Path) -> None:
        """Test project config overrides global config."""
        project_config = EnvironmentConfig(
            variables={"API_KEY": "project_key"}, file_path=str(tmp_path / ".env"), scope=InstallationScope.PROJECT
        )
        global_config = EnvironmentConfig(
            variables={"API_KEY": "global_key"}, file_path=str(Path.home() / ".env"), scope=InstallationScope.GLOBAL
        )

        merged = merge_env_configs(project_config, global_config)

        assert merged.variables["API_KEY"] == "project_key"  # Project takes precedence

    def test_merge_env_configs_empty_project(self, tmp_path: Path) -> None:
        """Test merge with empty project config."""
        project_config = EnvironmentConfig(
            variables={}, file_path=str(tmp_path / ".env"), scope=InstallationScope.PROJECT
        )
        global_config = EnvironmentConfig(
            variables={"GLOBAL_KEY": "global_value"},
            file_path=str(Path.home() / ".env"),
            scope=InstallationScope.GLOBAL,
        )

        merged = merge_env_configs(project_config, global_config)

        assert merged.variables == {"GLOBAL_KEY": "global_value"}
        assert merged.scope == InstallationScope.PROJECT

    def test_merge_env_configs_empty_global(self, tmp_path: Path) -> None:
        """Test merge with empty global config."""
        project_config = EnvironmentConfig(
            variables={"PROJECT_KEY": "project_value"},
            file_path=str(tmp_path / ".env"),
            scope=InstallationScope.PROJECT,
        )
        global_config = EnvironmentConfig(
            variables={}, file_path=str(Path.home() / ".env"), scope=InstallationScope.GLOBAL
        )

        merged = merge_env_configs(project_config, global_config)

        assert merged.variables == {"PROJECT_KEY": "project_value"}

    def test_merge_env_configs_both_empty(self, tmp_path: Path) -> None:
        """Test merge with both configs empty."""
        project_config = EnvironmentConfig(
            variables={}, file_path=str(tmp_path / ".env"), scope=InstallationScope.PROJECT
        )
        global_config = EnvironmentConfig(
            variables={}, file_path=str(Path.home() / ".env"), scope=InstallationScope.GLOBAL
        )

        merged = merge_env_configs(project_config, global_config)

        assert merged.variables == {}
        assert merged.scope == InstallationScope.PROJECT

    def test_merge_env_configs_preserves_project_file_path(self, tmp_path: Path) -> None:
        """Test merge preserves project file path."""
        project_path = str(tmp_path / ".env")
        global_path = str(Path.home() / ".env")

        project_config = EnvironmentConfig(variables={}, file_path=project_path, scope=InstallationScope.PROJECT)
        global_config = EnvironmentConfig(variables={}, file_path=global_path, scope=InstallationScope.GLOBAL)

        merged = merge_env_configs(project_config, global_config)

        assert merged.file_path == project_path

    def test_merge_env_configs_multiple_overlapping(self, tmp_path: Path) -> None:
        """Test merge with multiple overlapping variables."""
        project_config = EnvironmentConfig(
            variables={"KEY1": "project1", "KEY2": "project2", "KEY3": "project3"},
            file_path=str(tmp_path / ".env"),
            scope=InstallationScope.PROJECT,
        )
        global_config = EnvironmentConfig(
            variables={"KEY1": "global1", "KEY2": "global2", "KEY4": "global4"},
            file_path=str(Path.home() / ".env"),
            scope=InstallationScope.GLOBAL,
        )

        merged = merge_env_configs(project_config, global_config)

        assert merged.variables["KEY1"] == "project1"  # Project override
        assert merged.variables["KEY2"] == "project2"  # Project override
        assert merged.variables["KEY3"] == "project3"  # Project only
        assert merged.variables["KEY4"] == "global4"  # Global only
