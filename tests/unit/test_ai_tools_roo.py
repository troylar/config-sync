"""Tests for Roo Code AI tool integration."""

import pytest

from aiconfigkit.ai_tools.roo import RooTool
from aiconfigkit.core.models import AIToolType, InstallationScope, Instruction


@pytest.fixture
def roo_tool():
    """Create a Roo Code tool instance."""
    return RooTool()


@pytest.fixture
def mock_roo_installed(monkeypatch, temp_dir):
    """Mock Roo Code as installed."""
    import os

    home_dir = temp_dir / "home"
    home_dir.mkdir(parents=True)

    # Roo Code is a VS Code extension — detection uses globalStorage path
    if os.name == "nt":  # Windows
        roo_dir = home_dir / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline"
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():  # macOS
            roo_dir = (
                home_dir
                / "Library"
                / "Application Support"
                / "Code"
                / "User"
                / "globalStorage"
                / "rooveterinaryinc.roo-cline"
            )
        else:  # Linux
            roo_dir = home_dir / ".config" / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline"
    else:
        raise OSError(f"Unsupported operating system: {os.name}")

    roo_dir.mkdir(parents=True)

    monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
    return roo_dir


class TestRooTool:
    """Test suite for RooTool."""

    def test_tool_type(self, roo_tool):
        """Test tool type property."""
        assert roo_tool.tool_type == AIToolType.ROO

    def test_tool_name(self, roo_tool):
        """Test tool name property."""
        assert roo_tool.tool_name == "Roo Code"

    def test_is_installed_when_present(self, roo_tool, mock_roo_installed):
        """Test is_installed returns True when Roo Code is present."""
        assert roo_tool.is_installed() is True

    def test_is_installed_when_absent(self, temp_dir, monkeypatch):
        """Test is_installed returns False when Roo Code is not present."""
        home_dir = temp_dir / "empty_home"
        home_dir.mkdir()
        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
        roo_tool = RooTool()
        assert roo_tool.is_installed() is False

    def test_is_installed_handles_exception(self, monkeypatch):
        """Test is_installed handles exceptions gracefully."""

        def raise_error():
            raise RuntimeError("Test error")

        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", raise_error)
        roo_tool = RooTool()
        assert roo_tool.is_installed() is False

    def test_get_instructions_directory(self, roo_tool, mock_roo_installed):
        """Test get_instructions_directory returns global rules directory."""
        instructions_dir = roo_tool.get_instructions_directory()
        assert instructions_dir.name == "rules"
        assert ".roo" in str(instructions_dir)

    def test_get_instructions_directory_not_installed(self, temp_dir, monkeypatch):
        """Test get_instructions_directory raises when not installed."""
        home_dir = temp_dir / "empty_home"
        home_dir.mkdir()
        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
        roo_tool = RooTool()
        with pytest.raises(FileNotFoundError):
            roo_tool.get_instructions_directory()

    def test_get_instruction_file_extension(self, roo_tool):
        """Test instruction file extension."""
        assert roo_tool.get_instruction_file_extension() == ".md"

    def test_get_project_instructions_directory(self, roo_tool, temp_dir):
        """Test project instructions directory uses .roo/rules/."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        instructions_dir = roo_tool.get_project_instructions_directory(project_root)

        assert instructions_dir == project_root / ".roo" / "rules"
        assert instructions_dir.exists()

    def test_install_instruction(self, roo_tool, temp_dir):
        """Test install_instruction creates .md file in .roo/rules/."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        instruction = Instruction(
            name="test-instruction",
            description="Test",
            content="Test content",
            file_path="test.md",
            tags=[],
        )

        path = roo_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        assert path.exists()
        assert path.read_text() == "Test content"
        assert path.suffix == ".md"
        assert ".roo" in str(path)
        assert "rules" in str(path)

    def test_get_mcp_config_path(self, roo_tool, mock_roo_installed):
        """Test MCP config path returns globalStorage settings path."""
        mcp_path = roo_tool.get_mcp_config_path()
        assert "cline_mcp_settings.json" in str(mcp_path)
        assert "settings" in str(mcp_path)

    def test_repr(self, roo_tool):
        """Test string representation."""
        repr_str = repr(roo_tool)
        assert "RooTool" in repr_str
        assert AIToolType.ROO.value in repr_str
