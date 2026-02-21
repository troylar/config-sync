# OpenAI Codex CLI

Codex CLI uses a single `AGENTS.md` file at the project root. DevSync manages individual instruction sections within this file using HTML comment markers, allowing multiple instructions to coexist without conflicts.

## Overview

| Property | Value |
|----------|-------|
| **Instruction file** | `AGENTS.md` (project root) |
| **File pattern** | Single file with section markers |
| **MCP support** | No |
| **Hooks** | No |
| **Commands** | No |
| **Project scope** | Yes |
| **Global scope** | No |

---

## How It Works

Unlike multi-file IDEs (Cursor, Claude Code, etc.), Codex CLI reads a single `AGENTS.md` file. DevSync handles this by embedding each instruction as a marked section:

```markdown
<!-- devsync:start:code-style -->
# Code Style Guidelines

- Use type hints on all function signatures
- Prefer early returns to reduce nesting
- Maximum line length: 120 characters
<!-- devsync:end:code-style -->

<!-- devsync:start:testing-standards -->
# Testing Standards

- Write tests before implementation
- Minimum 80% code coverage
- Use fixtures for shared test state
<!-- devsync:end:testing-standards -->
```

### Section Markers

Each instruction is wrapped in a pair of HTML comment markers:

```
<!-- devsync:start:<instruction-name> -->
... instruction content ...
<!-- devsync:end:<instruction-name> -->
```

- Codex CLI treats HTML comments as invisible, so the markers do not affect the instructions.
- Each section can be independently installed, updated, or uninstalled.
- Manual content outside of DevSync markers is preserved.

---

## Installing Instructions

```bash
# Install a package from a local path
devsync install ./my-package --tool codex

# Install a package from a Git repository
devsync install https://github.com/acme/standards --tool codex

# Overwrite an existing section
devsync install ./my-package --tool codex --conflict overwrite
```

### What Happens During Installation

1. If `AGENTS.md` does not exist, DevSync creates it with the instruction section.
2. If `AGENTS.md` exists and does not contain the instruction's markers, DevSync appends the section.
3. If the markers already exist and `--conflict overwrite` is set, DevSync replaces the section content.
4. If the markers already exist and no conflict flag is set, DevSync reports the conflict and skips.

---

## Uninstalling Instructions

```bash
devsync uninstall my-package --tool codex
```

DevSync removes the section between the matching markers and cleans up extra blank lines. Other content in `AGENTS.md` -- including other DevSync sections and manually written content -- is preserved.

---

## Shared File: Codex CLI, Amp, and OpenCode

Codex CLI, [Amp](other-ides.md#amp), and [OpenCode](other-ides.md#opencode) all use `AGENTS.md` at the project root. If you install instructions to multiple single-file IDEs that share the same file, the sections coexist:

```bash
# These all write to the same AGENTS.md
devsync install ./my-package --tool codex
devsync install ./my-package --tool amp
devsync install ./my-package --tool opencode
```

!!! note
    DevSync tracks each installation separately per IDE. Installing the same instruction to both Codex and Amp creates a single section in `AGENTS.md` (not duplicates), but both installations are recorded in the tracker.

---

## Detection

DevSync detects Codex CLI by checking if the `codex` binary is available on the system PATH. Verify with:

```bash
devsync tools
```

---

## Package Component Support

| Component | Supported | Install Location |
|-----------|:---------:|-----------------|
| Instructions | Yes | `AGENTS.md` (section) |
| MCP Servers | -- | Not supported |
| Hooks | -- | Not supported |
| Commands | -- | Not supported |
| Skills | -- | Not supported |
| Workflows | -- | Not supported |
| Resources | Yes | Project directory |

---

## Example: Multiple Instructions

```bash
# Install a package containing several practices
devsync install ./team-standards --tool codex
```

Result in `AGENTS.md`:

```markdown
<!-- devsync:start:code-style -->
# Code Style Guidelines

Use type hints on all functions. Prefer early returns.
<!-- devsync:end:code-style -->

<!-- devsync:start:security-rules -->
# Security Rules

Never hardcode credentials. Use parameterized queries.
<!-- devsync:end:security-rules -->

<!-- devsync:start:api-conventions -->
# API Conventions

Use RESTful naming. Version all endpoints.
<!-- devsync:end:api-conventions -->
```
