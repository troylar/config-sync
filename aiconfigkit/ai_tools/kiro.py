"""Kiro AI tool integration."""

from pathlib import Path

from aiconfigkit.ai_tools.base import AITool
from aiconfigkit.core.models import AIToolType
from aiconfigkit.utils.paths import get_kiro_config_dir


class KiroTool(AITool):
    """Integration for Kiro AI coding tool."""

    @property
    def tool_type(self) -> AIToolType:
        """Return the AI tool type identifier."""
        return AIToolType.KIRO

    @property
    def tool_name(self) -> str:
        """Return human-readable tool name."""
        return "Kiro"

    def is_installed(self) -> bool:
        """
        Check if Kiro is installed on the system.

        Checks for existence of Kiro configuration directory.

        Returns:
            True if Kiro is detected
        """
        try:
            config_dir = get_kiro_config_dir()
            # Check if parent directory exists
            # Kiro config dir structure: .../Kiro/User/globalStorage
            kiro_base = config_dir.parent.parent
            return kiro_base.exists()
        except Exception:
            return False

    def get_instructions_directory(self) -> Path:
        """
        Get the directory where Kiro instructions should be installed.

        Note: Kiro uses ~/.kiro/steering/ for global steering files.
        This tool currently only supports project-level installations.

        Returns:
            Path to Kiro instructions directory

        Raises:
            NotImplementedError: Global installation not supported for Kiro
        """
        raise NotImplementedError(
            f"{self.tool_name} global installation is not supported. "
            "Please use project-level installation instead (--scope project)."
        )

    def get_instruction_file_extension(self) -> str:
        """
        Get the file extension for Kiro instructions.

        Kiro uses markdown (.md) files for steering.

        Returns:
            File extension including the dot
        """
        return ".md"

    def get_project_instructions_directory(self, project_root: Path) -> Path:
        """
        Get the directory for project-specific Kiro instructions.

        Kiro stores project-specific steering files in .kiro/steering/ directory
        in the project root. It supports multiple .md files in this directory.

        Args:
            project_root: Path to the project root directory

        Returns:
            Path to project instructions directory (.kiro/steering/)
        """
        instructions_dir = project_root / ".kiro" / "steering"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        return instructions_dir
