"""Unit tests for component detection."""

import json
from pathlib import Path

import pytest

from devsync.core.component_detector import (
    ComponentDetector,
    DetectedHook,
    DetectedInstruction,
    DetectedMCPServer,
    DetectedResource,
    DetectionResult,
    filter_detection_result,
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


class TestMultiToolMCPDetection:
    """Test MCP server detection from multiple AI tools."""

    def test_detect_cursor_mcp(self, temp_project: Path) -> None:
        """Test detection of MCP servers from Cursor config."""
        cursor_dir = temp_project / ".cursor"
        cursor_dir.mkdir(parents=True)

        config = {"mcpServers": {"my-server": {"command": "node", "args": ["server.js"]}}}
        (cursor_dir / "mcp.json").write_text(json.dumps(config))

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        cursor_servers = [s for s in result.mcp_servers if s.source_tool == "cursor"]
        assert len(cursor_servers) == 1
        assert cursor_servers[0].name == "my-server"

    def test_detect_roo_mcp(self, temp_project: Path) -> None:
        """Test detection of MCP servers from Roo Code config."""
        roo_dir = temp_project / ".roo"
        roo_dir.mkdir(parents=True)

        config = {"mcpServers": {"roo-server": {"command": "python", "args": ["-m", "server"]}}}
        (roo_dir / "mcp.json").write_text(json.dumps(config))

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        roo_servers = [s for s in result.mcp_servers if s.source_tool == "roo"]
        assert len(roo_servers) == 1
        assert roo_servers[0].name == "roo-server"

    def test_detect_copilot_mcp_uses_servers_key(self, temp_project: Path) -> None:
        """Test that Copilot MCP uses 'servers' key, not 'mcpServers'."""
        vscode_dir = temp_project / ".vscode"
        vscode_dir.mkdir(parents=True)

        config = {"servers": {"copilot-server": {"command": "npx", "args": ["server"]}}}
        (vscode_dir / "mcp.json").write_text(json.dumps(config))

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        copilot_servers = [s for s in result.mcp_servers if s.source_tool == "copilot"]
        assert len(copilot_servers) == 1
        assert copilot_servers[0].name == "copilot-server"

    def test_detect_claude_mcp(self, temp_project: Path) -> None:
        """Test detection of MCP servers from Claude config."""
        claude_dir = temp_project / ".claude"
        claude_dir.mkdir(parents=True)

        config = {"mcpServers": {"claude-server": {"command": "uvx", "args": ["mcp-server"]}}}
        (claude_dir / "settings.local.json").write_text(json.dumps(config))

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        claude_servers = [s for s in result.mcp_servers if s.source_tool == "claude"]
        assert len(claude_servers) == 1
        assert claude_servers[0].name == "claude-server"

    def test_detect_multi_tool_mcp(self, temp_project: Path) -> None:
        """Test detection of MCP servers from multiple tools simultaneously."""
        # Claude
        claude_dir = temp_project / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "settings.local.json").write_text(
            json.dumps({"mcpServers": {"shared-server": {"command": "cmd1"}}})
        )

        # Cursor
        cursor_dir = temp_project / ".cursor"
        cursor_dir.mkdir(parents=True)
        (cursor_dir / "mcp.json").write_text(json.dumps({"mcpServers": {"cursor-only": {"command": "cmd2"}}}))

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.mcp_servers) >= 2
        tools = {s.source_tool for s in result.mcp_servers}
        assert "claude" in tools
        assert "cursor" in tools

    def test_source_tool_set_on_mcp_from_devsync_dir(self, temp_project: Path) -> None:
        """Test that MCP servers from .devsync/mcp/ get source_tool='devsync'."""
        mcp_dir = temp_project / ".devsync" / "mcp"
        mcp_dir.mkdir(parents=True)
        (mcp_dir / "fallback.json").write_text(json.dumps({"command": "python"}))

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.mcp_servers) == 1
        assert result.mcp_servers[0].source_tool == "devsync"


class TestToolFilter:
    """Test tool filtering on ComponentDetector."""

    def test_single_tool_filter(self, temp_project: Path) -> None:
        """Test filtering to a single tool."""
        # Create claude + cursor instructions
        (temp_project / ".claude" / "rules").mkdir(parents=True)
        (temp_project / ".claude" / "rules" / "rule.md").write_text("# Rule")
        (temp_project / ".cursor" / "rules").mkdir(parents=True)
        (temp_project / ".cursor" / "rules" / "rule.mdc").write_text("# Rule")

        detector = ComponentDetector(temp_project, tool_filter=["claude"])
        result = detector.detect_all()

        assert len(result.instructions) == 1
        assert result.instructions[0].source_ide == "claude"

    def test_multiple_tool_filter(self, temp_project: Path) -> None:
        """Test filtering to multiple tools."""
        (temp_project / ".claude" / "rules").mkdir(parents=True)
        (temp_project / ".claude" / "rules" / "rule.md").write_text("# Rule")
        (temp_project / ".cursor" / "rules").mkdir(parents=True)
        (temp_project / ".cursor" / "rules" / "rule.mdc").write_text("# Rule")
        (temp_project / ".windsurf" / "rules").mkdir(parents=True)
        (temp_project / ".windsurf" / "rules" / "rule.md").write_text("# Rule")

        detector = ComponentDetector(temp_project, tool_filter=["claude", "cursor"])
        result = detector.detect_all()

        assert len(result.instructions) == 2
        ides = {i.source_ide for i in result.instructions}
        assert ides == {"claude", "cursor"}

    def test_no_filter_returns_all(self, temp_project: Path) -> None:
        """Test that no filter returns everything."""
        (temp_project / ".claude" / "rules").mkdir(parents=True)
        (temp_project / ".claude" / "rules" / "rule.md").write_text("# Rule")
        (temp_project / ".cursor" / "rules").mkdir(parents=True)
        (temp_project / ".cursor" / "rules" / "rule.mdc").write_text("# Rule")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.instructions) == 2


class TestComponentFilter:
    """Test component type filtering via filter_detection_result."""

    def test_filter_instructions_only(self) -> None:
        """Test filtering to instructions only."""
        result = DetectionResult(
            instructions=[
                DetectedInstruction(name="r", file_path=Path("/r.md"), relative_path="r.md", source_ide="claude")
            ],
            mcp_servers=[
                DetectedMCPServer(name="s", file_path=Path("/fake"), config={}, source="x", source_tool="claude")
            ],
        )

        filtered = filter_detection_result(result, component_filter=["rules"])
        assert len(filtered.instructions) == 1
        assert len(filtered.mcp_servers) == 0

    def test_filter_mcp_only(self) -> None:
        """Test filtering to MCP servers only."""
        result = DetectionResult(
            instructions=[
                DetectedInstruction(name="r", file_path=Path("/r.md"), relative_path="r.md", source_ide="claude")
            ],
            mcp_servers=[
                DetectedMCPServer(name="s", file_path=Path("/fake"), config={}, source="x", source_tool="claude")
            ],
        )

        filtered = filter_detection_result(result, component_filter=["mcp"])
        assert len(filtered.instructions) == 0
        assert len(filtered.mcp_servers) == 1

    def test_filter_combined(self) -> None:
        """Test filtering to multiple component types."""
        result = DetectionResult(
            instructions=[
                DetectedInstruction(name="r", file_path=Path("/r.md"), relative_path="r.md", source_ide="claude")
            ],
            mcp_servers=[
                DetectedMCPServer(name="s", file_path=Path("/fake"), config={}, source="x", source_tool="claude")
            ],
            hooks=[DetectedHook(name="h", file_path=Path("/h.sh"), relative_path="h.sh", hook_type="PreToolUse")],
        )

        filtered = filter_detection_result(result, component_filter=["rules", "mcp"])
        assert len(filtered.instructions) == 1
        assert len(filtered.mcp_servers) == 1
        assert len(filtered.hooks) == 0

    def test_filter_by_tool_and_component(self) -> None:
        """Test filtering by both tool and component."""
        result = DetectionResult(
            mcp_servers=[
                DetectedMCPServer(name="s1", file_path=Path("/fake"), config={}, source="x", source_tool="claude"),
                DetectedMCPServer(name="s2", file_path=Path("/fake"), config={}, source="y", source_tool="cursor"),
            ],
        )

        filtered = filter_detection_result(result, tool_filter=["claude"], component_filter=["mcp"])
        assert len(filtered.mcp_servers) == 1
        assert filtered.mcp_servers[0].source_tool == "claude"

    def test_no_filter_returns_all(self) -> None:
        """Test that no filter returns everything."""
        result = DetectionResult(
            instructions=[
                DetectedInstruction(name="r", file_path=Path("/r.md"), relative_path="r.md", source_ide="claude")
            ],
            mcp_servers=[
                DetectedMCPServer(name="s", file_path=Path("/fake"), config={}, source="x", source_tool="claude")
            ],
        )

        filtered = filter_detection_result(result)
        assert len(filtered.instructions) == 1
        assert len(filtered.mcp_servers) == 1

    def test_tool_filter_on_instructions(self) -> None:
        """Test that tool_filter filters instructions by source_ide."""
        result = DetectionResult(
            instructions=[
                DetectedInstruction(name="r1", file_path=Path("/r1.md"), relative_path="r1.md", source_ide="claude"),
                DetectedInstruction(name="r2", file_path=Path("/r2.md"), relative_path="r2.md", source_ide="cursor"),
                DetectedInstruction(name="r3", file_path=Path("/r3.md"), relative_path="r3.md", source_ide="windsurf"),
            ],
        )

        filtered = filter_detection_result(result, tool_filter=["cursor"])
        assert len(filtered.instructions) == 1
        assert filtered.instructions[0].source_ide == "cursor"

    def test_tool_filter_preserves_resources(self) -> None:
        """Test that tool_filter does not drop resources (they are tool-agnostic)."""
        result = DetectionResult(
            mcp_servers=[
                DetectedMCPServer(name="s", file_path=Path("/fake"), config={}, source="x", source_tool="claude"),
            ],
            resources=[
                DetectedResource(name="res", file_path=Path("/r.txt"), relative_path="r.txt", size=10, checksum="abc"),
            ],
        )

        filtered = filter_detection_result(result, tool_filter=["cursor"])
        # MCP filtered out (source_tool=claude, filter=cursor)
        assert len(filtered.mcp_servers) == 0
        # Resources preserved despite tool_filter (they're tool-agnostic)
        assert len(filtered.resources) == 1

    def test_tool_filter_multiple_on_instructions(self) -> None:
        """Test that tool_filter with multiple tools filters instructions correctly."""
        result = DetectionResult(
            instructions=[
                DetectedInstruction(name="r1", file_path=Path("/r1.md"), relative_path="r1.md", source_ide="claude"),
                DetectedInstruction(name="r2", file_path=Path("/r2.md"), relative_path="r2.md", source_ide="cursor"),
                DetectedInstruction(name="r3", file_path=Path("/r3.md"), relative_path="r3.md", source_ide="windsurf"),
            ],
        )

        filtered = filter_detection_result(result, tool_filter=["claude", "windsurf"])
        assert len(filtered.instructions) == 2
        ides = {i.source_ide for i in filtered.instructions}
        assert ides == {"claude", "windsurf"}


class TestScopeFilter:
    """Test scope-based detection."""

    def test_project_scope_default(self, temp_project: Path) -> None:
        """Test that project scope is the default."""
        detector = ComponentDetector(temp_project)
        assert detector.scope == "project"

    def test_project_scope_detects_project_configs(self, temp_project: Path) -> None:
        """Test that project scope detects project-level MCP configs."""
        claude_dir = temp_project / ".claude"
        claude_dir.mkdir(parents=True)
        config = {"mcpServers": {"server": {"command": "cmd"}}}
        (claude_dir / "settings.local.json").write_text(json.dumps(config))

        detector = ComponentDetector(temp_project, scope="project")
        result = detector.detect_all()

        assert len(result.mcp_servers) >= 1

    def test_source_tool_on_hooks(self, temp_project: Path) -> None:
        """Test that source_tool is set on detected hooks."""
        hooks_dir = temp_project / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "preToolUse.sh").write_text("#!/bin/bash")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.hooks) == 1
        assert result.hooks[0].source_tool == "claude"

    def test_source_tool_on_commands(self, temp_project: Path) -> None:
        """Test that source_tool is set on detected commands."""
        cmd_dir = temp_project / ".claude" / "commands"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "build.sh").write_text("#!/bin/bash")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        assert len(result.commands) == 1
        assert result.commands[0].source_tool == "claude"

    def test_invalid_scope_rejected(self, temp_project: Path) -> None:
        """Test that invalid scope raises ValueError."""
        with pytest.raises(ValueError, match="Invalid scope"):
            ComponentDetector(temp_project, scope="invalid")

    def test_source_tool_on_roo_commands(self, temp_project: Path) -> None:
        """Test that source_tool is set correctly on Roo commands."""
        cmd_dir = temp_project / ".roo" / "commands"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "deploy.sh").write_text("#!/bin/bash")

        detector = ComponentDetector(temp_project)
        result = detector.detect_all()

        roo_cmds = [c for c in result.commands if c.source_tool == "roo"]
        assert len(roo_cmds) == 1
        assert roo_cmds[0].name == "deploy"
