"""IDE capability registry for package component support."""

from dataclasses import dataclass

from aiconfigkit.core.models import AIToolType, ComponentType


@dataclass
class IDECapability:
    """
    Defines what component types an IDE supports.

    Tracks which package components (instructions, MCP servers, hooks, etc.)
    can be installed to each AI coding tool.
    """

    tool_type: AIToolType
    tool_name: str
    supported_components: set[ComponentType]
    instructions_directory: str
    instruction_file_extension: str
    supports_project_scope: bool = True
    supports_global_scope: bool = False
    mcp_config_path: str | None = None
    mcp_project_config_path: str | None = None  # Project-level MCP config
    hooks_directory: str | None = None
    commands_directory: str | None = None
    skills_directory: str | None = None  # Claude skills
    workflows_directory: str | None = None  # Windsurf workflows
    memory_file_name: str | None = None  # CLAUDE.md
    notes: str = ""

    def supports_component(self, component_type: ComponentType) -> bool:
        """
        Check if IDE supports a specific component type.

        Args:
            component_type: Component type to check

        Returns:
            True if supported, False otherwise
        """
        return component_type in self.supported_components


# IDE Capability Registry
# Maps each AI tool to its supported component types and installation paths

CAPABILITY_REGISTRY: dict[AIToolType, IDECapability] = {
    AIToolType.CURSOR: IDECapability(
        tool_type=AIToolType.CURSOR,
        tool_name="Cursor",
        supported_components={
            ComponentType.INSTRUCTION,
            ComponentType.MCP_SERVER,
            ComponentType.RESOURCE,
        },
        instructions_directory=".cursor/rules/",
        instruction_file_extension=".mdc",
        supports_project_scope=True,
        supports_global_scope=True,
        mcp_config_path="~/.cursor/mcp.json",
        mcp_project_config_path=".cursor/mcp.json",
        hooks_directory=None,  # Hooks not supported
        commands_directory=None,  # Commands not supported
        notes=(
            "Cursor uses .mdc (markdown with metadata) files in .cursor/rules/. "
            "MCP servers configured via ~/.cursor/mcp.json (global) or .cursor/mcp.json (project). "
            "Supports up to 40 MCP tools. Resources not yet supported in MCP."
        ),
    ),
    AIToolType.CLAUDE: IDECapability(
        tool_type=AIToolType.CLAUDE,
        tool_name="Claude Code",
        supported_components={
            ComponentType.INSTRUCTION,
            ComponentType.MCP_SERVER,
            ComponentType.HOOK,
            ComponentType.COMMAND,
            ComponentType.SKILL,
            ComponentType.MEMORY_FILE,
            ComponentType.RESOURCE,
        },
        instructions_directory=".claude/rules/",
        instruction_file_extension=".md",
        supports_project_scope=True,
        supports_global_scope=False,
        mcp_config_path="~/.claude/settings.json",
        mcp_project_config_path=".claude/settings.local.json",
        hooks_directory=".claude/hooks/",
        commands_directory=".claude/commands/",
        skills_directory=".claude/skills/",
        memory_file_name="CLAUDE.md",
        notes=(
            "Claude Code uses .md files in .claude/rules/. "
            "Full support for MCP servers, hooks, slash commands, and skills. "
            "CLAUDE.md files persist context across sessions."
        ),
    ),
    AIToolType.WINSURF: IDECapability(
        tool_type=AIToolType.WINSURF,
        tool_name="Windsurf",
        supported_components={
            ComponentType.INSTRUCTION,
            ComponentType.MCP_SERVER,
            ComponentType.WORKFLOW,
            ComponentType.RESOURCE,
        },
        instructions_directory=".windsurf/rules/",
        instruction_file_extension=".md",
        supports_project_scope=True,
        supports_global_scope=True,
        mcp_config_path="~/.codeium/windsurf/mcp_config.json",
        mcp_project_config_path=None,  # Windsurf uses global MCP config only
        hooks_directory=None,  # Hooks not supported
        commands_directory=None,  # Commands not supported
        workflows_directory=".windsurf/workflows/",
        notes=(
            "Windsurf uses .md files in .windsurf/rules/ with 4 activation modes. "
            "MCP servers configured via ~/.codeium/windsurf/mcp_config.json. "
            "Supports workflows in .windsurf/workflows/. Limit of 100 MCP tools."
        ),
    ),
    AIToolType.KIRO: IDECapability(
        tool_type=AIToolType.KIRO,
        tool_name="Kiro",
        supported_components={
            ComponentType.INSTRUCTION,
            ComponentType.RESOURCE,
        },
        instructions_directory=".kiro/steering/",
        instruction_file_extension=".md",
        supports_project_scope=True,
        supports_global_scope=False,
        mcp_config_path=None,  # Kiro uses .kiro/settings/mcp.json but not yet supported
        mcp_project_config_path=None,
        hooks_directory=None,  # Kiro hooks use .kiro.hook JSON format, not yet supported
        commands_directory=None,
        notes=(
            "Kiro uses .md files in .kiro/steering/ with optional YAML front matter "
            "for inclusion modes (always, fileMatch, manual, auto). "
            "MCP and hooks support deferred to future release."
        ),
    ),
    AIToolType.CLINE: IDECapability(
        tool_type=AIToolType.CLINE,
        tool_name="Cline",
        supported_components={
            ComponentType.INSTRUCTION,
            ComponentType.RESOURCE,
        },
        instructions_directory=".clinerules/",
        instruction_file_extension=".md",
        supports_project_scope=True,
        supports_global_scope=False,
        mcp_config_path=None,  # Cline MCP is global-only via cline_mcp_settings.json in VS Code globalStorage
        mcp_project_config_path=None,
        hooks_directory=None,
        commands_directory=None,
        notes=(
            "Cline uses .md files in .clinerules/ directory (recursive). "
            "Supports optional YAML frontmatter with paths: for conditional activation. "
            "MCP configured globally via cline_mcp_settings.json, no project-level MCP support."
        ),
    ),
    AIToolType.ROO: IDECapability(
        tool_type=AIToolType.ROO,
        tool_name="Roo Code",
        supported_components={
            ComponentType.INSTRUCTION,
            ComponentType.MCP_SERVER,
            ComponentType.COMMAND,
            ComponentType.RESOURCE,
        },
        instructions_directory=".roo/rules/",
        instruction_file_extension=".md",
        supports_project_scope=True,
        supports_global_scope=True,
        mcp_config_path=None,  # Global MCP via globalStorage cline_mcp_settings.json
        mcp_project_config_path=".roo/mcp.json",
        hooks_directory=None,  # Hooks not supported
        commands_directory=".roo/commands/",
        notes=(
            "Roo Code uses .md files in .roo/rules/ directory (recursive). "
            "Mode-specific rules in .roo/rules-{mode-slug}/. "
            "MCP configured via .roo/mcp.json (project) or globalStorage (global). "
            "Slash commands in .roo/commands/. Global rules at ~/.roo/rules/."
        ),
    ),
    AIToolType.COPILOT: IDECapability(
        tool_type=AIToolType.COPILOT,
        tool_name="GitHub Copilot",
        supported_components={
            ComponentType.INSTRUCTION,
            ComponentType.MCP_SERVER,
        },
        instructions_directory=".github/instructions/",
        instruction_file_extension=".instructions.md",
        supports_project_scope=True,
        supports_global_scope=True,
        mcp_config_path="~/.vscode/mcp.json",  # User-level MCP config
        mcp_project_config_path=".vscode/mcp.json",  # Workspace-level MCP config
        hooks_directory=None,  # Hooks not supported
        commands_directory=None,  # Commands not supported
        notes=(
            "GitHub Copilot uses .github/copilot-instructions.md (main) and "
            ".github/instructions/**/*.instructions.md (file-specific with globs). "
            "MCP servers configured via .vscode/mcp.json. Limit of 128 tools."
        ),
    ),
}


def get_capability(tool_type: AIToolType) -> IDECapability:
    """
    Get capability information for an IDE.

    Args:
        tool_type: AI tool type

    Returns:
        IDECapability for the tool

    Raises:
        KeyError: If tool type is not in registry
    """
    return CAPABILITY_REGISTRY[tool_type]


def get_supported_tools_for_component(component_type: ComponentType) -> list[AIToolType]:
    """
    Get list of IDEs that support a specific component type.

    Args:
        component_type: Component type to check

    Returns:
        List of AI tool types that support this component
    """
    supported_tools = []
    for tool_type, capability in CAPABILITY_REGISTRY.items():
        if capability.supports_component(component_type):
            supported_tools.append(tool_type)
    return supported_tools


def validate_component_support(tool_type: AIToolType, component_type: ComponentType) -> bool:
    """
    Validate that an IDE supports a component type.

    Args:
        tool_type: AI tool type
        component_type: Component type to validate

    Returns:
        True if supported, False otherwise
    """
    try:
        capability = get_capability(tool_type)
        return capability.supports_component(component_type)
    except KeyError:
        return False
