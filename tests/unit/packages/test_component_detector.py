"""Unit tests for component detection."""

import json
from pathlib import Path

import pytest

from devsync.core.component_detector import (
    ComponentDetector,
    DetectedHook,
    DetectedInstruction,
    DetectionResult,
)


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    return tmp_path


class TestComponentDetector:
    """Test ComponentDetector class."""

    def test_init(self, temp_project: Path) -> None:
        """Test detector initialization."""
        detector = ComponentDetector(temp_project)
        assert detector.project_root == temp_project.resolve()

    def test_detect_no_components(self, temp_project: Path) -> None:
        """Test detection in empty project."""
        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert result.total_count == 0
        assert len(result.instructions) == 0
        assert len(result.mcp_servers) == 0
        assert len(result.hooks) == 0
        assert len(result.commands) == 0
        assert len(result.resources) == 0


class TestInstructionDetection:
    """Test instruction file detection."""

    def test_detect_claude_instructions(self, temp_project: Path) -> None:
        """Test detection of Claude Code instructions."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "coding-style.md").write_text("# Coding Style\nBest practices...")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.instructions) == 1
        inst = result.instructions[0]
        assert inst.name == "coding-style"
        assert inst.source_ide == "claude"
        assert inst.relative_path == str(Path(".claude") / "rules" / "coding-style.md")

    def test_detect_cursor_instructions(self, temp_project: Path) -> None:
        """Test detection of Cursor instructions."""
        rules_dir = temp_project / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "project-rules.mdc").write_text("# Project Rules")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.instructions) == 1
        assert result.instructions[0].source_ide == "cursor"

    def test_detect_windsurf_instructions(self, temp_project: Path) -> None:
        """Test detection of Windsurf instructions."""
        rules_dir = temp_project / ".windsurf" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "guidelines.md").write_text("# Guidelines")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.instructions) == 1
        assert result.instructions[0].source_ide == "windsurf"

    def test_detect_copilot_instructions(self, temp_project: Path) -> None:
        """Test detection of GitHub Copilot instructions."""
        rules_dir = temp_project / ".github" / "instructions"
        rules_dir.mkdir(parents=True)
        (rules_dir / "copilot.md").write_text("# Copilot Instructions")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.instructions) == 1
        assert result.instructions[0].source_ide == "copilot"

    def test_detect_multiple_instructions(self, temp_project: Path) -> None:
        """Test detection of multiple instruction files."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "style.md").write_text("# Style")
        (rules_dir / "testing.md").write_text("# Testing")
        (rules_dir / "security.md").write_text("# Security")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.instructions) == 3
        names = {i.name for i in result.instructions}
        assert names == {"style", "testing", "security"}

    def test_ignore_non_instruction_files(self, temp_project: Path) -> None:
        """Test that non-md/mdc files are ignored."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "valid.md").write_text("# Valid")
        (rules_dir / "ignored.txt").write_text("Ignored")
        (rules_dir / "ignored.json").write_text("{}")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.instructions) == 1
        assert result.instructions[0].name == "valid"


class TestMCPServerDetection:
    """Test MCP server configuration detection."""

    def test_detect_mcp_from_settings(self, temp_project: Path) -> None:
        """Test detection of MCP servers from settings.local.json."""
        claude_dir = temp_project / ".claude"
        claude_dir.mkdir(parents=True)

        settings = {
            "mcpServers": {
                "github": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "env": {"GITHUB_TOKEN": "ghp_xxxx"},
                }
            }
        }
        (claude_dir / "settings.local.json").write_text(json.dumps(settings))

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.mcp_servers) == 1
        mcp = result.mcp_servers[0]
        assert mcp.name == "github"
        assert mcp.config["command"] == "npx"
        assert "GITHUB_TOKEN" in mcp.env_vars

    def test_detect_multiple_mcp_servers(self, temp_project: Path) -> None:
        """Test detection of multiple MCP servers."""
        claude_dir = temp_project / ".claude"
        claude_dir.mkdir(parents=True)

        settings = {
            "mcpServers": {
                "server1": {"command": "cmd1"},
                "server2": {"command": "cmd2"},
            }
        }
        (claude_dir / "settings.local.json").write_text(json.dumps(settings))

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.mcp_servers) == 2
        names = {m.name for m in result.mcp_servers}
        assert names == {"server1", "server2"}

    def test_detect_mcp_from_dedicated_dir(self, temp_project: Path) -> None:
        """Test detection of MCP configs from dedicated directory."""
        mcp_dir = temp_project / ".devsync" / "mcp"
        mcp_dir.mkdir(parents=True)

        config = {"command": "python", "args": ["-m", "my_server"]}
        (mcp_dir / "custom-server.json").write_text(json.dumps(config))

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.mcp_servers) == 1
        assert result.mcp_servers[0].name == "custom-server"

    def test_handle_invalid_json(self, temp_project: Path) -> None:
        """Test handling of invalid JSON in MCP config."""
        claude_dir = temp_project / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "settings.local.json").write_text("not valid json")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.mcp_servers) == 0


class TestHookDetection:
    """Test hook script detection."""

    def test_detect_hooks(self, temp_project: Path) -> None:
        """Test detection of hook scripts."""
        hooks_dir = temp_project / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "preToolUse.sh").write_text("#!/bin/bash")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.hooks) == 1
        hook = result.hooks[0]
        assert hook.name == "preToolUse"
        assert hook.hook_type == "PreToolUse"

    def test_detect_post_tool_hook(self, temp_project: Path) -> None:
        """Test detection of PostToolUse hook."""
        hooks_dir = temp_project / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "post-tool-handler.sh").write_text("#!/bin/bash")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.hooks) == 1
        assert result.hooks[0].hook_type == "PostToolUse"

    def test_detect_notification_hook(self, temp_project: Path) -> None:
        """Test detection of Notification hook."""
        hooks_dir = temp_project / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "notification.py").write_text("# notification hook")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert result.hooks[0].hook_type == "Notification"

    def test_detect_unknown_hook_type(self, temp_project: Path) -> None:
        """Test detection of unknown hook type."""
        hooks_dir = temp_project / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "custom-hook.sh").write_text("#!/bin/bash")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert result.hooks[0].hook_type == "Unknown"


class TestCommandDetection:
    """Test command script detection."""

    def test_detect_shell_command(self, temp_project: Path) -> None:
        """Test detection of shell commands."""
        cmd_dir = temp_project / ".claude" / "commands"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "build.sh").write_text("#!/bin/bash\necho 'building'")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.commands) == 1
        cmd = result.commands[0]
        assert cmd.name == "build"
        assert cmd.command_type == "shell"

    def test_detect_slash_command(self, temp_project: Path) -> None:
        """Test detection of slash commands."""
        cmd_dir = temp_project / ".claude" / "commands"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "review.md").write_text("# Review Command")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.commands) == 1
        assert result.commands[0].command_type == "slash"


class TestResourceDetection:
    """Test resource file detection."""

    def test_detect_resources(self, temp_project: Path) -> None:
        """Test detection of resource files."""
        res_dir = temp_project / ".devsync" / "resources"
        res_dir.mkdir(parents=True)
        (res_dir / "config.json").write_text('{"key": "value"}')

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.resources) == 1
        res = result.resources[0]
        assert res.name == "config"
        assert res.size > 0
        assert len(res.checksum) == 64

    def test_detect_nested_resources(self, temp_project: Path) -> None:
        """Test detection of nested resource files."""
        res_dir = temp_project / ".devsync" / "resources" / "templates"
        res_dir.mkdir(parents=True)
        (res_dir / "template.txt").write_text("template content")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.resources) == 1


class TestToPackageComponents:
    """Test conversion to PackageComponents."""

    def test_convert_to_package_components(self, temp_project: Path) -> None:
        """Test conversion of detection results to PackageComponents."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "style.md").write_text("# Style Guide")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()
        components = detector.to_package_components(result)

        assert components.total_count == 1
        assert len(components.instructions) == 1
        assert components.instructions[0].name == "style"
        assert components.instructions[0].file == str(Path(".claude") / "rules" / "style.md")

    def test_convert_all_component_types(self, temp_project: Path) -> None:
        """Test conversion of all component types."""
        (temp_project / ".claude" / "rules").mkdir(parents=True)
        (temp_project / ".claude" / "rules" / "inst.md").write_text("# Inst")

        (temp_project / ".claude" / "hooks").mkdir(parents=True)
        (temp_project / ".claude" / "hooks" / "preToolUse.sh").write_text("#!/bin/bash")

        (temp_project / ".claude" / "commands").mkdir(parents=True)
        (temp_project / ".claude" / "commands" / "build.sh").write_text("#!/bin/bash")

        (temp_project / ".devsync" / "resources").mkdir(parents=True)
        (temp_project / ".devsync" / "resources" / "data.json").write_text("{}")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()
        components = detector.to_package_components(result)

        assert len(components.instructions) == 1
        assert len(components.hooks) == 1
        assert len(components.commands) == 1
        assert len(components.resources) == 1


class TestDetectionResult:
    """Test DetectionResult class."""

    def test_total_count(self) -> None:
        """Test total count calculation."""
        result = DetectionResult(
            instructions=[
                DetectedInstruction(
                    name="test",
                    file_path=Path("/test.md"),
                    relative_path="test.md",
                    source_ide="claude",
                )
            ],
            hooks=[
                DetectedHook(
                    name="hook",
                    file_path=Path("/hook.sh"),
                    relative_path="hook.sh",
                    hook_type="PreToolUse",
                )
            ],
        )

        assert result.total_count == 2

    def test_empty_result(self) -> None:
        """Test empty detection result."""
        result = DetectionResult()
        assert result.total_count == 0
        assert len(result.warnings) == 0


class TestSkillDetection:
    """Test Claude skill detection."""

    def test_detect_skill_directory(self, temp_project: Path) -> None:
        """Test detection of skill directory with SKILL.md."""
        skills_dir = temp_project / ".claude" / "skills"
        skill_dir = skills_dir / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            """---
name: my-skill
description: A test skill
---
# My Skill
Instructions for the skill.
"""
        )

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.skills) == 1
        skill = result.skills[0]
        assert skill.name == "my-skill"
        assert skill.description == "A test skill"

    def test_detect_skill_with_scripts(self, temp_project: Path) -> None:
        """Test detection of skill with supporting scripts."""
        skills_dir = temp_project / ".claude" / "skills"
        skill_dir = skills_dir / "script-skill"
        script_dir = skill_dir / "scripts"
        script_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Script Skill")
        (script_dir / "helper.sh").write_text("#!/bin/bash")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.skills) == 1
        assert result.skills[0].has_scripts is True

    def test_skip_directory_without_skill_md(self, temp_project: Path) -> None:
        """Test that directories without SKILL.md are skipped."""
        skills_dir = temp_project / ".claude" / "skills"
        (skills_dir / "not-a-skill").mkdir(parents=True)
        (skills_dir / "not-a-skill" / "readme.txt").write_text("Not a skill")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.skills) == 0


class TestWorkflowDetection:
    """Test Windsurf workflow detection."""

    def test_detect_workflow_file(self, temp_project: Path) -> None:
        """Test detection of workflow file."""
        workflows_dir = temp_project / ".windsurf" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "deploy.md").write_text(
            """---
description: Deploy workflow
---
# Deploy Workflow
Steps for deployment.
"""
        )

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.workflows) == 1
        wf = result.workflows[0]
        assert wf.name == "deploy"
        assert wf.description == "Deploy workflow"

    def test_detect_yaml_workflow(self, temp_project: Path) -> None:
        """Test detection of YAML workflow file."""
        workflows_dir = temp_project / ".windsurf" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "build.yaml").write_text("name: build")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.workflows) == 1
        assert result.workflows[0].name == "build"


class TestMemoryFileDetection:
    """Test CLAUDE.md memory file detection."""

    def test_detect_root_claude_md(self, temp_project: Path) -> None:
        """Test detection of root CLAUDE.md file."""
        (temp_project / "CLAUDE.md").write_text("# Project Memory\nContext for this project.")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.memory_files) == 1
        mem = result.memory_files[0]
        assert mem.name == "CLAUDE"
        assert mem.is_root is True

    def test_detect_subdirectory_claude_md(self, temp_project: Path) -> None:
        """Test detection of CLAUDE.md in subdirectories."""
        (temp_project / "CLAUDE.md").write_text("# Root memory")
        subdir = temp_project / "packages" / "frontend"
        subdir.mkdir(parents=True)
        (subdir / "CLAUDE.md").write_text("# Frontend memory")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.memory_files) == 2
        root_mem = next(m for m in result.memory_files if m.is_root)
        subdir_mem = next(m for m in result.memory_files if not m.is_root)
        assert root_mem.name == "CLAUDE"
        assert "packages" in subdir_mem.name or "frontend" in subdir_mem.name

    def test_skip_ignored_directories(self, temp_project: Path) -> None:
        """Test that node_modules and venv are skipped."""
        (temp_project / "node_modules").mkdir()
        (temp_project / "node_modules" / "CLAUDE.md").write_text("# Should be ignored")
        (temp_project / "venv").mkdir()
        (temp_project / "venv" / "CLAUDE.md").write_text("# Should be ignored")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.memory_files) == 0


class TestCopilotMainInstructionsDetection:
    """Test detection of .github/copilot-instructions.md."""

    def test_detect_copilot_instructions_file(self, temp_project: Path) -> None:
        """Test detection of single copilot-instructions.md file."""
        github_dir = temp_project / ".github"
        github_dir.mkdir(parents=True)
        (github_dir / "copilot-instructions.md").write_text("# Main Copilot Instructions")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.instructions) == 1
        inst = result.instructions[0]
        assert inst.name == "copilot-instructions"
        assert inst.source_ide == "copilot"

    def test_detect_recursive_copilot_instructions(self, temp_project: Path) -> None:
        """Test detection of nested .instructions.md files."""
        instructions_dir = temp_project / ".github" / "instructions"
        subdir = instructions_dir / "backend"
        subdir.mkdir(parents=True)
        (subdir / "api.instructions.md").write_text("# API Instructions")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.instructions) == 1
        inst = result.instructions[0]
        assert "backend" in inst.name or "api" in inst.name
        assert inst.source_ide == "copilot"
