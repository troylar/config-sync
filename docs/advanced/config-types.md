# Configuration Types and Detection

DevSync manages several distinct configuration types across 23+ supported AI coding tools. Each type has specific file formats, installation patterns, and detection rules.

## Configuration Types

### Practices

Practices are the primary configuration type in v2. They are abstract, tool-agnostic declarations of development standards that the LLM reads and adapts into IDE-specific rule files. Practices are defined in the `practices` section of a `devsync-package.yaml` manifest and include structured fields: intent, principles, enforcement patterns, and examples.

During installation, the AI adaptation engine reads each practice and generates the appropriate content for each target IDE -- formatting it as a `.mdc` file for Cursor, a `.md` file for Claude Code, a section in `AGENTS.md` for Codex, etc.

### Instructions (v1)

In v1, instructions were explicit markdown files distributed directly to IDE rule directories. In v2, the equivalent is the `practices` section in the package manifest, which the LLM uses to generate IDE-adapted content. File-copy fallback (using `--no-ai`) still writes instructions as-is to their target locations.

DevSync supports two installation patterns for instructions depending on the target IDE.

#### Multi-File Pattern

Most IDEs use a **multi-file pattern** where each instruction is a separate file in a dedicated directory.

| IDE | Directory | Extension |
|-----|-----------|-----------|
| Claude Code | `.claude/rules/` | `.md` |
| Cursor | `.cursor/rules/` | `.mdc` |
| Windsurf | `.windsurf/rules/` | `.md` |
| GitHub Copilot | `.github/instructions/` | `.instructions.md` |
| Kiro | `.kiro/steering/` | `.md` |
| Cline | `.clinerules/` | `.md` |
| Roo Code | `.roo/rules/` | `.md` |
| Antigravity | `.agent/rules/` | `.md` |
| Amazon Q | `.amazonq/rules/` | `.md` |
| JetBrains AI | `.aiassistant/rules/` | `.md` |
| Continue.dev | `.continue/rules/` | `.md` |
| Trae | `.trae/rules/` | `.md` |
| Augment | `.augment/rules/` | `.md` |
| Tabnine | `.tabnine/guidelines/` | `.md` |
| OpenHands | `.openhands/microagents/` | `.md` |

With multi-file installations, each instruction is installed as its own file. Installing `python-style` to Claude Code creates `.claude/rules/python-style.md`.

#### Single-File Pattern

Some IDEs use a **single-file pattern** where all instructions are managed as sections within a single file at the project root. DevSync uses HTML comment markers to delimit each instruction section.

| IDE | File | Location |
|-----|------|----------|
| OpenAI Codex CLI | `AGENTS.md` | Project root |
| Gemini CLI | `GEMINI.md` | Project root |
| Aider | `CONVENTIONS.md` | Project root |
| Junie | `.junie/guidelines.md` | Project root |
| Zed | `.rules` | Project root |
| Amp | `AGENTS.md` | Project root |
| OpenCode | `AGENTS.md` | Project root |

!!! info "Section Markers"
    Single-file IDEs use HTML comment markers to separate instructions within the shared file:

    ```markdown
    <!-- devsync:start:python-style -->
    # Python Style Guide
    Follow PEP 8 conventions...
    <!-- devsync:end:python-style -->

    <!-- devsync:start:testing-guide -->
    # Testing Guide
    Write pytest tests for all new code...
    <!-- devsync:end:testing-guide -->
    ```

    These markers allow DevSync to install, update, and uninstall individual instructions without affecting other sections in the file.

!!! note "Shared files"
    Codex CLI, Amp, and OpenCode all use `AGENTS.md`. If you install instructions for multiple single-file IDEs that share the same file, they coexist using their respective section markers.

### MCP Server Configs

MCP (Model Context Protocol) server configurations define external tools that AI assistants can invoke. These are JSON-format configuration files.

**Detection locations:**

- `.claude/settings.local.json` -- the `mcpServers` key within this file
- `.devsync/mcp/*.json` -- standalone JSON config files

**IDE support for MCP:**

| IDE | MCP Config Path |
|-----|----------------|
| Claude Code | `.claude/settings.local.json` |
| Cursor | `.cursor/mcp.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| GitHub Copilot | `.vscode/mcp.json` |
| Roo Code | `.roo/mcp.json` |
| Antigravity | `.mcp.json` |
| Amazon Q | `.amazonq/mcp.json` |
| JetBrains AI | `.aiassistant/mcp.json` |
| Zed | `.zed/settings.json` |
| Continue.dev | `.continue/config.json` |
| Trae | `.mcp.json` |
| Augment | `.augment/mcp.json` |
| Tabnine | `.tabnine/mcp.json` |
| OpenHands | `.openhands/mcp.json` |

### Hooks

Hook scripts run at specific points in an AI tool's lifecycle. Currently supported by Claude Code only.

**Detection location:** `.claude/hooks/`

**Hook types** (inferred from filename):

| Filename Pattern | Hook Type |
|-----------------|-----------|
| `*pretooluse*` or `*pre-tool*` | `PreToolUse` |
| `*posttooluse*` or `*post-tool*` | `PostToolUse` |
| `*notification*` | `Notification` |
| `*stop*` | `Stop` |

### Commands

Command scripts (slash commands or shell scripts) that extend IDE functionality. This is a legacy component type primarily for Claude Code.

**Detection location:** `.claude/commands/`

**Command types** (inferred from extension):

| Extension | Command Type |
|-----------|-------------|
| `.sh`, `.bash` | `shell` |
| `.md`, `.txt` | `slash` |

### Skills

Skills are Claude Code directories containing a `SKILL.md` file with optional supporting scripts. They can be invoked via slash commands.

**Detection location:** `.claude/skills/*/SKILL.md`

Each skill is a subdirectory under `.claude/skills/`. The detector looks for a `SKILL.md` (or `Skill.md`) file in each subdirectory and extracts a description from YAML frontmatter if present.

```
.claude/skills/
  deploy/
    SKILL.md          # Required
    scripts/
      deploy.sh       # Optional supporting files
  review/
    SKILL.md
```

### Workflows

Workflows define multi-step automated processes for Windsurf.

**Detection location:** `.windsurf/workflows/`

Supported file types: `.md`, `.yaml`, `.yml`. Descriptions are extracted from YAML frontmatter.

### Memory Files

Memory files (`CLAUDE.md`) persist context across Claude Code sessions. They can exist at the project root and in subdirectories.

**Detection locations:**

- `CLAUDE.md` at project root (flagged as `is_root=True`)
- `CLAUDE.md` in subdirectories (recursive scan, skipping `node_modules`, `venv`, `dist`, `build`, and hidden directories)

### Resources

Resources are arbitrary files of any type that are distributed alongside other components in a package.

**Detection location:** `.devsync/resources/`

Resources are scanned recursively with the following limits:

- Maximum file size: 200 MB (files exceeding this are skipped)
- Warning threshold: 50 MB (a warning is logged for large files)

Each resource is checksummed with SHA-256 for integrity verification.

## Component Detection

The `ComponentDetector` class in `devsync/core/component_detector.py` scans a project directory to discover all existing configurations. This is used by `devsync extract` to auto-detect components when generating a package from an existing project.

### How Detection Works

```python
from devsync.core.component_detector import ComponentDetector
from pathlib import Path

detector = ComponentDetector(Path("/path/to/project"))
result = detector.detect_all()

print(f"Found {result.total_count} components")
print(f"  Instructions: {len(result.instructions)}")
print(f"  MCP Servers: {len(result.mcp_servers)}")
print(f"  Hooks: {len(result.hooks)}")
print(f"  Commands: {len(result.commands)}")
print(f"  Skills: {len(result.skills)}")
print(f"  Workflows: {len(result.workflows)}")
print(f"  Memory Files: {len(result.memory_files)}")
print(f"  Resources: {len(result.resources)}")
```

### Detection Scan Order

1. **Instructions** -- Scans all multi-file directories (`.claude/rules/`, `.cursor/rules/`, etc.) and single-file locations (`AGENTS.md`, `.github/copilot-instructions.md`)
2. **MCP Servers** -- Reads `mcpServers` from `.claude/settings.local.json` and standalone configs from `.devsync/mcp/`
3. **Hooks** -- Scans `.claude/hooks/` for script files
4. **Commands** -- Scans `.claude/commands/` for script and markdown files
5. **Skills** -- Scans `.claude/skills/` for subdirectories containing `SKILL.md`
6. **Workflows** -- Scans `.windsurf/workflows/` for `.md` and `.yaml` files
7. **Memory Files** -- Finds `CLAUDE.md` at root and in subdirectories
8. **Resources** -- Scans `.devsync/resources/` recursively

### Recognized File Extensions for Instructions

The detector recognizes these extensions as instruction files:

- `.md` -- Standard Markdown
- `.mdc` -- Cursor Markdown with metadata
- `.instructions.md` -- GitHub Copilot format

### GitHub Copilot Recursive Detection

GitHub Copilot instructions in `.github/instructions/` are scanned recursively to support subdirectory organization. The instruction name includes the subdirectory path with slashes replaced by hyphens:

```
.github/instructions/
  python/
    style.instructions.md    -> name: "python-style"
  testing/
    unit.instructions.md     -> name: "testing-unit"
```

### Converting Detection Results to Package Components

The detector can convert its results into `PackageComponents` for manifest generation:

```python
components = detector.to_package_components(result)
# components.instructions, components.mcp_servers, etc.
```

This conversion is used internally by `devsync extract` to build the `devsync-package.yaml` manifest.
