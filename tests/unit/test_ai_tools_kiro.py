"""Tests for Kiro AI tool integration."""

import pytest

from aiconfigkit.ai_tools.kiro import KiroTool
from aiconfigkit.core.models import AIToolType, InstallationScope, Instruction


@pytest.fixture
def kiro_tool():
    """Create a Kiro tool instance."""
    return KiroTool()


@pytest.fixture
def mock_kiro_installed(monkeypatch, temp_dir):
    """Mock Kiro as installed."""
    import os

    home_dir = temp_dir / "home"
    home_dir.mkdir(parents=True)

    # Create platform-specific directory structure
    if os.name == "nt":  # Windows
        kiro_dir = home_dir / "AppData" / "Roaming" / "Kiro" / "User" / "globalStorage"
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():  # macOS
            kiro_dir = home_dir / "Library" / "Application Support" / "Kiro" / "User" / "globalStorage"
        else:  # Linux
            kiro_dir = home_dir / ".config" / "Kiro" / "User" / "globalStorage"
    else:
        raise OSError(f"Unsupported operating system: {os.name}")

    kiro_dir.mkdir(parents=True)

    monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
    return kiro_dir


class TestKiroTool:
    """Test suite for KiroTool."""

    def test_tool_type(self, kiro_tool):
        """Test tool type property."""
        assert kiro_tool.tool_type == AIToolType.KIRO

    def test_tool_name(self, kiro_tool):
        """Test tool name property."""
        assert kiro_tool.tool_name == "Kiro"

    def test_is_installed_when_present(self, kiro_tool, mock_kiro_installed):
        """Test is_installed returns True when Kiro is present."""
        assert kiro_tool.is_installed() is True

    def test_is_installed_when_absent(self, temp_dir, monkeypatch):
        """Test is_installed returns False when Kiro is not present."""
        home_dir = temp_dir / "empty_home"
        home_dir.mkdir()
        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", lambda: home_dir)
        kiro_tool = KiroTool()
        assert kiro_tool.is_installed() is False

    def test_is_installed_handles_exception(self, monkeypatch):
        """Test is_installed handles exceptions gracefully."""

        def raise_error():
            raise RuntimeError("Test error")

        monkeypatch.setattr("aiconfigkit.utils.paths.get_home_directory", raise_error)
        kiro_tool = KiroTool()
        assert kiro_tool.is_installed() is False

    def test_get_instructions_directory_raises_not_implemented(self, kiro_tool):
        """Test get_instructions_directory raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            kiro_tool.get_instructions_directory()

        assert "global installation is not supported" in str(exc_info.value).lower()

    def test_get_instruction_file_extension(self, kiro_tool):
        """Test instruction file extension."""
        assert kiro_tool.get_instruction_file_extension() == ".md"

    def test_get_project_instructions_directory(self, kiro_tool, temp_dir):
        """Test project instructions directory."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        instructions_dir = kiro_tool.get_project_instructions_directory(project_root)

        assert instructions_dir == project_root / ".kiro" / "steering"
        assert instructions_dir.exists()

    def test_install_instruction(self, kiro_tool, temp_dir):
        """Test install_instruction."""
        project_root = temp_dir / "project"
        project_root.mkdir()

        instruction = Instruction(
            name="test-instruction",
            description="Test",
            content="Test content",
            file_path="test.md",
            tags=[],
        )

        path = kiro_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        assert path.exists()
        assert path.read_text() == "Test content"
        assert path.suffix == ".md"

    def test_repr(self, kiro_tool):
        """Test string representation."""
        repr_str = repr(kiro_tool)
        assert "KiroTool" in repr_str
        assert AIToolType.KIRO.value in repr_str
