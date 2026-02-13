<div align="center">

# 🎯 AI Config Kit

**Distribute and sync coding standards, AI tool configurations, and MCP servers across your team**

[![CI](https://github.com/troylar/ai-config-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/troylar/ai-config-kit/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/troylar/ai-config-kit/branch/main/graph/badge.svg)](https://codecov.io/gh/troylar/ai-config-kit)
[![PyPI version](https://img.shields.io/pypi/v/ai-config-kit.svg)](https://pypi.org/project/ai-config-kit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Works with:** Claude Code • Claude Desktop • Cline • Cursor • GitHub Copilot • Kiro • Windsurf

</div>

---

## What is AI Config Kit?

AI Config Kit is a CLI tool for distributing and managing AI coding assistant configurations across teams:

- **📋 Templates**: Share coding standards, slash commands, and IDE configurations from Git repositories
- **🔌 MCP Servers**: Distribute and manage Model Context Protocol server configurations
- **🔄 Sync**: Keep your team aligned with single-command updates
- **✅ Safe**: Built-in validation, automatic backups, conflict resolution

> **Note:** Commands use `aiconfig` (short for AI Config Kit)

---

## 🚀 Quick Start

### Install

```bash
pip install ai-config-kit
```

### Templates: Share Coding Standards (30 seconds)

```bash
# Navigate to where you want to create the template
cd ~/projects  # or your preferred location

# Create template repository (creates 'my-standards' directory here)
aiconfig template init my-standards

# Work inside it and install locally to test
cd my-standards
aiconfig template install . --as demo

# Your IDE now has coding standards in .claude/rules/demo.*
```

### MCP: Configure AI Tool Servers (2 minutes)

```bash
# Install MCP server configurations from a repository
aiconfig mcp install https://github.com/company/mcp-servers --as backend

# Configure credentials securely (stored in gitignored .env)
aiconfig mcp configure backend

# Sync to AI tools (Claude Desktop, Cursor, Windsurf)
aiconfig mcp sync --tool all
```

### Packages: Install Complete Development Setups (1 minute)

```bash
# Install a complete package with instructions, hooks, and commands
aiconfig package install ./example-package --ide claude

# List installed packages
aiconfig package list

# Your IDE now has everything: instructions, MCP servers, hooks, commands
```

---

## Core Features

### 🎨 Template System

Distribute any IDE-specific content from Git repositories:

- **Coding Standards** → `.claude/rules/` (instructions for AI)
- **Slash Commands** → `.claude/commands/` (accessible as `/command-name`)
- **IDE Hooks** → Pre/post prompt automation
- **Any Configuration** → Snippets, settings, etc.

**Key Commands:**
```bash
aiconfig template install <repo> --as <namespace>  # Install templates
aiconfig template list                             # Show installed templates
aiconfig template update <namespace>               # Update to latest version
aiconfig template uninstall <namespace>            # Remove templates
```

[📖 Full Template Documentation →](docs/templates.md)

### 🔌 MCP Server Management

Manage Model Context Protocol servers across your team:

- **Share Configurations** → Distribute MCP server setups via Git
- **Secure Credentials** → Store secrets in gitignored `.env` files
- **Multi-Tool Sync** → One command syncs to Claude Code, Claude Desktop, Cursor, Windsurf
- **Environment Resolution** → Automatically inject credentials at sync time

**Supported IDEs:**
| IDE | MCP Config Location | Tool Limit |
|-----|---------------------|------------|
| Claude Code | `.claude/settings.local.json` | Unlimited |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` | Unlimited |
| Cursor | `.cursor/mcp.json` or `~/.cursor/mcp.json` | 40 tools |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | 100 tools |
| GitHub Copilot | `.vscode/mcp.json` | 128 tools |

**Key Commands:**
```bash
aiconfig mcp install <repo> --as <namespace>       # Install MCP configs
aiconfig mcp configure <namespace>                 # Set up credentials
aiconfig mcp sync --tool all                       # Sync to AI tools
aiconfig mcp list                                  # Show installed servers
```

[📖 Full MCP Documentation →](docs/mcp.md)

### 📦 Configuration Packages

Bundle and distribute complete AI assistant configurations:

- **Multi-Component Packages** → Combine instructions, MCP servers, hooks, commands, skills, workflows
- **IDE-Aware Installation** → Automatically adapts to target IDE capabilities
- **Package Creation** → Generate packages from existing project configurations
- **Secret Detection** → Automatically templates secrets in MCP configs
- **Conflict Resolution** → Handle existing files with skip, overwrite, or rename strategies

**Key Commands:**
```bash
aiconfig package create --name my-pkg                # Create package from project
aiconfig package install <package-path> --ide <ide>  # Install package
aiconfig package list                                 # Show installed packages
aiconfig package uninstall <package-name>            # Remove package
```

[📖 Full Package Documentation →](docs/packages/)

---

## Why AI Config Kit?

### For Teams

✅ **Consistency** - Everyone uses the same standards and tools
✅ **Onboarding** - New members get configured in minutes
✅ **Compliance** - Enforce security policies and code review checklists
✅ **No Secrets in Git** - Credentials stay local, configs are shared

### For Individuals

✅ **Portable** - Same setup across all your machines
✅ **Composable** - Mix company + team + personal configurations
✅ **Discoverable** - Install templates from any Git repository
✅ **Safe** - Automatic backups, conflict resolution, validation

---

## Real-World Example

Here's how a team at ACME Corp uses AI Config Kit:

```bash
# 1. Everyone installs company security policies (global, applies to all projects)
aiconfig template install https://github.com/acme/security-policy --as acme-security --scope global

# 2. Backend team members clone their project
git clone https://github.com/acme/backend-api.git && cd backend-api

# 3. Install team-specific templates (project scope)
aiconfig template install https://github.com/acme/backend-standards --as backend
aiconfig template install https://github.com/acme/python-patterns --as python

# 4. Install and configure MCP servers (for enhanced AI capabilities)
aiconfig mcp install https://github.com/acme/mcp-servers --as backend-mcp
aiconfig mcp configure backend-mcp
aiconfig mcp sync --tool claude

# Done! IDE now has:
# - Global security rules (all projects)
# - Backend coding standards (this project)
# - Python patterns (this project)
# - MCP servers configured (Claude Desktop, Cursor, etc.)
```

Team members update everything with:
```bash
aiconfig template update --all
aiconfig mcp update --all
```

---

## Documentation

| Guide | Description |
|-------|-------------|
| [**Templates**](docs/templates.md) | Comprehensive guide to the template system |
| [**MCP Servers**](docs/mcp.md) | Managing Model Context Protocol servers |
| [**Packages**](docs/packages/) | Complete package management guide (install, create, manage) |
| [**CLI Reference**](docs/cli-reference.md) | Complete command reference |
| [**Advanced Usage**](docs/advanced.md) | Scopes, namespaces, conflict resolution |
| [**Creating Templates**](docs/creating-templates.md) | How to build your own template repositories |

---

## Project vs Global Scope

AI Config Kit supports two installation scopes:

| Scope | Where Files Go | When Active | Best For |
|-------|---------------|-------------|----------|
| **Project** (default) | `<project>/.claude/rules/`<br>`<project>/.ai-config-kit/` | Only in that project | Team practices, project standards |
| **Global** | `~/.claude/rules/`<br>`~/.ai-config-kit/` | All projects | Personal tools, company policies |

**Example:**
```bash
# Global: Company-wide security policy (applies everywhere)
aiconfig template install https://github.com/company/security --as security --scope global

# Project: Team-specific patterns (only this project)
cd ~/projects/backend-api
aiconfig template install https://github.com/team/backend-patterns --as backend
```

Your IDE gets **both**: global templates (always available) + project templates (context-specific).

---

## What Can You Distribute?

### Templates

Any IDE-specific content from Git repositories:

- Coding standards and style guides
- Security checklists and compliance rules
- Custom slash commands (accessible as `/command-name`)
- Code review templates
- Architecture decision records (ADRs)
- Testing patterns and strategies
- IDE automation hooks (pre-prompt, post-prompt)

### Packages

Complete configuration bundles with multiple component types:

| Component | Claude | Cline | Cursor | Kiro | Windsurf | Copilot |
|-----------|--------|-------|--------|------|----------|---------|
| Instructions | `.claude/rules/` | `.clinerules/` | `.cursor/rules/` | `.kiro/steering/` | `.windsurf/rules/` | `.github/instructions/` |
| MCP Servers | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ |
| Hooks | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Commands | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Skills | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Workflows | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Memory Files | ✅ (CLAUDE.md) | ❌ | ❌ | ❌ | ❌ | ❌ |
| Resources | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

### MCP Server Configurations

Model Context Protocol server setups for enhanced AI capabilities:

- Database access (PostgreSQL, MySQL, SQLite)
- API integrations (GitHub, Jira, Slack)
- File system access with proper permissions
- Custom tools and commands
- Development environment connections

---

## Installation & Setup

### Requirements

- Python 3.10 or higher
- Git (for cloning template repositories)
- One of: Claude Code, Claude Desktop, Cline, Cursor, GitHub Copilot, Kiro, or Windsurf

### Install AI Config Kit

```bash
# Using pip
pip install ai-config-kit

# Verify installation
aiconfig --version
```

### Quick Configuration

```bash
# Check which AI tools are installed
aiconfig tools

# Navigate to where you want to create templates
cd ~/projects  # or your preferred location

# Create template repository (creates 'my-standards' directory here)
aiconfig template init my-standards

# Work inside it and install to test
cd my-standards
aiconfig template install . --as demo

# View installed templates
aiconfig template list
```

---

## Common Use Cases

### Scenario 1: New Team Member Onboarding

```bash
# Install company standards (once per machine)
aiconfig template install https://github.com/company/standards --as company --scope global

# Clone team project
git clone https://github.com/team/project.git && cd project

# Install project-specific templates
aiconfig template install https://github.com/team/backend-standards --as backend

# Set up MCP servers
aiconfig mcp install https://github.com/team/mcp-servers --as team-mcp
aiconfig mcp configure team-mcp
aiconfig mcp sync --tool all
```

### Scenario 2: Applying Templates to Existing Project

```bash
# You're working on a project, discover useful templates
cd ~/projects/my-api

# Install templates immediately
aiconfig template install https://github.com/owasp/security-templates --as owasp

# Templates are now in .claude/rules/owasp.*
# AI assistant immediately knows these security patterns
```

### Scenario 3: Solo Developer / Personal Use

```bash
# Install your personal tools globally (applies to all projects)
aiconfig template install https://github.com/yourname/my-tools --as personal --scope global

# Done! All your projects now have your preferred templates
```

---

## Development

### Running Tests

```bash
# Run all tests
invoke test

# Run with coverage
invoke test --coverage

# Code quality checks
invoke quality

# Auto-fix linting issues
invoke lint --fix
```

### Project Structure

```
ai-config-kit/
├── ai_tools/          # AI tool integrations (Claude, Cursor, etc.)
├── cli/               # CLI commands
├── core/              # Core business logic
│   ├── mcp/          # MCP server management
│   └── template/     # Template system
├── storage/           # Data persistence
└── utils/             # Utilities

tests/
├── unit/              # Unit tests
└── integration/       # Integration tests
```

---

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`invoke test`)
5. **Commit** (`git commit -m 'feat: add amazing feature'`)
6. **Push** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/troylar/ai-config-kit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/troylar/ai-config-kit/discussions)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

<div align="center">

**Made with ❤️ for AI-powered development teams**

</div>
