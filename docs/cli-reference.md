# CLI Reference

Complete command-line interface reference for DevSync.

## Table of Contents

- [Template Commands](#template-commands)
- [MCP Commands](#mcp-commands)
- [Utility Commands](#utility-commands)
- [Global Options](#global-options)

---

## Template Commands

### `aiconfig template install`

Install a template repository.

```bash
aiconfig template install <source> --as <namespace> [options]
```

**Arguments:**
- `<source>` - Git URL or local directory path

**Options:**
- `--as <namespace>` - Namespace for installed templates (required)
- `--scope <scope>` - Installation scope: `project` (default) or `global`
- `--force` - Overwrite existing installation
- `--ref <ref>` - Git branch, tag, or commit (default: main)

**Examples:**
```bash
# Install from GitHub
aiconfig template install https://github.com/company/standards --as company

# Install from local directory
aiconfig template install ./my-templates --as local

# Install specific version
aiconfig template install https://github.com/company/standards --as company --ref v1.2.0

# Install globally
aiconfig template install https://github.com/personal/tools --as personal --scope global
```

### `aiconfig template list`

List installed templates.

```bash
aiconfig template list [namespace] [options]
```

**Options:**
- `--scope <scope>` - Filter by scope: `project` or `global`
- `--json` - Output as JSON

**Examples:**
```bash
# List all templates
aiconfig template list

# List specific namespace
aiconfig template list company

# JSON output
aiconfig template list --json
```

### `aiconfig template update`

Update installed templates to latest version.

```bash
aiconfig template update <namespace> [options]
aiconfig template update --all [options]
```

**Options:**
- `--all` - Update all installed templates
- `--scope <scope>` - Update scope: `project` or `global`

**Examples:**
```bash
# Update specific namespace
aiconfig template update company

# Update all templates
aiconfig template update --all
```

### `aiconfig template uninstall`

Uninstall template repository.

```bash
aiconfig template uninstall <namespace> [options]
```

**Options:**
- `--scope <scope>` - Uninstall scope: `project` or `global`
- `--force` - Skip confirmation

**Examples:**
```bash
# Uninstall namespace
aiconfig template uninstall company

# Uninstall global
aiconfig template uninstall personal --scope global
```

### `aiconfig template init`

Create a new template repository (creates directory in current location).

```bash
aiconfig template init <name> [options]
```

**Arguments:**
- `<name>` - Directory name for new repository (created in current directory)

**Options:**
- `--minimal` - Create minimal structure (no examples)

**Examples:**
```bash
# Navigate to where you want to create the template
cd ~/projects  # or your preferred location

# Create with examples (creates 'my-standards' directory here)
aiconfig template init my-standards

# Create minimal structure
aiconfig template init my-standards --minimal
```

### `aiconfig template validate`

Validate a template repository.

```bash
aiconfig template validate <path>
```

**Arguments:**
- `<path>` - Path to template repository

**Examples:**
```bash
# Validate current directory
aiconfig template validate .

# Validate specific path
aiconfig template validate ./my-templates
```

---

## MCP Commands

### `aiconfig mcp install`

Install MCP server configurations.

```bash
aiconfig mcp install <source> --as <namespace> [options]
```

**Arguments:**
- `<source>` - Git URL or local directory path

**Options:**
- `--as <namespace>` - Namespace for MCP servers (required)
- `--scope <scope>` - Installation scope: `project` (default) or `global`
- `--force` - Overwrite existing installation
- `--ref <ref>` - Git branch, tag, or commit

**Examples:**
```bash
# Install from GitHub
aiconfig mcp install https://github.com/company/mcp-servers --as backend

# Install from local directory
aiconfig mcp install ./my-mcp-servers --as local

# Install globally
aiconfig mcp install https://github.com/personal/mcp --as personal --scope global
```

### `aiconfig mcp configure`

Configure credentials for MCP servers.

```bash
aiconfig mcp configure <server-ref> [options]
```

**Arguments:**
- `<server-ref>` - Format: `namespace` or `namespace.server`

**Options:**
- `--scope <scope>` - Configuration scope: `project` (default) or `global`
- `--non-interactive` - Read credentials from environment
- `--show-current` - Show current credentials (masked)
- `--json` - Output as JSON

**Examples:**
```bash
# Configure all servers in namespace (interactive)
aiconfig mcp configure backend

# Configure specific server
aiconfig mcp configure backend.github

# Non-interactive (from environment)
export GITHUB_TOKEN=ghp_xxxxx
aiconfig mcp configure backend --non-interactive

# Show current credentials
aiconfig mcp configure backend --show-current
```

### `aiconfig mcp sync`

Sync MCP servers to AI tool configuration files.

```bash
aiconfig mcp sync [options]
```

**Options:**
- `--tool <tool>` - Target tool: `claude`, `cursor`, `windsurf`, or `all` (default: `all`)
- `--scope <scope>` - Load from scope: `project` (default) or `global`
- `--dry-run` - Show what would be synced without making changes
- `--no-backup` - Skip creating backup files
- `--json` - Output as JSON

**Examples:**
```bash
# Sync to all detected tools
aiconfig mcp sync --tool all

# Sync to Claude Desktop only
aiconfig mcp sync --tool claude

# Dry run (no changes)
aiconfig mcp sync --tool all --dry-run

# Skip backups
aiconfig mcp sync --tool claude --no-backup
```

### `aiconfig mcp list`

List installed MCP servers.

```bash
aiconfig mcp list [namespace] [options]
```

**Options:**
- `--scope <scope>` - Filter by scope: `project` or `global`
- `--sets` - Show MCP sets
- `--json` - Output as JSON

**Examples:**
```bash
# List all servers
aiconfig mcp list

# List specific namespace
aiconfig mcp list backend

# Show sets
aiconfig mcp list --sets
```

### `aiconfig mcp update`

Update MCP server configurations.

```bash
aiconfig mcp update <namespace> [options]
aiconfig mcp update --all [options]
```

**Options:**
- `--all` - Update all MCP templates
- `--scope <scope>` - Update scope: `project` or `global`

**Examples:**
```bash
# Update specific namespace
aiconfig mcp update backend

# Update all MCP templates
aiconfig mcp update --all
```

### `aiconfig mcp uninstall`

Uninstall MCP template.

```bash
aiconfig mcp uninstall <namespace> [options]
```

**Options:**
- `--scope <scope>` - Uninstall scope: `project` or `global`

**Examples:**
```bash
# Uninstall namespace
aiconfig mcp uninstall backend

# Uninstall global
aiconfig mcp uninstall company --scope global
```

---

## Utility Commands

### `aiconfig tools`

Show detected AI coding tools.

```bash
aiconfig tools
```

Displays which AI tools are installed (Claude Code, Claude Desktop, Cursor, Copilot, Windsurf) and their configuration directories.

**Example output:**
```
AI Coding Tools
Tool               Installed    Config Directory
Claude Code        ✓            ~/.claude
Claude Desktop     ✓            ~/Library/Application Support/Claude
Cursor             ✓            ~/Library/Application Support/Cursor
GitHub Copilot     ✗            Not found
Windsurf           ✓            ~/Library/Application Support/Windsurf
```

### `aiconfig --version`

Show DevSync version.

```bash
aiconfig --version
```

### `aiconfig --help`

Show help information.

```bash
# General help
aiconfig --help

# Command-specific help
aiconfig template --help
aiconfig template install --help
aiconfig mcp --help
aiconfig mcp configure --help
```

---

## Global Options

These options can be used with any command:

- `--help` - Show help for command
- `--version` - Show version

---

## Environment Variables

### LOGLEVEL

Control logging verbosity:

```bash
# Debug mode
export LOGLEVEL=DEBUG
aiconfig mcp sync --tool all

# Quiet mode
export LOGLEVEL=ERROR
aiconfig template install <repo> --as demo
```

**Levels:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Command-line syntax error |

---

## Configuration Files

DevSync uses these configuration files:

| File | Location | Purpose |
|------|----------|---------|
| `template-installations.json` | `.ai-config-kit/` | Tracks installed templates |
| `mcp-installations.json` | `.ai-config-kit/` | Tracks installed MCP servers |
| `.env` | `.ai-config-kit/` | Project-scoped credentials (gitignored) |
| `.env` | `~/.ai-config-kit/global/` | Global-scoped credentials (gitignored) |

---

**[← Back to Main Documentation](../README.md)**
