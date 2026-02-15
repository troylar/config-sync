"""Tests for Antigravity IDE AI tool integration."""

import pytest

from devsync.ai_tools.antigravity import AntigravityTool
from devsync.core.models import AIToolType, InstallationScope, Instruction


@pytest.fixture
def antigravity_tool():
    """Create an Antigravity tool instance."""
    return AntigravityTool()


class TestAntigravityTool:
    """Test suite for AntigravityTool."""

    def test_tool_type(self, antigravity_tool: AntigravityTool) -> None:
        assert antigravity_tool.tool_type == AIToolType.ANTIGRAVITY

    def test_tool_name(self, antigravity_tool: AntigravityTool) -> None:
        assert antigravity_tool.tool_name == "Antigravity IDE"

    def test_is_installed_when_binary_present(
        self, antigravity_tool: AntigravityTool, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("devsync.ai_tools.antigravity.shutil.which", lambda cmd: "/usr/local/bin/antigravity")
        assert antigravity_tool.is_installed() is True

    def test_is_installed_when_config_dir_exists(
        self, antigravity_tool: AntigravityTool, monkeypatch: pytest.MonkeyPatch, temp_dir
    ) -> None:  # type: ignore[no-untyped-def]
        monkeypatch.setattr("devsync.ai_tools.antigravity.shutil.which", lambda cmd: None)
        antigravity_dir = temp_dir / ".gemini" / "antigravity"
        antigravity_dir.mkdir(parents=True)
        monkeypatch.setattr("devsync.ai_tools.antigravity.Path.home", lambda: temp_dir)
        assert antigravity_tool.is_installed() is True

    def test_is_installed_when_absent(
        self, antigravity_tool: AntigravityTool, monkeypatch: pytest.MonkeyPatch, temp_dir
    ) -> None:  # type: ignore[no-untyped-def]
        monkeypatch.setattr("devsync.ai_tools.antigravity.shutil.which", lambda cmd: None)
        monkeypatch.setattr("devsync.ai_tools.antigravity.Path.home", lambda: temp_dir)
        assert antigravity_tool.is_installed() is False

    def test_get_instructions_directory_raises_not_implemented(self, antigravity_tool: AntigravityTool) -> None:
        with pytest.raises(NotImplementedError) as exc_info:
            antigravity_tool.get_instructions_directory()
        assert "global installation is not supported" in str(exc_info.value).lower()

    def test_get_instruction_file_extension(self, antigravity_tool: AntigravityTool) -> None:
        assert antigravity_tool.get_instruction_file_extension() == ".md"

    def test_get_project_instructions_directory(self, antigravity_tool: AntigravityTool, temp_dir) -> None:  # type: ignore[no-untyped-def]
        project_root = temp_dir / "project"
        project_root.mkdir()

        instructions_dir = antigravity_tool.get_project_instructions_directory(project_root)

        assert instructions_dir == project_root / ".agent" / "rules"
        assert instructions_dir.exists()

    def test_install_instruction(self, antigravity_tool: AntigravityTool, temp_dir) -> None:  # type: ignore[no-untyped-def]
        project_root = temp_dir / "project"
        project_root.mkdir()

        instruction = Instruction(
            name="test-instruction",
            description="Test",
            content="Test content",
            file_path="test.md",
            tags=[],
        )

        path = antigravity_tool.install_instruction(
            instruction, scope=InstallationScope.PROJECT, project_root=project_root
        )

        assert path.exists()
        assert path.read_text() == "Test content"
        assert path.suffix == ".md"
        assert path.parent == project_root / ".agent" / "rules"

    def test_install_instruction_overwrite(self, antigravity_tool: AntigravityTool, temp_dir) -> None:  # type: ignore[no-untyped-def]
        project_root = temp_dir / "project"
        project_root.mkdir()

        instruction = Instruction(
            name="test-instruction",
            description="Test",
            content="Original content",
            file_path="test.md",
        )
        antigravity_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        updated = Instruction(
            name="test-instruction",
            description="Test",
            content="Updated content",
            file_path="test.md",
        )
        path = antigravity_tool.install_instruction(
            updated, overwrite=True, scope=InstallationScope.PROJECT, project_root=project_root
        )

        assert path.read_text() == "Updated content"

    def test_install_existing_raises_without_overwrite(self, antigravity_tool: AntigravityTool, temp_dir) -> None:  # type: ignore[no-untyped-def]
        project_root = temp_dir / "project"
        project_root.mkdir()

        instruction = Instruction(
            name="test-instruction",
            description="Test",
            content="Test content",
            file_path="test.md",
        )
        antigravity_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        with pytest.raises(FileExistsError):
            antigravity_tool.install_instruction(
                instruction, scope=InstallationScope.PROJECT, project_root=project_root
            )

    def test_uninstall_instruction(self, antigravity_tool: AntigravityTool, temp_dir) -> None:  # type: ignore[no-untyped-def]
        project_root = temp_dir / "project"
        project_root.mkdir()

        instruction = Instruction(
            name="test-instruction",
            description="Test",
            content="Test content",
            file_path="test.md",
        )
        antigravity_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        result = antigravity_tool.uninstall_instruction(
            "test-instruction", scope=InstallationScope.PROJECT, project_root=project_root
        )

        assert result is True
        path = antigravity_tool.get_instruction_path(
            "test-instruction", scope=InstallationScope.PROJECT, project_root=project_root
        )
        assert not path.exists()

    def test_uninstall_nonexistent_returns_false(self, antigravity_tool: AntigravityTool, temp_dir) -> None:  # type: ignore[no-untyped-def]
        project_root = temp_dir / "project"
        project_root.mkdir()

        result = antigravity_tool.uninstall_instruction(
            "nonexistent", scope=InstallationScope.PROJECT, project_root=project_root
        )
        assert result is False

    def test_instruction_exists(self, antigravity_tool: AntigravityTool, temp_dir) -> None:  # type: ignore[no-untyped-def]
        project_root = temp_dir / "project"
        project_root.mkdir()

        assert (
            antigravity_tool.instruction_exists(
                "test-instruction", scope=InstallationScope.PROJECT, project_root=project_root
            )
            is False
        )

        instruction = Instruction(
            name="test-instruction",
            description="Test",
            content="Test content",
            file_path="test.md",
        )
        antigravity_tool.install_instruction(instruction, scope=InstallationScope.PROJECT, project_root=project_root)

        assert (
            antigravity_tool.instruction_exists(
                "test-instruction", scope=InstallationScope.PROJECT, project_root=project_root
            )
            is True
        )

    def test_repr(self, antigravity_tool: AntigravityTool) -> None:
        repr_str = repr(antigravity_tool)
        assert "AntigravityTool" in repr_str
        assert AIToolType.ANTIGRAVITY.value in repr_str
