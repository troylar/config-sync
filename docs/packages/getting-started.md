# Getting Started with Packages

**Install your first configuration package in under 5 minutes**

This guide will walk you through installing and using your first configuration package. By the end, you'll have a complete development setup running in your AI coding assistant.

## Prerequisites

Before you begin, make sure you have:

- ✅ DevSync installed (`pip install ai-config-kit`)
- ✅ One of the supported IDEs:
  - Claude Code (claude.ai/code)
  - Cursor (cursor.sh)
  - Windsurf (codeium.com/windsurf)
  - GitHub Copilot (github.com/features/copilot)
- ✅ A project directory (any folder with code)

**Check your installation:**

```bash
aiconfig --version
# Should show: ai-config-kit, version X.X.X
```

## Step 1: Find a Package

For this guide, we'll use the `example-package` included with DevSync. This package demonstrates all component types.

**What's in the example package:**
- ✓ 2 Instructions (code quality, testing strategy)
- ✓ 1 MCP Server (filesystem access)
- ✓ 1 Hook (pre-commit linting)
- ✓ 1 Command (test runner)
- ✓ 1 Resource (.gitignore file)

**Locate the package:**

```bash
# If you cloned the repo
cd devsync
ls example-package/

# You should see:
# ai-config-kit-package.yaml
# instructions/
# mcp/
# hooks/
# commands/
# resources/
```

> **💡 Tip**: You can also create your own package or download one from the community. See [Creating Packages](creating-packages.md) for details.

## Step 2: Navigate to Your Project

```bash
cd ~/path/to/your/project
```

The package will be installed to this project directory.

## Step 3: Install the Package

Now install the package:

```bash
aiconfig package install /path/to/ai-config-kit/example-package --ide claude
```

**Replace `claude` with your IDE:**
- `claude` - Claude Code
- `cursor` - Cursor
- `windsurf` - Windsurf
- `copilot` - GitHub Copilot

**What happens:**

```
Installing package from /path/to/example-package...
Target IDE: claude
Project root: /Users/you/your-project

✓ Successfully installed example-package v1.0.0

Installation Summary
┏━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Component Type  ┃ Count ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ instruction     │     2 │
│ mcp_server      │     1 │
│ hook            │     1 │
│ command         │     1 │
│ resource        │     1 │
└─────────────────┴───────┘

  Installed: 6
  Skipped: 0
  Failed: 0
```

🎉 **Success!** The package is now installed in your project.

## Step 4: Verify the Installation

Check what got installed:

```bash
# List installed packages
aiconfig package list
```

**Output:**

```
Installed packages in /Users/you/your-project:

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Package                      ┃ Version ┃ Status      ┃ Components ┃ Installed       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ aiconfigkit/examples/...     │ 1.0.0   │ ✓ complete  │          6 │ 2025-01-14 10:30│
└──────────────────────────────┴─────────┴─────────────┴────────────┴─────────────────┘

Total: 1 package(s)
```

### Check Installed Files

Files were created in your project:

```bash
# For Claude Code
ls .claude/rules/          # Instructions
ls .claude/hooks/          # Hooks
ls .claude/commands/       # Commands

# For Cursor
ls .cursor/rules/          # Instructions

# For other IDEs, similar structure
```

## Step 5: Use the Package Components

Now that the package is installed, let's use its components.

### A. Instructions Are Active

The AI assistant automatically reads instructions from the IDE-specific directory.

**Try it:**

Ask your AI assistant: "What are the Python style guidelines for this project?"

The AI will reference the `code-quality.md` instruction you just installed.

### B. Hooks Run Automatically (Claude Code only)

The pre-commit hook runs automatically:

```bash
# Make a change and commit
echo "print('test')" > test.py
git add test.py
git commit -m "test"

# The hook runs automatically:
# Running pre-commit checks...
# → Running linter...
# → Running formatter...
# ✓ All pre-commit checks passed!
```

### C. Commands Are Available (Claude Code only)

Run the test command:

```bash
./.claude/commands/test.sh

# Running test suite...
# ✓ All tests passed!
# Coverage report: htmlcov/index.html
```

### D. MCP Server Is Configured (Claude Code only)

The filesystem MCP server is ready to use. Configure credentials:

```bash
# Set the allowed directories
export ALLOWED_DIRECTORIES="/path/to/project"

# Restart your IDE to load the MCP server
```

## Step 6: Customize the Package (Optional)

Installed files are just regular files in your project. You can edit them:

```bash
# Edit an instruction
vim .claude/rules/code-quality.md

# Edit a hook
vim .claude/hooks/pre-commit.sh

# Changes take effect immediately
```

**Note:** If you reinstall the package, your changes will be kept (by default) or overwritten (with `--conflict overwrite`).

## Step 7: Share with Your Team

The package installation is tracked in `.ai-config-kit/packages.json`:

```bash
# Commit this file to share the setup with your team
git add .ai-config-kit/
git commit -m "Add AI assistant configuration package"
git push
```

Team members can then see what packages are installed on the shared configuration:

```bash
# Clone the repo
git clone <repo-url>
cd <repo>

# See installed packages
aiconfig package list
```

## What Just Happened?

Let's break down what the package system did:

1. **Read the Manifest**: Parsed `ai-config-kit-package.yaml` to understand components
2. **Filtered Components**: Checked which components your IDE supports
3. **Translated Formats**: Converted instructions to IDE-specific format (`.md` vs `.mdc`)
4. **Installed Files**: Copied files to correct IDE directories
5. **Tracked Installation**: Recorded in `.ai-config-kit/packages.json`

## Common Next Steps

### Try Different Conflict Strategies

Reinstall with different behavior:

```bash
# Skip existing files (default)
aiconfig package install example-package --ide claude --conflict skip

# Overwrite existing files
aiconfig package install example-package --ide claude --conflict overwrite

# Create numbered copies (file-1.md, file-2.md)
aiconfig package install example-package --ide claude --conflict rename

# Force reinstall
aiconfig package install example-package --ide claude --force
```

### Uninstall the Package

Remove the package when you're done:

```bash
aiconfig package uninstall example-package

# Or skip confirmation
aiconfig package uninstall example-package --yes
```

### Create Your Own Package

Ready to create your own? See [Creating Packages](creating-packages.md).

## Troubleshooting

### Package Install Failed

**Problem:** Installation fails with "Manifest not found"

**Solution:** Make sure you're pointing to the package directory (containing `ai-config-kit-package.yaml`):

```bash
# ✓ Correct - directory containing manifest
aiconfig package install ./my-package

# ✗ Wrong - pointing to manifest file itself
aiconfig package install ./my-package/ai-config-kit-package.yaml
```

### Components Not Showing Up

**Problem:** Installed but components aren't working

**Possible causes:**

1. **Wrong IDE**: Components were filtered for a different IDE
   ```bash
   # Check what was actually installed
   aiconfig package list --json
   ```

2. **IDE not restarted**: Restart your IDE to load new configurations

3. **Wrong directory**: Make sure you're in the project where you installed
   ```bash
   # Check current directory
   pwd
   ```

### Want to Install Globally?

Currently, package installation is project-scoped only. To use a package across multiple projects, install it in each one:

```bash
cd ~/project1
aiconfig package install my-package --ide claude

cd ~/project2
aiconfig package install my-package --ide claude
```

## Next Steps

Congratulations! You've successfully installed and used your first configuration package.

**Where to go from here:**

- **[Installation Guide](installation.md)** - Learn all installation options and strategies
- **[Creating Packages](creating-packages.md)** - Build your own custom packages
- **[Examples](examples.md)** - See more real-world package examples
- **[CLI Reference](cli-reference.md)** - Complete command documentation

---

**Questions?** Check the [Troubleshooting Guide](troubleshooting.md) or [open an issue](https://github.com/troylar/devsync/issues).
