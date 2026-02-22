"""Component detection for scanning project directories to find packageable components."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from devsync.core.checksum import calculate_file_checksum
from devsync.core.models import (
    CommandComponent,
    HookComponent,
    InstructionComponent,
    MCPServerComponent,
    MemoryFileComponent,
    PackageComponents,
    ResourceComponent,
    SkillComponent,
    WorkflowComponent,
)

logger = logging.getLogger(__name__)


@dataclass
class DetectedInstruction:
    """An instruction file detected in the project.

    Attributes:
        name: Derived instruction name
        file_path: Absolute path to file
        relative_path: Path relative to project root
        source_ide: Which IDE directory it was found in
        content_preview: First 100 chars of content
    """

    name: str
    file_path: Path
    relative_path: str
    source_ide: str
    content_preview: str = ""


@dataclass
class DetectedMCPServer:
    """An MCP server configuration detected in the project.

    Attributes:
        name: Server name from config
        file_path: Path to config file (if file-based)
        config: The MCP server configuration dict
        source: Where the config was found (e.g., ".claude/settings.local.json")
        env_vars: Environment variables used by this server
    """

    name: str
    file_path: Optional[Path]
    config: dict
    source: str
    env_vars: list[str] = field(default_factory=list)
    pip_package: Optional[str] = None
    source_tool: str = ""


@dataclass
class DetectedHook:
    """A hook script detected in the project.

    Attributes:
        name: Hook name
        file_path: Absolute path to file
        relative_path: Path relative to project root
        hook_type: Type of hook (e.g., PreToolUse, PostToolUse)
    """

    name: str
    file_path: Path
    relative_path: str
    hook_type: str
    source_tool: str = ""


@dataclass
class DetectedCommand:
    """A command script detected in the project.

    Attributes:
        name: Command name
        file_path: Absolute path to file
        relative_path: Path relative to project root
        command_type: Type of command (slash, shell)
    """

    name: str
    file_path: Path
    relative_path: str
    command_type: str
    source_tool: str = ""


@dataclass
class DetectedResource:
    """A resource file detected in the project.

    Attributes:
        name: Resource name
        file_path: Absolute path to file
        relative_path: Path relative to project root
        size: File size in bytes
        checksum: SHA256 checksum
    """

    name: str
    file_path: Path
    relative_path: str
    size: int
    checksum: str


@dataclass
class DetectedSkill:
    """A Claude skill detected in the project.

    Skills are directories containing SKILL.md with optional supporting files.

    Attributes:
        name: Skill name (directory name)
        dir_path: Absolute path to skill directory
        relative_path: Path relative to project root
        description: Description from SKILL.md frontmatter
        has_scripts: Whether skill has supporting scripts
    """

    name: str
    dir_path: Path
    relative_path: str
    description: str = ""
    has_scripts: bool = False
    source_tool: str = ""


@dataclass
class DetectedWorkflow:
    """A Windsurf workflow detected in the project.

    Attributes:
        name: Workflow name
        file_path: Absolute path to workflow file
        relative_path: Path relative to project root
        description: Workflow description
        source_tool: Which tool this workflow belongs to
    """

    name: str
    file_path: Path
    relative_path: str
    description: str = ""
    source_tool: str = ""


@dataclass
class DetectedMemoryFile:
    """A memory file detected in the project (e.g. CLAUDE.md, GEMINI.md).

    Memory files persist context across AI tool sessions.

    Attributes:
        name: Identifier (path-based for subdirectory files)
        file_path: Absolute path to file
        relative_path: Path relative to project root
        is_root: Whether this is the root memory file
        content_preview: First 100 chars of content
        source_tool: Which tool this memory file belongs to
    """

    name: str
    file_path: Path
    relative_path: str
    is_root: bool = False
    content_preview: str = ""
    source_tool: str = ""


@dataclass
class DetectionResult:
    """Result of component detection scan.

    Attributes:
        instructions: Detected instruction files
        mcp_servers: Detected MCP server configurations
        hooks: Detected hook scripts
        commands: Detected command scripts (legacy)
        skills: Detected Claude skills
        workflows: Detected Windsurf workflows
        memory_files: Detected CLAUDE.md memory files
        resources: Detected resource files
        warnings: Non-fatal issues encountered
    """

    instructions: list[DetectedInstruction] = field(default_factory=list)
    mcp_servers: list[DetectedMCPServer] = field(default_factory=list)
    hooks: list[DetectedHook] = field(default_factory=list)
    commands: list[DetectedCommand] = field(default_factory=list)
    skills: list[DetectedSkill] = field(default_factory=list)
    workflows: list[DetectedWorkflow] = field(default_factory=list)
    memory_files: list[DetectedMemoryFile] = field(default_factory=list)
    resources: list[DetectedResource] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        """Total number of detected components."""
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


COMPONENT_TYPE_MAP: dict[str, str] = {
    "rules": "instructions",
    "instructions": "instructions",
    "mcp": "mcp_servers",
    "mcp_servers": "mcp_servers",
    "hooks": "hooks",
    "commands": "commands",
    "skills": "skills",
    "workflows": "workflows",
    "memory": "memory_files",
    "memory_files": "memory_files",
    "resources": "resources",
}


def filter_detection_result(
    result: DetectionResult,
    tool_filter: list[str] | None = None,
    component_filter: list[str] | None = None,
) -> DetectionResult:
    """Filter a DetectionResult by tool and/or component type.

    Args:
        result: The detection result to filter.
        tool_filter: If set, only keep components from these tools.
        component_filter: If set, only keep these component types
            (keys from COMPONENT_TYPE_MAP).

    Returns:
        A new DetectionResult with filtered lists.
    """
    allowed_fields: set[str] | None = None
    if component_filter:
        allowed_fields = set()
        for comp in component_filter:
            mapped = COMPONENT_TYPE_MAP.get(comp.lower())
            if mapped:
                allowed_fields.add(mapped)

    def _filter_by_tool(items: list, tool_attr: str = "source_tool") -> list:
        if not tool_filter:
            return items
        lower_filter = {t.lower() for t in tool_filter}
        return [item for item in items if getattr(item, tool_attr, "").lower() in lower_filter]

    def _get_field(field_name: str, items: list, tool_attr: str = "source_tool") -> list:
        if allowed_fields is not None and field_name not in allowed_fields:
            return []
        return _filter_by_tool(items, tool_attr)

    return DetectionResult(
        instructions=_get_field("instructions", result.instructions, "source_ide"),
        mcp_servers=_get_field("mcp_servers", result.mcp_servers),
        hooks=_get_field("hooks", result.hooks),
        commands=_get_field("commands", result.commands),
        skills=_get_field("skills", result.skills),
        workflows=_get_field("workflows", result.workflows),
        memory_files=_get_field("memory_files", result.memory_files),
        # Resources are tool-agnostic (.devsync/resources/), skip tool filtering
        resources=result.resources if (allowed_fields is None or "resources" in allowed_fields) else [],
        warnings=result.warnings,
    )


class ComponentDetector:
    """Scans project directories to detect packageable components.

    Uses the IDE capability registry to discover components from all supported
    AI tools, not just Claude. Supports project and global scope detection.

    Detection locations are derived from CAPABILITY_REGISTRY plus:
    - Instructions: INSTRUCTION_LOCATIONS (kept as-is for directory-based)
    - Single-file instructions: SINGLE_INSTRUCTION_FILES
    - MCP servers: Registry mcp_project_config_path / mcp_config_path
    - Hooks/Commands/Skills/Workflows/Memory: Registry directories
    - Resources: .devsync/resources/
    - Fallback MCP: .devsync/mcp/
    """

    INSTRUCTION_LOCATIONS = {
        ".claude/rules": "claude",
        ".cursor/rules": "cursor",
        ".windsurf/rules": "windsurf",
        ".kiro/steering": "kiro",
        ".clinerules": "cline",
        ".roo/rules": "roo",
        ".github/instructions": "copilot",
    }

    SINGLE_INSTRUCTION_FILES = {
        ".github/copilot-instructions.md": "copilot",
        "AGENTS.md": "codex",
        "ANTEROOM.md": "anteroom",
    }

    INSTRUCTION_EXTENSIONS = {".md", ".mdc", ".instructions.md"}

    RESOURCE_LOCATIONS = [
        ".devsync/resources",
    ]

    MAX_RESOURCE_SIZE = 200 * 1024 * 1024  # 200 MB
    WARN_RESOURCE_SIZE = 50 * 1024 * 1024  # 50 MB

    VALID_SCOPES = {"project", "global", "all"}

    def __init__(self, project_root: Path, scope: str = "project", tool_filter: list[str] | None = None):
        """Initialize detector with project root.

        Args:
            project_root: Path to project root directory
            scope: Detection scope — "project", "global", or "all"
            tool_filter: If set, only scan paths for these tool names

        Raises:
            ValueError: If scope is not one of project, global, all
        """
        if scope not in self.VALID_SCOPES:
            raise ValueError(f"Invalid scope: {scope!r}. Must be one of {self.VALID_SCOPES}")
        self.project_root = project_root.resolve()
        self.scope = scope
        self.tool_filter = tool_filter

    def _get_registry_entries(self) -> list[tuple[str, Any]]:
        """Get registry entries filtered by tool_filter.

        Returns:
            List of (tool_name, capability) tuples.
        """
        from devsync.ai_tools.capability_registry import CAPABILITY_REGISTRY

        entries = []
        for _tool_type, cap in CAPABILITY_REGISTRY.items():
            tool_name = cap.tool_type.value
            if self.tool_filter:
                if tool_name not in {t.lower() for t in self.tool_filter}:
                    continue
            entries.append((tool_name, cap))
        return entries

    def detect_all(self) -> DetectionResult:
        """Detect all packageable components in the project.

        Returns:
            DetectionResult with all detected components
        """
        result = DetectionResult()
        result.instructions = self._detect_instructions()
        result.mcp_servers = self._detect_mcp_servers()
        result.hooks = self._detect_hooks()
        result.commands = self._detect_commands()
        result.skills = self._detect_skills()
        result.workflows = self._detect_workflows()
        result.memory_files = self._detect_memory_files()
        result.resources = self._detect_resources()
        return result

    def _detect_instructions(self) -> list[DetectedInstruction]:
        """Detect instruction files in IDE-specific directories.

        Supports:
        - Directory-based: .claude/rules/, .cursor/rules/, .windsurf/rules/
        - Recursive: .github/instructions/**/*.instructions.md
        - Single-file: .github/copilot-instructions.md

        Returns:
            List of detected instructions
        """
        instructions: list[DetectedInstruction] = []

        for location, ide_name in self.INSTRUCTION_LOCATIONS.items():
            if self.tool_filter and ide_name not in {t.lower() for t in self.tool_filter}:
                continue

            dir_path = self.project_root / location
            if not dir_path.exists() or not dir_path.is_dir():
                continue

            if ide_name == "copilot":
                file_iter = dir_path.rglob("*")
            else:
                file_iter = dir_path.iterdir()

            for file_path in file_iter:
                if not file_path.is_file():
                    continue

                suffix = file_path.suffix.lower()
                if suffix not in self.INSTRUCTION_EXTENSIONS:
                    continue

                try:
                    if ide_name == "copilot":
                        rel_to_dir = file_path.relative_to(dir_path)
                        if file_path.name.endswith(".instructions.md"):
                            name = str(rel_to_dir).replace(".instructions.md", "").replace("/", "-")
                        else:
                            name = file_path.stem
                    else:
                        name = file_path.stem
                    relative_path = str(file_path.relative_to(self.project_root))
                    content = file_path.read_text(encoding="utf-8")
                    content_preview = content[:100] if content else ""

                    instructions.append(
                        DetectedInstruction(
                            name=name,
                            file_path=file_path,
                            relative_path=relative_path,
                            source_ide=ide_name,
                            content_preview=content_preview,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to read instruction {file_path}: {e}")

        for file_location, ide_name in self.SINGLE_INSTRUCTION_FILES.items():
            if self.tool_filter and ide_name not in {t.lower() for t in self.tool_filter}:
                continue

            file_path = self.project_root / file_location
            if not file_path.exists() or not file_path.is_file():
                continue

            try:
                name = file_path.stem
                relative_path = str(file_path.relative_to(self.project_root))
                content = file_path.read_text(encoding="utf-8")
                content_preview = content[:100] if content else ""

                instructions.append(
                    DetectedInstruction(
                        name=name,
                        file_path=file_path,
                        relative_path=relative_path,
                        source_ide=ide_name,
                        content_preview=content_preview,
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to read instruction {file_path}: {e}")

        return instructions

    def _detect_mcp_servers(self) -> list[DetectedMCPServer]:
        """Detect MCP server configurations from all registered tools.

        Iterates registry-derived project and global config paths, using
        each tool's mcp_servers_json_key for parsing.

        Returns:
            List of detected MCP servers
        """
        servers: list[DetectedMCPServer] = []
        seen_paths: set[Path] = set()

        for tool_name, cap in self._get_registry_entries():
            paths_to_check: list[tuple[Path, str]] = []

            if self.scope in ("project", "all") and cap.mcp_project_config_path:
                paths_to_check.append((self.project_root / cap.mcp_project_config_path, cap.mcp_project_config_path))

            if self.scope in ("global", "all") and cap.mcp_config_path:
                expanded = Path(cap.mcp_config_path).expanduser().resolve()
                if not str(expanded).startswith(str(Path.home())):
                    logger.warning(f"Skipping global MCP path that escapes home directory: {cap.mcp_config_path}")
                    continue
                paths_to_check.append((expanded, cap.mcp_config_path))

            json_key = cap.mcp_servers_json_key

            for config_path, source_label in paths_to_check:
                resolved = config_path.resolve()
                if resolved in seen_paths:
                    continue
                if not config_path.exists():
                    continue
                seen_paths.add(resolved)

                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)

                    mcp_servers = config_data.get(json_key, {})
                    for server_name, server_config in mcp_servers.items():
                        env_vars = list(server_config.get("env", {}).keys())
                        pip_package = self._resolve_pip_package(
                            server_config.get("command", ""),
                            server_config.get("args", []),
                        )
                        servers.append(
                            DetectedMCPServer(
                                name=server_name,
                                file_path=config_path,
                                config=server_config,
                                source=source_label,
                                env_vars=env_vars,
                                pip_package=pip_package,
                                source_tool=tool_name,
                            )
                        )
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON in {config_path}: {e}")
                except Exception as e:
                    logger.warning(f"Failed to read MCP config {config_path}: {e}")

        # Fallback: .devsync/mcp/ directory (tool-agnostic)
        mcp_dir = self.project_root / ".devsync" / "mcp"
        if mcp_dir.exists() and mcp_dir.is_dir():
            for file_path in mcp_dir.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        server_config = json.load(f)
                    env_vars = list(server_config.get("env", {}).keys())
                    pip_package = self._resolve_pip_package(
                        server_config.get("command", ""),
                        server_config.get("args", []),
                    )
                    servers.append(
                        DetectedMCPServer(
                            name=file_path.stem,
                            file_path=file_path,
                            config=server_config,
                            source=str(file_path.relative_to(self.project_root)),
                            env_vars=env_vars,
                            pip_package=pip_package,
                            source_tool="devsync",
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to read MCP config {file_path}: {e}")

        return servers

    def _resolve_pip_package(self, command: str, args: list[str]) -> Optional[str]:
        """Attempt to resolve a pip package from an MCP server command.

        Non-fatal: returns None on any failure.

        Args:
            command: Server executable command.
            args: Server command arguments.

        Returns:
            Pip package name or None.
        """
        if not command:
            return None
        from devsync.core.pip_utils import resolve_pip_package_for_command

        return resolve_pip_package_for_command(command, args)

    def _detect_hooks(self) -> list[DetectedHook]:
        """Detect hook scripts from registry-derived paths.

        Returns:
            List of detected hooks
        """
        hooks: list[DetectedHook] = []

        for tool_name, cap in self._get_registry_entries():
            if not cap.hooks_directory:
                continue

            hook_dir = self.project_root / cap.hooks_directory
            if not hook_dir.exists() or not hook_dir.is_dir():
                continue

            for file_path in hook_dir.iterdir():
                if not file_path.is_file():
                    continue

                hook_type = self._infer_hook_type(file_path.name)
                name = file_path.stem

                hooks.append(
                    DetectedHook(
                        name=name,
                        file_path=file_path,
                        relative_path=str(file_path.relative_to(self.project_root)),
                        hook_type=hook_type,
                        source_tool=tool_name,
                    )
                )

        return hooks

    def _infer_hook_type(self, filename: str) -> str:
        """Infer hook type from filename.

        Args:
            filename: Name of the hook file

        Returns:
            Hook type string
        """
        filename_lower = filename.lower()
        if "pretooluse" in filename_lower or "pre-tool" in filename_lower:
            return "PreToolUse"
        elif "posttooluse" in filename_lower or "post-tool" in filename_lower:
            return "PostToolUse"
        elif "notification" in filename_lower:
            return "Notification"
        elif "stop" in filename_lower:
            return "Stop"
        return "Unknown"

    def _detect_commands(self) -> list[DetectedCommand]:
        """Detect command scripts from registry-derived paths.

        Returns:
            List of detected commands
        """
        commands: list[DetectedCommand] = []

        for tool_name, cap in self._get_registry_entries():
            if not cap.commands_directory:
                continue

            cmd_dir = self.project_root / cap.commands_directory
            if not cmd_dir.exists() or not cmd_dir.is_dir():
                continue

            for file_path in cmd_dir.iterdir():
                if not file_path.is_file():
                    continue

                command_type = self._infer_command_type(file_path)
                name = file_path.stem

                commands.append(
                    DetectedCommand(
                        name=name,
                        file_path=file_path,
                        relative_path=str(file_path.relative_to(self.project_root)),
                        command_type=command_type,
                        source_tool=tool_name,
                    )
                )

        return commands

    def _infer_command_type(self, file_path: Path) -> str:
        """Infer command type from file extension.

        Args:
            file_path: Path to command file

        Returns:
            Command type string
        """
        suffix = file_path.suffix.lower()
        if suffix in (".sh", ".bash"):
            return "shell"
        elif suffix in (".md", ".txt"):
            return "slash"
        return "shell"

    def _detect_resources(self) -> list[DetectedResource]:
        """Detect resource files.

        Returns:
            List of detected resources
        """
        resources: list[DetectedResource] = []

        for location in self.RESOURCE_LOCATIONS:
            res_dir = self.project_root / location
            if not res_dir.exists() or not res_dir.is_dir():
                continue

            for file_path in res_dir.rglob("*"):
                if not file_path.is_file():
                    continue

                try:
                    size = file_path.stat().st_size

                    if size > self.MAX_RESOURCE_SIZE:
                        logger.warning(f"Resource {file_path} exceeds max size ({size} > {self.MAX_RESOURCE_SIZE})")
                        continue

                    if size > self.WARN_RESOURCE_SIZE:
                        logger.warning(f"Resource {file_path} is large ({size} bytes)")

                    checksum = calculate_file_checksum(str(file_path))
                    name = file_path.stem

                    resources.append(
                        DetectedResource(
                            name=name,
                            file_path=file_path,
                            relative_path=str(file_path.relative_to(self.project_root)),
                            size=size,
                            checksum=checksum,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to process resource {file_path}: {e}")

        return resources

    def _detect_skills(self) -> list[DetectedSkill]:
        """Detect skill directories from registry-derived paths.

        Skills are directories containing SKILL.md with optional supporting files.

        Returns:
            List of detected skills
        """
        skills: list[DetectedSkill] = []

        for tool_name, cap in self._get_registry_entries():
            if not cap.skills_directory:
                continue

            skill_dir = self.project_root / cap.skills_directory
            if not skill_dir.exists() or not skill_dir.is_dir():
                continue

            for item in skill_dir.iterdir():
                if not item.is_dir():
                    continue

                skill_md = item / "SKILL.md"
                if not skill_md.exists():
                    skill_md_lower = item / "Skill.md"
                    if skill_md_lower.exists():
                        skill_md = skill_md_lower
                    else:
                        continue

                try:
                    name = item.name
                    relative_path = str(item.relative_to(self.project_root))
                    description = self._extract_skill_description(skill_md)
                    has_scripts = any(item.glob("scripts/*")) or any(item.glob("*.sh"))

                    skills.append(
                        DetectedSkill(
                            name=name,
                            dir_path=item,
                            relative_path=relative_path,
                            description=description,
                            has_scripts=has_scripts,
                            source_tool=tool_name,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to process skill {item}: {e}")

        return skills

    def _extract_skill_description(self, skill_md_path: Path) -> str:
        """Extract description from SKILL.md frontmatter.

        Args:
            skill_md_path: Path to SKILL.md file

        Returns:
            Description string or empty string if not found
        """
        try:
            content = skill_md_path.read_text(encoding="utf-8")
            if content.startswith("---"):
                # Parse YAML frontmatter
                end_idx = content.find("---", 3)
                if end_idx != -1:
                    frontmatter = content[3:end_idx].strip()
                    for line in frontmatter.split("\n"):
                        if line.startswith("description:"):
                            return line.split(":", 1)[1].strip().strip("\"'")
        except Exception:
            pass
        return ""

    def _detect_workflows(self) -> list[DetectedWorkflow]:
        """Detect workflow files from registry-derived paths.

        Returns:
            List of detected workflows
        """
        workflows: list[DetectedWorkflow] = []

        for tool_name, cap in self._get_registry_entries():
            if not cap.workflows_directory:
                continue

            workflow_dir = self.project_root / cap.workflows_directory
            if not workflow_dir.exists() or not workflow_dir.is_dir():
                continue

            for file_path in workflow_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                if file_path.suffix.lower() not in {".md", ".yaml", ".yml"}:
                    continue

                try:
                    name = file_path.stem
                    relative_path = str(file_path.relative_to(self.project_root))
                    description = self._extract_workflow_description(file_path)

                    workflows.append(
                        DetectedWorkflow(
                            name=name,
                            file_path=file_path,
                            relative_path=relative_path,
                            description=description,
                            source_tool=tool_name,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to process workflow {file_path}: {e}")

        return workflows

    def _extract_workflow_description(self, workflow_path: Path) -> str:
        """Extract description from workflow file.

        Args:
            workflow_path: Path to workflow file

        Returns:
            Description string or empty string if not found
        """
        try:
            content = workflow_path.read_text(encoding="utf-8")
            if content.startswith("---"):
                end_idx = content.find("---", 3)
                if end_idx != -1:
                    frontmatter = content[3:end_idx].strip()
                    for line in frontmatter.split("\n"):
                        if line.startswith("description:"):
                            return line.split(":", 1)[1].strip().strip("\"'")
        except Exception:
            pass
        return ""

    def _detect_memory_files(self) -> list[DetectedMemoryFile]:
        """Detect memory files from registry-derived names.

        Detects memory files (e.g. CLAUDE.md, GEMINI.md) at project root
        and in subdirectories.

        Returns:
            List of detected memory files
        """
        memory_files: list[DetectedMemoryFile] = []
        seen_files: set[Path] = set()

        memory_file_names: dict[str, str] = {}
        for tool_name, cap in self._get_registry_entries():
            if cap.memory_file_name:
                memory_file_names[cap.memory_file_name] = tool_name

        for mem_file_name, tool_name in memory_file_names.items():
            stem = Path(mem_file_name).stem

            root_memory = self.project_root / mem_file_name
            if root_memory.exists() and root_memory.is_file() and root_memory not in seen_files:
                seen_files.add(root_memory)
                try:
                    content = root_memory.read_text(encoding="utf-8")
                    content_preview = content[:100] if content else ""
                    memory_files.append(
                        DetectedMemoryFile(
                            name=stem,
                            file_path=root_memory,
                            relative_path=mem_file_name,
                            is_root=True,
                            content_preview=content_preview,
                            source_tool=tool_name,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to read memory file {root_memory}: {e}")

            for file_path in self.project_root.rglob(mem_file_name):
                if file_path == root_memory:
                    continue
                if not file_path.is_file():
                    continue
                if file_path in seen_files:
                    continue
                seen_files.add(file_path)

                rel_path = file_path.relative_to(self.project_root)
                parts = rel_path.parts
                if any(p.startswith(".") and p not in {".claude", ".github"} for p in parts[:-1]):
                    continue
                if any(p in {"node_modules", "venv", ".venv", "__pycache__", "dist", "build"} for p in parts):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8")
                    content_preview = content[:100] if content else ""
                    parent_parts = parts[:-1]
                    name = "-".join(parent_parts) + f"-{stem}" if parent_parts else stem

                    memory_files.append(
                        DetectedMemoryFile(
                            name=name,
                            file_path=file_path,
                            relative_path=str(rel_path),
                            is_root=False,
                            content_preview=content_preview,
                            source_tool=tool_name,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to read memory file {file_path}: {e}")

        return memory_files

    def to_package_components(
        self,
        detection_result: DetectionResult,
        include_descriptions: bool = True,
    ) -> PackageComponents:
        """Convert detection results to PackageComponents for manifest generation.

        Args:
            detection_result: Detection scan result
            include_descriptions: Whether to generate placeholder descriptions

        Returns:
            PackageComponents ready for manifest
        """
        instructions = [
            InstructionComponent(
                name=inst.name,
                file=inst.relative_path,
                description=f"Instruction from {inst.source_ide}" if include_descriptions else "",
                tags=[inst.source_ide],
            )
            for inst in detection_result.instructions
        ]

        mcp_servers = []
        for mcp in detection_result.mcp_servers:
            ide = [mcp.source_tool] if mcp.source_tool else ["claude"]
            mcp_servers.append(
                MCPServerComponent(
                    name=mcp.name,
                    file=f"mcp/{mcp.name}.json",
                    description=f"MCP server from {mcp.source}" if include_descriptions else "",
                    credentials=[],
                    ide_support=ide,
                )
            )

        hooks = [
            HookComponent(
                name=hook.name,
                file=hook.relative_path,
                description=f"{hook.hook_type} hook" if include_descriptions else "",
                hook_type=hook.hook_type,
                ide_support=[hook.source_tool] if hook.source_tool else ["claude"],
            )
            for hook in detection_result.hooks
        ]

        commands = [
            CommandComponent(
                name=cmd.name,
                file=cmd.relative_path,
                description=f"{cmd.command_type} command" if include_descriptions else "",
                command_type=cmd.command_type,
                ide_support=[cmd.source_tool] if cmd.source_tool else ["claude"],
            )
            for cmd in detection_result.commands
        ]

        resources = [
            ResourceComponent(
                name=res.name,
                file=res.relative_path,
                description="Resource file" if include_descriptions else "",
                install_path=res.relative_path,
                checksum=f"sha256:{res.checksum}",
                size=res.size,
            )
            for res in detection_result.resources
        ]

        skills = [
            SkillComponent(
                name=skill.name,
                file=skill.relative_path,
                description=skill.description or ("Skill" if include_descriptions else ""),
                ide_support=[skill.source_tool] if skill.source_tool else ["claude"],
            )
            for skill in detection_result.skills
        ]

        workflows = [
            WorkflowComponent(
                name=wf.name,
                file=wf.relative_path,
                description=wf.description or ("Workflow" if include_descriptions else ""),
                ide_support=[wf.source_tool] if wf.source_tool else ["windsurf"],
            )
            for wf in detection_result.workflows
        ]

        memory_files = [
            MemoryFileComponent(
                name=mem.name,
                file=mem.relative_path,
                description=("Root memory file" if mem.is_root else "Memory file") if include_descriptions else "",
                ide_support=[mem.source_tool] if mem.source_tool else ["claude"],
            )
            for mem in detection_result.memory_files
        ]

        return PackageComponents(
            instructions=instructions,
            mcp_servers=mcp_servers,
            hooks=hooks,
            commands=commands,
            skills=skills,
            workflows=workflows,
            memory_files=memory_files,
            resources=resources,
        )
