"""Tests for MCP credential prompting."""

from unittest.mock import MagicMock, patch

from devsync.core.mcp_credential_prompter import build_mcp_config, prompt_mcp_credentials
from devsync.core.practice import CredentialSpec, MCPDeclaration


class TestBuildMCPConfig:
    def test_basic_config(self) -> None:
        server = MCPDeclaration(
            name="github",
            description="GitHub API",
            command="npx",
            args=["-y", "server"],
        )
        config = build_mcp_config(server, {})
        assert config["command"] == "npx"
        assert config["args"] == ["-y", "server"]
        assert "env" not in config

    def test_config_with_credentials(self) -> None:
        server = MCPDeclaration(
            name="github",
            description="GitHub API",
            command="npx",
            args=["-y", "server"],
            credentials=[CredentialSpec(name="GITHUB_TOKEN", description="PAT")],
        )
        config = build_mcp_config(server, {"GITHUB_TOKEN": "ghp_abc123"})
        assert config["env"]["GITHUB_TOKEN"] == "ghp_abc123"

    def test_config_with_env_vars_and_credentials(self) -> None:
        server = MCPDeclaration(
            name="db",
            description="Database",
            command="python",
            args=["server.py"],
            env_vars={"DB_HOST": "localhost"},
            credentials=[CredentialSpec(name="DB_PASS", description="Password")],
        )
        config = build_mcp_config(server, {"DB_PASS": "secret"})
        assert config["env"]["DB_HOST"] == "localhost"
        assert config["env"]["DB_PASS"] == "secret"

    def test_empty_credential_not_included(self) -> None:
        server = MCPDeclaration(
            name="test",
            description="Test",
            command="cmd",
            credentials=[CredentialSpec(name="KEY", description="Key", required=False)],
        )
        config = build_mcp_config(server, {"KEY": ""})
        assert "env" not in config or "KEY" not in config.get("env", {})


class TestPromptMCPCredentials:
    @patch("devsync.core.mcp_credential_prompter.Prompt.ask", return_value="my-token")
    def test_prompts_for_required_credential(self, mock_ask: MagicMock) -> None:
        servers = [
            MCPDeclaration(
                name="github",
                description="GitHub API",
                credentials=[CredentialSpec(name="TOKEN", description="Auth token")],
            )
        ]
        result = prompt_mcp_credentials(servers)
        assert result["github"]["TOKEN"] == "my-token"

    def test_no_credentials_returns_empty(self) -> None:
        servers = [MCPDeclaration(name="test", description="No creds")]
        result = prompt_mcp_credentials(servers)
        assert result == {}
