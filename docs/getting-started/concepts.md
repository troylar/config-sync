# Core Concepts

Key ideas behind how DevSync v2 works.

## Practices

A **practice** is an abstract declaration of a coding standard or convention. Unlike raw instruction files, practices capture the _intent_ behind a rule, making them adaptable across different projects and IDEs.

A practice declaration includes:

| Field | Description |
|-------|-------------|
| `name` | Short identifier (e.g., `type-safety`) |
| `intent` | One-line description of what it enforces |
| `principles` | List of rules and guidelines |
| `enforcement_patterns` | How to enforce (CI checks, linting, etc.) |
| `examples` | Code examples demonstrating the practice |
| `tags` | Categorization tags |

When installed, DevSync's AI adapts each practice to the recipient's existing rules, merging rather than blindly overwriting.

## Packages

A **package** is a shareable bundle containing practices, MCP server configurations, and metadata. Packages are defined by a `devsync-package.yaml` manifest.

```
team-standards/
├── devsync-package.yaml    # Package manifest
├── practices/              # Practice declaration files
│   ├── type-safety.md
│   └── error-handling.md
├── mcp/                    # MCP server configurations
│   └── github.json
└── README.md
```

Packages can also include v1-format components (instructions, hooks, commands, resources) for backward compatibility with `ai-config-kit-package.yaml` manifests.

## Extraction

**Extraction** is the process of reading a project's existing AI rules and configurations to produce a package of practice declarations.

```bash
$ devsync extract --output ./team-standards --name team-standards
```

The AI reads rule files from `.claude/rules/`, `.cursor/rules/`, MCP configs, and other tool-specific locations. It produces abstract practice declarations that capture the intent of each rule, independent of any specific IDE format.

In **file-copy mode** (`--no-ai`), extraction copies source files verbatim without AI processing.

## Installation

**Installation** takes a package and applies its practices to a target project's AI tools.

```bash
$ devsync install ./team-standards
```

With AI enabled, installation reads the target project's existing rules and intelligently merges incoming practices -- avoiding duplication, resolving conflicts, and adapting content to the recipient's conventions.

In **file-copy mode** (`--no-ai`), installation copies files directly to tool-specific directories without AI adaptation.

## Graceful Degradation

DevSync works with or without an LLM API key:

| Mode | Extraction | Installation |
|------|-----------|-------------|
| **AI-powered** (default) | Reads rules, produces practice declarations | Adapts practices to existing setup |
| **File-copy** (`--no-ai`) | Copies source files verbatim | Copies files to tool directories |

No API key? DevSync automatically falls back to file-copy mode. You can also force it with `--no-ai`.

## v1 vs v2 Package Format

DevSync v2 introduces `devsync-package.yaml` with a `practices` section for AI-native content. It also supports the v1 `ai-config-kit-package.yaml` format for backward compatibility.

| Feature | v1 (`ai-config-kit-package.yaml`) | v2 (`devsync-package.yaml`) |
|---------|----------------------------------|---------------------------|
| Instructions | File-copy only | AI-adapted practices |
| MCP servers | Supported | Supported |
| Hooks, commands, resources | Supported | Supported |
| AI extraction | Not available | Built-in |
| AI installation | Not available | Built-in |

Use `devsync extract --upgrade <v1-package-path>` to convert a v1 package to v2 format.

## Conflict Resolution

When installing practices that overlap with existing rules, DevSync offers strategies:

| Strategy | Behavior |
|----------|----------|
| **prompt** | Ask what to do (default) |
| **skip** | Leave the existing file, don't install |
| **rename** | Install with a suffix (e.g., `rule-1.md`) |
| **overwrite** | Replace the existing file |

With AI enabled, DevSync can also **merge** practices into existing rules, combining content intelligently.

```bash
$ devsync install ./package --conflict overwrite
```

See [Conflict Resolution](../advanced/conflict-resolution.md) for details.

## Project Root Detection

DevSync automatically detects your project root by looking for markers like `.git/`, `pyproject.toml`, `package.json`, `Cargo.toml`, and others. This lets you run `devsync` from any subdirectory within a project.

See [Project Root Detection](../advanced/project-root-detection.md) for the full list of markers.

## AI Tool Detection

DevSync scans your system for installed AI tools by checking for their CLI commands and configuration directories. Run `devsync tools` to see what's detected. Each tool has its own file format, directory structure, and feature set -- DevSync handles the translation automatically.

See [IDE Integrations](../ide-integrations/index.md) for the full comparison.
