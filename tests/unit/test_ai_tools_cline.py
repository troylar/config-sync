"""Tests for Cline AI tool integration."""

import pytest

from aiconfigkit.ai_tools.cline import ClineTool
from aiconfigkit.core.models import AIToolType, InstallationScope, Instruction


@pytest.fixture
def cline_tool():
    """Create a Cline tool instance."""
    return ClineTool()


@pytest.fixture
def mock_cline_installed(monkeypatch, temp_dir):
    """Mock Cline as installed."""
    import os

    home_dir = temp_dir / "home"
    home_dir.mkdir(parents=True)

    # Cline is a VS Code extension — detection uses globalStorage path
    if os.name == "nt":  # Windows
        cline_dir = home_dir / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev"
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():  # macOS
            cline_dir = (
                home_dir
                / "Library"
                / "Application Support"
                / "Code"
                / "User"
                / "globalStorage"
                / "saoudrizwan.claude-dev"
            )
        else:  # Linux
            cline_dir = home_dir / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev"
    else:
        raise OSError(f"Unsupported operating system: {os.name}")

    cline_dir.mkdir(parents=True)

    monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
    return cline_dir


class TestClineTool:
    """Test suite for ClineTool."""

    def test_tool_type(self, cline_tool):
        """Test tool type property."""
        assert cline_tool.tool_type == AIToolType.CLINE

    def test_tool_name(self, cline_tool):
        """Test tool name property."""
        assert cline_tool.tool_name == "Cline"

    def test_is_installed_when_present(self, cline_tool, mock_cline_installed):
        """Test is_installed returns True when Cline is present."""
        assert cline_tool.is_installed() is True

    def test_is_installed_when_absent(self, temp_dir, monkeypatch):
        """Test is_installed returns False when Cline is not present."""
        home_dir = temp_dir / "empty_home"
        home_dir.mkdir()
        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
        cline_tool = ClineTool()
        assert cline_tool.is_installed() is False

    def test_is_installed_handles_exception(self, monkeypatch):
        """Test is_installed handles exceptions gracefully."""

        def raise_error():
            raise RuntimeError("Test error")

        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", raise_error)
        cline_tool = ClineTool()
        assert cline_tool.is_installed() is False

    def test_get_instructions_directory_raises_not_implemented(self, cline_tool):
        """Test get_instructions_directory raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            cline_tool.get_instructions_directory()

        assert "global installation is not supported" in str(exc_info.value).lower()

    def test_get_instruction_file_extension(self, cline_tool):
        """Test instruction file extension."""
        assert cline_tool.get_instruction_file_extension() == ".md"

    def test_get_project_instructions_directory(self, cline_tool, temp_dir):
        """Test project instructions directory uses .clinerules/."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        instructions_dir = cline_tool.get_project_instructions_directory(project_root)

        assert instructions_dir == project_root / ".clinerules"
        assert instructions_dir.exists()

    def test_install_instruction(self, cline_tool, temp_dir):
        """Test install_instruction creates .md file in .clinerules/."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        instruction = Instruction(
            name="test-instruction",
            description="Test",
            content="Test content",
            file_path="test.md",
            tags=[],
        )

        path = cline_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        assert path.exists()
        assert path.read_text() == "Test content"
        assert path.suffix == ".md"
        assert ".clinerules" in str(path)

    def test_repr(self, cline_tool):
        """Test string representation."""
        repr_str = repr(cline_tool)
        assert "ClineTool" in repr_str
        assert AIToolType.CLINE.value in repr_str
