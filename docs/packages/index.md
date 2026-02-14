# Configuration Packages

**A comprehensive guide to DevSync's package management system**

## Overview

Configuration packages are the easiest way to bundle and share AI coding assistant configurations. Instead of manually managing individual instructions, MCP servers, hooks, and commands, packages let you install complete development environments with a single command.

### What Are Configuration Packages?

A configuration package is a collection of related components that work together to enhance your AI coding assistant. Think of it like a software package manager (npm, pip, brew), but for AI assistant configurations.

**A package can contain:**

- **Instructions**: Guidelines and rules for how the AI should behave
- **MCP Servers**: Model Context Protocol servers for extended capabilities
- **Hooks**: Scripts that run automatically at specific points (pre-commit, etc.)
- **Commands**: Reusable scripts you can invoke on demand
- **Resources**: Configuration files, templates, and other assets

### Why Use Packages?

**Before Packages:**
```bash
# Manual installation - tedious and error-prone
aiconfig install python-style-guide
aiconfig mcp install filesystem
# Manually create hooks...
# Manually configure commands...
# Hope everything works together...
```

**With Packages:**
```bash
# One command installs everything
aiconfig package install python-dev-setup --ide claude

# ✓ 5 instructions installed
# ✓ 2 MCP servers configured
# ✓ 3 hooks activated
# ✓ 4 commands ready
# ✓ All components working together
```

### Key Benefits

#### 🎯 **Consistency**
Packages ensure everyone on your team uses the same AI assistant configuration. No more "works on my machine" problems.

#### 🚀 **Speed**
Install complete development environments in seconds. Get new team members productive immediately.

#### 🔄 **Reusability**
Create a package once, use it across all your projects. Share packages with the community.

#### 🛡️ **Safety**
Packages are versioned and tracked. You can always see what's installed and roll back if needed.

#### 🎨 **Flexibility**
Packages automatically adapt to your IDE (Claude Code, Cursor, Windsurf, or GitHub Copilot), installing only compatible components.

## Quick Example

Here's a complete package that sets up Python development best practices:

```yaml
# ai-config-kit-package.yaml
name: python-dev-setup
version: 1.0.0
description: Complete Python development configuration
author: Your Team
namespace: your-org/packages

components:
  instructions:
    - name: python-style
      file: instructions/python-style.md
      description: PEP 8 style guidelines

  hooks:
    - name: pre-commit
      file: hooks/pre-commit.sh
      description: Run linting before commits

  commands:
    - name: test
      file: commands/test.sh
      description: Run test suite with coverage
```

Install it:

```bash
aiconfig package install python-dev-setup --ide claude
```

That's it! Your AI assistant now:
- Follows Python style guidelines
- Runs linting before every commit
- Has a test command ready to use

## How It Works

### 1. Package Structure

Packages live in a directory with this structure:

```
my-package/
├── ai-config-kit-package.yaml    # Package manifest
├── instructions/                  # Instruction files
│   └── style-guide.md
├── mcp/                          # MCP server configs
│   └── filesystem.json
├── hooks/                        # Hook scripts
│   └── pre-commit.sh
├── commands/                     # Command scripts
│   └── test.sh
└── resources/                    # Additional files
    └── .gitignore
```

### 2. Installation Process

When you install a package:

```bash
aiconfig package install ./my-package --ide claude
```

DevSync:

1. **Parses** the manifest to understand what's in the package
2. **Filters** components based on your IDE's capabilities
3. **Translates** components to IDE-specific formats
4. **Installs** files to the correct locations
5. **Tracks** the installation in `.ai-config-kit/packages.json`

### 3. IDE Compatibility

Different IDEs support different component types:

| Component     | Claude Code | Cursor | Windsurf | GitHub Copilot |
|---------------|-------------|--------|----------|----------------|
| Instructions  | ✓           | ✓      | ✓        | ✓              |
| MCP Servers   | ✓           | ✗      | ✗        | ✗              |
| Hooks         | ✓           | ✗      | ✗        | ✗              |
| Commands      | ✓           | ✗      | ✗        | ✗              |
| Resources     | ✓           | ✓      | ✓        | ✗              |

Packages automatically skip unsupported components for your IDE.

### 4. Translation Layer

Components are translated to IDE-specific formats:

**Claude Code:**
- Instructions → `.claude/rules/*.md`
- Hooks → `.claude/hooks/*.sh`
- Commands → `.claude/commands/*.sh`

**Cursor:**
- Instructions → `.cursor/rules/*.mdc` (Cursor-specific format)

**Windsurf:**
- Instructions → `.windsurf/rules/*.md`

**GitHub Copilot:**
- Instructions → `.github/instructions/*.md`

## Documentation Navigation

This documentation is organized into focused guides:

### 📖 Core Guides

1. **[Getting Started](getting-started.md)** - Install your first package in 5 minutes
2. **[Installing Packages](installation.md)** - Complete installation guide with all options
3. **[Creating Packages](creating-packages.md)** - Build your own packages from scratch

### 📚 Reference

4. **[Manifest Reference](manifest-reference.md)** - Complete YAML schema documentation
5. **[CLI Reference](cli-reference.md)** - All commands and options
6. **[Examples](examples.md)** - Real-world package examples

### 🔧 Help

7. **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## What's Next?

- **New to packages?** Start with the [Getting Started](getting-started.md) guide
- **Installing a package?** See the [Installation Guide](installation.md)
- **Creating a package?** Follow the [Package Creation Guide](creating-packages.md)
- **Need reference docs?** Check the [Manifest Reference](manifest-reference.md) or [CLI Reference](cli-reference.md)

## Community & Support

- **Examples**: Browse the `example-package/` directory in this repo
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/troylar/devsync/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/troylar/devsync/discussions)

---

**Ready to get started?** Head to the [Getting Started Guide](getting-started.md) →
