# Template System

Comprehensive guide to DevSync's template system for distributing IDE configurations.

> **Note:** This document is being reorganized. For now, see the main [README](../README.md) for template system documentation. Full documentation coming soon.

## Quick Links

- [Template System Overview](../README.md#core-features)
- [Installation & Setup](../README.md#installation--setup)
- [Common Use Cases](../README.md#common-use-cases)

## Key Concepts

### What are Templates?

Templates are IDE-specific content distributed via Git repositories:

- **Coding Standards** → `.claude/rules/` (instructions for AI)
- **Slash Commands** → `.claude/commands/` (accessible as `/command-name`)
- **IDE Hooks** → Pre/post prompt automation
- **Any Configuration** → Snippets, settings, etc.

### Repository Structure

```
my-templates/
├── templatekit.yaml          # Manifest file
├── templates/
│   ├── rules/
│   │   ├── python-standards.md
│   │   └── security-checklist.md
│   ├── commands/
│   │   ├── test-api.md
│   │   └── review-pr.md
│   └── hooks/
│       ├── pre-prompt.md
│       └── post-prompt.md
```

### templatekit.yaml Format

```yaml
name: My Templates
version: 1.0.0
description: Team coding standards

templates:
  - name: python-standards
    description: Python coding standards
    ide: claude
    files:
      - path: .claude/rules/python-standards.md
        type: instruction
    tags: [python, standards]

  - name: test-api
    description: Test API endpoints
    ide: claude
    files:
      - path: .claude/commands/test-api.md
        type: command
    tags: [testing, api]
```

## Basic Commands

```bash
# Install templates
aiconfig template install <repo> --as <namespace>

# List installed templates
aiconfig template list

# Update templates
aiconfig template update <namespace>

# Uninstall templates
aiconfig template uninstall <namespace>

# Create new template repository (creates directory in current location)
aiconfig template init <name>

# Validate repository
aiconfig template validate <path>
```

## Installation Scopes

| Scope | Location | Use Case |
|-------|----------|----------|
| **Project** (default) | `<project>/.claude/rules/` | Team/project-specific |
| **Global** | `~/.claude/rules/` | Personal tools, company-wide |

```bash
# Project scope (default)
aiconfig template install <repo> --as team

# Global scope
aiconfig template install <repo> --as personal --scope global
```

## Namespaces

Namespaces prevent conflicts when installing multiple template repositories:

```bash
# Install with namespace "acme"
aiconfig template install https://github.com/acme/standards --as acme

# Templates become:
# .claude/rules/acme.python-standards.md
# .claude/commands/acme.test-api.md
```

## Real-World Workflows

### New Team Member Onboarding

```bash
# Global: Company standards
aiconfig template install https://github.com/company/standards --as company --scope global

# Project: Team-specific
cd ~/projects/backend-api
aiconfig template install https://github.com/team/backend --as backend
```

### Applying to Existing Project

```bash
cd ~/projects/my-api
aiconfig template install https://github.com/owasp/security --as owasp

# Templates immediately available in .claude/rules/owasp.*
```

### Creating Your Own Templates

```bash
# Navigate to where you want to create the template
cd ~/projects  # or your preferred location

# Initialize new template repository (creates 'my-standards' directory here)
aiconfig template init my-standards

# Edit templatekit.yaml and add your content
cd my-standards
# ... edit files ...

# Test locally
aiconfig template install . --as test

# Push to Git and share with team
git remote add origin https://github.com/yourorg/templates
git push -u origin main
```

---

**Full documentation coming soon. For now, see [README](../README.md) for complete examples.**

**[← Back to Main Documentation](../README.md)**
