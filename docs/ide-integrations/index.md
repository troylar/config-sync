# IDE Integrations

DevSync supports **23+ AI coding assistants**, each with its own file format, directory structure, and feature set. This page provides a complete comparison and links to detailed guides for the most popular tools.

## How DevSync Handles Different IDEs

AI coding tools fall into two patterns for storing instructions:

- **Multi-file**: Each instruction is a separate file in a directory (e.g., `.cursor/rules/code-style.mdc`). DevSync creates one file per instruction.
- **Single-file**: All instructions live in one file at the project root (e.g., `AGENTS.md`). DevSync manages sections within the file using HTML comment markers.

DevSync abstracts this difference away. The same `devsync install` command works regardless of the target IDE.

---

## Full Comparison Table

### Multi-File IDEs

These tools store instructions as individual files in a directory.

| Tool | Instruction Path | Extension | MCP Support | MCP Config Path | Hooks | Commands | Other |
|------|-----------------|-----------|:-----------:|-----------------|:-----:|:--------:|-------|
| [Claude Code](claude-code.md) | `.claude/rules/` | `.md` | Yes | `.claude/settings.local.json` | Yes | Yes | Skills, memory files |
| [Cursor](cursor.md) | `.cursor/rules/` | `.mdc` | Yes | `.cursor/mcp.json` | -- | -- | 40-tool MCP limit |
| [Windsurf](windsurf.md) | `.windsurf/rules/` | `.md` | Yes | `~/.codeium/windsurf/mcp_config.json` | -- | -- | Workflows, 100-tool limit |
| [GitHub Copilot](copilot.md) | `.github/instructions/` | `.instructions.md` | Yes | `.vscode/mcp.json` | -- | -- | 128-tool MCP limit |
| [Cline](other-ides.md#cline) | `.clinerules/` | `.md` | -- | -- | -- | -- | YAML frontmatter activation |
| [Kiro](other-ides.md#kiro) | `.kiro/steering/` | `.md` | -- | -- | -- | -- | YAML frontmatter modes |
| [Roo Code](other-ides.md#roo-code) | `.roo/rules/` | `.md` | Yes | `.roo/mcp.json` | -- | Yes | Mode-specific rules |
| [Amazon Q](other-ides.md#amazon-q) | `.amazonq/rules/` | `.md` | Yes | `.amazonq/mcp.json` | -- | -- | -- |
| [JetBrains AI](other-ides.md#jetbrains-ai) | `.aiassistant/rules/` | `.md` | Yes | `.aiassistant/mcp.json` | -- | -- | -- |
| [Continue.dev](other-ides.md#continuedev) | `.continue/rules/` | `.md` | Yes | `.continue/config.json` | -- | -- | -- |
| [Trae](other-ides.md#trae) | `.trae/rules/` | `.md` | Yes | `.mcp.json` | -- | -- | -- |
| [Augment](other-ides.md#augment) | `.augment/rules/` | `.md` | Yes | `.augment/mcp.json` | -- | -- | -- |
| [Tabnine](other-ides.md#tabnine) | `.tabnine/guidelines/` | `.md` | Yes | `.tabnine/mcp.json` | -- | -- | -- |
| [OpenHands](other-ides.md#openhands) | `.openhands/microagents/` | `.md` | Yes | `.openhands/mcp.json` | -- | -- | -- |
| [Antigravity](other-ides.md#antigravity) | `.agent/rules/` | `.md` | Yes | `.mcp.json` | -- | -- | -- |

### Single-File IDEs

These tools use a single file at the project root. DevSync manages sections with HTML comment markers.

| Tool | Instruction File | MCP Support | MCP Config Path | Section Marker Format |
|------|-----------------|:-----------:|-----------------|----------------------|
| [Codex CLI](codex.md) | `AGENTS.md` | -- | -- | `<!-- devsync:start:name -->` |
| [Amp](other-ides.md#amp) | `AGENTS.md` | -- | -- | `<!-- devsync:start:name -->` |
| [OpenCode](other-ides.md#opencode) | `AGENTS.md` | -- | -- | `<!-- devsync:start:name -->` |
| [Junie](other-ides.md#junie) | `.junie/guidelines.md` | -- | -- | `<!-- devsync:start:name -->` |
| [Zed](other-ides.md#zed) | `.rules` | Yes | `.zed/settings.json` | `<!-- devsync:start:name -->` |
| [Aider](other-ides.md#aider) | `CONVENTIONS.md` | -- | -- | `<!-- devsync:start:name -->` |
| [Gemini CLI](other-ides.md#gemini-cli) | `GEMINI.md` | Yes | `~/.gemini/settings.json` | `<!-- devsync:start:name -->` |

### MCP-Only

| Tool | Instructions | MCP Config Path | Notes |
|------|:----------:|-----------------|-------|
| [Claude Desktop](other-ides.md#claude-desktop) | -- | `~/Library/Application Support/Claude/claude_desktop_config.json` | MCP server configuration only |

---

## Package Component Support

Not every IDE supports every package component type. When you install a package, DevSync automatically skips unsupported components and reports what was skipped.

| Component | Claude Code | Cursor | Windsurf | Copilot | Roo Code | Others |
|-----------|:-----------:|:------:|:--------:|:-------:|:--------:|:------:|
| Instructions | Yes | Yes | Yes | Yes | Yes | Yes |
| MCP Servers | Yes | Yes | Yes | Yes | Yes | Varies |
| Hooks | Yes | -- | -- | -- | -- | -- |
| Commands | Yes | -- | -- | -- | Yes | -- |
| Skills | Yes | -- | -- | -- | -- | -- |
| Workflows | -- | -- | Yes | -- | -- | -- |
| Memory Files | Yes | -- | -- | -- | -- | -- |
| Resources | Yes | Yes | Yes | -- | Yes | Varies |

---

## Choosing an IDE

All IDEs receive the same instruction content. The differences are in what additional components they support:

- **Full package support**: Claude Code is the only IDE that supports all component types (instructions, MCP, hooks, commands, skills, memory files).
- **MCP + instructions**: Cursor, Windsurf, Copilot, Roo Code, and several others support both instructions and MCP server configuration.
- **Instructions only**: Cline, Kiro, Codex CLI, Aider, Amp, OpenCode, and Junie support instructions but not MCP configuration through DevSync.

For detailed setup instructions, see the individual IDE pages linked in the tables above.
