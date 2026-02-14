# Installing Packages

**Complete guide to installing, managing, and updating configuration packages**

This guide covers everything you need to know about installing packages, from basic installation to advanced conflict resolution strategies.

## Table of Contents

- [Basic Installation](#basic-installation)
- [Installation Options](#installation-options)
- [Conflict Resolution](#conflict-resolution)
- [IDE-Specific Behavior](#ide-specific-behavior)
- [Managing Installed Packages](#managing-installed-packages)
- [Best Practices](#best-practices)

## Basic Installation

### Simple Install

The most basic way to install a package:

```bash
aiconfig package install <package-path> --ide <ide-name>
```

**Example:**

```bash
cd ~/my-project
aiconfig package install ./python-dev-setup --ide claude
```

### From Different Locations

Install from various sources:

```bash
# Local directory (relative path)
aiconfig package install ./my-package --ide claude

# Local directory (absolute path)
aiconfig package install /Users/you/packages/my-package --ide claude

# Parent directory
aiconfig package install ../shared-packages/python-setup --ide cursor
```

### Specifying Project Directory

By default, packages install to the current directory. Override with `--project`:

```bash
# Install to a different project
aiconfig package install ./my-package --ide claude --project ~/other-project

# Install to multiple projects
aiconfig package install ./my-package --ide claude --project ~/project1
aiconfig package install ./my-package --ide claude --project ~/project2
```

## Installation Options

### Full Command Syntax

```bash
aiconfig package install <package-path> \
  --ide <ide-name> \
  [--project <project-path>] \
  [--conflict <strategy>] \
  [--force] \
  [--quiet] \
  [--json]
```

### Option Reference

#### `--ide, -i` (required)

Specify the target IDE:

```bash
--ide claude      # Claude Code
--ide cursor      # Cursor
--ide windsurf    # Windsurf
--ide copilot     # GitHub Copilot
```

**IDE affects:**
- Which components are installed (capability filtering)
- File format (`.md` vs `.mdc`)
- Installation paths (`.claude/` vs `.cursor/`)

#### `--project, -p` (optional)

Project root directory (defaults to current directory):

```bash
# Explicit project path
aiconfig package install ./pkg --ide claude --project ~/my-app

# Auto-detected from current directory
cd ~/my-app
aiconfig package install ./pkg --ide claude
```

**Project detection:**

DevSync searches for project markers:
- `.git/` directory
- `pyproject.toml`
- `package.json`
- `.ai-config-kit/` directory

#### `--conflict, -c` (optional)

How to handle existing files (default: `skip`):

```bash
--conflict skip       # Keep existing files (default)
--conflict overwrite  # Replace existing files
--conflict rename     # Create numbered copies
```

See [Conflict Resolution](#conflict-resolution) for details.

#### `--force, -f` (optional)

Force reinstallation even if already installed:

```bash
# Normal install (skips if already installed)
aiconfig package install ./pkg --ide claude

# Force reinstall
aiconfig package install ./pkg --ide claude --force
```

**Use cases:**
- Revert local changes to package files
- Fix corrupted installations
- Update to newer package version

#### `--quiet, -q` (optional)

Minimal output (errors only):

```bash
aiconfig package install ./pkg --ide claude --quiet
```

**Output comparison:**

```bash
# Normal output
Installing package from ./pkg...
Target IDE: claude
Project root: /Users/you/project
✓ Successfully installed pkg v1.0.0
  Installed: 5
  Skipped: 0

# Quiet output
✓ Successfully installed pkg v1.0.0
```

#### `--json` (optional)

Output results as JSON for scripting:

```bash
aiconfig package install ./pkg --ide claude --json
```

**JSON output:**

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

## Conflict Resolution

When installing a package, files may already exist. Use conflict resolution strategies to control behavior.

### Skip Strategy (Default)

**Behavior:** Leave existing files unchanged, skip installation of conflicting components

```bash
aiconfig package install ./pkg --ide claude --conflict skip
```

**Example:**

```bash
# First install
aiconfig package install ./pkg --ide claude
# ✓ Installs code-quality.md

# Modify the file
echo "Custom rules..." >> .claude/rules/code-quality.md

# Reinstall with skip
aiconfig package install ./pkg --ide claude --conflict skip
# ✓ Keeps your custom rules intact
```

**When to use:**
- Preserving local customizations
- Default safe behavior
- Incremental package updates

**Result:**
```
  Installed: 4
  Skipped: 1    ← Existing file kept
  Failed: 0
```

### Overwrite Strategy

**Behavior:** Replace existing files with package versions

```bash
aiconfig package install ./pkg --ide claude --conflict overwrite
```

**Example:**

```bash
# Modified file exists
cat .claude/rules/code-quality.md
# Custom rules...

# Reinstall with overwrite
aiconfig package install ./pkg --ide claude --conflict overwrite
# ✓ Replaces with package version

cat .claude/rules/code-quality.md
# Code Quality Guidelines (original package content)
```

**When to use:**
- Reverting local changes
- Upgrading to new package version
- Fixing corrupted files

**Result:**
```
  Installed: 5    ← All files replaced
  Skipped: 0
  Failed: 0
```

⚠️ **Warning:** This permanently overwrites local changes!

### Rename Strategy

**Behavior:** Create numbered copies, preserve both versions

```bash
aiconfig package install ./pkg --ide claude --conflict rename
```

**Example:**

```bash
# Existing file
.claude/rules/code-quality.md   (your version)

# Install with rename
aiconfig package install ./pkg --ide claude --conflict rename

# Result
.claude/rules/code-quality.md    (original, unchanged)
.claude/rules/code-quality-1.md  (new from package)
```

**Multiple renames:**

```bash
# Install again
aiconfig package install ./pkg --ide claude --conflict rename

# Creates
.claude/rules/code-quality-2.md

# And again
.claude/rules/code-quality-3.md
```

**When to use:**
- Comparing versions
- Keeping both custom and package files
- Gradual migration to new package version

**Result:**
```
  Installed: 5    ← All components installed with new names
  Skipped: 0
  Failed: 0
```

### Strategy Comparison

| Strategy   | Existing File | New File | Result                           |
|------------|---------------|----------|----------------------------------|
| `skip`     | Preserved     | Ignored  | Original file unchanged          |
| `overwrite`| Replaced      | Installed| Package version replaces original|
| `rename`   | Preserved     | Renamed  | Both versions exist              |

### Choosing a Strategy

```bash
# Safe exploration
--conflict skip       # Won't break anything

# Fresh start
--conflict overwrite  # Clean package install

# Comparison
--conflict rename     # Keep both, decide later
```

## IDE-Specific Behavior

Different IDEs have different capabilities. Packages automatically adapt.

### Capability Matrix

| Component Type | Claude Code | Cursor | Windsurf | Copilot |
|----------------|-------------|--------|----------|---------|
| Instructions   | ✓           | ✓      | ✓        | ✓       |
| MCP Servers    | ✓           | ✗      | ✗        | ✗       |
| Hooks          | ✓           | ✗      | ✗        | ✗       |
| Commands       | ✓           | ✗      | ✗        | ✗       |
| Resources      | ✓           | ✓      | ✓        | ✗       |

### Filtering Example

Package contains:
- 2 instructions
- 1 MCP server
- 1 hook
- 1 command

**Install to Claude Code:**

```bash
aiconfig package install ./pkg --ide claude

# Result:
✓ Successfully installed pkg v1.0.0
  Installed: 5    ← All components
  Skipped: 0
```

**Install to Cursor:**

```bash
aiconfig package install ./pkg --ide cursor

# Result:
⚠ Partially installed pkg v1.0.0
  Installed: 2    ← Only instructions
  Skipped: 3      ← MCP, hook, command filtered
```

**Install to Copilot:**

```bash
aiconfig package install ./pkg --ide copilot

# Result:
⚠ Partially installed pkg v1.0.0
  Installed: 2    ← Only instructions
  Skipped: 3      ← Everything else filtered
```

### File Format Translation

Components are translated to IDE-specific formats:

#### Instructions

**Claude Code:**
```
Source: instructions/style-guide.md
Target: .claude/rules/style-guide.md
Format: Markdown (.md)
```

**Cursor:**
```
Source: instructions/style-guide.md
Target: .cursor/rules/style-guide.mdc
Format: Cursor Markdown (.mdc)
```

**Windsurf:**
```
Source: instructions/style-guide.md
Target: .windsurf/rules/style-guide.md
Format: Markdown (.md)
```

**GitHub Copilot:**
```
Source: instructions/style-guide.md
Target: .github/instructions/style-guide.md
Format: Markdown (.md)
```

#### Other Components (Claude Code only)

```
Hooks:    hooks/pre-commit.sh    → .claude/hooks/pre-commit.sh
Commands: commands/test.sh       → .claude/commands/test.sh
Resources: resources/.gitignore  → .gitignore (or specified path)
```

## Managing Installed Packages

### List Installed Packages

View all packages in current project:

```bash
aiconfig package list
```

**Output:**

```
Installed packages in /Users/you/project:

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Package            ┃ Version ┃ Status   ┃ Components ┃ Installed      ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ python-dev-setup   │ 1.0.0   │ ✓ complete│         5 │ 2025-01-14 10:30│
│ react-best-practices│ 2.1.0   │ ⚠ partial│         3 │ 2025-01-14 11:15│
└────────────────────┴─────────┴──────────┴────────────┴────────────────┘

Total: 2 package(s)
```

### List Specific Project

```bash
aiconfig package list --project ~/other-project
```

### JSON Output

```bash
aiconfig package list --json
```

**Output:**

```json
[
  {
    "name": "python-dev-setup",
    "namespace": "my-org/packages",
    "version": "1.0.0",
    "status": "complete",
    "scope": "project",
    "installed_at": "2025-01-14T10:30:00",
    "updated_at": "2025-01-14T10:30:00",
    "component_count": 5
  }
]
```

### Uninstall Packages

Remove a package and its files:

```bash
aiconfig package uninstall <package-name>
```

**Interactive (default):**

```bash
aiconfig package uninstall python-dev-setup

# Prompts:
Package to uninstall:
  Name: python-dev-setup
  Version: 1.0.0
  Components: 5

Are you sure you want to uninstall this package? [y/N]: y

# Removes files:
  Removed: .claude/rules/code-quality.md
  Removed: .claude/rules/testing-strategy.md
  ...

✓ Uninstalled python-dev-setup v1.0.0
  Removed 5 file(s)
```

**Non-interactive (auto-confirm):**

```bash
aiconfig package uninstall python-dev-setup --yes

# No prompts, removes immediately
✓ Uninstalled python-dev-setup v1.0.0
  Removed 5 file(s)
```

## Best Practices

### 1. Use Specific Conflict Strategies

Don't rely on defaults - be explicit:

```bash
# ✓ Good - clear intent
aiconfig package install ./pkg --ide claude --conflict skip

# ✗ Unclear - what happens to existing files?
aiconfig package install ./pkg --ide claude
```

### 2. Test in One Project First

Before rolling out to team:

```bash
# Test locally
cd ~/test-project
aiconfig package install ./new-package --ide claude

# Verify it works
# ...

# Then share with team
git add .ai-config-kit/
git commit -m "Add new AI config package"
```

### 3. Document Package Choices

Add a README explaining why packages are installed:

```bash
# .ai-config-kit/README.md
# AI Assistant Configuration

This project uses the following packages:

- **python-dev-setup**: Python best practices and linting
- **react-patterns**: React-specific coding guidelines
```

### 4. Version Control Package Tracking

Always commit the tracking file:

```bash
# Include in git
git add .ai-config-kit/packages.json
git commit -m "Track AI config packages"
```

### 5. Use Force Reinstall Sparingly

Only use `--force` when needed:

```bash
# ✓ Good reasons to use --force:
# - Fixing corrupted installation
# - Reverting local changes
# - Updating to new package version

# ✗ Don't use --force:
# - Regular installs
# - When --conflict strategies work better
```

### 6. Check Compatibility Before Installing

Know what your IDE supports:

```bash
# Claude Code: All components ✓
aiconfig package install ./full-featured-pkg --ide claude

# Cursor: Instructions + Resources only
# (Don't expect hooks/commands to work)
aiconfig package install ./full-featured-pkg --ide cursor
```

## Troubleshooting

### Installation Fails: "Manifest not found"

**Problem:**

```bash
aiconfig package install ./my-package
# Error: Manifest not found
```

**Solution:** Point to package directory, not manifest file:

```bash
# ✓ Correct
aiconfig package install ./my-package

# ✗ Wrong
aiconfig package install ./my-package/ai-config-kit-package.yaml
```

### Installation Fails: "Invalid manifest"

**Problem:**

```bash
# Error: Manifest validation failed: Missing required field: 'version'
```

**Solution:** Fix the manifest. Required fields:
- `name`
- `version`
- `description`
- `author`
- `namespace`

See [Manifest Reference](manifest-reference.md).

### Components Don't Appear

**Problem:** Package installed but components not working

**Solutions:**

1. **Check IDE compatibility:**
   ```bash
   # See what was actually installed
   aiconfig package list --json
   ```

2. **Restart IDE:** Some IDEs need restart to load new configs

3. **Verify files exist:**
   ```bash
   ls .claude/rules/  # Claude Code
   ls .cursor/rules/  # Cursor
   ```

### Want to Reinstall Clean

**Problem:** Installation is messy, want fresh start

**Solution:**

```bash
# 1. Uninstall
aiconfig package uninstall my-package --yes

# 2. Clean reinstall
aiconfig package install ./my-package --ide claude --conflict overwrite
```

## Next Steps

- **[Creating Packages](creating-packages.md)** - Build your own packages
- **[Manifest Reference](manifest-reference.md)** - Complete YAML schema
- **[CLI Reference](cli-reference.md)** - All commands and options
- **[Troubleshooting](troubleshooting.md)** - More problem-solving help

---

**Need more help?** Check the [Troubleshooting Guide](troubleshooting.md) or [open an issue](https://github.com/troylar/devsync/issues).
