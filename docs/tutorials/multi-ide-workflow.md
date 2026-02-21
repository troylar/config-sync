# Tutorial: Multi-IDE Workflow

**Time:** 10 minutes | **Level:** Beginner

Install the same coding standards across multiple AI coding tools simultaneously.

---

## What You Will Learn

- How DevSync auto-detects installed tools
- How packages adapt to different IDE formats
- How to target specific tools

## Prerequisites

- DevSync installed (`pip install devsync`)
- Two or more AI coding tools installed

---

## Step 1: Detect Your Tools

```bash
devsync tools
```

```
AI Coding Tools
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Tool                ┃ Status        ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ Claude Code         │ ✓ Installed   │
│ Cursor              │ ✓ Installed   │
│ GitHub Copilot      │ ✓ Installed   │
│ Windsurf            │ ✗ Not found   │
│ Kiro                │ ✗ Not found   │
└─────────────────────┴───────────────┘

Found 3 installed tool(s)
```

## Step 2: Install to All Detected Tools

```bash
devsync install ./team-standards
```

DevSync automatically installs to every detected tool, adapting the format:

```
Installing team-standards...

  Claude Code:
    Created: .claude/rules/code-style.md
    Created: .claude/rules/testing.md

  Cursor:
    Created: .cursor/rules/code-style.mdc
    Created: .cursor/rules/testing.mdc

  GitHub Copilot:
    Created: .github/instructions/code-style.instructions.md
    Created: .github/instructions/testing.instructions.md
```

## File Format Differences

Each IDE has its own format. DevSync handles the translation:

| IDE | Directory | Extension | Notes |
|-----|-----------|-----------|-------|
| Claude Code | `.claude/rules/` | `.md` | Standard markdown |
| Cursor | `.cursor/rules/` | `.mdc` | Cursor markdown format |
| Windsurf | `.windsurf/rules/` | `.md` | Standard markdown |
| GitHub Copilot | `.github/instructions/` | `.instructions.md` | Special extension |
| Kiro | `.kiro/steering/` | `.md` | Standard markdown |
| Cline | `.clinerules/` | `.md` | Standard markdown |
| Roo Code | `.roo/rules/` | `.md` | Standard markdown |
| Codex CLI | `AGENTS.md` | Section markers | Single-file with sections |

## Step 3: Target Specific Tools

Install to specific tools only:

```bash
# Just Claude Code and Cursor
devsync install ./team-standards --tool claude --tool cursor

# Just Copilot
devsync install ./team-standards --tool copilot
```

## Step 4: Verify Across Tools

```bash
devsync list
```

Check individual IDE directories:

```bash
ls .claude/rules/
ls .cursor/rules/
ls .github/instructions/
```

## Component Support by IDE

Not all IDEs support all component types. DevSync automatically skips unsupported components:

| Component | Claude | Cursor | Windsurf | Copilot | Kiro | Cline | Roo |
|-----------|:------:|:------:|:--------:|:-------:|:----:|:-----:|:---:|
| Practices | Y | Y | Y | Y | Y | Y | Y |
| MCP Servers | Y | Y | Y | Y | -- | -- | Y |
| Hooks | Y | -- | -- | -- | -- | -- | -- |
| Commands | Y | -- | -- | -- | -- | -- | Y |
| Resources | Y | Y | Y | -- | Y | Y | Y |

---

## Keeping Tools in Sync

When you update your package, reinstall to all tools:

```bash
devsync install ./team-standards --conflict overwrite
```

This updates all detected tools at once.

---

## Next Steps

- [Team Config Repository](team-config-repo.md) -- share standards via Git
- [IDE Integrations](../ide-integrations/index.md) -- detailed guide for each IDE
