# CLI Reference

**Complete command-line interface reference for package management**

This document provides detailed reference for all package-related commands, options, and flags.

## Table of Contents

- [Overview](#overview)
- [Global Options](#global-options)
- [Commands](#commands)
  - [package install](#package-install)
  - [package list](#package-list)
  - [package uninstall](#package-uninstall)
- [Common Workflows](#common-workflows)
- [Exit Codes](#exit-codes)
- [Environment Variables](#environment-variables)

## Overview

All package commands are accessed through the `aiconfig package` subcommand:

```bash
aiconfig package <command> [options]
```

**Available commands:**
- `install` - Install a package to a project
- `list` - List installed packages
- `uninstall` - Remove a package from a project

## Global Options

These options work with all commands:

### `--help, -h`

Show help message and exit.

```bash
aiconfig package --help
aiconfig package install --help
```

### `--version`

Show DevSync version and exit.

```bash
aiconfig --version
# Output: ai-config-kit, version 0.3.0
```

---

## Commands

## package install

Install a configuration package to a project.

### Synopsis

```bash
aiconfig package install <package-path> --ide <ide-name> [options]
```

### Arguments

#### `<package-path>`

**Type**: Path (string)

**Required**: Yes

**Description**: Path to package directory (containing `ai-config-kit-package.yaml`)

**Accepts**:
- Relative path: `./my-package`
- Absolute path: `/Users/you/packages/my-package`
- Parent directory: `../shared-packages/python`

**Examples**:
```bash
aiconfig package install ./python-dev
aiconfig package install /Users/you/packages/django-setup
aiconfig package install ../shared/python-package
```

### Options

#### `--ide, -i`

**Type**: String (choice)

**Required**: Yes

**Description**: Target IDE for installation

**Choices**: `claude`, `cursor`, `windsurf`, `copilot`

**Default**: None (must be specified)

**Examples**:
```bash
--ide claude
--ide cursor
-i windsurf
```

**IDE details**:
- `claude` - Claude Code (all components supported)
- `cursor` - Cursor (instructions + resources only)
- `windsurf` - Windsurf (instructions + resources only)
- `copilot` - GitHub Copilot (instructions only)

---

#### `--project, -p`

**Type**: Path (string)

**Required**: No

**Description**: Project root directory (defaults to current directory)

**Default**: Current working directory

**Behavior**: DevSync searches for project markers (`.git/`, `pyproject.toml`, `package.json`, etc.)

**Examples**:
```bash
# Use current directory (default)
aiconfig package install ./pkg --ide claude

# Specify project explicitly
aiconfig package install ./pkg --ide claude --project ~/my-app

# Install to different project
aiconfig package install ./pkg --ide claude -p /path/to/project
```

---

#### `--conflict, -c`

**Type**: String (choice)

**Required**: No

**Description**: How to handle existing files

**Choices**: `skip`, `overwrite`, `rename`

**Default**: `skip`

**Behavior**:
- `skip` - Keep existing files unchanged, skip conflicting components
- `overwrite` - Replace existing files with package versions
- `rename` - Create numbered copies (e.g., `file-1.md`, `file-2.md`)

**Examples**:
```bash
# Default: skip existing files
aiconfig package install ./pkg --ide claude

# Overwrite existing files
aiconfig package install ./pkg --ide claude --conflict overwrite

# Create numbered copies
aiconfig package install ./pkg --ide claude -c rename
```

**Detailed behavior**:

| Strategy   | Existing File | Package File | Result |
|------------|---------------|--------------|--------|
| `skip`     | Preserved     | Not installed | Original unchanged |
| `overwrite`| Replaced      | Installed | Package version replaces original |
| `rename`   | Preserved     | Installed with `-N` suffix | Both versions exist |

---

#### `--force, -f`

**Type**: Boolean flag

**Required**: No

**Description**: Force reinstallation even if already installed

**Default**: False

**Behavior**: Skips the "already installed" check and proceeds with installation

**Examples**:
```bash
# Normal install (checks if already installed)
aiconfig package install ./pkg --ide claude

# Force reinstall
aiconfig package install ./pkg --ide claude --force
aiconfig package install ./pkg --ide claude -f
```

**Use cases**:
- Revert local modifications to package files
- Fix corrupted installation
- Update to newer package version
- Reset to package defaults

---

#### `--quiet, -q`

**Type**: Boolean flag

**Required**: No

**Description**: Minimal output (errors only)

**Default**: False

**Behavior**: Suppresses verbose installation progress, shows only final result

**Examples**:
```bash
# Normal output (verbose)
aiconfig package install ./pkg --ide claude

# Quiet output (minimal)
aiconfig package install ./pkg --ide claude --quiet
aiconfig package install ./pkg --ide claude -q
```

**Output comparison**:

Normal:
```
Installing package from ./pkg...
Target IDE: claude
Project root: /Users/you/project
Installing components...
✓ Successfully installed pkg v1.0.0
  Installed: 5
  Skipped: 0
  Failed: 0
```

Quiet:
```
✓ Successfully installed pkg v1.0.0
```

---

#### `--json`

**Type**: Boolean flag

**Required**: No

**Description**: Output result as JSON (for scripting)

**Default**: False

**Behavior**: Outputs structured JSON instead of human-readable text

**Examples**:
```bash
# Normal output
aiconfig package install ./pkg --ide claude

# JSON output
aiconfig package install ./pkg --ide claude --json
```

**JSON schema**:
```json
{
  "success": true,
  "status": "complete",
  "package_name": "pkg",
  "version": "1.0.0",
  "installed_count": 5,
  "skipped_count": 0,
  "failed_count": 0,
  "components_installed": {
    "instruction": 2,
    "mcp_server": 1,
    "hook": 1,
    "command": 1
  },
  "is_reinstall": false,
  "error_message": null
}
```

**Status values**:
- `"complete"` - All components installed successfully
- `"partial"` - Some components installed, some skipped/failed
- `"failed"` - Installation failed
- `"pending_credentials"` - Requires credential configuration

---

### Examples

**Basic installation**:
```bash
aiconfig package install ./python-dev --ide claude
```

**Explicit project**:
```bash
aiconfig package install ./python-dev --ide claude --project ~/my-app
```

**Overwrite existing files**:
```bash
aiconfig package install ./python-dev --ide claude --conflict overwrite
```

**Force reinstall**:
```bash
aiconfig package install ./python-dev --ide claude --force
```

**Multiple options**:
```bash
aiconfig package install ./python-dev \
  --ide claude \
  --project ~/my-app \
  --conflict overwrite \
  --force \
  --quiet
```

**Scripting with JSON**:
```bash
result=$(aiconfig package install ./pkg --ide claude --json)
echo $result | jq '.success'
# Output: true
```

---

## package list

List installed packages in a project.

### Synopsis

```bash
aiconfig package list [options]
```

### Arguments

None

### Options

#### `--project, -p`

**Type**: Path (string)

**Required**: No

**Description**: Project to list packages from

**Default**: Current working directory

**Examples**:
```bash
# List in current project
aiconfig package list

# List in specific project
aiconfig package list --project ~/my-app
aiconfig package list -p /path/to/project
```

---

#### `--json`

**Type**: Boolean flag

**Required**: No

**Description**: Output as JSON array

**Default**: False

**Examples**:
```bash
# Table output (default)
aiconfig package list

# JSON output
aiconfig package list --json
```

**JSON schema**:
```json
[
  {
    "name": "python-dev-setup",
    "namespace": "acme/python",
    "version": "1.0.0",
    "status": "complete",
    "scope": "project",
    "installed_at": "2025-01-14T10:30:00",
    "updated_at": "2025-01-14T10:30:00",
    "component_count": 5
  }
]
```

---

### Output Format

**Table format** (default):
```
Installed packages in /Users/you/project:

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Package            ┃ Version ┃ Status   ┃ Components ┃ Installed      ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ python-dev-setup   │ 1.0.0   │ ✓ complete│         5 │ 2025-01-14 10:30│
│ django-toolkit     │ 2.1.0   │ ⚠ partial│         3 │ 2025-01-14 11:15│
└────────────────────┴─────────┴──────────┴────────────┴────────────────┘

Total: 2 package(s)
```

**Status indicators**:
- `✓ complete` - All components installed successfully
- `⚠ partial` - Some components skipped (IDE filtering or conflicts)
- `✗ failed` - Installation failed
- `⏸ pending_credentials` - Requires credential setup

---

### Examples

**List in current project**:
```bash
cd ~/my-project
aiconfig package list
```

**List in specific project**:
```bash
aiconfig package list --project ~/other-project
```

**JSON for scripting**:
```bash
packages=$(aiconfig package list --json)
echo $packages | jq '.[0].name'
# Output: "python-dev-setup"
```

**Count packages**:
```bash
aiconfig package list --json | jq 'length'
# Output: 2
```

---

## package uninstall

Remove a package from a project.

### Synopsis

```bash
aiconfig package uninstall <package-name> [options]
```

### Arguments

#### `<package-name>`

**Type**: String

**Required**: Yes

**Description**: Name of package to uninstall (from manifest `name` field)

**Examples**:
```bash
aiconfig package uninstall python-dev-setup
aiconfig package uninstall django-toolkit
```

### Options

#### `--project, -p`

**Type**: Path (string)

**Required**: No

**Description**: Project to uninstall from

**Default**: Current working directory

**Examples**:
```bash
# Uninstall from current project
aiconfig package uninstall python-dev

# Uninstall from specific project
aiconfig package uninstall python-dev --project ~/my-app
aiconfig package uninstall python-dev -p /path/to/project
```

---

#### `--yes, -y`

**Type**: Boolean flag

**Required**: No

**Description**: Skip confirmation prompt (auto-confirm)

**Default**: False (prompts for confirmation)

**Examples**:
```bash
# Interactive (prompts for confirmation)
aiconfig package uninstall python-dev

# Auto-confirm (no prompt)
aiconfig package uninstall python-dev --yes
aiconfig package uninstall python-dev -y
```

---

#### `--json`

**Type**: Boolean flag

**Required**: No

**Description**: Output result as JSON

**Default**: False

**Examples**:
```bash
# Normal output
aiconfig package uninstall python-dev --yes

# JSON output
aiconfig package uninstall python-dev --yes --json
```

**JSON schema**:
```json
{
  "success": true,
  "package_name": "python-dev-setup",
  "files_removed": 5,
  "error_message": null
}
```

---

### Behavior

**Interactive mode** (default):
```bash
aiconfig package uninstall python-dev-setup

# Prompts:
Package to uninstall:
  Name: python-dev-setup
  Version: 1.0.0
  Components: 5

Are you sure you want to uninstall this package? [y/N]: y

# Then removes files:
  Removed: .claude/rules/code-quality.md
  Removed: .claude/rules/testing-strategy.md
  Removed: .claude/mcp/filesystem.json
  Removed: .claude/hooks/pre-commit.sh
  Removed: .claude/commands/test.sh

✓ Uninstalled python-dev-setup v1.0.0
  Removed 5 file(s)
```

**Auto-confirm mode** (`--yes`):
```bash
aiconfig package uninstall python-dev-setup --yes

# No prompt, immediate removal:
✓ Uninstalled python-dev-setup v1.0.0
  Removed 5 file(s)
```

---

### Examples

**Interactive uninstall**:
```bash
aiconfig package uninstall python-dev-setup
# Prompts for confirmation
```

**Auto-confirm**:
```bash
aiconfig package uninstall python-dev-setup --yes
```

**From specific project**:
```bash
aiconfig package uninstall python-dev --project ~/other-project --yes
```

**JSON output for scripting**:
```bash
result=$(aiconfig package uninstall python-dev --yes --json)
echo $result | jq '.success'
# Output: true
```

---

## Common Workflows

### Install and Verify

```bash
# 1. Install package
aiconfig package install ./python-dev --ide claude

# 2. Verify installation
aiconfig package list

# 3. Check installed files
ls .claude/rules/
```

### Update Package

```bash
# 1. Reinstall with overwrite to get latest version
aiconfig package install ./python-dev --ide claude --conflict overwrite --force

# 2. Verify version updated
aiconfig package list
```

### Clean Install

```bash
# 1. Remove old version
aiconfig package uninstall python-dev-setup --yes

# 2. Fresh install
aiconfig package install ./python-dev --ide claude
```

### Install to Multiple Projects

```bash
# Install to project 1
aiconfig package install ./python-dev --ide claude --project ~/project1

# Install to project 2
aiconfig package install ./python-dev --ide claude --project ~/project2

# Verify both installations
aiconfig package list --project ~/project1
aiconfig package list --project ~/project2
```

### Scripting: Install if Not Exists

```bash
#!/usr/bin/env bash
# Install package only if not already installed

PROJECT="~/my-project"
PACKAGE="./python-dev"

# Check if already installed
if aiconfig package list --project "$PROJECT" --json | jq -e '.[] | select(.name == "python-dev")' > /dev/null; then
    echo "Package already installed"
else
    echo "Installing package..."
    aiconfig package install "$PACKAGE" --ide claude --project "$PROJECT"
fi
```

### Scripting: Batch Uninstall

```bash
#!/usr/bin/env bash
# Uninstall all packages from project

PROJECT="~/my-project"

# Get all package names
packages=$(aiconfig package list --project "$PROJECT" --json | jq -r '.[].name')

# Uninstall each
for pkg in $packages; do
    echo "Uninstalling $pkg..."
    aiconfig package uninstall "$pkg" --project "$PROJECT" --yes
done
```

---

## Exit Codes

DevSync commands use standard exit codes:

| Code | Meaning | When Used |
|------|---------|-----------|
| 0 | Success | Command completed successfully |
| 1 | General error | Invalid arguments, file not found, etc. |
| 2 | Installation failed | Package installation encountered errors |
| 3 | Validation error | Invalid manifest or package structure |
| 4 | Package not found | Specified package not installed |

**Usage in scripts**:
```bash
# Check exit code
if aiconfig package install ./pkg --ide claude; then
    echo "Installation successful"
else
    echo "Installation failed with code: $?"
    exit 1
fi
```

---

## Environment Variables

### `LOGLEVEL`

**Description**: Control logging verbosity

**Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

**Default**: `INFO`

**Usage**:
```bash
# Debug logging
LOGLEVEL=DEBUG aiconfig package install ./pkg --ide claude

# Error logging only
LOGLEVEL=ERROR aiconfig package install ./pkg --ide claude
```

### `NO_COLOR`

**Description**: Disable colored output

**Values**: Any value (presence detected)

**Default**: Not set (colors enabled)

**Usage**:
```bash
# Disable colors
NO_COLOR=1 aiconfig package list

# Enable colors (default)
aiconfig package list
```

### `AICONFIG_PROJECT_ROOT`

**Description**: Override project root detection

**Values**: Absolute path to project

**Default**: Auto-detected from current directory

**Usage**:
```bash
# Override project root
AICONFIG_PROJECT_ROOT=~/my-app aiconfig package install ./pkg --ide claude
```

---

## Related Documentation

- **[Getting Started](getting-started.md)** - Quick start guide
- **[Installation Guide](installation.md)** - Detailed installation options
- **[Creating Packages](creating-packages.md)** - Build your own packages
- **[Manifest Reference](manifest-reference.md)** - Package manifest schema

---

**Need help?** Run `aiconfig package --help` or check the [Troubleshooting Guide](troubleshooting.md).
