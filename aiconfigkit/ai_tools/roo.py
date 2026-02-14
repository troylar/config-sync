"""Roo Code AI tool integration."""

from pathlib import Path

from aiconfigkit.ai_tools.base import AITool
from aiconfigkit.core.models import AIToolType
from aiconfigkit.utils.paths import get_roo_config_dir


class RooTool(AITool):
    """Integration for Roo Code AI coding tool (VS Code extension).

    Roo Code (formerly Roo Cline) uses .roo/rules/ directory at the project root
    for AI instructions. Files are .md (Markdown) and are read recursively in
    alphabetical order by filename. Numeric prefixes control load order.

    Mode-specific rules can be placed in .roo/rules-{mode-slug}/ directories.
    Project-level MCP config is at .roo/mcp.json.

    Detection is based on the VS Code extension rooveterinaryinc.roo-cline
    globalStorage directory.
    """

    @property
    def tool_type(self) -> AIToolType:
        """Return the AI tool type identifier."""
        return AIToolType.ROO

    @property
    def tool_name(self) -> str:
        """Return human-readable tool name."""
        return "Roo Code"

    def is_installed(self) -> bool:
        """
        Check if Roo Code is installed on the system.

        Checks for existence of the Roo Code VS Code extension globalStorage directory
        (rooveterinaryinc.roo-cline).

        Returns:
            True if Roo Code is detected
        """
        try:
            config_dir = get_roo_config_dir()
            return config_dir.exists()
        except Exception:
            return False

    def get_instructions_directory(self) -> Path:
        """
        Get the directory where Roo Code global instructions should be installed.

        Roo Code supports global rules at ~/.roo/rules/.

        Returns:
            Path to Roo Code global instructions directory

        Raises:
            FileNotFoundError: If Roo Code is not installed
        """
        if not self.is_installed():
            raise FileNotFoundError(f"{self.tool_name} is not installed")
        from aiconfigkit.utils.paths import get_home_directory

        global_dir = get_home_directory() / ".roo" / "rules"
        global_dir.mkdir(parents=True, exist_ok=True)
        return global_dir

    def get_instruction_file_extension(self) -> str:
        """
        Get the file extension for Roo Code instructions.

        Roo Code uses markdown (.md) files in the .roo/rules/ directory.

        Returns:
            File extension including the dot
        """
        return ".md"

    def get_project_instructions_directory(self, project_root: Path) -> Path:
        """
        Get the directory for project-specific Roo Code instructions.

        Roo Code stores project-specific rules in .roo/rules/ directory at the
        project root. It reads .md files recursively from this directory.
        Numeric prefixes (e.g., 01-coding-standards.md) control load order.

        Args:
            project_root: Path to the project root directory

        Returns:
            Path to project instructions directory (.roo/rules/)
        """
        instructions_dir = project_root / ".roo" / "rules"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        return instructions_dir

    def get_mcp_config_path(self) -> Path:
        """
        Get the path to the MCP configuration file for Roo Code.

        Roo Code stores project-level MCP config at .roo/mcp.json.
        Global MCP config is at the globalStorage settings directory.

        Returns:
            Path to global MCP configuration file
        """
        config_dir = get_roo_config_dir()
        return config_dir / "settings" / "cline_mcp_settings.json"
