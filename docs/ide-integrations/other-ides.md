# Other IDE Integrations

This page covers all IDE integrations not detailed in their own pages. They are grouped by file pattern: multi-file IDEs (one file per instruction) and single-file IDEs (sections within a shared file).

---

## Multi-File IDEs

These tools store each instruction as a separate file in a dedicated directory.

### Cline

| Property | Value |
|----------|-------|
| **Instruction path** | `.clinerules/*.md` |
| **File extension** | `.md` |
| **MCP support** | No (global-only via VS Code globalStorage) |
| **Detection** | Cline extension directory in VS Code globalStorage |

Cline reads `.md` files from the `.clinerules/` directory recursively. Files support optional YAML frontmatter with a `paths:` field for conditional activation based on file paths.

```bash
devsync install ./my-package --tool cline
```

```
my-project/
  .clinerules/
    code-style.md
    testing.md
```

---

### Kiro

| Property | Value |
|----------|-------|
| **Instruction path** | `.kiro/steering/*.md` |
| **File extension** | `.md` |
| **MCP support** | No (deferred to future release) |
| **Detection** | `.kiro/` directory or Kiro application config |

Kiro reads markdown files from `.kiro/steering/`. Files support optional YAML frontmatter for inclusion modes: `always`, `fileMatch`, `manual`, and `auto`.

```bash
devsync install ./my-package --tool kiro
```

```
my-project/
  .kiro/
    steering/
      code-style.md
      testing.md
```

---

### Roo Code

| Property | Value |
|----------|-------|
| **Instruction path** | `.roo/rules/*.md` |
| **File extension** | `.md` |
| **MCP config (project)** | `.roo/mcp.json` |
| **Commands directory** | `.roo/commands/` |
| **Global rules** | `~/.roo/rules/` |
| **Detection** | Roo Code extension in VS Code globalStorage |

Roo Code supports instructions, MCP servers, and slash commands. It also supports mode-specific rules in `.roo/rules-{mode-slug}/` directories (e.g., `.roo/rules-code/`, `.roo/rules-architect/`).

```bash
devsync install ./my-package --tool roo
```

```
my-project/
  .roo/
    mcp.json
    rules/
      code-style.md
    commands/
      deploy.md
```

**Supported components**: Instructions, MCP Servers, Commands, Resources

---

### Amazon Q

| Property | Value |
|----------|-------|
| **Instruction path** | `.amazonq/rules/*.md` |
| **File extension** | `.md` |
| **MCP config (project)** | `.amazonq/mcp.json` |
| **Detection** | Amazon Q extension or application config |

```bash
devsync install ./my-package --tool amazonq
```

**Supported components**: Instructions, MCP Servers, Resources

---

### JetBrains AI

| Property | Value |
|----------|-------|
| **Instruction path** | `.aiassistant/rules/*.md` |
| **File extension** | `.md` |
| **MCP config (project)** | `.aiassistant/mcp.json` |
| **Detection** | JetBrains IDE configuration directory |

```bash
devsync install ./my-package --tool jetbrains
```

**Supported components**: Instructions, MCP Servers, Resources

---

### Continue.dev

| Property | Value |
|----------|-------|
| **Instruction path** | `.continue/rules/*.md` |
| **File extension** | `.md` |
| **MCP config (project)** | `.continue/config.json` |
| **Detection** | Continue extension in VS Code globalStorage |

```bash
devsync install ./my-package --tool continue
```

**Supported components**: Instructions, MCP Servers, Resources

---

### Trae

| Property | Value |
|----------|-------|
| **Instruction path** | `.trae/rules/*.md` |
| **File extension** | `.md` |
| **MCP config (project)** | `.mcp.json` (project root) |
| **Detection** | Trae application configuration directory |

```bash
devsync install ./my-package --tool trae
```

**Supported components**: Instructions, MCP Servers, Resources

---

### Augment

| Property | Value |
|----------|-------|
| **Instruction path** | `.augment/rules/*.md` |
| **File extension** | `.md` |
| **MCP config (project)** | `.augment/mcp.json` |
| **Detection** | Augment extension or application config |

```bash
devsync install ./my-package --tool augment
```

**Supported components**: Instructions, MCP Servers, Resources

---

### Tabnine

| Property | Value |
|----------|-------|
| **Instruction path** | `.tabnine/guidelines/*.md` |
| **File extension** | `.md` |
| **MCP config (project)** | `.tabnine/mcp.json` |
| **Detection** | Tabnine application configuration directory |

```bash
devsync install ./my-package --tool tabnine
```

**Supported components**: Instructions, MCP Servers, Resources

---

### OpenHands

| Property | Value |
|----------|-------|
| **Instruction path** | `.openhands/microagents/*.md` |
| **File extension** | `.md` |
| **MCP config (project)** | `.openhands/mcp.json` |
| **Detection** | OpenHands configuration directory |

```bash
devsync install ./my-package --tool openhands
```

**Supported components**: Instructions, MCP Servers, Resources

---

### Antigravity

| Property | Value |
|----------|-------|
| **Instruction path** | `.agent/rules/*.md` |
| **File extension** | `.md` |
| **MCP config (project)** | `.mcp.json` (project root) |
| **Detection** | `.agent/` directory or Antigravity application config |

Antigravity IDE (Google's VS Code fork) reads instructions from `.agent/rules/` and MCP configuration from `.mcp.json` at the project root.

```bash
devsync install ./my-package --tool antigravity
```

**Supported components**: Instructions, MCP Servers, Resources

---

## Multi-File Summary

| Tool | Instruction Path | MCP Config | Commands |
|------|-----------------|------------|:--------:|
| Cline | `.clinerules/*.md` | -- | -- |
| Kiro | `.kiro/steering/*.md` | -- | -- |
| Roo Code | `.roo/rules/*.md` | `.roo/mcp.json` | Yes |
| Amazon Q | `.amazonq/rules/*.md` | `.amazonq/mcp.json` | -- |
| JetBrains AI | `.aiassistant/rules/*.md` | `.aiassistant/mcp.json` | -- |
| Continue.dev | `.continue/rules/*.md` | `.continue/config.json` | -- |
| Trae | `.trae/rules/*.md` | `.mcp.json` | -- |
| Augment | `.augment/rules/*.md` | `.augment/mcp.json` | -- |
| Tabnine | `.tabnine/guidelines/*.md` | `.tabnine/mcp.json` | -- |
| OpenHands | `.openhands/microagents/*.md` | `.openhands/mcp.json` | -- |
| Antigravity | `.agent/rules/*.md` | `.mcp.json` | -- |

---

## Single-File IDEs

These tools use a single file at the project root. DevSync manages sections within the file using HTML comment markers (`<!-- devsync:start:name -->` / `<!-- devsync:end:name -->`).

For a detailed explanation of how section markers work, see the [Codex CLI](codex.md) page.

### Junie

| Property | Value |
|----------|-------|
| **Instruction file** | `.junie/guidelines.md` |
| **MCP support** | No |
| **Detection** | JetBrains Junie extension or `.junie/` directory |

JetBrains Junie reads a single `.junie/guidelines.md` file. DevSync inserts sections with markers.

```bash
devsync install ./my-package --tool junie
```

**Supported components**: Instructions, Resources

---

### Zed

| Property | Value |
|----------|-------|
| **Instruction file** | `.rules` (project root) |
| **MCP config (project)** | `.zed/settings.json` |
| **Detection** | Zed application configuration or `.zed/` directory |

Zed reads a single `.rules` file at the project root. MCP servers are configured through `.zed/settings.json`.

```bash
devsync install ./my-package --tool zed
```

**Supported components**: Instructions, MCP Servers, Resources

---

### Aider

| Property | Value |
|----------|-------|
| **Instruction file** | `CONVENTIONS.md` (project root) |
| **MCP support** | No |
| **Detection** | `aider` binary on system PATH |

Aider reads a single `CONVENTIONS.md` file at the project root.

```bash
devsync install ./my-package --tool aider
```

**Supported components**: Instructions, Resources

---

### Amp

| Property | Value |
|----------|-------|
| **Instruction file** | `AGENTS.md` (project root) |
| **MCP support** | No |
| **Detection** | `amp` binary on system PATH or Amp configuration directory |

Amp uses the same `AGENTS.md` file as Codex CLI and OpenCode. See the [Codex CLI](codex.md#shared-file-codex-cli-amp-and-opencode) page for details on how shared files are handled.

```bash
devsync install ./my-package --tool amp
```

**Supported components**: Instructions, Resources

---

### OpenCode

| Property | Value |
|----------|-------|
| **Instruction file** | `AGENTS.md` (project root) |
| **MCP support** | No |
| **Detection** | `opencode` binary on system PATH or OpenCode configuration directory |

OpenCode uses the same `AGENTS.md` file as Codex CLI and Amp. See the [Codex CLI](codex.md#shared-file-codex-cli-amp-and-opencode) page for details on how shared files are handled.

```bash
devsync install ./my-package --tool opencode
```

**Supported components**: Instructions, Resources

---

### Gemini CLI

| Property | Value |
|----------|-------|
| **Instruction file** | `GEMINI.md` (project root) |
| **MCP config (global)** | `~/.gemini/settings.json` |
| **Detection** | `gemini` binary on system PATH or `~/.gemini/` directory |

Gemini CLI and Gemini Code Assist read a single `GEMINI.md` file at the project root. MCP servers are configured globally via `~/.gemini/settings.json`.

```bash
devsync install ./my-package --tool gemini
```

**Supported components**: Instructions, Resources

---

## Single-File Summary

| Tool | Instruction File | MCP Config |
|------|-----------------|------------|
| Junie | `.junie/guidelines.md` | -- |
| Zed | `.rules` | `.zed/settings.json` |
| Aider | `CONVENTIONS.md` | -- |
| Amp | `AGENTS.md` | -- |
| OpenCode | `AGENTS.md` | -- |
| Gemini CLI | `GEMINI.md` | `~/.gemini/settings.json` |

---

## Claude Desktop

| Property | Value |
|----------|-------|
| **Instructions** | Not supported |
| **MCP config** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Detection** | Claude Desktop application support directory |

Claude Desktop is an MCP-only integration. It does not support instruction files. DevSync can manage MCP server configuration in the Claude Desktop config file.

The MCP config path is platform-specific:

| Platform | Path |
|----------|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

```bash
# Install a package with MCP server configuration to Claude Desktop
devsync install ./my-package --tool claude-desktop
```
