# Windsurf

Windsurf supports multi-file instructions, MCP server configuration, and workflows. It uses a global-only MCP configuration path with a 100-tool limit.

## Overview

| Property | Value |
|----------|-------|
| **Instruction path** | `.windsurf/rules/*.md` |
| **File extension** | `.md` |
| **MCP config (global)** | `~/.codeium/windsurf/mcp_config.json` |
| **MCP config (project)** | Not supported |
| **MCP tool limit** | 100 tools |
| **Workflows directory** | `.windsurf/workflows/` |
| **Project scope** | Yes |
| **Global scope** | Yes |

---

## Instructions

Windsurf reads markdown files from `.windsurf/rules/` in the project root. DevSync installs one `.md` file per instruction:

```
my-project/
  .windsurf/
    rules/
      code-style.md
      testing-standards.md
```

### Installing Instructions

```bash
# Install a package from a local path
devsync install ./my-package --tool windsurf

# Install a package from a Git repository
devsync install https://github.com/acme/standards --tool windsurf
```

### Activation Modes

Windsurf supports four activation modes for rules, controlled via file metadata:

| Mode | Behavior |
|------|----------|
| **Always** | Rule is always included in context |
| **Auto** | Windsurf decides when the rule is relevant |
| **File match** | Rule applies when working with files matching a glob pattern |
| **Manual** | User must explicitly reference the rule |

DevSync installs instructions as-is. If the source instruction includes Windsurf-specific activation metadata, it will be preserved.

---

## MCP Server Configuration

Windsurf uses a **global-only** MCP configuration with a limit of **100 tools**.

```json title="~/.codeium/windsurf/mcp_config.json"
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

!!! info "Global-Only MCP"
    Unlike Cursor and Claude Code, Windsurf does not support project-level MCP configuration. All MCP servers are configured in the global `~/.codeium/windsurf/mcp_config.json` file.

!!! warning "100-Tool Limit"
    Windsurf enforces a maximum of 100 MCP tools across all configured servers. This is more generous than Cursor's 40-tool limit but still requires planning when configuring multiple servers.

### Installing MCP via Packages

```bash
devsync install ./my-package --tool windsurf
```

DevSync merges MCP entries into the global configuration file.

---

## Workflows

Windsurf supports workflows in `.windsurf/workflows/`. Workflows define multi-step automation sequences that Windsurf can execute.

```
my-project/
  .windsurf/
    workflows/
      deploy.md
      code-review.md
```

DevSync can install workflow files as part of a package.

---

## Unsupported Components

Windsurf does not support hooks, commands, or skills. When installing a package that contains these components, DevSync skips them automatically.

---

## Detection

DevSync detects Windsurf by checking for the Windsurf application configuration directory. Verify with:

```bash
devsync tools
```

---

## Package Component Support

| Component | Supported | Install Location |
|-----------|:---------:|-----------------|
| Instructions | Yes | `.windsurf/rules/*.md` |
| MCP Servers | Yes | `~/.codeium/windsurf/mcp_config.json` |
| Hooks | -- | Not supported |
| Commands | -- | Not supported |
| Skills | -- | Not supported |
| Workflows | Yes | `.windsurf/workflows/` |
| Resources | Yes | Project directory |

---

## Example: Project Setup

```bash
# Install team standards from a Git repository
devsync install https://github.com/acme/standards --tool windsurf
```

Result:

```
my-project/
  .windsurf/
    rules/
      code-style.md
      testing.md
    workflows/
      deploy.md                # If package includes workflows
```
