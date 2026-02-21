# Cursor

Cursor uses `.mdc` files (markdown with metadata) for project rules and supports MCP server configuration at both project and global levels.

## Overview

| Property | Value |
|----------|-------|
| **Instruction path** | `.cursor/rules/*.mdc` |
| **File extension** | `.mdc` |
| **MCP config (project)** | `.cursor/mcp.json` |
| **MCP config (global)** | `~/.cursor/mcp.json` |
| **MCP tool limit** | 40 tools |
| **Project scope** | Yes |
| **Global scope** | Yes |

---

## Instructions

Cursor reads rule files from `.cursor/rules/` in the project root. DevSync installs one `.mdc` file per instruction:

```
my-project/
  .cursor/
    rules/
      code-style.mdc
      testing-standards.mdc
```

### Installing Instructions

```bash
# Install a package from a local path
devsync install ./my-package --tool cursor

# Install a package from a Git repository
devsync install https://github.com/acme/standards --tool cursor
```

### The .mdc File Format

Cursor uses `.mdc` files, which are markdown files with an optional YAML frontmatter block for metadata:

```markdown
---
description: Enforce consistent code style across the project
globs: ["src/**/*.tsx", "src/**/*.ts"]
alwaysApply: false
---

# Code Style Guidelines

- Use functional components, never class components
- Prefer named exports over default exports
- Maximum line length: 120 characters
```

#### Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `description` | `string` | Short description of the rule's purpose |
| `globs` | `string[]` | File patterns that trigger this rule (e.g., `["src/**/*.ts"]`) |
| `alwaysApply` | `boolean` | If `true`, the rule applies to all files regardless of globs |

!!! note
    When DevSync installs instructions to Cursor, the instruction content is written as-is. If your instruction source includes frontmatter, it will be preserved. If it does not, Cursor treats the file as an always-applied rule.

---

## MCP Server Configuration

Cursor supports MCP servers with a limit of **40 tools** across all configured servers.

### Configuration Locations

=== "Project-level"

    Project MCP servers are configured in `.cursor/mcp.json`:

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

=== "Global"

    Global MCP servers are configured in `~/.cursor/mcp.json`:

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

!!! warning "40-Tool Limit"
    Cursor enforces a maximum of 40 MCP tools across all configured servers. If your servers collectively expose more than 40 tools, Cursor will not load them all. Plan your MCP server selection accordingly.

### Installing MCP via Packages

```bash
devsync install ./my-package --tool cursor
```

DevSync merges MCP entries into the project-level `.cursor/mcp.json` by default.

---

## Unsupported Components

Cursor does not support hooks, commands, skills, or workflows. When installing a package that contains these components, DevSync automatically skips them and reports the count:

```
Installed 3 of 5 components (2 skipped: hooks, commands not supported by Cursor)
```

---

## Detection

DevSync detects Cursor by checking for the Cursor application configuration directory. Verify with:

```bash
devsync tools
```

---

## Package Component Support

| Component | Supported | Install Location |
|-----------|:---------:|-----------------|
| Instructions | Yes | `.cursor/rules/*.mdc` |
| MCP Servers | Yes | `.cursor/mcp.json` |
| Hooks | -- | Not supported |
| Commands | -- | Not supported |
| Skills | -- | Not supported |
| Workflows | -- | Not supported |
| Resources | Yes | Project directory |

---

## Example: Project Setup

```bash
# Install team standards from a Git repository
devsync install https://github.com/acme/standards --tool cursor
```

Result:

```
my-project/
  .cursor/
    mcp.json                    # MCP servers (if package includes them)
    rules/
      code-style.mdc            # Team coding standard
      testing.mdc               # Testing conventions
```
