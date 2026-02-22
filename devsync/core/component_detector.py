"""Component detection for scanning project directories to find packageable components."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

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


@dataclass
class DetectedWorkflow:
    """A Windsurf workflow detected in the project.

    Attributes:
        name: Workflow name
        file_path: Absolute path to workflow file
        relative_path: Path relative to project root
        description: Workflow description
    """

    name: str
    file_path: Path
    relative_path: str
    description: str = ""


@dataclass
class DetectedMemoryFile:
    """A CLAUDE.md memory file detected in the project.

    Memory files persist context across Claude Code sessions.

    Attributes:
        name: Identifier (path-based for subdirectory files)
        file_path: Absolute path to file
        relative_path: Path relative to project root
        is_root: Whether this is the root CLAUDE.md
        content_preview: First 100 chars of content
    """

    name: str
    file_path: Path
    relative_path: str
    is_root: bool = False
    content_preview: str = ""


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


class ComponentDetector:
    """Scans project directories to detect packageable components.

    Detection locations:
    - Instructions: .claude/rules/, .cursor/rules/, .windsurf/rules/, .github/instructions/**/*
    - Main Copilot instructions: .github/copilot-instructions.md
    - MCP servers: .claude/settings.local.json (mcpServers section), .devsync/mcp/
    - Hooks: .claude/hooks/
    - Commands: .claude/commands/ (legacy)
    - Skills: .claude/skills/ (directories with SKILL.md)
    - Workflows: .windsurf/workflows/
    - Memory files: CLAUDE.md at root and subdirectories
    - Resources: .devsync/resources/
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

    # Single-file instruction locations (not directories)
    SINGLE_INSTRUCTION_FILES = {
        ".github/copilot-instructions.md": "copilot",
        "AGENTS.md": "codex",
        "ANTEROOM.md": "anteroom",
    }

    INSTRUCTION_EXTENSIONS = {".md", ".mdc", ".instructions.md"}

    MCP_CONFIG_LOCATIONS = [
        ".claude/settings.local.json",
    ]

    HOOK_LOCATIONS = [
        ".claude/hooks",
    ]

    COMMAND_LOCATIONS = [
        ".claude/commands",
    ]

    SKILL_LOCATIONS = [
        ".claude/skills",
    ]

    WORKFLOW_LOCATIONS = [
        ".windsurf/workflows",
    ]

    MEMORY_FILE_NAME = "CLAUDE.md"

    RESOURCE_LOCATIONS = [
        ".devsync/resources",
    ]

    MAX_RESOURCE_SIZE = 200 * 1024 * 1024  # 200 MB
    WARN_RESOURCE_SIZE = 50 * 1024 * 1024  # 50 MB

    def __init__(self, project_root: Path):
        """Initialize detector with project root.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root.resolve()

    def detect_all(self) -> DetectionResult:
        """Detect all packageable components in the project.

        Returns:
            DetectionResult with all detected components
        """
        result = DetectionResult()

        detected_instructions = self._detect_instructions()
        result.instructions = detected_instructions

        detected_mcp = self._detect_mcp_servers()
        result.mcp_servers = detected_mcp

        detected_hooks = self._detect_hooks()
        result.hooks = detected_hooks

        detected_commands = self._detect_commands()
        result.commands = detected_commands

        detected_skills = self._detect_skills()
        result.skills = detected_skills

        detected_workflows = self._detect_workflows()
        result.workflows = detected_workflows

        detected_memory_files = self._detect_memory_files()
        result.memory_files = detected_memory_files

        detected_resources = self._detect_resources()
        result.resources = detected_resources

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

        # Detect directory-based instructions
        for location, ide_name in self.INSTRUCTION_LOCATIONS.items():
            dir_path = self.project_root / location
            if not dir_path.exists() or not dir_path.is_dir():
                continue

            # Use recursive glob for copilot to support subdirectories
            if ide_name == "copilot":
                file_iter = dir_path.rglob("*")
            else:
                file_iter = dir_path.iterdir()

            for file_path in file_iter:
                if not file_path.is_file():
                    continue

                # Check extension
                suffix = file_path.suffix.lower()
                if suffix not in self.INSTRUCTION_EXTENSIONS:
                    continue

                try:
                    # For copilot, include subdirectory in name
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

        # Detect single-file instructions (e.g., .github/copilot-instructions.md)
        for file_location, ide_name in self.SINGLE_INSTRUCTION_FILES.items():
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
        """Detect MCP server configurations.

        Returns:
            List of detected MCP servers
        """
        servers: list[DetectedMCPServer] = []

        for config_location in self.MCP_CONFIG_LOCATIONS:
            config_path = self.project_root / config_location
            if not config_path.exists():
                continue

            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                mcp_servers = config_data.get("mcpServers", {})
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
                            source=config_location,
                            env_vars=env_vars,
                            pip_package=pip_package,
                        )
                    )
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in {config_path}: {e}")
            except Exception as e:
                logger.warning(f"Failed to read MCP config {config_path}: {e}")

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
        """Detect hook scripts.

        Returns:
            List of detected hooks
        """
        hooks: list[DetectedHook] = []

        for location in self.HOOK_LOCATIONS:
            hook_dir = self.project_root / location
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
        """Detect command scripts.

        Returns:
            List of detected commands
        """
        commands: list[DetectedCommand] = []

        for location in self.COMMAND_LOCATIONS:
            cmd_dir = self.project_root / location
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
        """Detect Claude skill directories.

        Skills are directories containing SKILL.md with optional supporting files.

        Returns:
            List of detected skills
        """
        skills: list[DetectedSkill] = []

        for location in self.SKILL_LOCATIONS:
            skill_dir = self.project_root / location
            if not skill_dir.exists() or not skill_dir.is_dir():
                continue

            for item in skill_dir.iterdir():
                if not item.is_dir():
                    continue

                skill_md = item / "SKILL.md"
                if not skill_md.exists():
                    # Also check for Skill.md (case-insensitive)
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
        """Detect Windsurf workflow files.

        Returns:
            List of detected workflows
        """
        workflows: list[DetectedWorkflow] = []

        for location in self.WORKFLOW_LOCATIONS:
            workflow_dir = self.project_root / location
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
        """Detect CLAUDE.md memory files.

        Detects CLAUDE.md at project root and in subdirectories.

        Returns:
            List of detected memory files
        """
        memory_files: list[DetectedMemoryFile] = []

        # Check root CLAUDE.md
        root_memory = self.project_root / self.MEMORY_FILE_NAME
        if root_memory.exists() and root_memory.is_file():
            try:
                content = root_memory.read_text(encoding="utf-8")
                content_preview = content[:100] if content else ""
                memory_files.append(
                    DetectedMemoryFile(
                        name="CLAUDE",
                        file_path=root_memory,
                        relative_path=self.MEMORY_FILE_NAME,
                        is_root=True,
                        content_preview=content_preview,
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to read memory file {root_memory}: {e}")

        # Find CLAUDE.md in subdirectories (not too deep)
        for file_path in self.project_root.rglob(self.MEMORY_FILE_NAME):
            if file_path == root_memory:
                continue
            if not file_path.is_file():
                continue

            # Skip common non-project directories
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts
            if any(p.startswith(".") and p not in {".claude", ".github"} for p in parts[:-1]):
                continue
            if any(p in {"node_modules", "venv", ".venv", "__pycache__", "dist", "build"} for p in parts):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                content_preview = content[:100] if content else ""
                # Create name from directory path
                parent_parts = parts[:-1]
                name = "-".join(parent_parts) + "-CLAUDE" if parent_parts else "CLAUDE"

                memory_files.append(
                    DetectedMemoryFile(
                        name=name,
                        file_path=file_path,
                        relative_path=str(rel_path),
                        is_root=False,
                        content_preview=content_preview,
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
            mcp_servers.append(
                MCPServerComponent(
                    name=mcp.name,
                    file=f"mcp/{mcp.name}.json",
                    description=f"MCP server from {mcp.source}" if include_descriptions else "",
                    credentials=[],
                    ide_support=["claude"],
                )
            )

        hooks = [
            HookComponent(
                name=hook.name,
                file=hook.relative_path,
                description=f"{hook.hook_type} hook" if include_descriptions else "",
                hook_type=hook.hook_type,
                ide_support=["claude"],
            )
            for hook in detection_result.hooks
        ]

        commands = [
            CommandComponent(
                name=cmd.name,
                file=cmd.relative_path,
                description=f"{cmd.command_type} command" if include_descriptions else "",
                command_type=cmd.command_type,
                ide_support=["claude"],
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
                description=skill.description or ("Claude skill" if include_descriptions else ""),
                ide_support=["claude"],
            )
            for skill in detection_result.skills
        ]

        workflows = [
            WorkflowComponent(
                name=wf.name,
                file=wf.relative_path,
                description=wf.description or ("Windsurf workflow" if include_descriptions else ""),
                ide_support=["windsurf"],
            )
            for wf in detection_result.workflows
        ]

        memory_files = [
            MemoryFileComponent(
                name=mem.name,
                file=mem.relative_path,
                description=("Root memory file" if mem.is_root else "Memory file") if include_descriptions else "",
                ide_support=["claude"],
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
