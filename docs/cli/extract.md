# devsync extract

Extract practices from a project into a shareable package. DevSync reads the project's existing AI rules, MCP configurations, and commands, then produces abstract practice declarations that can be installed into any project.

## Usage

```
$ devsync extract [OPTIONS]
```

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output directory for the package | `./devsync-package` |
| `--name` | `-n` | Package name | -- |
| `--no-ai` | -- | Use file-copy mode instead of AI extraction | `False` |
| `--project` | `-p` | Project directory to extract from | `.` |
| `--upgrade` | -- | Path to v1 package to upgrade to v2 format | -- |
| `--tool` | `-t` | Only extract from specific AI tool(s). Repeatable. | -- |
| `--component` | `-c` | Only extract specific component types (rules, mcp, hooks, commands, skills, workflows, memory, resources). Repeatable. | -- |
| `--dry-run` | -- | Show detected components without writing files or calling the LLM | `False` |
| `--include-global` | -- | Include home directory / global configs in extraction | `False` |

## Preview with Dry Run

Use `--dry-run` to see what would be extracted without writing any files or making LLM calls:

```bash
$ devsync extract --dry-run
```

```
Detected Components

  Component   Source    Count
  Rules       claude        6
  Rules       cursor        2
  MCP         claude        3
  Commands    claude       13

  Total: 24 components from 2 tools

Dry run — no files written.
```

Combine with filters to check what a filtered extraction would find:

```bash
$ devsync extract --dry-run --tool cursor --component rules
```

When filters match nothing, you'll see suggestions:

```
No components found matching your filters.

  Active: --tool cursor --component hooks

  Suggestions:
  - Run devsync extract --dry-run without filters to see all available components
  - Try --include-global to include home directory configs
```

## AI-Powered Mode (Default)

With an LLM configured (`devsync setup`), extraction reads rule files and produces abstract practice declarations that capture the _intent_ behind each rule:

```bash
$ devsync extract --output ./team-standards --name team-standards
```

```
Detected Components

  Component   Source    Count
  Rules       claude        3
  Rules       cursor        2
  MCP         claude        1

  Total: 6 components from 2 tools

Extraction complete (AI-powered)
  Practices generated: 4
  MCP servers: 1
  Source files: 5

  Package written to: ./team-standards/
```

The output directory contains:

```
team-standards/
├── devsync-package.yaml    # Package manifest with practices
├── practices/              # Practice declaration files
│   ├── type-safety.md
│   ├── error-handling.md
│   ├── code-style.md
│   └── testing.md
└── mcp/                    # MCP server configs
    └── github.json
```

## File-Copy Mode

Use `--no-ai` when you don't have an LLM configured or want exact file copies:

```bash
$ devsync extract --output ./team-standards --name team-standards --no-ai
```

In file-copy mode, source files are copied verbatim instead of being processed by an LLM. The resulting package works with `devsync install --no-ai`.

## Upgrading v1 Packages

Convert an existing v1 package (`ai-config-kit-package.yaml`) to v2 format:

```bash
$ devsync extract --upgrade ./old-v1-package --output ./v2-package --name my-package
```

This reads the v1 manifest and its component files, extracts practice declarations from the instructions, and produces a v2 package.

## Examples

### Extract from current directory

```bash
$ devsync extract --name my-project-standards
```

### Extract from a different project

```bash
$ devsync extract --project-dir ~/other-project --output ./other-standards --name other-standards
```

### Extract to a specific output location

```bash
$ devsync extract --output ~/shared/team-standards --name team-standards
```

### Extract only from specific tools

```bash
$ devsync extract --tool cursor --tool claude
```

Extract only from Cursor and Claude Code, skipping other tools.

### Extract only specific component types

```bash
$ devsync extract --component rules --component mcp
```

Extract only instruction rules and MCP configurations, skipping hooks, commands, etc.

### Include global configurations

```bash
$ devsync extract --include-global
```

By default, DevSync only scans the project directory. Use `--include-global` to include global AI tool configurations (e.g. `~/.cursor/mcp.json`) in addition to project-level ones.

### Combine filters

```bash
$ devsync extract --tool claude --component rules --include-global
```

Extract only instruction rules from Claude Code, including global configurations.

## What Gets Extracted

DevSync scans for:

| Source | Locations |
|--------|----------|
| Instructions/rules | `.claude/rules/`, `.cursor/rules/`, `.windsurf/rules/`, `.github/instructions/`, `.kiro/steering/`, `.clinerules/`, `.roo/rules/` |
| MCP configurations | `.claude/settings.local.json`, `.cursor/mcp.json`, `.vscode/mcp.json` |
| Hooks | `.claude/hooks/` |
| Commands | `.claude/commands/`, `.roo/commands/` |
| Skills | `.claude/skills/` |
| Workflows | `.windsurf/workflows/` |
| Memory files | `CLAUDE.md`, `GEMINI.md` |
| Single-file configs | `AGENTS.md`, `CONVENTIONS.md`, `ANTEROOM.md` |
| Resources | `.devsync/resources/` |

!!! tip
    Use `devsync tools --verbose` to see which component types each tool supports and the valid `--component` filter names.

!!! tip
    The more AI rule files your project has, the richer the extracted practices will be. DevSync works best when extracting from projects that already have well-defined coding standards.
