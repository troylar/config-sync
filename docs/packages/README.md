# Configuration Packages Documentation

**Complete documentation for DevSync's package management system**

This directory contains comprehensive documentation for creating, installing, and managing configuration packages.

## Documentation Structure

### 📖 Getting Started

Start here if you're new to packages:

1. **[Package Overview](index.md)** - Introduction to packages, benefits, and how they work
2. **[Getting Started Guide](getting-started.md)** - Install your first package in 5 minutes

### 📚 User Guides

Detailed guides for working with packages:

3. **[Installation Guide](installation.md)** - Complete guide to installing packages with all options
4. **[Creating Packages](creating-packages.md)** - Build your own packages from scratch

### 📋 Reference Documentation

Technical reference materials:

5. **[Manifest Reference](manifest-reference.md)** - Complete YAML schema for package manifests
6. **[CLI Reference](cli-reference.md)** - All commands, options, and flags
7. **[Examples](examples.md)** - Real-world package examples for common scenarios

## Quick Navigation

### I want to...

**...install a package**
→ Start with [Getting Started Guide](getting-started.md), then see [Installation Guide](installation.md)

**...create my own package**
→ Follow [Creating Packages](creating-packages.md), reference [Manifest Reference](manifest-reference.md)

**...see example packages**
→ Browse [Examples](examples.md) for real-world packages

**...understand a command**
→ Check [CLI Reference](cli-reference.md) for detailed command documentation

**...understand package concepts**
→ Read [Package Overview](index.md)

## What Are Configuration Packages?

Configuration packages bundle related AI assistant configurations together. Instead of manually managing individual instructions, MCP servers, hooks, and commands, packages let you install complete development environments with a single command.

**Example:**
```bash
# Install everything you need for Python development
aiconfig package install ./python-dev-setup --ide claude

# ✓ 5 instructions installed
# ✓ 2 MCP servers configured
# ✓ 3 hooks activated
# ✓ 4 commands ready
```

## Key Features

- **🎯 Consistency**: Everyone on your team uses the same configuration
- **🚀 Speed**: Install complete setups in seconds
- **🔄 Reusability**: Create once, use across all projects
- **🛡️ Safety**: Versioned and tracked installations
- **🎨 Flexibility**: Automatically adapts to your IDE

## Supported IDEs

| IDE | Instructions | MCP Servers | Hooks | Commands | Resources |
|-----|-------------|-------------|-------|----------|-----------|
| Claude Code | ✓ | ✓ | ✓ | ✓ | ✓ |
| Cursor | ✓ | ✗ | ✗ | ✗ | ✓ |
| Windsurf | ✓ | ✗ | ✗ | ✗ | ✓ |
| GitHub Copilot | ✓ | ✗ | ✗ | ✗ | ✗ |

Packages automatically filter components based on IDE capabilities.

## Quick Start

### Install a Package

```bash
# Navigate to your project
cd ~/my-project

# Install package
aiconfig package install ./example-package --ide claude

# Verify installation
aiconfig package list
```

### Create a Package

```bash
# Create package directory
mkdir my-package
cd my-package

# Create manifest
cat > ai-config-kit-package.yaml << 'EOF'
name: my-package
version: 1.0.0
description: My first configuration package
author: Your Name
namespace: your-org/packages

components:
  instructions:
    - name: my-instruction
      description: What it does
      file: instructions/my-instruction.md
      tags: [tag1, tag2]
EOF

# Create instruction
mkdir instructions
cat > instructions/my-instruction.md << 'EOF'
# My Instruction

Guidelines for the AI assistant...
EOF

# Test installation
cd ~/test-project
aiconfig package install /path/to/my-package --ide claude
```

## Common Tasks

### List Installed Packages

```bash
aiconfig package list
```

### Uninstall a Package

```bash
aiconfig package uninstall my-package
```

### Update a Package

```bash
# Reinstall with overwrite to update
aiconfig package install ./my-package --ide claude --conflict overwrite --force
```

### Install to Multiple Projects

```bash
aiconfig package install ./my-package --ide claude --project ~/project1
aiconfig package install ./my-package --ide claude --project ~/project2
```

## Documentation Conventions

Throughout this documentation:

- **Code blocks** show exact commands to run
- **Examples** use realistic scenarios
- **Notes** provide additional context
- **Warnings** highlight important gotchas

## Getting Help

- **Questions?** Check individual guides for detailed information
- **Issues?** Report bugs at [GitHub Issues](https://github.com/troylar/devsync/issues)
- **Discussions?** Ask questions in [GitHub Discussions](https://github.com/troylar/devsync/discussions)

## Contributing

Want to improve this documentation?

1. **Found an error?** Open an issue
2. **Have a suggestion?** Start a discussion
3. **Want to contribute?** Submit a pull request

## Related Documentation

- **[Main README](../../README.md)** - DevSync overview
- **[MCP Documentation](../mcp/)** - MCP server management (if available)

---

**Ready to get started?** Head to the [Getting Started Guide](getting-started.md) →
