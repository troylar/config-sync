# Tutorial: Onboard a New Developer

**Time:** 10 minutes | **Level:** Beginner

Get a new team member fully configured with your team's AI coding standards.

---

## What You Will Learn

- Install DevSync and detect AI tools
- Install team standards from a Git repository
- Verify the installation

## Prerequisites

- Python 3.10+ installed
- One or more AI coding tools installed (Claude Code, Cursor, etc.)
- Your team's standards package hosted in a Git repository

---

## Step 1: Install DevSync

```bash
pip install devsync
```

Verify:

```bash
devsync version
```

## Step 2: Configure LLM (Optional)

For AI-powered adaptation:

```bash
devsync setup
```

!!! info
    If the new developer doesn't have an API key, they can skip this step. Installation still works using `--no-ai` for file-copy mode.

## Step 3: Detect AI Tools

```bash
devsync tools
```

Expected output:

```
Detected AI Tools:
  Claude Code    .claude/rules/          (.md)
  Cursor         .cursor/rules/          (.mdc)
```

## Step 4: Install Team Standards

Navigate to the project and install:

```bash
cd ~/the-project
devsync install https://github.com/company/team-standards
```

DevSync will:

1. Clone the team standards repository
2. Read the practice declarations
3. Detect installed AI tools
4. Adapt practices to the project's existing setup
5. Prompt for any MCP server credentials

```
Installing team-standards...

  Detected tools: Claude Code, Cursor
  Adapting 4 practices + 1 MCP server...

  Claude Code:
    Created: .claude/rules/code-style.md
    Created: .claude/rules/testing.md
    Created: .claude/rules/security.md
    Created: .claude/rules/error-handling.md

  Cursor:
    Created: .cursor/rules/code-style.mdc
    Created: .cursor/rules/testing.mdc
    Created: .cursor/rules/security.mdc
    Created: .cursor/rules/error-handling.mdc

  MCP server "github" requires credentials:
    GITHUB_TOKEN (required): GitHub personal access token
    > ghp_xxxxxxxxxxxxxxxxxxxx

Installation complete.
```

## Step 5: Verify

```bash
devsync list
```

```
Installed packages:
  team-standards     v1.0.0    4 practices, 1 MCP server    Claude Code, Cursor
```

Check the installed files:

```bash
ls .claude/rules/
ls .cursor/rules/
```

Open your IDE -- the AI coding assistant now follows your team's standards.

---

## Without AI (File-Copy Mode)

If the developer doesn't have an LLM API key:

```bash
devsync install https://github.com/company/team-standards --no-ai
```

Files are copied directly without AI adaptation. This still works -- the developer gets the same standards, just without intelligent merging with existing rules.

---

## Onboarding Script

Automate the entire process with a shell script:

```bash
#!/usr/bin/env bash
set -e

echo "Installing DevSync..."
pip install devsync

echo "Detecting AI tools..."
devsync tools

echo "Installing team standards..."
devsync install https://github.com/company/team-standards

echo "Verifying installation..."
devsync list

echo "Done! Your AI tools are configured."
```

---

## Next Steps

- [Team Config Repository](team-config-repo.md) -- create your own team standards
- [Multi-IDE Workflow](multi-ide-workflow.md) -- managing standards across multiple IDEs
