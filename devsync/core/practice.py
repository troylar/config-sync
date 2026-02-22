"""Practice declaration models for v2 AI-powered config distribution."""

from dataclasses import dataclass, field
from typing import Optional

from devsync.core.pip_utils import validate_pip_spec


@dataclass
class CredentialSpec:
    """Specification for a credential required by an MCP server.

    Attributes:
        name: Environment variable name (e.g., 'GITHUB_PERSONAL_ACCESS_TOKEN').
        description: Human-readable description for prompting.
        required: Whether the credential is mandatory.
        default: Default value hint (not the actual secret).
    """

    name: str
    description: str
    required: bool = True
    default: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("CredentialSpec name cannot be empty")
        if not self.description:
            raise ValueError("CredentialSpec description cannot be empty")

    def to_dict(self) -> dict:
        result: dict = {
            "name": self.name,
            "description": self.description,
            "required": self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "CredentialSpec":
        return cls(
            name=data["name"],
            description=data["description"],
            required=data.get("required", True),
            default=data.get("default"),
        )


@dataclass
class PracticeDeclaration:
    """An abstract coding practice extracted from project configs.

    Unlike v1 file copies, practices are semantic declarations of intent
    that can be adapted to any AI tool's format.

    Attributes:
        name: Short identifier (e.g., 'type-safety').
        intent: One-line description of what this practice enforces.
        principles: List of specific rules/guidelines.
        enforcement_patterns: How to enforce (CI checks, linting, etc.).
        examples: Code examples demonstrating the practice.
        tags: Categorization tags.
        source_file: Original file this was extracted from (for reference).
        raw_content: Original file content (fallback for no-AI mode).
    """

    name: str
    intent: str
    principles: list[str] = field(default_factory=list)
    enforcement_patterns: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    source_file: Optional[str] = None
    raw_content: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("PracticeDeclaration name cannot be empty")
        if not self.intent:
            raise ValueError("PracticeDeclaration intent cannot be empty")

    def to_dict(self) -> dict:
        result: dict = {
            "name": self.name,
            "intent": self.intent,
        }
        if self.principles:
            result["principles"] = self.principles
        if self.enforcement_patterns:
            result["enforcement_patterns"] = self.enforcement_patterns
        if self.examples:
            result["examples"] = self.examples
        if self.tags:
            result["tags"] = self.tags
        if self.source_file:
            result["source_file"] = self.source_file
        if self.raw_content:
            result["raw_content"] = self.raw_content
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "PracticeDeclaration":
        return cls(
            name=data["name"],
            intent=data["intent"],
            principles=data.get("principles", []),
            enforcement_patterns=data.get("enforcement_patterns", []),
            examples=data.get("examples", []),
            tags=data.get("tags", []),
            source_file=data.get("source_file"),
            raw_content=data.get("raw_content"),
        )


@dataclass
class MCPDeclaration:
    """Declaration for an MCP server configuration.

    Credentials are stripped — only metadata and credential specs are stored.

    Attributes:
        name: Server identifier (e.g., 'github-mcp').
        description: What the server provides.
        protocol: Communication protocol ('stdio' or 'sse').
        command: Executable command (e.g., 'npx').
        args: Command arguments.
        env_vars: Non-secret environment variables.
        credentials: Required credential specifications.
    """

    name: str
    description: str
    protocol: str = "stdio"
    command: str = ""
    args: list[str] = field(default_factory=list)
    env_vars: dict[str, str] = field(default_factory=dict)
    credentials: list[CredentialSpec] = field(default_factory=list)
    pip_package: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("MCPDeclaration name cannot be empty")
        if not self.description:
            raise ValueError("MCPDeclaration description cannot be empty")
        if self.protocol not in ("stdio", "sse"):
            raise ValueError(f"MCPDeclaration protocol must be 'stdio' or 'sse', got '{self.protocol}'")
        if self.pip_package is not None:
            if not validate_pip_spec(self.pip_package):
                raise ValueError(f"MCPDeclaration pip_package is not a valid pip spec: '{self.pip_package}'")

    def to_dict(self) -> dict:
        result: dict = {
            "name": self.name,
            "description": self.description,
            "protocol": self.protocol,
        }
        if self.command:
            result["command"] = self.command
        if self.args:
            result["args"] = self.args
        if self.env_vars:
            result["env_vars"] = self.env_vars
        if self.credentials:
            result["credentials"] = [c.to_dict() for c in self.credentials]
        if self.pip_package is not None:
            result["pip_package"] = self.pip_package
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "MCPDeclaration":
        credentials = [CredentialSpec.from_dict(c) for c in data.get("credentials", [])]
        return cls(
            name=data["name"],
            description=data["description"],
            protocol=data.get("protocol", "stdio"),
            command=data.get("command", ""),
            args=data.get("args", []),
            env_vars=data.get("env_vars", {}),
            credentials=credentials,
            pip_package=data.get("pip_package"),
        )
