# Advanced Usage

Advanced patterns and techniques for DevSync power users.

## Table of Contents

- [Scopes Deep Dive](#scopes-deep-dive)
- [Namespace Strategies](#namespace-strategies)
- [Conflict Resolution](#conflict-resolution)
- [Git References](#git-references)
- [Credential Management](#credential-management)
- [Multiple Environments](#multiple-environments)
- [CI/CD Integration](#cicd-integration)
- [Backup and Recovery](#backup-and-recovery)

---

## Scopes Deep Dive

### Understanding Project vs Global

**Project Scope:**
- Files: `<project>/.claude/rules/`, `.ai-config-kit/`
- Active: Only in that project directory
- Use: Team practices, project-specific patterns

**Global Scope:**
- Files: `~/.claude/rules/`, `~/.ai-config-kit/global/`
- Active: All projects on your machine
- Use: Personal tools, company-wide policies

### Mixing Scopes

Your IDE sees templates from **both** scopes simultaneously:

```bash
# Global templates (always available)
~/.claude/rules/
├── personal.productivity.md
├── company.security-policy.md
└── company.code-review.md

# Project templates (context-specific)
~/projects/backend-api/.claude/rules/
├── backend.api-patterns.md
├── backend.database-patterns.md
└── python.async-patterns.md
```

When working in `~/projects/backend-api/`, AI sees **all 6 templates**.

### Scope Precedence

When same-named templates exist in both scopes, **project wins**:

```bash
# Global
~/.claude/rules/standards.python.md

# Project (this one is used)
~/projects/my-app/.claude/rules/standards.python.md
```

---

## Namespace Strategies

### Company-Wide Namespaces

Use consistent namespaces across your organization:

```bash
# Convention: company.category
aiconfig template install <repo> --as acme.security
aiconfig template install <repo> --as acme.code-review
aiconfig template install <repo> --as acme.legal
```

### Team Namespaces

```bash
# Convention: team.category
aiconfig template install <repo> --as backend.api
aiconfig template install <repo> --as backend.database
aiconfig template install <repo> --as frontend.react
```

### Environment Namespaces

```bash
# Different configs per environment
cd ~/projects/app-dev
aiconfig mcp install <repo> --as dev

cd ~/projects/app-staging
aiconfig mcp install <repo> --as staging

cd ~/projects/app-prod
aiconfig mcp install <repo> --as prod
```

### Personal Namespaces

```bash
# Your personal tools (global scope)
aiconfig template install <repo> --as personal.shortcuts --scope global
aiconfig template install <repo> --as personal.templates --scope global
```

---

## Conflict Resolution

### Handling Name Conflicts

When installing templates with conflicting names, DevSync provides strategies:

**Skip (default):**
```bash
# Existing template kept, new template not installed
aiconfig template install <repo> --as namespace
# Conflict: namespace.standards.md already exists
# Action: Skip
```

**Rename:**
```bash
# New template gets suffix
aiconfig template install <repo> --as namespace --conflict rename
# Existing: namespace.standards.md
# New: namespace.standards-1.md
```

**Overwrite:**
```bash
# New template replaces existing
aiconfig template install <repo> --as namespace --conflict overwrite
# Existing: namespace.standards.md (deleted)
# New: namespace.standards.md (installed)
```

### Automatic Conflict Detection

DevSync checks for conflicts before installation:

```bash
aiconfig template install <repo> --as namespace

# Output:
# ⚠ Conflicts detected:
#   - namespace.python-standards.md (exists)
#   - namespace.security-checklist.md (exists)
#
# Choose resolution strategy:
#   [s]kip - Keep existing, don't install new (default)
#   [r]ename - Install with suffix (-1, -2, etc.)
#   [o]verwrite - Replace existing with new
#   [a]bort - Cancel installation
```

---

## Git References

### Using Branches

```bash
# Install from specific branch
aiconfig template install https://github.com/org/repo --as namespace --ref develop
aiconfig template install https://github.com/org/repo --as namespace --ref feature/new-templates
```

### Using Tags/Versions

```bash
# Pin to specific version
aiconfig template install https://github.com/org/repo --as namespace --ref v1.2.0

# Use semantic versioning
aiconfig template install https://github.com/org/repo --as namespace --ref v2.0.0
```

### Using Commits

```bash
# Pin to specific commit
aiconfig template install https://github.com/org/repo --as namespace --ref abc123def456
```

### Version Management

**Lock versions for stability:**
```bash
# Production: Use tagged releases
aiconfig template install <repo> --as prod --ref v1.0.0

# Development: Use latest from branch
aiconfig template install <repo> --as dev --ref main
```

**Update workflow:**
```bash
# Check current version
aiconfig template list namespace

# Update to latest
aiconfig template update namespace

# Or update to specific version
aiconfig template uninstall namespace
aiconfig template install <repo> --as namespace --ref v2.0.0
```

---

## Credential Management

### Environment Variable Patterns

**Recommended naming:**
```bash
# Pattern: <SYSTEM>_<PURPOSE>_<TYPE>
GITHUB_API_TOKEN=ghp_xxxxx
POSTGRES_CONNECTION_URL=postgresql://...
SLACK_BOT_TOKEN=xoxb-xxxxx
AWS_ACCESS_KEY_ID=AKIA...
```

### Credential Rotation

```bash
# Update credentials without reinstalling
aiconfig mcp configure backend.github

# Or update via environment
export GITHUB_TOKEN=ghp_new_token
aiconfig mcp configure backend --non-interactive
```

### Per-Environment Credentials

```bash
# Development
cd ~/projects/app-dev
export DATABASE_URL=postgresql://localhost/dev_db
aiconfig mcp configure dev --non-interactive

# Production
cd ~/projects/app-prod
export DATABASE_URL=postgresql://prod-host/prod_db
aiconfig mcp configure prod --non-interactive
```

### Credential Validation

```bash
# Check which credentials are configured
aiconfig mcp configure backend --show-current

# Validate all credentials
aiconfig mcp validate

# Validate specific namespace
aiconfig mcp validate backend
```

---

## Multiple Environments

### Pattern 1: Separate Projects

```bash
# One project per environment
~/projects/
├── app-dev/          # Development environment
├── app-staging/      # Staging environment
└── app-prod/         # Production environment

# Each has own templates and credentials
cd ~/projects/app-dev
aiconfig mcp install <repo> --as dev
aiconfig mcp configure dev

cd ~/projects/app-staging
aiconfig mcp install <repo> --as staging
aiconfig mcp configure staging
```

### Pattern 2: Same Project, Different Namespaces

```bash
# Single project, multiple MCP configurations
cd ~/projects/app

# Install environment-specific configs
aiconfig mcp install <repo-dev> --as dev
aiconfig mcp install <repo-staging> --as staging
aiconfig mcp install <repo-prod> --as prod

# Configure separately
aiconfig mcp configure dev
aiconfig mcp configure staging
aiconfig mcp configure prod

# Sync specific environment
aiconfig mcp sync --tool claude  # Syncs all configured servers
```

### Pattern 3: Global + Project Mix

```bash
# Global: Company-wide tools (same everywhere)
aiconfig template install <company-tools> --as company --scope global

# Project: Environment-specific
cd ~/projects/app-dev
aiconfig mcp install <dev-mcp> --as dev

cd ~/projects/app-prod
aiconfig mcp install <prod-mcp> --as prod
```

---

## CI/CD Integration

### Non-Interactive Installation

```bash
#!/bin/bash
# setup.sh - Automated template installation

# Set credentials from CI environment
export GITHUB_TOKEN="${CI_GITHUB_TOKEN}"
export DATABASE_URL="${CI_DATABASE_URL}"

# Install templates
aiconfig template install https://github.com/company/standards --as company --force

# Install MCP servers
aiconfig mcp install https://github.com/company/mcp-servers --as backend --force

# Configure credentials (non-interactive)
aiconfig mcp configure backend --non-interactive

# Sync to tools
aiconfig mcp sync --tool all
```

### Docker Integration

```dockerfile
# Dockerfile
FROM python:3.11

# Install DevSync
RUN pip install ai-config-kit

# Copy credentials from build args
ARG GITHUB_TOKEN
ARG DATABASE_URL
ENV GITHUB_TOKEN=${GITHUB_TOKEN}
ENV DATABASE_URL=${DATABASE_URL}

# Install templates
RUN aiconfig template install https://github.com/company/standards --as company --force

# Install and configure MCP
RUN aiconfig mcp install https://github.com/company/mcp --as backend --force && \
    aiconfig mcp configure backend --non-interactive

WORKDIR /app
```

### GitHub Actions

```yaml
# .github/workflows/setup-templates.yml
name: Setup Templates

on: [push]

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install DevSync
        run: pip install ai-config-kit

      - name: Install Templates
        run: |
          aiconfig template install https://github.com/company/standards --as company --force

      - name: Configure MCP
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          aiconfig mcp install https://github.com/company/mcp --as backend --force
          aiconfig mcp configure backend --non-interactive
```

---

## Backup and Recovery

### Automatic Backups

DevSync automatically backs up config files before syncing:

```bash
# Backup files created:
~/Library/Application Support/Claude/claude_desktop_config.json.bak
~/Library/Application Support/Cursor/User/globalStorage/mcp_config.json.bak
```

### Manual Backup

```bash
# Before major changes
cp ~/.claude/rules ~/.claude/rules.backup
cp .ai-config-kit .ai-config-kit.backup

# Or use tar
tar -czf ai-config-kit-backup-$(date +%Y%m%d).tar.gz .ai-config-kit ~/.claude/rules
```

### Recovery

```bash
# Restore from automatic backup
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json.bak \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restore from manual backup
cp -r ~/.claude/rules.backup ~/.claude/rules
cp -r .ai-config-kit.backup .ai-config-kit
```

### Disaster Recovery

```bash
# Complete fresh start
rm -rf ~/.ai-config-kit
rm -rf .ai-config-kit
rm -rf ~/.claude/rules/*

# Reinstall everything
aiconfig template install <repo1> --as namespace1
aiconfig template install <repo2> --as namespace2
aiconfig mcp install <mcp-repo> --as backend
aiconfig mcp configure backend
aiconfig mcp sync --tool all
```

---

## Tips and Tricks

### List All Installed Content

```bash
# Templates
find ~/.claude/rules -type f -name "*.md" | sort
find .claude/rules -type f -name "*.md" | sort

# MCP installations
aiconfig mcp list --json | jq .
```

### Bulk Operations

```bash
# Update all templates and MCP configs
aiconfig template update --all
aiconfig mcp update --all

# Sync to all tools
aiconfig mcp sync --tool all
```

### Debugging

```bash
# Enable debug logging
export LOGLEVEL=DEBUG
aiconfig mcp sync --tool all

# Dry run (preview changes)
aiconfig mcp sync --tool all --dry-run

# Check what's installed
aiconfig template list
aiconfig mcp list
aiconfig tools
```

### Performance

```bash
# Skip backups for faster syncing
aiconfig mcp sync --tool claude --no-backup

# Use specific tool instead of "all"
aiconfig mcp sync --tool claude
```

---

**[← Back to Main Documentation](../README.md)**
