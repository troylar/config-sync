"""Unit tests for IDE capability registry."""

import pytest

from aiconfigkit.ai_tools.capability_registry import (
    CAPABILITY_REGISTRY,
    IDECapability,
    get_capability,
    get_supported_tools_for_component,
    validate_component_support,
)
from aiconfigkit.core.models import AIToolType, ComponentType


class TestIDECapability:
    """Test IDECapability dataclass."""

    def test_create_capability(self) -> None:
        """Test creating an IDE capability."""
        capability = IDECapability(
            tool_type=AIToolType.CURSOR,
            tool_name="Cursor",
            supported_components={ComponentType.INSTRUCTION},
            instructions_directory=".cursor/rules/",
            instruction_file_extension=".mdc",
        )

        assert capability.tool_type == AIToolType.CURSOR
        assert capability.tool_name == "Cursor"
        assert ComponentType.INSTRUCTION in capability.supported_components
        assert capability.instructions_directory == ".cursor/rules/"
        assert capability.instruction_file_extension == ".mdc"

    def test_supports_component_true(self) -> None:
        """Test checking for supported component."""
        capability = IDECapability(
            tool_type=AIToolType.CURSOR,
            tool_name="Cursor",
            supported_components={ComponentType.INSTRUCTION, ComponentType.RESOURCE},
            instructions_directory=".cursor/rules/",
            instruction_file_extension=".mdc",
        )

        assert capability.supports_component(ComponentType.INSTRUCTION)
        assert capability.supports_component(ComponentType.RESOURCE)

    def test_supports_component_false(self) -> None:
        """Test checking for unsupported component."""
        capability = IDECapability(
            tool_type=AIToolType.CURSOR,
            tool_name="Cursor",
            supported_components={ComponentType.INSTRUCTION},
            instructions_directory=".cursor/rules/",
            instruction_file_extension=".mdc",
        )

        assert not capability.supports_component(ComponentType.MCP_SERVER)
        assert not capability.supports_component(ComponentType.HOOK)


class TestCapabilityRegistry:
    """Test CAPABILITY_REGISTRY and utility functions."""

    def test_registry_contains_all_tools(self) -> None:
        """Test that registry contains all AI tool types."""
        assert AIToolType.CURSOR in CAPABILITY_REGISTRY
        assert AIToolType.CLAUDE in CAPABILITY_REGISTRY
        assert AIToolType.WINSURF in CAPABILITY_REGISTRY
        assert AIToolType.COPILOT in CAPABILITY_REGISTRY
        assert AIToolType.KIRO in CAPABILITY_REGISTRY

    def test_cursor_capabilities(self) -> None:
        """Test Cursor IDE capabilities."""
        cursor = CAPABILITY_REGISTRY[AIToolType.CURSOR]

        assert cursor.tool_type == AIToolType.CURSOR
        assert cursor.tool_name == "Cursor"
        assert cursor.instructions_directory == ".cursor/rules/"
        assert cursor.instruction_file_extension == ".mdc"
        assert cursor.supports_project_scope
        assert cursor.supports_global_scope  # Cursor now supports global scope
        assert cursor.mcp_config_path == "~/.cursor/mcp.json"
        assert cursor.mcp_project_config_path == ".cursor/mcp.json"

        # Cursor supports instructions, MCP, and resources
        assert cursor.supports_component(ComponentType.INSTRUCTION)
        assert cursor.supports_component(ComponentType.MCP_SERVER)  # Now supported
        assert cursor.supports_component(ComponentType.RESOURCE)

        # Cursor does not support hooks or commands
        assert not cursor.supports_component(ComponentType.HOOK)
        assert not cursor.supports_component(ComponentType.COMMAND)

    def test_claude_code_capabilities(self) -> None:
        """Test Claude Code IDE capabilities."""
        claude = CAPABILITY_REGISTRY[AIToolType.CLAUDE]

        assert claude.tool_type == AIToolType.CLAUDE
        assert claude.tool_name == "Claude Code"
        assert claude.instructions_directory == ".claude/rules/"
        assert claude.instruction_file_extension == ".md"
        assert claude.supports_project_scope
        assert not claude.supports_global_scope
        assert claude.mcp_config_path == "~/.claude/settings.json"
        assert claude.mcp_project_config_path == ".claude/settings.local.json"
        assert claude.hooks_directory == ".claude/hooks/"
        assert claude.commands_directory == ".claude/commands/"
        assert claude.skills_directory == ".claude/skills/"
        assert claude.memory_file_name == "CLAUDE.md"

        # Claude Code supports all component types including skills and memory files
        assert claude.supports_component(ComponentType.INSTRUCTION)
        assert claude.supports_component(ComponentType.MCP_SERVER)
        assert claude.supports_component(ComponentType.HOOK)
        assert claude.supports_component(ComponentType.COMMAND)
        assert claude.supports_component(ComponentType.SKILL)
        assert claude.supports_component(ComponentType.MEMORY_FILE)
        assert claude.supports_component(ComponentType.RESOURCE)

    def test_windsurf_capabilities(self) -> None:
        """Test Windsurf IDE capabilities."""
        windsurf = CAPABILITY_REGISTRY[AIToolType.WINSURF]

        assert windsurf.tool_type == AIToolType.WINSURF
        assert windsurf.tool_name == "Windsurf"
        assert windsurf.instructions_directory == ".windsurf/rules/"
        assert windsurf.instruction_file_extension == ".md"
        assert windsurf.supports_project_scope
        assert windsurf.supports_global_scope  # Windsurf supports global scope
        assert windsurf.mcp_config_path == "~/.codeium/windsurf/mcp_config.json"
        assert windsurf.workflows_directory == ".windsurf/workflows/"

        # Windsurf supports instructions, MCP, workflows, and resources
        assert windsurf.supports_component(ComponentType.INSTRUCTION)
        assert windsurf.supports_component(ComponentType.MCP_SERVER)  # Now supported
        assert windsurf.supports_component(ComponentType.WORKFLOW)
        assert windsurf.supports_component(ComponentType.RESOURCE)

        # Windsurf does not support hooks, commands, or skills
        assert not windsurf.supports_component(ComponentType.HOOK)
        assert not windsurf.supports_component(ComponentType.COMMAND)
        assert not windsurf.supports_component(ComponentType.SKILL)

    def test_copilot_capabilities(self) -> None:
        """Test GitHub Copilot capabilities."""
        copilot = CAPABILITY_REGISTRY[AIToolType.COPILOT]

        assert copilot.tool_type == AIToolType.COPILOT
        assert copilot.tool_name == "GitHub Copilot"
        assert copilot.instructions_directory == ".github/instructions/"
        assert copilot.instruction_file_extension == ".instructions.md"
        assert copilot.supports_project_scope
        assert copilot.supports_global_scope  # Copilot supports global scope
        assert copilot.mcp_config_path == "~/.vscode/mcp.json"
        assert copilot.mcp_project_config_path == ".vscode/mcp.json"

        # Copilot supports instructions and MCP
        assert copilot.supports_component(ComponentType.INSTRUCTION)
        assert copilot.supports_component(ComponentType.MCP_SERVER)  # Now supported
        assert not copilot.supports_component(ComponentType.RESOURCE)  # Not supported

        # Copilot does not support hooks or commands
        assert not copilot.supports_component(ComponentType.HOOK)
        assert not copilot.supports_component(ComponentType.COMMAND)

    def test_get_capability_valid_tool(self) -> None:
        """Test getting capability for valid tool."""
        capability = get_capability(AIToolType.CURSOR)

        assert capability.tool_type == AIToolType.CURSOR
        assert capability.tool_name == "Cursor"

    def test_get_capability_invalid_tool_raises_error(self) -> None:
        """Test that getting capability for invalid tool raises KeyError."""
        with pytest.raises(KeyError):
            # Use a value that's not in the registry
            get_capability("INVALID_TOOL")  # type: ignore

    def test_kiro_capabilities(self) -> None:
        """Test Kiro IDE capabilities."""
        kiro = CAPABILITY_REGISTRY[AIToolType.KIRO]

        assert kiro.tool_type == AIToolType.KIRO
        assert kiro.tool_name == "Kiro"
        assert kiro.instructions_directory == ".kiro/steering/"
        assert kiro.instruction_file_extension == ".md"
        assert kiro.supports_project_scope
        assert not kiro.supports_global_scope

        # Kiro supports instructions and resources
        assert kiro.supports_component(ComponentType.INSTRUCTION)
        assert kiro.supports_component(ComponentType.RESOURCE)

        # Kiro does not support hooks, commands, MCP, or skills (yet)
        assert not kiro.supports_component(ComponentType.HOOK)
        assert not kiro.supports_component(ComponentType.COMMAND)
        assert not kiro.supports_component(ComponentType.MCP_SERVER)
        assert not kiro.supports_component(ComponentType.SKILL)

    def test_get_supported_tools_for_instruction(self) -> None:
        """Test getting tools that support instructions."""
        tools = get_supported_tools_for_component(ComponentType.INSTRUCTION)

        # All tools support instructions
        assert len(tools) == 5
        assert AIToolType.CURSOR in tools
        assert AIToolType.CLAUDE in tools
        assert AIToolType.WINSURF in tools
        assert AIToolType.COPILOT in tools
        assert AIToolType.KIRO in tools

    def test_get_supported_tools_for_mcp_server(self) -> None:
        """Test getting tools that support MCP servers."""
        tools = get_supported_tools_for_component(ComponentType.MCP_SERVER)

        # All IDEs now support MCP (Claude, Cursor, Windsurf, Copilot)
        assert len(tools) == 4
        assert AIToolType.CLAUDE in tools
        assert AIToolType.CURSOR in tools
        assert AIToolType.WINSURF in tools
        assert AIToolType.COPILOT in tools  # Now supported via VS Code

    def test_get_supported_tools_for_hook(self) -> None:
        """Test getting tools that support hooks."""
        tools = get_supported_tools_for_component(ComponentType.HOOK)

        # Only Claude Code supports hooks
        assert len(tools) == 1
        assert AIToolType.CLAUDE in tools

    def test_get_supported_tools_for_command(self) -> None:
        """Test getting tools that support commands."""
        tools = get_supported_tools_for_component(ComponentType.COMMAND)

        # Only Claude Code supports commands
        assert len(tools) == 1
        assert AIToolType.CLAUDE in tools

    def test_get_supported_tools_for_resource(self) -> None:
        """Test getting tools that support resources."""
        tools = get_supported_tools_for_component(ComponentType.RESOURCE)

        # Cursor, Claude, Windsurf, and Kiro support resources (not Copilot)
        assert len(tools) == 4
        assert AIToolType.CURSOR in tools
        assert AIToolType.CLAUDE in tools
        assert AIToolType.WINSURF in tools
        assert AIToolType.KIRO in tools
        assert AIToolType.COPILOT not in tools  # Instructions only

    def test_validate_component_support_true(self) -> None:
        """Test validating supported component."""
        assert validate_component_support(AIToolType.CLAUDE, ComponentType.MCP_SERVER)
        assert validate_component_support(AIToolType.CURSOR, ComponentType.INSTRUCTION)

    def test_validate_component_support_false(self) -> None:
        """Test validating unsupported component."""
        assert not validate_component_support(AIToolType.CURSOR, ComponentType.HOOK)  # Cursor doesn't support hooks
        assert not validate_component_support(AIToolType.COPILOT, ComponentType.HOOK)  # Copilot doesn't support hooks
        # Copilot doesn't support resources
        assert not validate_component_support(AIToolType.COPILOT, ComponentType.RESOURCE)

    def test_validate_component_support_invalid_tool(self) -> None:
        """Test validating component for invalid tool returns False."""
        assert not validate_component_support("INVALID_TOOL", ComponentType.INSTRUCTION)  # type: ignore
