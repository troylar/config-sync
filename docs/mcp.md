# MCP Server Management

Complete guide to managing Model Context Protocol (MCP) servers with DevSync.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Concepts](#concepts)
- [Installation](#installation)
- [Configuration](#configuration)
- [Syncing](#syncing)
- [Managing Servers](#managing-servers)
- [Template Repository Format](#template-repository-format)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

---

## Overview

MCP (Model Context Protocol) servers extend AI coding assistants with additional capabilities like database access, API integrations, and file system operations. DevSync makes it easy to:

- **Distribute** MCP server configurations across your team via Git
- **Configure** credentials securely without committing secrets
- **Sync** to multiple AI tools (Claude Desktop, Cursor, Windsurf) with one command
- **Update** server configurations as they evolve

### What Problem Does This Solve?

**Without DevSync:**
- Everyone manually edits `claude_desktop_config.json`
- Credentials accidentally committed to Git
- Configuration drift across team members
- Difficult to update when servers change

**With DevSync:**
```bash
# Install MCP servers (shared via Git)
aiconfig mcp install https://github.com/company/mcp-servers --as backend

# Configure credentials (stored locally in gitignored .env)
aiconfig mcp configure backend

# Sync to AI tools (one command, all tools)
aiconfig mcp sync --tool all
```

---

## Quick Start

### 1. Install MCP Server Configurations

```bash
# Install from a Git repository
aiconfig mcp install https://github.com/company/mcp-servers --as backend

# Or install from a local directory
aiconfig mcp install ./my-mcp-servers --as backend
```

This downloads the MCP server definitions to your library (`~/.ai-config-kit/library/`).

### 2. Configure Credentials

```bash
# Configure interactively (prompts for each credential)
aiconfig mcp configure backend

# Or configure specific server
aiconfig mcp configure backend.github
```

Credentials are stored in `.ai-config-kit/.env` (automatically gitignored).

### 3. Sync to AI Tools

```bash
# Sync to all detected AI tools
aiconfig mcp sync --tool all

# Or sync to specific tool
aiconfig mcp sync --tool claude
```

This writes the MCP configuration to your AI tool's config file (e.g., `claude_desktop_config.json`).

### 4. Verify

Check your AI tool's MCP configuration:

**Claude Desktop:**
```bash
# macOS
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
cat ~/.config/Claude/claude_desktop_config.json

# Windows
type %APPDATA%\Claude\claude_desktop_config.json
```

You should see your MCP servers with resolved environment variables.

---

## Concepts

### MCP Templates

An **MCP template** is a Git repository containing `templatekit.yaml` with MCP server definitions:

```yaml
name: Backend MCP Servers
version: 1.0.0
description: MCP servers for backend development

mcp_servers:
  - name: github
    command: uvx
    args: [mcp-server-github]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: null  # null = user must configure

  - name: postgres
    command: python
    args: [-m, mcp_server_postgres]
    env:
      DATABASE_URL: null

  - name: filesystem
    command: npx
    args: [-y, "@modelcontextprotocol/server-filesystem", "/workspace"]
    env: {}  # No credentials required
```

### Namespaces

Each MCP template gets a **namespace** to prevent conflicts:

```bash
# Install with namespace "backend"
aiconfig mcp install <repo> --as backend

# Servers become: backend.github, backend.postgres, backend.filesystem
```

This allows you to install multiple MCP template repositories without conflicts.

### Scopes

MCP templates can be installed at two scopes:

| Scope | Library Location | Credentials Location | Use Case |
|-------|-----------------|---------------------|----------|
| **Project** (default) | `~/.ai-config-kit/library/` | `.ai-config-kit/.env` | Project-specific servers |
| **Global** | `~/.ai-config-kit/library/global/` | `~/.ai-config-kit/global/.env` | Personal or company-wide servers |

**Example:**
```bash
# Project scope (default)
cd ~/projects/backend-api
aiconfig mcp install <repo> --as backend
# Credentials in: ~/projects/backend-api/.ai-config-kit/.env

# Global scope
aiconfig mcp install <repo> --as personal --scope global
# Credentials in: ~/.ai-config-kit/global/.env
```

When syncing, DevSync merges global and project credentials (project takes precedence).

---

## Installation

### Install from Git Repository

```bash
# Install from GitHub
aiconfig mcp install https://github.com/company/mcp-servers --as backend

# Install from specific branch
aiconfig mcp install https://github.com/company/mcp-servers --as backend --ref develop

# Install from specific tag/version
aiconfig mcp install https://github.com/company/mcp-servers --as backend --ref v1.2.0
```

### Install from Local Directory

```bash
# Install from local path (useful for testing)
aiconfig mcp install ./my-mcp-servers --as backend

# Absolute path
aiconfig mcp install /Users/troy/projects/mcp-servers --as backend
```

### Install with Scope

```bash
# Project scope (default)
aiconfig mcp install <repo> --as backend

# Global scope (available in all projects)
aiconfig mcp install <repo> --as company --scope global
```

### Force Reinstall

```bash
# Overwrite existing installation
aiconfig mcp install <repo> --as backend --force
```

### List Installed Templates

```bash
# List all installed MCP templates
aiconfig mcp list

# List with JSON output
aiconfig mcp list --json
```

---

## Configuration

### Interactive Configuration

The recommended way to configure credentials:

```bash
# Configure all servers in a namespace
aiconfig mcp configure backend

# Configure specific server
aiconfig mcp configure backend.github

# Show current credentials (masked)
aiconfig mcp configure backend.github --show-current
```

**Interactive prompts:**
```
Configuring MCP server: backend.github
Required environment variables: 1

Enter value for GITHUB_PERSONAL_ACCESS_TOKEN:
  GITHUB_PERSONAL_ACCESS_TOKEN: ****
✓ Set GITHUB_PERSONAL_ACCESS_TOKEN

✓ Credential configuration complete!
  Configured: 1 server(s)

Credentials saved to: /Users/troy/projects/backend-api/.ai-config-kit/.env
(This file is automatically gitignored)

Next step:
  Sync to AI tools: aiconfig mcp sync --tool all
```

### Non-Interactive Configuration

For CI/CD pipelines or automation:

```bash
# Set environment variables
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxx
export DATABASE_URL=postgresql://localhost/mydb

# Configure from environment
aiconfig mcp configure backend --non-interactive
```

### Show Current Credentials

```bash
# Show current credentials (masked)
aiconfig mcp configure backend.github --show-current

# Output:
# Current Credentials (project scope)
# Server                    Variable                         Value          Status
# backend.github            GITHUB_PERSONAL_ACCESS_TOKEN     ****abc123     ✓
```

### Scope-Specific Configuration

```bash
# Configure for project scope (default)
aiconfig mcp configure backend

# Configure for global scope
aiconfig mcp configure company --scope global
```

### JSON Output

```bash
# Machine-readable output
aiconfig mcp configure backend --json

# Output:
# {
#   "success": true,
#   "namespace": "backend",
#   "configured": 2,
#   "skipped": 1,
#   "total": 3,
#   "scope": "project"
# }
```

---

## Syncing

### Sync to AI Tools

```bash
# Sync to all detected AI tools
aiconfig mcp sync --tool all

# Sync to specific tool
aiconfig mcp sync --tool claude
aiconfig mcp sync --tool cursor
aiconfig mcp sync --tool windsurf
```

**Output:**
```
Syncing MCP servers to AI tools
Scope: project
Tools: all

✓ Synced to 2 tool(s):
  • claude
  • cursor

Server Summary:
  Synced: 3 server(s)
  Skipped: 1 server(s)

Skipped Servers:
Server              Reason
backend.postgres    Missing credentials: DATABASE_URL

Tip: Run 'aiconfig mcp configure backend' to configure missing credentials
```

### Dry Run

Preview what would be synced without making changes:

```bash
aiconfig mcp sync --tool all --dry-run
```

### Scope Control

```bash
# Sync project-scoped servers only (default)
aiconfig mcp sync --tool all --scope project

# Sync global-scoped servers only
aiconfig mcp sync --tool all --scope global
```

### Backup Control

By default, DevSync creates backups before modifying config files:

```bash
# Create backup (default)
aiconfig mcp sync --tool all

# Skip backup creation
aiconfig mcp sync --tool all --no-backup
```

Backup files are saved as:
- `claude_desktop_config.json.bak`
- `mcp_config.json.bak`

### JSON Output

```bash
# Machine-readable output
aiconfig mcp sync --tool all --json

# Output:
# {
#   "success": true,
#   "synced_tools": ["claude", "cursor"],
#   "skipped_tools": [],
#   "synced_servers": ["backend.github", "backend.filesystem"],
#   "skipped_servers": [
#     {"name": "backend.postgres", "reason": "Missing credentials: DATABASE_URL"}
#   ]
# }
```

---

## Managing Servers

### List Servers

```bash
# List all installed MCP servers
aiconfig mcp list

# Filter by namespace
aiconfig mcp list backend

# Show only sets
aiconfig mcp list --sets

# JSON output
aiconfig mcp list --json
```

### Update Servers

```bash
# Update specific namespace
aiconfig mcp update backend

# Update all MCP templates
aiconfig mcp update --all
```

Updates pull the latest changes from the source repository while preserving your credentials.

### Uninstall Servers

```bash
# Uninstall MCP template
aiconfig mcp uninstall backend

# Uninstall with scope
aiconfig mcp uninstall company --scope global
```

This removes the template from your library but **does not** remove credentials or synced configurations from AI tools.

### Validate Configuration

```bash
# Check if all credentials are configured
aiconfig mcp validate

# Check specific namespace
aiconfig mcp validate backend
```

---

## Template Repository Format

### Minimal ai-config-kit.yaml

```yaml
name: My MCP Servers
version: 1.0.0
description: MCP servers for development

mcp_servers:
  - name: github
    command: uvx
    args: [mcp-server-github]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: null
```

### Complete Example

```yaml
name: Backend Development Servers
version: 2.1.0
description: MCP servers for backend team
author: Backend Team <backend@example.com>

# Define individual MCP servers
mcp_servers:
  # GitHub integration
  - name: github
    command: uvx
    args: [mcp-server-github]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: null  # Required: user must configure
    tags: [github, api, scm]

  # PostgreSQL database access
  - name: postgres
    command: python
    args: [-m, mcp_server_postgres]
    env:
      DATABASE_URL: null  # Required
      DATABASE_POOL_SIZE: "10"  # Optional: has default value
    tags: [database, postgres]

  # File system access
  - name: filesystem
    command: npx
    args: [-y, "@modelcontextprotocol/server-filesystem", "/workspace"]
    env: {}  # No credentials needed
    tags: [filesystem, local]

  # Slack integration
  - name: slack
    command: python
    args: [-m, mcp_server_slack]
    env:
      SLACK_BOT_TOKEN: null
      SLACK_SIGNING_SECRET: null
    tags: [slack, communication]

# Define sets for different workflows
mcp_sets:
  - name: backend-dev
    description: Servers for backend development
    servers: [github, postgres, filesystem]
    tags: [backend, development]

  - name: full-stack
    description: All servers for full-stack development
    servers: [github, postgres, filesystem, slack]
    tags: [fullstack]
```

### Field Reference

**mcp_servers:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Server identifier (alphanumeric, underscores, hyphens) |
| `command` | string | Yes | Command to launch server (e.g., `uvx`, `npx`, `python`) |
| `args` | list[string] | Yes | Command arguments |
| `env` | dict | No | Environment variables (null = required, value = default) |
| `tags` | list[string] | No | Tags for organization |

**mcp_sets:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Set identifier |
| `description` | string | No | Human-readable description |
| `servers` | list[string] | Yes | List of server names to include |
| `tags` | list[string] | No | Tags for organization |

### Environment Variables

**Required credentials** (user must configure):
```yaml
env:
  GITHUB_TOKEN: null
  API_KEY: null
```

**Optional credentials** (has default):
```yaml
env:
  PORT: "8080"
  TIMEOUT: "30"
```

**No credentials**:
```yaml
env: {}
```

---

## Security

### Credential Storage

Credentials are stored in `.ai-config-kit/.env` files which are **automatically gitignored**:

```bash
# Project credentials
<project>/.ai-config-kit/.env

# Global credentials
~/.ai-config-kit/global/.env
```

**File format:**
```
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxx
DATABASE_URL=postgresql://user:pass@localhost/db
SLACK_BOT_TOKEN=xoxb-xxxxx
```

### Automatic Gitignore

DevSync automatically creates `.gitignore` files to prevent committing secrets:

```
.ai-config-kit/.env
```

**Verify it's gitignored:**
```bash
git status
# Should NOT show .ai-config-kit/.env
```

### Best Practices

✅ **DO:**
- Store credentials in `.ai-config-kit/.env`
- Use different credentials for development/production
- Rotate credentials regularly
- Use environment-specific namespaces (dev, staging, prod)

❌ **DON'T:**
- Commit `.ai-config-kit/.env` to Git
- Put credentials in `templatekit.yaml`
- Share credentials in chat/email
- Use production credentials for development

### Credential Scope Precedence

When syncing, credentials are merged with this precedence:

1. **Project credentials** (`.ai-config-kit/.env`)
2. **Global credentials** (`~/.ai-config-kit/global/.env`)

Project credentials override global credentials for the same variable name.

---

## Troubleshooting

### Common Issues

#### "Template not found"

```bash
aiconfig mcp configure backend
# Error: Template 'backend' not found in project scope
```

**Solution:** Install the template first:
```bash
aiconfig mcp install <repo> --as backend
```

#### "Missing credentials"

```bash
aiconfig mcp sync --tool all
# Skipped Servers:
# backend.github    Missing credentials: GITHUB_PERSONAL_ACCESS_TOKEN
```

**Solution:** Configure the missing credentials:
```bash
aiconfig mcp configure backend.github
```

#### "No AI tools detected"

```bash
aiconfig mcp sync --tool all
# Warning: No AI tools detected
```

**Solution:** Check which tools are installed:
```bash
aiconfig tools
```

Install a supported AI tool (Claude Desktop, Cursor, or Windsurf).

#### "Command not found: uvx"

```bash
# In claude_desktop_config.json:
# "command": "uvx" → Error: command not found
```

**Solution:** Install `uv` (Python package installer):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```

#### "Permission denied" when syncing

**Solution:** Check file permissions:
```bash
# macOS
chmod 644 ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
chmod 644 ~/.config/Claude/claude_desktop_config.json
```

### Debugging

#### Enable Debug Logging

```bash
export LOGLEVEL=DEBUG
aiconfig mcp sync --tool all
```

#### Check Config Files

```bash
# Claude Desktop config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .

# Cursor config
cat ~/Library/Application\ Support/Cursor/User/globalStorage/mcp_config.json | jq .
```

#### Verify Environment Variables

```bash
# Check your .env file
cat .ai-config-kit/.env

# Verify variables are set (after sync)
# Check Claude Desktop logs for environment variable resolution
```

#### Test MCP Server Manually

```bash
# Test server command directly
uvx mcp-server-github

# Or with environment variables
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxx uvx mcp-server-github
```

### Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/troylar/devsync/issues)
- **Discussions**: [Ask questions](https://github.com/troylar/devsync/discussions)
- **Documentation**: Check other guides in `docs/`

---

## Examples

### Example 1: GitHub + PostgreSQL Setup

```bash
# 1. Create ai-config-kit.yaml
cat > ai-config-kit.yaml <<EOF
name: Backend Servers
version: 1.0.0

mcp_servers:
  - name: github
    command: uvx
    args: [mcp-server-github]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: null

  - name: postgres
    command: python
    args: [-m, mcp_server_postgres]
    env:
      DATABASE_URL: null
EOF

# 2. Install
aiconfig mcp install . --as backend

# 3. Configure
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxx
export DATABASE_URL=postgresql://localhost/mydb
aiconfig mcp configure backend --non-interactive

# 4. Sync
aiconfig mcp sync --tool claude
```

### Example 2: Team Onboarding

```bash
# New team member setup script
#!/bin/bash

echo "Setting up MCP servers..."

# Install company MCP servers
aiconfig mcp install https://github.com/company/mcp-servers --as company

# Configure credentials
echo "Please configure your credentials:"
aiconfig mcp configure company

# Sync to AI tools
aiconfig mcp sync --tool all

echo "✓ MCP servers configured!"
```

### Example 3: Multiple Environments

```bash
# Development environment
cd ~/projects/my-app-dev
aiconfig mcp install https://github.com/company/mcp-dev --as dev
export DATABASE_URL=postgresql://localhost/dev_db
aiconfig mcp configure dev --non-interactive
aiconfig mcp sync --tool all

# Production environment
cd ~/projects/my-app-prod
aiconfig mcp install https://github.com/company/mcp-prod --as prod
export DATABASE_URL=postgresql://prod-host/prod_db
aiconfig mcp configure prod --non-interactive
aiconfig mcp sync --tool all
```

---

**[← Back to Main Documentation](../README.md)**
