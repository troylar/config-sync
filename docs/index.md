# DevSync

**AI-powered dev config distribution across AI coding assistants.**

DevSync extracts coding practices from any project and installs them into 23+ AI coding assistants with intelligent adaptation. Two commands replace hours of manual configuration copying.

---

<div class="feature-grid" markdown>

<div class="feature-card" markdown>

### AI-Powered Extraction

Extract coding standards, style guides, and MCP configs from any project into shareable practice declarations.

[Get started](getting-started/quickstart.md){ .md-button }

</div>

<div class="feature-card" markdown>

### Intelligent Installation

AI adapts incoming practices to your existing setup -- merging, not overwriting.

[Install guide](cli/install.md){ .md-button }

</div>

<div class="feature-card" markdown>

### Configuration Packages

Bundle practices, MCP servers, hooks, commands, and resources into installable packages.

[Package guide](packages/index.md){ .md-button }

</div>

<div class="feature-card" markdown>

### 23+ IDE Integrations

Claude Code, Cursor, Windsurf, GitHub Copilot, Codex CLI, Cline, Kiro, Roo Code, Anteroom, and more.

[See all IDEs](ide-integrations/index.md){ .md-button }

</div>

</div>

---

## Quick Start

```bash
# Install DevSync
$ pip install devsync

# Configure your LLM provider (one-time)
$ devsync setup

# Check which AI tools are detected
$ devsync tools

# Extract practices from a project with existing rules
$ cd ~/my-team-project
$ devsync extract --output ./team-standards --name team-standards

# Install those practices into another project
$ cd ~/new-project
$ devsync install ~/my-team-project/team-standards
```

See the full [quickstart guide](getting-started/quickstart.md) for a 5-minute walkthrough.

---

## Why DevSync?

**For teams:**

- **Consistency** -- everyone uses the same AI instructions and tool configs
- **Onboarding** -- new developers get configured in minutes, not hours
- **Compliance** -- enforce security policies and review checklists automatically
- **No secrets in Git** -- credentials stay local, configurations are shared

**For individuals:**

- **Portable** -- same setup across all your machines
- **Composable** -- layer company, team, and personal configs
- **Works without AI** -- graceful degradation to file-copy mode when no API key
- **Safe** -- conflict resolution, checksums, installation tracking

---

## Supported IDEs

### Multi-file IDEs

| Tool | Instruction Path | Extension |
|------|-----------------|-----------|
| [Claude Code](ide-integrations/claude-code.md) | `.claude/rules/` | `.md` |
| [Cursor](ide-integrations/cursor.md) | `.cursor/rules/` | `.mdc` |
| [Windsurf](ide-integrations/windsurf.md) | `.windsurf/rules/` | `.md` |
| [GitHub Copilot](ide-integrations/copilot.md) | `.github/instructions/` | `.instructions.md` |
| [Roo Code](ide-integrations/other-ides.md#roo-code) | `.roo/rules/` | `.md` |
| [Cline](ide-integrations/other-ides.md#cline) | `.clinerules/` | `.md` |
| [Kiro](ide-integrations/other-ides.md#kiro) | `.kiro/steering/` | `.md` |
| + 8 more | [Full list](ide-integrations/index.md) | |

### Single-file IDEs

| Tool | Instruction File |
|------|-----------------|
| [Codex CLI](ide-integrations/codex.md) | `AGENTS.md` |
| [Aider](ide-integrations/other-ides.md#aider) | `CONVENTIONS.md` |
| [Gemini CLI](ide-integrations/other-ides.md#gemini-cli) | `GEMINI.md` |
| + 4 more | [Full list](ide-integrations/index.md) |

---

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Source Project  │────>│  Package with    │────>│  Target Project │
│  (team configs)  │     │  Practices       │     │  IDE Config     │
│                  │     │                  │     │  .cursor/rules/ │
└─────────────────┘     └──────────────────┘     │  .claude/rules/ │
    devsync extract         devsync install      │  .windsurf/...  │
                                                 └─────────────────┘
```

1. **Extract** practices from a project's existing rules, MCP configs, and commands
2. **Share** the resulting package via Git or local directory
3. **Install** into any project -- AI adapts practices to the recipient's existing setup
4. **Track** installations in `.devsync/packages.json` for management

---

## Documentation

| Section | What you'll find |
|---------|-----------------|
| [Getting Started](getting-started/installation.md) | Installation, quickstart, core concepts |
| [CLI Reference](cli/index.md) | All 6 commands with examples |
| [IDE Integrations](ide-integrations/index.md) | Setup guides for each AI tool |
| [Packages](packages/index.md) | Creating and installing config packages |
| [Tutorials](tutorials/team-config-repo.md) | Step-by-step walkthroughs |
| [Advanced](advanced/config-types.md) | Config types, conflict resolution, contributing |
| [Reference](reference/cli-reference.md) | Full CLI reference, YAML schemas |
