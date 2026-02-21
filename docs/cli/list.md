# devsync list

Show installed packages in the current project.

## Usage

```
$ devsync list [OPTIONS]
```

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--tool` | `-t` | Filter by AI tool | -- |
| `--json` | -- | Output as JSON | `False` |

## Examples

### List all installed packages

```bash
$ devsync list
```

```
Installed packages in /home/user/my-project:

  team-standards     v1.0.0    4 practices, 1 MCP server    Claude Code, Cursor
  security-rules     v2.1.0    3 practices                  Claude Code

Total: 2 package(s)
```

### Filter by tool

```bash
$ devsync list --tool claude
```

Shows only packages installed to Claude Code.

### JSON output

```bash
$ devsync list --json
```

```json
[
  {
    "name": "team-standards",
    "version": "1.0.0",
    "tools": ["claude", "cursor"],
    "components": {
      "practices": 4,
      "mcp_servers": 1
    }
  }
]
```

## Installation Tracking

Installed packages are tracked in `.devsync/packages.json` at the project root. This file records package names, versions, installed components, and timestamps. DevSync uses this to manage installations and detect conflicts.

!!! tip
    Use `devsync list --json` for scripting and CI/CD integration.
