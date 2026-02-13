"""Base interface for AI coding tool integrations."""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from aiconfigkit.core.models import AIToolType, InstallationScope, Instruction


class AITool(ABC):
    """
    Abstract base class for AI coding tool integrations.

    Each AI tool (Cursor, Copilot, Kiro, Winsurf, Claude) implements this interface
    to provide tool-specific installation logic.
    """

    @property
    @abstractmethod
    def tool_type(self) -> AIToolType:
        """Return the AI tool type identifier."""
        pass

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Return human-readable tool name."""
        pass

    @abstractmethod
    def is_installed(self) -> bool:
        """
        Check if this AI tool is installed on the system.

        Returns:
            True if tool is detected, False otherwise
        """
        pass

    @abstractmethod
    def get_instructions_directory(self) -> Path:
        """
        Get the directory where instructions should be installed.

        Returns:
            Path to instructions directory

        Raises:
            FileNotFoundError: If tool is not installed
        """
        pass

    @abstractmethod
    def get_instruction_file_extension(self) -> str:
        """
        Get the file extension for instructions (e.g., '.md', '.txt').

        Returns:
            File extension including the dot
        """
        pass

    @abstractmethod
    def get_project_instructions_directory(self, project_root: Path) -> Path:
        """
        Get the directory where project-specific instructions should be installed.

        Args:
            project_root: Path to the project root directory

        Returns:
            Path to project instructions directory
        """
        pass

    def get_mcp_config_path(self) -> Path:
        """
        Get the path to the MCP configuration file for this AI tool.

        This is an optional method - tools that support MCP server configuration
        should override this method.

        Returns:
            Path to MCP configuration file

        Raises:
            NotImplementedError: If tool doesn't support MCP configuration
        """
        raise NotImplementedError(f"{self.tool_name} does not support MCP server configuration")

    def get_instruction_path(
        self,
        instruction_name: str,
        scope: InstallationScope = InstallationScope.GLOBAL,
        project_root: Optional[Path] = None,
    ) -> Path:
        """
        Get the full path where an instruction file should be installed.

        Args:
            instruction_name: Name of the instruction
            scope: Installation scope (global or project)
            project_root: Project root path (required if scope is PROJECT)

        Returns:
            Full path to instruction file

        Raises:
            ValueError: If scope is PROJECT but project_root is None
        """
        if scope == InstallationScope.PROJECT:
            if project_root is None:
                raise ValueError("project_root is required for PROJECT scope")
            directory = self.get_project_instructions_directory(project_root)
        else:
            directory = self.get_instructions_directory()

        extension = self.get_instruction_file_extension()
        filename = f"{instruction_name}{extension}"
        return directory / filename

    def instruction_exists(
        self,
        instruction_name: str,
        scope: InstallationScope = InstallationScope.GLOBAL,
        project_root: Optional[Path] = None,
    ) -> bool:
        """
        Check if an instruction is already installed.

        Args:
            instruction_name: Name of the instruction
            scope: Installation scope (global or project)
            project_root: Project root path (required if scope is PROJECT)

        Returns:
            True if instruction file exists
        """
        try:
            path = self.get_instruction_path(instruction_name, scope, project_root)
            return path.exists()
        except (FileNotFoundError, ValueError):
            return False

    def install_instruction(
        self,
        instruction: Instruction,
        overwrite: bool = False,
        scope: InstallationScope = InstallationScope.GLOBAL,
        project_root: Optional[Path] = None,
    ) -> Path:
        """
        Install an instruction to this AI tool.

        Args:
            instruction: Instruction to install
            overwrite: Whether to overwrite existing file
            scope: Installation scope (global or project)
            project_root: Project root path (required if scope is PROJECT)

        Returns:
            Path where instruction was installed

        Raises:
            FileExistsError: If instruction exists and overwrite=False
            FileNotFoundError: If tool is not installed
            ValueError: If scope is PROJECT but project_root is None
        """
        path = self.get_instruction_path(instruction.name, scope, project_root)

        if path.exists() and not overwrite:
            raise FileExistsError(f"Instruction already exists: {path}")

        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write instruction content
        path.write_text(instruction.content, encoding="utf-8")

        return path

    def uninstall_instruction(
        self,
        instruction_name: str,
        scope: InstallationScope = InstallationScope.GLOBAL,
        project_root: Optional[Path] = None,
    ) -> bool:
        """
        Uninstall an instruction from this AI tool.

        Args:
            instruction_name: Name of instruction to remove
            scope: Installation scope (global or project)
            project_root: Project root path (required if scope is PROJECT)

        Returns:
            True if file was removed, False if it didn't exist
        """
        try:
            path = self.get_instruction_path(instruction_name, scope, project_root)
            if path.exists():
                path.unlink()
                return True
            return False
        except (FileNotFoundError, ValueError):
            return False

    def validate_installation(self) -> Optional[str]:
        """
        Validate that tool installation is correct and accessible.

        Returns:
            None if valid, error message if invalid
        """
        if not self.is_installed():
            return f"{self.tool_name} is not installed or not found"

        try:
            directory = self.get_instructions_directory()
            if not directory.exists():
                # Try to create it
                directory.mkdir(parents=True, exist_ok=True)

            # Check write permissions
            if not os.access(directory, os.W_OK):
                return f"No write permission for {directory}"

        except Exception as e:
            return f"Error accessing {self.tool_name} directory: {str(e)}"

        return None

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__} tool_type={self.tool_type.value}>"
