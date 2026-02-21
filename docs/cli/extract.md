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
| `--project-dir` | `-p` | Project directory to extract from | `.` |
| `--upgrade` | `-u` | Path to v1 package to upgrade to v2 format | -- |

## AI-Powered Mode (Default)

With an LLM configured (`devsync setup`), extraction reads rule files and produces abstract practice declarations that capture the _intent_ behind each rule:

```bash
$ devsync extract --output ./team-standards --name team-standards
```

```
Extracting practices from /home/user/my-project...

  Scanning: .claude/rules/ (3 files)
  Scanning: .cursor/rules/ (2 files)
  Scanning: MCP configurations (1 server)

  Extracted 4 practice declarations:
    - type-safety: Enforce strict type annotations
    - error-handling: Structured error handling patterns
    - code-style: Formatting and naming conventions
    - testing: Test-first development practices

  Extracted 1 MCP server:
    - github: GitHub API access

Package written to: ./team-standards/devsync-package.yaml
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

## What Gets Extracted

DevSync scans for:

| Source | Locations |
|--------|----------|
| Instructions/rules | `.claude/rules/`, `.cursor/rules/`, `.windsurf/rules/`, `.github/instructions/`, `.kiro/steering/`, `.clinerules/`, `.roo/rules/` |
| MCP configurations | `.claude/settings.local.json`, `.cursor/mcp.json`, `.vscode/mcp.json` |
| Single-file configs | `AGENTS.md`, `CONVENTIONS.md`, `GEMINI.md` |

!!! tip
    The more AI rule files your project has, the richer the extracted practices will be. DevSync works best when extracting from projects that already have well-defined coding standards.
