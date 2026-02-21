# GitHub Copilot

GitHub Copilot uses a unique `.instructions.md` file extension for its instruction files and supports MCP server configuration through VS Code's MCP integration with a 128-tool limit.

## Overview

| Property | Value |
|----------|-------|
| **Instruction path** | `.github/instructions/*.instructions.md` |
| **File extension** | `.instructions.md` |
| **MCP config (project)** | `.vscode/mcp.json` |
| **MCP config (global)** | `~/.vscode/mcp.json` |
| **MCP tool limit** | 128 tools |
| **Project scope** | Yes |
| **Global scope** | Yes |

---

## Instructions

GitHub Copilot reads instruction files from `.github/instructions/` in the project root. Files **must** use the `.instructions.md` extension -- plain `.md` files are ignored.

DevSync installs one file per instruction with the correct extension:

```
my-project/
  .github/
    instructions/
      code-style.instructions.md
      testing-standards.instructions.md
```

!!! warning "File Extension Requirement"
    Copilot requires the `.instructions.md` extension for path-specific instruction files. DevSync handles this automatically. If you manually create instruction files, make sure they end with `.instructions.md`, not just `.md`.

### Installing Instructions

```bash
# Install a package from a local path
devsync install ./my-package --tool copilot

# Install a package from a Git repository
devsync install https://github.com/acme/standards --tool copilot
```

### Alternative: copilot-instructions.md

GitHub Copilot also supports a single `.github/copilot-instructions.md` file for project-wide instructions. DevSync uses the multi-file `.github/instructions/` approach instead, which provides better organization and granular control.

### Instruction File Format

Copilot instruction files are plain markdown:

```markdown
# TypeScript Conventions

- Use strict TypeScript configuration
- Prefer interfaces over type aliases for object shapes
- Use branded types for domain identifiers
```

Copilot supports glob-based file matching via VS Code settings, allowing instructions to apply conditionally based on the file being edited.

---

## MCP Server Configuration

GitHub Copilot supports MCP servers through VS Code's built-in MCP integration with a limit of **128 tools**.

### Configuration Locations

=== "Project-level"

    Project MCP servers are configured in `.vscode/mcp.json`:

    ```json
    {
      "servers": {
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

    Global MCP servers are configured in `~/.vscode/mcp.json`:

    ```json
    {
      "servers": {
        "filesystem": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/you/projects"]
        }
      }
    }
    ```

!!! note "128-Tool Limit"
    Copilot supports up to 128 MCP tools across all servers. This is the highest limit among the major IDE integrations.

### Installing MCP via Packages

```bash
devsync install ./my-package --tool copilot
```

DevSync merges MCP entries into `.vscode/mcp.json`.

---

## Unsupported Components

GitHub Copilot does not support hooks, commands, skills, workflows, or resources through DevSync. Unsupported components are skipped during package installation.

---

## Detection

DevSync detects GitHub Copilot by checking for the VS Code configuration directory and the Copilot extension. Verify with:

```bash
devsync tools
```

---

## Package Component Support

| Component | Supported | Install Location |
|-----------|:---------:|-----------------|
| Instructions | Yes | `.github/instructions/*.instructions.md` |
| MCP Servers | Yes | `.vscode/mcp.json` |
| Hooks | -- | Not supported |
| Commands | -- | Not supported |
| Skills | -- | Not supported |
| Workflows | -- | Not supported |
| Resources | -- | Not supported |

---

## Example: Project Setup

```bash
# Install team standards from a Git repository
devsync install https://github.com/acme/standards --tool copilot
```

Result:

```
my-project/
  .github/
    instructions/
      code-style.instructions.md
      testing.instructions.md
  .vscode/
    mcp.json                              # If package includes MCP servers
```
