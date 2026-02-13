"""Cline AI tool integration."""

from pathlib import Path

from aiconfigkit.ai_tools.base import AITool
from aiconfigkit.core.models import AIToolType
from aiconfigkit.utils.paths import get_cline_config_dir


class ClineTool(AITool):
    """Integration for Cline AI coding tool (VS Code extension).

    Cline uses .clinerules/ directory at the project root for AI instructions.
    Files are .md (Markdown) and are read recursively. Optional YAML frontmatter
    with `paths:` field enables conditional rule activation based on file globs.

    Detection is based on the VS Code extension saoudrizwan.claude-dev
    globalStorage directory.
    """

    @property
    def tool_type(self) -> AIToolType:
        """Return the AI tool type identifier."""
        return AIToolType.CLINE

    @property
    def tool_name(self) -> str:
        """Return human-readable tool name."""
        return "Cline"

    def is_installed(self) -> bool:
        """
        Check if Cline is installed on the system.

        Checks for existence of the Cline VS Code extension globalStorage directory
        (saoudrizwan.claude-dev).

        Returns:
            True if Cline is detected
        """
        try:
            config_dir = get_cline_config_dir()
            return config_dir.exists()
        except Exception:
            return False

    def get_instructions_directory(self) -> Path:
        """
        Get the directory where Cline instructions should be installed.

        Note: Cline global rules live in ~/Documents/Cline/Rules/ but this
        is non-standard. This tool only supports project-level installations.

        Returns:
            Path to Cline instructions directory

        Raises:
            NotImplementedError: Global installation not supported for Cline
        """
        raise NotImplementedError(
            f"{self.tool_name} global installation is not supported. "
            "Please use project-level installation instead (--scope project)."
        )

    def get_instruction_file_extension(self) -> str:
        """
        Get the file extension for Cline instructions.

        Cline uses markdown (.md) files in the .clinerules/ directory.

        Returns:
            File extension including the dot
        """
        return ".md"

    def get_project_instructions_directory(self, project_root: Path) -> Path:
        """
        Get the directory for project-specific Cline instructions.

        Cline stores project-specific rules in .clinerules/ directory at the
        project root. It reads .md files recursively from this directory.
        Numeric prefixes (e.g., 01-coding-standards.md) control load order.

        Args:
            project_root: Path to the project root directory

        Returns:
            Path to project instructions directory (.clinerules/)
        """
        instructions_dir = project_root / ".clinerules"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        return instructions_dir
