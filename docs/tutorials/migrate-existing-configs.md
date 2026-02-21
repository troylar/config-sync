# Tutorial: Migrate Existing Configs

**Time:** 15 minutes | **Level:** Intermediate

Convert your existing AI tool configurations into a shareable DevSync package.

---

## What You Will Learn

- Audit existing AI tool configurations
- Extract them into a DevSync package
- Upgrade v1 packages to v2 format
- Distribute to your team

## Prerequisites

- DevSync installed (`pip install devsync`)
- LLM configured (`devsync setup`)
- An existing project with AI rules, MCP configs, or other tool-specific files

---

## Step 1: Audit Existing Configs

Check what AI configurations your project already has:

```bash
devsync tools
```

Then look at the tool-specific directories:

```bash
# Claude Code
ls .claude/rules/ 2>/dev/null

# Cursor
ls .cursor/rules/ 2>/dev/null

# Windsurf
ls .windsurf/rules/ 2>/dev/null

# GitHub Copilot
ls .github/instructions/ 2>/dev/null

# Single-file configs
ls AGENTS.md CONVENTIONS.md GEMINI.md 2>/dev/null
```

## Step 2: Extract into a Package

DevSync reads all detected configs and produces a package:

```bash
devsync extract --output ./migrated-standards --name my-standards
```

```
Extracting practices from /home/user/my-project...

  Scanning: .claude/rules/ (4 files)
  Scanning: .cursor/rules/ (3 files)
  Scanning: MCP configurations (2 servers)

  Extracted 5 practice declarations
  Extracted 2 MCP servers

Package written to: ./migrated-standards/devsync-package.yaml
```

## Step 3: Review the Package

Check the extracted practices:

```bash
cat migrated-standards/devsync-package.yaml
```

Verify that:

- Practice names are clear and descriptive
- Principles accurately capture your standards
- MCP server credentials are properly declared (not hardcoded)

Edit the manifest if needed to refine the extracted content.

## Step 4: Test the Package

Install into a clean project to verify:

```bash
mkdir /tmp/test-migration && cd /tmp/test-migration
git init
devsync install ~/my-project/migrated-standards
devsync list
```

## Step 5: Distribute

Push the package to Git for your team:

```bash
cd migrated-standards
git init && git add . && git commit -m "Initial migration"
git remote add origin https://github.com/company/team-standards
git push -u origin main
```

---

## Upgrading v1 Packages

If you have an existing v1 package (`ai-config-kit-package.yaml`), upgrade it to v2:

```bash
devsync extract --upgrade ./old-v1-package --output ./v2-package --name my-standards
```

This converts v1 instructions into v2 practice declarations while preserving MCP server configurations.

### Before (v1)

```yaml
# ai-config-kit-package.yaml
name: old-package
version: 1.0.0
components:
  instructions:
    - name: python-style
      file: instructions/python-style.md
      description: Python style guide
```

### After (v2)

```yaml
# devsync-package.yaml
name: my-standards
version: 1.0.0
practices:
  - name: python-style
    intent: Consistent Python code formatting and naming
    principles:
      - Line length 120 characters
      - Use black for formatting
      - snake_case for functions
    tags: [python, style]
```

---

## File-Copy Mode

If you don't have an LLM configured, use file-copy mode:

```bash
# Extract files verbatim
devsync extract --output ./pkg --name my-pkg --no-ai

# Install files verbatim
devsync install ./pkg --no-ai
```

This copies files directly without AI extraction or adaptation.

---

## Next Steps

- [Team Config Repository](team-config-repo.md) -- host and maintain your standards
- [Custom Packages](custom-packages.md) -- add hooks, commands, and resources
- [Package Examples](../packages/examples.md) -- see complete package examples
