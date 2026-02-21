# Claude Code

Claude Code is the most fully supported IDE integration in DevSync. It supports all package component types: instructions, MCP servers, hooks, commands, skills, and memory files.

## Overview

| Property | Value |
|----------|-------|
| **Instruction path** | `.claude/rules/*.md` |
| **File extension** | `.md` |
| **MCP config (project)** | `.claude/settings.local.json` |
| **MCP config (global)** | `~/.claude/settings.json` |
| **Hooks directory** | `.claude/hooks/` |
| **Commands directory** | `.claude/commands/` |
| **Skills directory** | `.claude/skills/` |
| **Memory file** | `CLAUDE.md` |
| **Project scope** | Yes |
| **Global scope** | No (DevSync uses project-level only) |

---

## Instructions

Claude Code reads markdown files from `.claude/rules/` in the project root. Each file is loaded automatically during a session.

DevSync installs one `.md` file per instruction:

```
my-project/
  .claude/
    rules/
      code-style.md        # Installed by DevSync
      testing-standards.md  # Installed by DevSync
      security-rules.md     # Installed by DevSync
```

### Installing Instructions

```bash
# Install a package from a local path
devsync install ./my-package --tool claude

# Install a package from a Git repository
devsync install https://github.com/acme/standards --tool claude

# Install with conflict handling
devsync install ./my-package --tool claude --conflict overwrite
```

### Instruction File Format

Claude Code rules are plain markdown. No frontmatter or metadata is required:

```markdown
# Code Style Guidelines

- Use type hints on all function signatures
- Prefer early returns to reduce nesting
- Maximum line length: 120 characters
```

---

## MCP Server Configuration

Claude Code supports MCP (Model Context Protocol) servers for extending its capabilities with external tools.

### Configuration Locations

=== "Project-level"

    Project MCP servers are configured in `.claude/settings.local.json`:

    ```json
    {
      "mcpServers": {
        "postgres": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-postgres"],
          "env": {
            "DATABASE_URL": "postgresql://localhost:5432/mydb"
          }
        }
      }
    }
    ```

    !!! tip
        Project-level configs are stored in `.claude/settings.local.json` (not `settings.json`). The `.local` variant is typically gitignored since it may contain credentials.

=== "Global"

    Global MCP servers are configured in `~/.claude/settings.json`:

    ```json
    {
      "mcpServers": {
        "filesystem": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/you/projects"]
        }
      }
    }
    ```

### Installing MCP via Packages

```bash
devsync install ./my-package --tool claude
```

DevSync merges MCP server entries into the existing configuration file without overwriting unrelated entries.

---

## Hooks

Claude Code supports hooks that run at specific lifecycle points. DevSync installs hook files to `.claude/hooks/`.

```
my-project/
  .claude/
    hooks/
      pre-commit.sh
      post-save.sh
```

Hooks are defined in package manifests and installed as executable scripts.

---

## Commands

Claude Code slash commands let users trigger predefined actions during a session. DevSync installs command files to `.claude/commands/`.

```
my-project/
  .claude/
    commands/
      deploy.md
      review.md
```

Each command file defines the prompt and behavior for a `/command-name` slash command.

---

## Skills

Skills are installed to `.claude/skills/` and provide reusable capabilities that Claude Code can reference during sessions.

```
my-project/
  .claude/
    skills/
      database-migration.md
      api-design.md
```

---

## Memory Files (CLAUDE.md)

The `CLAUDE.md` file at the project root persists context across Claude Code sessions. It serves as long-term memory for project-specific preferences, architecture decisions, and working context.

DevSync can install memory file content as part of a package:

```bash
devsync install ./team-setup --tool claude
```

!!! warning
    Memory files are additive. DevSync appends content to existing `CLAUDE.md` files rather than replacing them, to avoid overwriting user-maintained context.

---

## Detection

DevSync detects Claude Code by checking for the `~/.claude/` configuration directory. You can verify detection with:

```bash
devsync tools
```

---

## Package Component Support

Claude Code supports all DevSync package component types:

| Component | Supported | Install Location |
|-----------|:---------:|-----------------|
| Instructions | Yes | `.claude/rules/*.md` |
| MCP Servers | Yes | `.claude/settings.local.json` |
| Hooks | Yes | `.claude/hooks/` |
| Commands | Yes | `.claude/commands/` |
| Skills | Yes | `.claude/skills/` |
| Workflows | -- | Not applicable |
| Memory Files | Yes | `CLAUDE.md` |
| Resources | Yes | `.claude/resources/` |

---

## Example: Full Package Installation

Given a package with all component types:

```bash
devsync install ./full-stack-setup --tool claude
```

Result:

```
my-project/
  CLAUDE.md                          # Memory file content appended
  .claude/
    settings.local.json              # MCP servers merged
    rules/
      code-style.md                  # Instruction
      api-conventions.md             # Instruction
    hooks/
      pre-commit.sh                  # Hook
    commands/
      deploy.md                      # Slash command
    skills/
      database-patterns.md           # Skill
```
