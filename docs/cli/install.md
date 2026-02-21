# devsync install

Install a package into the current project. DevSync auto-detects your AI tools and adapts practices to your existing setup using AI.

## Usage

```
$ devsync install <source> [OPTIONS]
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `source` | Package source: local directory path or Git URL | Yes |

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--tool` | `-t` | Target AI tool(s), repeatable. Auto-detects if not specified | -- |
| `--no-ai` | -- | Use file-copy mode instead of AI adaptation | `False` |
| `--conflict` | `-c` | Conflict resolution: `prompt`, `skip`, `rename`, `overwrite` | `prompt` |
| `--project-dir` | `-p` | Target project directory | `.` |

## How It Works

1. **Parse package** -- reads `devsync-package.yaml` (v2) or `ai-config-kit-package.yaml` (v1)
2. **Detect tools** -- finds installed AI tools (or uses `--tool` filter)
3. **AI adaptation** -- uses LLM to merge practices with your existing rules
4. **Display plan** -- shows what will be created, merged, or skipped
5. **Install files** -- writes adapted files to tool-specific directories
6. **MCP credentials** -- prompts for any required MCP server credentials
7. **Track** -- records installation in `.devsync/packages.json`

## Sources

### Local directory

```bash
$ devsync install ./team-standards
$ devsync install ~/packages/security-compliance
```

### Git URL

```bash
$ devsync install https://github.com/company/team-standards
```

DevSync clones the repository and installs from it.

## AI Adaptation

With AI enabled (default), DevSync reads your existing rules and intelligently merges incoming practices:

- **New practices** are written as new files
- **Overlapping practices** are merged with existing rules, avoiding duplication
- **Conflicting content** follows the chosen conflict strategy

```bash
$ devsync install ./team-standards

Installing team-standards...

  Claude Code:
    Created: .claude/rules/type-safety.md
    Merged:  .claude/rules/code-style.md (adapted to existing)
    Created: .claude/rules/testing.md

  Cursor:
    Created: .cursor/rules/type-safety.mdc
    Merged:  .cursor/rules/code-style.mdc (adapted to existing)
    Created: .cursor/rules/testing.mdc
```

## File-Copy Mode

Use `--no-ai` to skip AI adaptation and copy files directly:

```bash
$ devsync install ./team-standards --no-ai
```

This copies practice files verbatim to each tool's directory, converting file extensions as needed (e.g., `.md` to `.mdc` for Cursor).

## Targeting Specific Tools

By default, DevSync installs to all detected AI tools. Use `--tool` to target specific ones:

```bash
# Install to Claude Code only
$ devsync install ./pkg --tool claude

# Install to Claude Code and Cursor
$ devsync install ./pkg --tool claude --tool cursor
```

Valid tool names: `claude`, `cursor`, `windsurf`, `copilot`, `kiro`, `cline`, `roo`, `codex`, `gemini`, and more. Run `devsync tools` for the full list.

## Conflict Resolution

When a file already exists at the target path:

| Strategy | Behavior |
|----------|----------|
| `prompt` | Ask what to do (default) |
| `skip` | Keep existing file, don't install |
| `rename` | Install with a numeric suffix (e.g., `rule-1.md`) |
| `overwrite` | Replace the existing file |

```bash
$ devsync install ./pkg --conflict skip
$ devsync install ./pkg --conflict overwrite
```

## MCP Credential Prompting

If a package includes MCP server configurations that require credentials, DevSync prompts for them during installation:

```
MCP server "github" requires credentials:

  GITHUB_TOKEN (required): GitHub personal access token
  > [enter value]
```

Credentials are written to environment-specific locations (never to tracked files).

## v1 Package Compatibility

DevSync automatically detects v1 packages (`ai-config-kit-package.yaml`) and installs them using file-copy mode. Components are filtered by IDE capability -- unsupported component types are skipped automatically.

## Examples

### Install from a local package

```bash
$ devsync install ./team-standards
```

### Install from Git

```bash
$ devsync install https://github.com/company/standards
```

### Install to specific tools with conflict handling

```bash
$ devsync install ./pkg --tool claude --tool cursor --conflict overwrite
```

### Install without AI

```bash
$ devsync install ./pkg --no-ai
```

### Install to a different project

```bash
$ devsync install ./pkg --project-dir ~/other-project
```
