"""Tests for practice declaration models."""

import pytest
import yaml

from devsync.core.practice import CredentialSpec, MCPDeclaration, PracticeDeclaration


class TestCredentialSpec:
    def test_create(self) -> None:
        spec = CredentialSpec(name="API_KEY", description="The API key")
        assert spec.name == "API_KEY"
        assert spec.required is True
        assert spec.default is None

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name cannot be empty"):
            CredentialSpec(name="", description="test")

    def test_empty_description_raises(self) -> None:
        with pytest.raises(ValueError, match="description cannot be empty"):
            CredentialSpec(name="KEY", description="")

    def test_to_dict(self) -> None:
        spec = CredentialSpec(name="TOKEN", description="Auth token", required=False, default="xxx")
        d = spec.to_dict()
        assert d["name"] == "TOKEN"
        assert d["required"] is False
        assert d["default"] == "xxx"

    def test_from_dict(self) -> None:
        data = {"name": "KEY", "description": "A key", "required": True}
        spec = CredentialSpec.from_dict(data)
        assert spec.name == "KEY"
        assert spec.default is None

    def test_roundtrip(self) -> None:
        original = CredentialSpec(name="SECRET", description="Secret value", required=False, default="default")
        restored = CredentialSpec.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.required == original.required
        assert restored.default == original.default


class TestPracticeDeclaration:
    def test_create_minimal(self) -> None:
        p = PracticeDeclaration(name="type-safety", intent="Enforce type hints")
        assert p.name == "type-safety"
        assert p.principles == []

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name cannot be empty"):
            PracticeDeclaration(name="", intent="test")

    def test_empty_intent_raises(self) -> None:
        with pytest.raises(ValueError, match="intent cannot be empty"):
            PracticeDeclaration(name="test", intent="")

    def test_create_full(self) -> None:
        p = PracticeDeclaration(
            name="type-safety",
            intent="Enforce strict type hints",
            principles=["All functions have type hints"],
            enforcement_patterns=["Run mypy strict"],
            examples=["def foo(x: int) -> str:"],
            tags=["python", "typing"],
            source_file="rules/types.md",
            raw_content="# Type Safety\n...",
        )
        assert len(p.principles) == 1
        assert p.tags == ["python", "typing"]

    def test_to_dict_minimal(self) -> None:
        p = PracticeDeclaration(name="test", intent="Test practice")
        d = p.to_dict()
        assert d == {"name": "test", "intent": "Test practice"}

    def test_to_dict_full(self) -> None:
        p = PracticeDeclaration(
            name="test",
            intent="Test",
            principles=["rule1"],
            tags=["tag1"],
        )
        d = p.to_dict()
        assert "principles" in d
        assert "tags" in d
        assert "enforcement_patterns" not in d  # empty list omitted

    def test_from_dict(self) -> None:
        data = {
            "name": "code-style",
            "intent": "Enforce code style",
            "principles": ["Use black", "Line length 120"],
            "tags": ["python"],
        }
        p = PracticeDeclaration.from_dict(data)
        assert p.name == "code-style"
        assert len(p.principles) == 2

    def test_roundtrip(self) -> None:
        original = PracticeDeclaration(
            name="testing",
            intent="Ensure test coverage",
            principles=["80% minimum", "Unit tests for public API"],
            enforcement_patterns=["pytest-cov"],
            examples=["def test_foo(): ..."],
            tags=["testing"],
            source_file="rules/testing.md",
        )
        restored = PracticeDeclaration.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.principles == original.principles
        assert restored.tags == original.tags

    def test_yaml_roundtrip(self) -> None:
        original = PracticeDeclaration(
            name="security",
            intent="Enforce security patterns",
            principles=["No eval()", "No hardcoded secrets"],
            tags=["security"],
        )
        yaml_str = yaml.dump(original.to_dict(), default_flow_style=False)
        loaded = yaml.safe_load(yaml_str)
        restored = PracticeDeclaration.from_dict(loaded)
        assert restored.name == original.name
        assert restored.principles == original.principles


class TestMCPDeclaration:
    def test_create_minimal(self) -> None:
        m = MCPDeclaration(name="github", description="GitHub API")
        assert m.protocol == "stdio"
        assert m.credentials == []

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name cannot be empty"):
            MCPDeclaration(name="", description="test")

    def test_invalid_protocol_raises(self) -> None:
        with pytest.raises(ValueError, match="protocol must be"):
            MCPDeclaration(name="test", description="test", protocol="grpc")

    def test_create_full(self) -> None:
        m = MCPDeclaration(
            name="github-mcp",
            description="GitHub API access",
            protocol="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env_vars={"NODE_ENV": "production"},
            credentials=[
                CredentialSpec(name="GITHUB_TOKEN", description="GitHub PAT"),
            ],
        )
        assert m.command == "npx"
        assert len(m.credentials) == 1

    def test_to_dict(self) -> None:
        m = MCPDeclaration(
            name="test",
            description="Test server",
            command="node",
            args=["server.js"],
            credentials=[CredentialSpec(name="KEY", description="API key")],
        )
        d = m.to_dict()
        assert d["command"] == "node"
        assert len(d["credentials"]) == 1

    def test_from_dict(self) -> None:
        data = {
            "name": "github",
            "description": "GitHub",
            "protocol": "stdio",
            "command": "npx",
            "args": ["-y", "server"],
            "credentials": [{"name": "TOKEN", "description": "Token"}],
        }
        m = MCPDeclaration.from_dict(data)
        assert m.command == "npx"
        assert len(m.credentials) == 1
        assert m.credentials[0].name == "TOKEN"

    def test_pip_package_field(self) -> None:
        m = MCPDeclaration(
            name="fetch",
            description="Fetch server",
            pip_package="mcp-server-fetch>=0.1",
        )
        assert m.pip_package == "mcp-server-fetch>=0.1"

    def test_pip_package_none_by_default(self) -> None:
        m = MCPDeclaration(name="test", description="Test")
        assert m.pip_package is None

    def test_pip_package_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="not a valid pip spec"):
            MCPDeclaration(name="test", description="Test", pip_package="git+https://evil.com")

    def test_pip_package_to_dict_included(self) -> None:
        m = MCPDeclaration(name="test", description="Test", pip_package="pkg>=1.0")
        d = m.to_dict()
        assert d["pip_package"] == "pkg>=1.0"

    def test_pip_package_to_dict_omitted_when_none(self) -> None:
        m = MCPDeclaration(name="test", description="Test")
        d = m.to_dict()
        assert "pip_package" not in d

    def test_pip_package_from_dict(self) -> None:
        data = {
            "name": "test",
            "description": "Test",
            "pip_package": "mcp-server>=2.0",
        }
        m = MCPDeclaration.from_dict(data)
        assert m.pip_package == "mcp-server>=2.0"

    def test_pip_package_from_dict_missing(self) -> None:
        data = {"name": "test", "description": "Test"}
        m = MCPDeclaration.from_dict(data)
        assert m.pip_package is None

    def test_pip_package_roundtrip(self) -> None:
        original = MCPDeclaration(
            name="fetch",
            description="Fetch server",
            command="python",
            args=["-m", "mcp_server_fetch"],
            pip_package="mcp-server-fetch>=0.5",
        )
        restored = MCPDeclaration.from_dict(original.to_dict())
        assert restored.pip_package == original.pip_package

    def test_roundtrip(self) -> None:
        original = MCPDeclaration(
            name="db",
            description="Database access",
            protocol="sse",
            command="python",
            args=["mcp_server.py"],
            env_vars={"DB_HOST": "localhost"},
            credentials=[
                CredentialSpec(name="DB_PASSWORD", description="Database password"),
            ],
        )
        restored = MCPDeclaration.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.protocol == original.protocol
        assert restored.env_vars == original.env_vars
        assert len(restored.credentials) == 1
