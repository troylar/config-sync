"""AI tool detection and auto-discovery."""

from typing import Optional

from aiconfigkit.ai_tools.base import AITool
from aiconfigkit.ai_tools.claude import ClaudeTool
from aiconfigkit.ai_tools.cline import ClineTool
from aiconfigkit.ai_tools.copilot import CopilotTool
from aiconfigkit.ai_tools.cursor import CursorTool
from aiconfigkit.ai_tools.kiro import KiroTool
from aiconfigkit.ai_tools.roo import RooTool
from aiconfigkit.ai_tools.winsurf import WinsurfTool
from aiconfigkit.core.models import AIToolType


class AIToolDetector:
    """Detect and manage AI coding tools."""

    def __init__(self) -> None:
        """Initialize detector with all supported tools."""
        self.tools: dict[AIToolType, AITool] = {
            AIToolType.CURSOR: CursorTool(),
            AIToolType.COPILOT: CopilotTool(),
            AIToolType.WINSURF: WinsurfTool(),
            AIToolType.CLAUDE: ClaudeTool(),
            AIToolType.KIRO: KiroTool(),
            AIToolType.CLINE: ClineTool(),
            AIToolType.ROO: RooTool(),
        }

    def detect_installed_tools(self) -> list[AITool]:
        """
        Detect all installed AI coding tools.

        Returns:
            List of installed AITool instances
        """
        installed = []
        for tool in self.tools.values():
            if tool.is_installed():
                installed.append(tool)
        return installed

    def get_tool_by_name(self, name: str) -> Optional[AITool]:
        """
        Get AI tool instance by name.

        Args:
            name: Tool name (cursor, copilot, winsurf, claude)

        Returns:
            AITool instance or None if not found
        """
        try:
            tool_type = AIToolType(name.lower())
            return self.tools.get(tool_type)
        except ValueError:
            return None

    def get_tool_by_type(self, tool_type: AIToolType) -> Optional[AITool]:
        """
        Get AI tool instance by type.

        Args:
            tool_type: AIToolType enum value

        Returns:
            AITool instance
        """
        return self.tools.get(tool_type)

    def get_primary_tool(self) -> Optional[AITool]:
        """
        Get the primary (first detected) AI tool.

        Priority order: Cursor, Copilot, Winsurf, Claude Code

        Returns:
            First installed AITool or None if none installed
        """
        # Check in priority order
        priority = [
            AIToolType.CURSOR,
            AIToolType.COPILOT,
            AIToolType.WINSURF,
            AIToolType.CLAUDE,
            AIToolType.KIRO,
            AIToolType.CLINE,
            AIToolType.ROO,
        ]

        for tool_type in priority:
            tool = self.tools[tool_type]
            if tool.is_installed():
                return tool

        return None

    def is_any_tool_installed(self) -> bool:
        """
        Check if any AI coding tool is installed.

        Returns:
            True if at least one tool is detected
        """
        return len(self.detect_installed_tools()) > 0

    def get_tool_names(self) -> list[str]:
        """
        Get list of all supported tool names.

        Returns:
            List of tool name strings
        """
        return [tool_type.value for tool_type in self.tools.keys()]

    def validate_tool_name(self, name: str) -> bool:
        """
        Validate if tool name is supported.

        Args:
            name: Tool name to validate

        Returns:
            True if tool is supported
        """
        return name.lower() in self.get_tool_names()

    def get_detection_summary(self) -> dict[str, bool]:
        """
        Get detection summary for all tools.

        Returns:
            Dictionary mapping tool names to installation status
        """
        return {tool_type.value: tool.is_installed() for tool_type, tool in self.tools.items()}

    def format_detection_summary(self) -> str:
        """
        Format detection summary as human-readable string.

        Returns:
            Formatted summary string
        """
        summary = self.get_detection_summary()
        lines = ["AI Coding Tools Detection:"]

        for tool_name, is_installed in summary.items():
            status = "✓ Installed" if is_installed else "✗ Not found"
            lines.append(f"  {tool_name.capitalize()}: {status}")

        return "\n".join(lines)


# Singleton instance for convenience
_detector_instance: Optional[AIToolDetector] = None


def get_detector() -> AIToolDetector:
    """
    Get singleton AIToolDetector instance.

    Returns:
        AIToolDetector instance
    """
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = AIToolDetector()
    return _detector_instance
