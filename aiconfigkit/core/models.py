"""Core data models for InstructionKit."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AIToolType(Enum):
    """Supported AI coding tool types."""

    CURSOR = "cursor"
    COPILOT = "copilot"
    WINSURF = "winsurf"
    CLAUDE = "claude"
    KIRO = "kiro"


class ConflictResolution(Enum):
    """Conflict resolution strategies."""

    PROMPT = "prompt"  # Interactive prompting (default)
    SKIP = "skip"
    RENAME = "rename"
    OVERWRITE = "overwrite"


class InstallationScope(Enum):
    """Installation scope."""

    GLOBAL = "global"
    PROJECT = "project"


class RefType(Enum):
    """Git reference types for version control."""

    TAG = "tag"
    BRANCH = "branch"
    COMMIT = "commit"


class ConflictType(Enum):
    """Types of conflicts during template updates."""

    NONE = "none"  # No conflict, safe to update
    LOCAL_MODIFIED = "local_modified"  # User modified local file
    BOTH_MODIFIED = "both_modified"  # Both local and remote changed


class IssueType(Enum):
    """Types of validation issues."""

    TRACKING_INCONSISTENCY = "tracking_inconsistency"  # File exists but not tracked
    MISSING_FILE = "missing_file"  # Tracked but file missing
    OUTDATED = "outdated"  # Newer version available
    BROKEN_DEPENDENCY = "broken_dependency"  # Required template not installed
    LOCAL_MODIFICATION = "local_modification"  # File changed since install
    SEMANTIC_CONFLICT = "semantic_conflict"  # AI detected conflicting guidance
    CLARITY_ISSUE = "clarity_issue"  # AI detected unclear instructions


class IssueSeverity(Enum):
    """Severity levels for validation issues."""

    ERROR = "error"  # Must fix
    WARNING = "warning"  # Should fix
    INFO = "info"  # Nice to know


@dataclass
class Instruction:
    """
    Represents a single instruction file.

    Attributes:
        name: Unique identifier (e.g., 'python-best-practices')
        description: Human-readable description
        content: The actual instruction text
        file_path: Relative path in repository (e.g., 'instructions/python-best-practices.md')
        tags: Categorization tags (e.g., ['python', 'backend'])
        checksum: SHA-256 hash for integrity validation
        ai_tools: List of compatible AI tools (empty = all compatible)
    """

    name: str
    description: str
    content: str
    file_path: str
    tags: list[str] = field(default_factory=list)
    checksum: Optional[str] = None
    ai_tools: list[AIToolType] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate instruction data."""
        if not self.name:
            raise ValueError("Instruction name cannot be empty")
        if not self.description:
            raise ValueError("Instruction description cannot be empty")
        if not self.content:
            raise ValueError("Instruction content cannot be empty")
        if not self.file_path:
            raise ValueError("Instruction file_path cannot be empty")


@dataclass
class InstructionBundle:
    """
    Represents a bundle of related instructions.

    Attributes:
        name: Bundle identifier (e.g., 'python-backend')
        description: What this bundle provides
        instructions: List of instruction names in this bundle
        tags: Bundle-level tags
    """

    name: str
    description: str
    instructions: list[str]
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate bundle data."""
        if not self.name:
            raise ValueError("Bundle name cannot be empty")
        if not self.description:
            raise ValueError("Bundle description cannot be empty")
        if not self.instructions:
            raise ValueError("Bundle must contain at least one instruction")


@dataclass
class Repository:
    """
    Represents an instruction repository.

    Attributes:
        url: Git repository URL (empty string if not yet set)
        instructions: Available instructions
        bundles: Available bundles
        metadata: Additional repository metadata
    """

    url: str = ""
    instructions: list[Instruction] = field(default_factory=list)
    bundles: list[InstructionBundle] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class InstallationRecord:
    """
    Tracks an installed instruction.

    Attributes:
        instruction_name: Name of installed instruction
        ai_tool: Which AI tool it's installed to
        source_repo: Repository URL it came from
        installed_path: Path where file was installed (relative to project root for PROJECT scope)
        installed_at: Installation timestamp
        checksum: File checksum at installation time
        bundle_name: If installed as part of bundle
        scope: Installation scope (global or project)
        source_ref: Git reference (tag, branch, or commit) the instruction came from
        source_ref_type: Type of Git reference (tag, branch, or commit)
    """

    instruction_name: str
    ai_tool: AIToolType
    source_repo: str
    installed_path: str
    installed_at: datetime
    checksum: Optional[str] = None
    bundle_name: Optional[str] = None
    scope: InstallationScope = InstallationScope.GLOBAL
    source_ref: Optional[str] = None
    source_ref_type: Optional[RefType] = None

    def __post_init__(self) -> None:
        """Validate installation record."""
        if not self.instruction_name:
            raise ValueError("Instruction name cannot be empty")
        if not self.source_repo:
            raise ValueError("Source repository cannot be empty")
        if not self.installed_path:
            raise ValueError("Installed path cannot be empty")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "instruction_name": self.instruction_name,
            "ai_tool": self.ai_tool.value,
            "source_repo": self.source_repo,
            "installed_path": self.installed_path,
            "installed_at": self.installed_at.isoformat(),
            "checksum": self.checksum,
            "bundle_name": self.bundle_name,
            "scope": self.scope.value,
            "source_ref": self.source_ref,
            "source_ref_type": self.source_ref_type.value if self.source_ref_type else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InstallationRecord":
        """Create from dictionary (JSON deserialization)."""
        # Handle backwards compatibility - old records won't have scope
        scope_value = data.get("scope", "global")
        scope = InstallationScope(scope_value) if isinstance(scope_value, str) else scope_value

        # Handle backwards compatibility - old records won't have ref fields
        source_ref = data.get("source_ref")
        source_ref_type = None
        if data.get("source_ref_type"):
            source_ref_type = RefType(data["source_ref_type"])

        return cls(
            instruction_name=data["instruction_name"],
            ai_tool=AIToolType(data["ai_tool"]),
            source_repo=data["source_repo"],
            installed_path=data["installed_path"],
            installed_at=datetime.fromisoformat(data["installed_at"]),
            checksum=data.get("checksum"),
            bundle_name=data.get("bundle_name"),
            scope=scope,
            source_ref=source_ref,
            source_ref_type=source_ref_type,
        )


@dataclass
class ConflictInfo:
    """
    Information about a file conflict.

    Attributes:
        instruction_name: Name of conflicting instruction
        existing_path: Path to existing file
        resolution: How the conflict was resolved
        new_path: New path if renamed
    """

    instruction_name: str
    existing_path: str
    resolution: ConflictResolution
    new_path: Optional[str] = None


@dataclass
class LibraryInstruction:
    """
    Represents an instruction in the local library (downloaded but not yet installed).

    Attributes:
        id: Unique identifier (repo_namespace/name)
        name: Instruction name
        description: Human-readable description
        repo_namespace: Repository namespace (e.g., 'company-instructions')
        repo_url: Source repository URL
        repo_name: Repository display name
        author: Author or team name
        version: Instruction version
        file_path: Path to instruction file in library
        tags: Categorization tags
        downloaded_at: When it was downloaded
        checksum: SHA-256 hash for integrity
    """

    id: str
    name: str
    description: str
    repo_namespace: str
    repo_url: str
    repo_name: str
    author: str
    version: str
    file_path: str
    tags: list[str] = field(default_factory=list)
    downloaded_at: Optional[datetime] = None
    checksum: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate library instruction data."""
        if not self.id:
            raise ValueError("Instruction id cannot be empty")
        if not self.name:
            raise ValueError("Instruction name cannot be empty")
        if not self.repo_namespace:
            raise ValueError("Repository namespace cannot be empty")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "repo_namespace": self.repo_namespace,
            "repo_url": self.repo_url,
            "repo_name": self.repo_name,
            "author": self.author,
            "version": self.version,
            "file_path": self.file_path,
            "tags": self.tags,
            "downloaded_at": self.downloaded_at.isoformat() if self.downloaded_at else None,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryInstruction":
        """Create from dictionary (JSON deserialization)."""
        downloaded_at = None
        if data.get("downloaded_at"):
            downloaded_at = datetime.fromisoformat(data["downloaded_at"])

        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            repo_namespace=data["repo_namespace"],
            repo_url=data["repo_url"],
            repo_name=data["repo_name"],
            author=data["author"],
            version=data["version"],
            file_path=data["file_path"],
            tags=data.get("tags", []),
            downloaded_at=downloaded_at,
            checksum=data.get("checksum"),
        )


@dataclass
class LibraryRepository:
    """
    Represents a downloaded repository in the library.

    Attributes:
        namespace: Repository namespace identifier (e.g., 'github.com_company_instructions')
        name: Repository display name
        description: Repository description
        url: Source repository URL
        author: Author or team name
        version: Repository version
        downloaded_at: When it was downloaded
        alias: User-friendly alias for this source (optional)
        instructions: List of instructions in this repository
    """

    namespace: str
    name: str
    description: str
    url: str
    author: str
    version: str
    downloaded_at: datetime
    alias: Optional[str] = None
    instructions: list[LibraryInstruction] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate library repository data."""
        if not self.namespace:
            raise ValueError("Repository namespace cannot be empty")
        if not self.name:
            raise ValueError("Repository name cannot be empty")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "namespace": self.namespace,
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "author": self.author,
            "version": self.version,
            "downloaded_at": self.downloaded_at.isoformat(),
            "alias": self.alias,
            "instructions": [inst.to_dict() for inst in self.instructions],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryRepository":
        """Create from dictionary (JSON deserialization)."""
        instructions = [LibraryInstruction.from_dict(inst) for inst in data.get("instructions", [])]

        return cls(
            namespace=data["namespace"],
            name=data["name"],
            description=data["description"],
            url=data["url"],
            author=data["author"],
            version=data["version"],
            downloaded_at=datetime.fromisoformat(data["downloaded_at"]),
            alias=data.get("alias"),  # Optional field, may not exist in old data
            instructions=instructions,
        )


# Template Sync System Models


@dataclass
class TemplateFile:
    """
    Represents a template file with IDE targeting.

    Attributes:
        path: Relative path from repository root
        ide: Target IDE ("all", "cursor", "claude", "windsurf", "copilot", "kiro")
    """

    path: str
    ide: str = "all"

    def __post_init__(self) -> None:
        """Validate template file data."""
        if not self.path:
            raise ValueError("Template file path cannot be empty")
        valid_ides = ["all", "cursor", "claude", "windsurf", "copilot", "kiro"]
        if self.ide not in valid_ides:
            raise ValueError(f"Invalid IDE type: {self.ide}. Must be one of {valid_ides}")


@dataclass
class TemplateDefinition:
    """
    Represents a single template definition from manifest.

    Attributes:
        name: Template identifier
        description: What this template provides
        files: List of template files
        tags: Categorization tags
        dependencies: Other templates required by this one
    """

    name: str
    description: str
    files: list[TemplateFile]
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate template definition."""
        if not self.name:
            raise ValueError("Template name cannot be empty")
        if not self.description:
            raise ValueError("Template description cannot be empty")
        if not self.files:
            raise ValueError("Template must have at least one file")


@dataclass
class TemplateBundle:
    """
    Represents a predefined bundle of templates.

    Attributes:
        name: Bundle identifier
        description: What this bundle provides
        template_refs: Template names in this bundle
        tags: Categorization tags
    """

    name: str
    description: str
    template_refs: list[str]
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate template bundle."""
        if not self.name:
            raise ValueError("Bundle name cannot be empty")
        if not self.description:
            raise ValueError("Bundle description cannot be empty")
        if len(self.template_refs) < 2:
            raise ValueError("Bundle must contain at least 2 templates")


@dataclass
class TemplateManifest:
    """
    Represents a template repository manifest (templatekit.yaml).

    Attributes:
        name: Repository name
        description: Repository description
        version: Semantic version
        author: Author or team name
        templates: Available templates
        bundles: Predefined bundles
    """

    name: str
    description: str
    version: str
    author: Optional[str] = None
    templates: list[TemplateDefinition] = field(default_factory=list)
    bundles: list[TemplateBundle] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate manifest data."""
        if not self.name:
            raise ValueError("Manifest name cannot be empty")
        if not self.description:
            raise ValueError("Manifest description cannot be empty")
        if not self.version:
            raise ValueError("Manifest version cannot be empty")
        if not self.templates:
            raise ValueError("Manifest must contain at least one template")


@dataclass
class TemplateInstallationRecord:
    """
    Tracks an installed template.

    Attributes:
        id: Unique installation ID (UUID)
        template_name: Installed template identifier
        source_repo: Source repository name
        source_version: Repository version at install
        namespace: Repository namespace (derived from repo name)
        installed_path: Absolute path to installed file
        scope: Installation scope (project or global)
        installed_at: Installation timestamp
        checksum: SHA-256 of installed content
        ide_type: Target IDE for this installation
        custom_metadata: User-defined metadata
    """

    id: str
    template_name: str
    source_repo: str
    source_version: str
    namespace: str
    installed_path: str
    scope: InstallationScope
    installed_at: datetime
    checksum: str
    ide_type: AIToolType
    custom_metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate installation record."""
        if not self.id:
            raise ValueError("Installation ID cannot be empty")
        if not self.template_name:
            raise ValueError("Template name cannot be empty")
        if not self.source_repo:
            raise ValueError("Source repository cannot be empty")
        if not self.namespace:
            raise ValueError("Namespace cannot be empty")
        if not self.installed_path:
            raise ValueError("Installed path cannot be empty")
        if len(self.checksum) != 64:  # SHA-256 is always 64 hex characters
            raise ValueError("Checksum must be a valid SHA-256 hash (64 characters)")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "template_name": self.template_name,
            "source_repo": self.source_repo,
            "source_version": self.source_version,
            "namespace": self.namespace,
            "installed_path": self.installed_path,
            "scope": self.scope.value,
            "installed_at": self.installed_at.isoformat(),
            "checksum": self.checksum,
            "ide_type": self.ide_type.value,
            "custom_metadata": self.custom_metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TemplateInstallationRecord":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            id=data["id"],
            template_name=data["template_name"],
            source_repo=data["source_repo"],
            source_version=data["source_version"],
            namespace=data["namespace"],
            installed_path=data["installed_path"],
            scope=InstallationScope(data["scope"]),
            installed_at=datetime.fromisoformat(data["installed_at"]),
            checksum=data["checksum"],
            ide_type=AIToolType(data["ide_type"]),
            custom_metadata=data.get("custom_metadata", {}),
        )


@dataclass
class AIAnalysis:
    """
    AI-provided analysis for validation issues.

    Attributes:
        confidence: AI confidence (0.0-1.0)
        explanation: Why AI flagged this
        suggested_fix: AI-generated fix
        can_merge: For conflicts: is merge possible?
        merge_suggestion: Merged version if applicable
    """

    confidence: float
    explanation: str
    suggested_fix: Optional[str] = None
    can_merge: Optional[bool] = None
    merge_suggestion: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate AI analysis data."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if not self.explanation:
            raise ValueError("Explanation cannot be empty")


@dataclass
class ValidationIssue:
    """
    Represents a problem detected during template validation.

    Attributes:
        issue_type: Type of validation issue
        severity: How critical the issue is
        title: Short description of issue
        description: Detailed explanation
        affected_items: Templates/repos affected
        recommendation: How to fix the issue
        auto_fixable: Can system auto-fix this?
        fix_command: Command to fix issue
        ai_analysis: AI-provided insights
    """

    issue_type: IssueType
    severity: IssueSeverity
    title: str
    description: str
    affected_items: list[str]
    recommendation: str
    auto_fixable: bool
    fix_command: Optional[str] = None
    ai_analysis: Optional[AIAnalysis] = None

    def __post_init__(self) -> None:
        """Validate validation issue data."""
        if not self.title:
            raise ValueError("Issue title cannot be empty")
        if not self.description:
            raise ValueError("Issue description cannot be empty")
        if not self.affected_items:
            raise ValueError("Issue must affect at least one item")
        if not self.recommendation:
            raise ValueError("Issue recommendation cannot be empty")


# MCP Server Configuration Management Models


@dataclass(frozen=True)
class MCPServer:
    """
    Represents a single MCP server definition from a template repository.

    Attributes:
        name: Unique identifier within namespace (alphanumeric, hyphens, underscores)
        command: Executable command to launch MCP server
        args: Command-line arguments for the server
        env: Environment variables (None = requires user configuration)
        namespace: Source template namespace (for namespaced identification)
    """

    name: str
    command: str
    args: list[str]
    env: dict[str, Optional[str]]
    namespace: str

    def __post_init__(self) -> None:
        """Validate MCP server data."""
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", self.name):
            raise ValueError(f"Invalid server name: {self.name}. Must match ^[a-zA-Z0-9_-]+$")
        if not self.command:
            raise ValueError("Server command cannot be empty")
        # Validate env var names
        for key in self.env.keys():
            if not re.match(r"^[A-Z][A-Z0-9_]*$", key):
                raise ValueError(f"Invalid environment variable name: {key}. Must match ^[A-Z][A-Z0-9_]*$")

    def get_fully_qualified_name(self) -> str:
        """Returns {namespace}.{name}."""
        return f"{self.namespace}.{self.name}"

    def get_required_env_vars(self) -> list[str]:
        """Returns env var names where value is None."""
        return [key for key, value in self.env.items() if value is None]

    def has_all_credentials(self, env_config: "EnvironmentConfig") -> bool:
        """Check if all required env vars are configured."""
        required = self.get_required_env_vars()
        return all(env_config.has(var) for var in required)

    def to_dict(self) -> dict:
        """Serialize for JSON."""
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "namespace": self.namespace,
        }

    @classmethod
    def from_dict(cls, data: dict, namespace: str) -> "MCPServer":
        """Deserialize from templatekit.yaml."""
        return cls(
            name=data["name"],
            command=data["command"],
            args=data.get("args", []),
            env=data.get("env", {}),
            namespace=namespace,
        )


@dataclass(frozen=True)
class MCPSet:
    """
    A named collection of MCP servers for a specific workflow or task context.

    Attributes:
        name: Set identifier (e.g., "backend-dev", "frontend-dev")
        description: Human-readable description of set purpose
        server_names: Names of MCP servers included in this set
        namespace: Source template namespace
    """

    name: str
    description: str
    server_names: list[str]
    namespace: str

    def __post_init__(self) -> None:
        """Validate MCP set data."""
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", self.name):
            raise ValueError(f"Invalid set name: {self.name}. Must match ^[a-zA-Z0-9_-]+$")
        if not self.server_names:
            raise ValueError("Set must contain at least one server")

    def get_fully_qualified_name(self) -> str:
        """Returns {namespace}.{name}."""
        return f"{self.namespace}.{self.name}"

    def resolve_servers(self, all_servers: list[MCPServer]) -> list[MCPServer]:
        """Get actual server objects."""
        server_map = {s.name: s for s in all_servers}
        resolved = []
        for server_name in self.server_names:
            if server_name not in server_map:
                raise ValueError(f"Set '{self.name}' references unknown server '{server_name}'")
            resolved.append(server_map[server_name])
        return resolved

    def to_dict(self) -> dict:
        """Serialize."""
        return {
            "name": self.name,
            "description": self.description,
            "servers": self.server_names,
            "namespace": self.namespace,
        }

    @classmethod
    def from_dict(cls, data: dict, namespace: str) -> "MCPSet":
        """Deserialize."""
        return cls(
            name=data["name"],
            description=data["description"],
            server_names=data.get("servers", []),
            namespace=namespace,
        )


@dataclass
class MCPTemplate:
    """
    Represents an installed MCP template from a repository.

    Attributes:
        namespace: Unique identifier for this template
        source_url: Git URL or None for local installs
        source_path: Local directory path or None for Git installs
        version: Template version from templatekit.yaml
        description: Template description
        installed_at: Installation timestamp
        servers: MCP servers defined in template
        sets: MCP sets defined in template
    """

    namespace: str
    source_url: Optional[str]
    source_path: Optional[str]
    version: str
    description: str
    installed_at: datetime
    servers: list[MCPServer] = field(default_factory=list)
    sets: list[MCPSet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate MCP template data."""
        if not self.namespace:
            raise ValueError("Template namespace cannot be empty")
        if self.source_url and self.source_path:
            raise ValueError("Template cannot have both source_url and source_path")
        if not self.source_url and not self.source_path:
            raise ValueError("Template must have either source_url or source_path")

    def get_server_by_name(self, name: str) -> Optional[MCPServer]:
        """Find server by name."""
        for server in self.servers:
            if server.name == name:
                return server
        return None

    def get_set_by_name(self, name: str) -> Optional[MCPSet]:
        """Find set by name."""
        for mcp_set in self.sets:
            if mcp_set.name == name:
                return mcp_set
        return None

    def to_dict(self) -> dict:
        """Serialize."""
        return {
            "namespace": self.namespace,
            "source_url": self.source_url,
            "source_path": self.source_path,
            "version": self.version,
            "description": self.description,
            "installed_at": self.installed_at.isoformat(),
            "servers": [s.to_dict() for s in self.servers],
            "sets": [s.to_dict() for s in self.sets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MCPTemplate":
        """Deserialize."""
        namespace = data["namespace"]
        return cls(
            namespace=namespace,
            source_url=data.get("source_url"),
            source_path=data.get("source_path"),
            version=data["version"],
            description=data["description"],
            installed_at=datetime.fromisoformat(data["installed_at"]),
            servers=[MCPServer.from_dict(s, namespace) for s in data.get("servers", [])],
            sets=[MCPSet.from_dict(s, namespace) for s in data.get("sets", [])],
        )


@dataclass
class EnvironmentConfig:
    """
    Manages environment variables from `.instructionkit/.env` file.

    Attributes:
        variables: Environment variable name-value pairs
        file_path: Path to .env file
        scope: PROJECT or GLOBAL
    """

    variables: dict[str, str] = field(default_factory=dict)
    file_path: Optional[str] = None
    scope: InstallationScope = InstallationScope.PROJECT

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get variable value."""
        return self.variables.get(key, default)

    def set(self, key: str, value: str) -> None:
        """Set variable value (validates name)."""
        import re

        if not re.match(r"^[A-Z][A-Z0-9_]*$", key):
            raise ValueError(f"Invalid environment variable name: {key}. Must match ^[A-Z][A-Z0-9_]*$")
        self.variables[key] = value

    def has(self, key: str) -> bool:
        """Check if variable exists."""
        return key in self.variables

    def validate_for_server(self, server: MCPServer) -> list[str]:
        """Return list of missing required vars."""
        required = server.get_required_env_vars()
        return [var for var in required if not self.has(var)]

    def to_dict(self) -> dict[str, str]:
        """Export as plain dictionary."""
        return self.variables.copy()


@dataclass
class ActiveSetState:
    """
    Tracks which MCP set is currently active in a project.

    Attributes:
        namespace: Active set's namespace (None = no active set)
        set_name: Active set's name (None = no active set)
        activated_at: When set was activated
        active_servers: Fully qualified server names currently active
    """

    namespace: Optional[str] = None
    set_name: Optional[str] = None
    activated_at: Optional[datetime] = None
    active_servers: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate state data."""
        if (self.namespace is None) != (self.set_name is None):
            raise ValueError("namespace and set_name must both be set or both be None")
        if not self.namespace and self.active_servers:
            raise ValueError("active_servers must be empty if no active set")

    def activate_set(self, mcp_set: MCPSet, servers: list[MCPServer]) -> None:
        """Set active set."""
        self.namespace = mcp_set.namespace
        self.set_name = mcp_set.name
        self.activated_at = datetime.now()
        self.active_servers = [s.get_fully_qualified_name() for s in servers]

    def deactivate(self) -> None:
        """Clear active set."""
        self.namespace = None
        self.set_name = None
        self.activated_at = None
        self.active_servers = []

    def is_active(self) -> bool:
        """Check if any set is active."""
        return self.namespace is not None and self.set_name is not None

    def get_active_set_fqn(self) -> Optional[str]:
        """Returns 'namespace.set_name' or None."""
        if self.is_active():
            return f"{self.namespace}.{self.set_name}"
        return None

    def to_dict(self) -> dict:
        """Serialize."""
        return {
            "namespace": self.namespace,
            "set_name": self.set_name,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "active_servers": self.active_servers,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActiveSetState":
        """Deserialize."""
        activated_at = None
        if data.get("activated_at"):
            activated_at = datetime.fromisoformat(data["activated_at"])
        return cls(
            namespace=data.get("namespace"),
            set_name=data.get("set_name"),
            activated_at=activated_at,
            active_servers=data.get("active_servers", []),
        )


# ============================================================================
# Package System Models (Feature 004-config-package)
# ============================================================================


class ComponentType(Enum):
    """Types of components that can be included in a package."""

    INSTRUCTION = "instruction"
    MCP_SERVER = "mcp_server"
    HOOK = "hook"
    COMMAND = "command"  # Legacy: .claude/commands/
    SKILL = "skill"  # Claude skills: .claude/skills/
    WORKFLOW = "workflow"  # Windsurf workflows: .windsurf/workflows/
    RESOURCE = "resource"
    MEMORY_FILE = "memory_file"  # CLAUDE.md files


class InstallationStatus(Enum):
    """Status of package installation."""

    INSTALLING = "installing"
    COMPLETE = "complete"
    PARTIAL = "partial"  # Some components failed
    UPDATING = "updating"
    FAILED = "failed"


class ComponentStatus(Enum):
    """Status of individual component installation."""

    INSTALLED = "installed"
    FAILED = "failed"
    SKIPPED = "skipped"  # Unsupported by IDE
    PENDING_CREDENTIALS = "pending_credentials"  # MCP missing credentials


class SecretConfidence(Enum):
    """Confidence level for secret detection."""

    HIGH = "high"  # Auto-template
    MEDIUM = "medium"  # Prompt user
    SAFE = "safe"  # Preserve value


@dataclass
class CredentialDescriptor:
    """
    Declaration of required environment variable for MCP server.

    Attributes:
        name: Environment variable name (UPPER_SNAKE_CASE)
        description: What the credential is for
        required: Whether credential is mandatory
        default: Default value if not required
        example: Example value for guidance
    """

    name: str
    description: str
    required: bool = True
    default: Optional[str] = None
    example: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate credential descriptor."""
        if not self.name:
            raise ValueError("Credential name cannot be empty")
        if not self.name.isupper() or not self.name.replace("_", "").isalnum():
            raise ValueError(f"Credential name '{self.name}' must be UPPER_SNAKE_CASE")
        if self.required and self.default:
            raise ValueError("Required credentials cannot have default values")

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "required": self.required,
            "default": self.default,
            "example": self.example,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CredentialDescriptor":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            required=data.get("required", True),
            default=data.get("default"),
            example=data.get("example"),
        )


@dataclass
class InstructionComponent:
    """
    Reference to an instruction file in a package.

    Attributes:
        name: Instruction identifier
        file: Relative path to instruction file
        description: What the instruction does
        tags: Searchable tags
        ide_support: Specific IDE support (if restricted)
    """

    name: str
    file: str
    description: str
    tags: list[str] = field(default_factory=list)
    ide_support: Optional[list[str]] = None

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "file": self.file,
            "description": self.description,
            "tags": self.tags,
            "ide_support": self.ide_support,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InstructionComponent":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            file=data["file"],
            description=data["description"],
            tags=data.get("tags", []),
            ide_support=data.get("ide_support"),
        )


@dataclass
class MCPServerComponent:
    """
    Reference to an MCP server configuration template.

    Attributes:
        name: Server identifier
        file: Relative path to MCP config template
        description: What the server provides
        credentials: Required environment variables
        ide_support: IDEs that support MCP
    """

    name: str
    file: str
    description: str
    credentials: list[CredentialDescriptor] = field(default_factory=list)
    ide_support: list[str] = field(default_factory=lambda: ["claude_code", "windsurf"])

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "file": self.file,
            "description": self.description,
            "credentials": [c.to_dict() for c in self.credentials],
            "ide_support": self.ide_support,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MCPServerComponent":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            file=data["file"],
            description=data["description"],
            credentials=[CredentialDescriptor.from_dict(c) for c in data.get("credentials", [])],
            ide_support=data.get("ide_support", ["claude_code", "windsurf"]),
        )


@dataclass
class HookComponent:
    """
    Reference to an IDE lifecycle hook script.

    Attributes:
        name: Hook identifier
        file: Relative path to hook script
        description: What the hook does
        hook_type: Hook trigger (e.g., pre-commit, post-install)
        ide_support: IDEs that support hooks
    """

    name: str
    file: str
    description: str
    hook_type: str
    ide_support: list[str] = field(default_factory=lambda: ["claude_code"])

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "file": self.file,
            "description": self.description,
            "hook_type": self.hook_type,
            "ide_support": self.ide_support,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HookComponent":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            file=data["file"],
            description=data["description"],
            hook_type=data["hook_type"],
            ide_support=data.get("ide_support", ["claude_code"]),
        )


@dataclass
class CommandComponent:
    """
    Reference to a slash command or script.

    Attributes:
        name: Command identifier
        file: Relative path to command script
        description: What the command does
        command_type: Type (slash, shell)
        ide_support: IDEs that support commands
    """

    name: str
    file: str
    description: str
    command_type: str
    ide_support: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "file": self.file,
            "description": self.description,
            "command_type": self.command_type,
            "ide_support": self.ide_support,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CommandComponent":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            file=data["file"],
            description=data["description"],
            command_type=data["command_type"],
            ide_support=data.get("ide_support", []),
        )


@dataclass
class ResourceComponent:
    """
    Reference to an arbitrary file resource.

    Attributes:
        name: Resource identifier
        file: Relative path to resource file
        description: What the resource is
        install_path: Where to install the resource (defaults to file path)
        checksum: SHA256 checksum for integrity
        size: File size in bytes
    """

    name: str
    file: str
    description: str
    install_path: str
    checksum: str
    size: int

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "file": self.file,
            "description": self.description,
            "install_path": self.install_path,
            "checksum": self.checksum,
            "size": self.size,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResourceComponent":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            file=data["file"],
            description=data["description"],
            install_path=data.get("install_path", data["file"]),  # Default to file path if not specified
            checksum=data["checksum"],
            size=data["size"],
        )


@dataclass
class SkillComponent:
    """
    Reference to a Claude skill directory.

    Skills are directories containing SKILL.md with optional supporting files.
    They can be invoked via slash commands and are shared across Claude products.

    Attributes:
        name: Skill identifier (directory name)
        file: Relative path to skill directory
        description: What the skill does (from SKILL.md frontmatter)
        ide_support: IDEs that support skills (Claude only)
    """

    name: str
    file: str
    description: str
    ide_support: list[str] = field(default_factory=lambda: ["claude"])

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "file": self.file,
            "description": self.description,
            "ide_support": self.ide_support,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SkillComponent":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            file=data["file"],
            description=data["description"],
            ide_support=data.get("ide_support", ["claude"]),
        )


@dataclass
class WorkflowComponent:
    """
    Reference to a Windsurf workflow.

    Workflows define multi-step automated processes in Windsurf.

    Attributes:
        name: Workflow identifier
        file: Relative path to workflow file
        description: What the workflow does
        ide_support: IDEs that support workflows (Windsurf only)
    """

    name: str
    file: str
    description: str
    ide_support: list[str] = field(default_factory=lambda: ["windsurf"])

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "file": self.file,
            "description": self.description,
            "ide_support": self.ide_support,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowComponent":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            file=data["file"],
            description=data["description"],
            ide_support=data.get("ide_support", ["windsurf"]),
        )


@dataclass
class MemoryFileComponent:
    """
    Reference to a CLAUDE.md memory file.

    Memory files persist context across Claude Code sessions and can exist
    at project root or in subdirectories.

    Attributes:
        name: File identifier (usually "CLAUDE" or path-based)
        file: Relative path to CLAUDE.md file
        description: What context the memory file provides
        ide_support: IDEs that support memory files (Claude only)
    """

    name: str
    file: str
    description: str
    ide_support: list[str] = field(default_factory=lambda: ["claude"])

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "file": self.file,
            "description": self.description,
            "ide_support": self.ide_support,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryFileComponent":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            file=data["file"],
            description=data["description"],
            ide_support=data.get("ide_support", ["claude"]),
        )


@dataclass
class PackageComponents:
    """
    Container for all component types in a package.

    Attributes:
        instructions: Instruction files
        mcp_servers: MCP server configs
        hooks: IDE lifecycle hooks
        commands: Slash commands/scripts (legacy)
        skills: Claude skills (directories with SKILL.md)
        workflows: Windsurf workflows
        memory_files: CLAUDE.md memory files
        resources: Arbitrary files
    """

    instructions: list[InstructionComponent] = field(default_factory=list)
    mcp_servers: list[MCPServerComponent] = field(default_factory=list)
    hooks: list[HookComponent] = field(default_factory=list)
    commands: list[CommandComponent] = field(default_factory=list)
    skills: list[SkillComponent] = field(default_factory=list)
    workflows: list[WorkflowComponent] = field(default_factory=list)
    memory_files: list[MemoryFileComponent] = field(default_factory=list)
    resources: list[ResourceComponent] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        """Total number of components."""
        return (
            len(self.instructions)
            + len(self.mcp_servers)
            + len(self.hooks)
            + len(self.commands)
            + len(self.skills)
            + len(self.workflows)
            + len(self.memory_files)
            + len(self.resources)
        )

    @property
    def component_types(self) -> list[str]:
        """List of component types present."""
        types = []
        if self.instructions:
            types.append("instructions")
        if self.mcp_servers:
            types.append("mcp_servers")
        if self.hooks:
            types.append("hooks")
        if self.commands:
            types.append("commands")
        if self.skills:
            types.append("skills")
        if self.workflows:
            types.append("workflows")
        if self.memory_files:
            types.append("memory_files")
        if self.resources:
            types.append("resources")
        return types

    def __post_init__(self) -> None:
        """Validate components (currently allows empty packages for testing)."""
        # Note: Validation for at least one component is done in PackageManifestParser.validate()
        # but we allow empty packages here for edge case testing
        pass

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "instructions": [i.to_dict() for i in self.instructions],
            "mcp_servers": [m.to_dict() for m in self.mcp_servers],
            "hooks": [h.to_dict() for h in self.hooks],
            "commands": [c.to_dict() for c in self.commands],
            "skills": [s.to_dict() for s in self.skills],
            "workflows": [w.to_dict() for w in self.workflows],
            "memory_files": [m.to_dict() for m in self.memory_files],
            "resources": [r.to_dict() for r in self.resources],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PackageComponents":
        """Deserialize from dictionary."""
        return cls(
            instructions=[InstructionComponent.from_dict(i) for i in data.get("instructions", [])],
            mcp_servers=[MCPServerComponent.from_dict(m) for m in data.get("mcp_servers", [])],
            hooks=[HookComponent.from_dict(h) for h in data.get("hooks", [])],
            commands=[CommandComponent.from_dict(c) for c in data.get("commands", [])],
            skills=[SkillComponent.from_dict(s) for s in data.get("skills", [])],
            workflows=[WorkflowComponent.from_dict(w) for w in data.get("workflows", [])],
            memory_files=[MemoryFileComponent.from_dict(m) for m in data.get("memory_files", [])],
            resources=[ResourceComponent.from_dict(r) for r in data.get("resources", [])],
        )


@dataclass
class Package:
    """
    A bundle of related configuration components with metadata.

    Attributes:
        name: Package identifier (lowercase, hyphenated)
        version: Semantic version (major.minor.patch)
        description: Human-readable description
        author: Package author/maintainer
        license: License identifier (e.g., MIT, Apache-2.0)
        namespace: Repository namespace (e.g., owner/repo)
        components: Included components
        created_at: Package creation timestamp
        updated_at: Last update timestamp
    """

    name: str
    version: str
    description: str
    author: str
    license: str
    namespace: str
    components: PackageComponents
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate package data."""
        if not self.name:
            raise ValueError("Package name cannot be empty")
        if not self.name.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"Package name '{self.name}' must be lowercase alphanumeric with hyphens")
        if not self.version:
            raise ValueError("Package version cannot be empty")
        if not self.namespace:
            raise ValueError("Package namespace cannot be empty")

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "namespace": self.namespace,
            "components": self.components.to_dict(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Package":
        """Deserialize from dictionary."""
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        updated_at = None
        if data.get("updated_at"):
            updated_at = datetime.fromisoformat(data["updated_at"])
        return cls(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            license=data["license"],
            namespace=data["namespace"],
            components=PackageComponents.from_dict(data["components"]),
            created_at=created_at,
            updated_at=updated_at,
        )


@dataclass
class InstalledComponent:
    """
    Tracks individual installed component within a package.

    Attributes:
        type: Component type
        name: Component name
        installed_path: Relative path where installed
        checksum: File checksum for update detection
        status: Installation status
    """

    type: ComponentType
    name: str
    installed_path: str
    checksum: str
    status: ComponentStatus

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "type": self.type.value,
            "name": self.name,
            "installed_path": self.installed_path,
            "checksum": self.checksum,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InstalledComponent":
        """Deserialize from dictionary."""
        return cls(
            type=ComponentType(data["type"]),
            name=data["name"],
            installed_path=data["installed_path"],
            checksum=data["checksum"],
            status=ComponentStatus(data["status"]),
        )


@dataclass
class PackageInstallationRecord:
    """
    Tracks installed package in a project.

    Attributes:
        package_name: Package identifier
        namespace: Repository namespace
        version: Installed version
        installed_at: Installation timestamp
        updated_at: Last update timestamp
        scope: Installation scope (project_level)
        components: Installed component details
        status: Installation state
    """

    package_name: str
    namespace: str
    version: str
    installed_at: datetime
    updated_at: datetime
    scope: InstallationScope
    components: list[InstalledComponent]
    status: InstallationStatus

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "package_name": self.package_name,
            "namespace": self.namespace,
            "version": self.version,
            "installed_at": self.installed_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "scope": self.scope.value,
            "components": [c.to_dict() for c in self.components],
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PackageInstallationRecord":
        """Deserialize from dictionary."""
        return cls(
            package_name=data["package_name"],
            namespace=data["namespace"],
            version=data["version"],
            installed_at=datetime.fromisoformat(data["installed_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            scope=InstallationScope(data["scope"]),
            components=[InstalledComponent.from_dict(c) for c in data.get("components", [])],
            status=InstallationStatus(data["status"]),
        )
