# CLI Reference

Complete reference for all `devsync` commands. Install with `pip install devsync`.

## `devsync setup`

Configure your LLM provider for AI-powered extraction and installation.

```
devsync setup
```

Interactive wizard that:

1. Prompts for provider selection (Anthropic, OpenAI, OpenRouter)
2. Auto-detects API keys from environment variables
3. Optionally overrides the default model
4. Saves configuration to `~/.devsync/config.yaml`

Default models per provider:

| Provider | Default Model |
|----------|--------------|
| Anthropic | `claude-sonnet-4-20250514` |
| OpenAI | `gpt-4o` |
| OpenRouter | `anthropic/claude-sonnet-4-20250514` |

!!! note
    API keys are never written to disk. Only the provider name and model are saved. Keys are read from environment variables at runtime.

---

## `devsync tools`

Show detected AI coding tools installed on your system.

```
devsync tools
```

No options. Displays a table of detected tools and their configuration directories.

---

## `devsync extract`

Extract practices from a project into a shareable package.

```
devsync extract [OPTIONS]
```

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output` | `-o` | `PATH` | `./devsync-package` | Output directory for the package |
| `--name` | `-n` | `TEXT` | -- | Package name |
| `--no-ai` | -- | flag | `False` | Use file-copy mode instead of AI extraction |
| `--project-dir` | `-p` | `PATH` | `.` | Project directory to extract from |
| `--upgrade` | `-u` | `PATH` | -- | Path to v1 package to upgrade to v2 format |

```bash
# AI-powered extraction
devsync extract --output ./team-standards --name team-standards

# File-copy mode (no LLM needed)
devsync extract --output ./team-standards --name team-standards --no-ai

# Extract from a different directory
devsync extract --project-dir ~/other-project --output ./pkg --name other-pkg

# Upgrade a v1 package to v2 format
devsync extract --upgrade ./old-v1-package --output ./v2-package --name my-package
```

---

## `devsync install`

Install a package into the current project with AI adaptation.

```
devsync install SOURCE [OPTIONS]
```

| Argument | Type | Description |
|----------|------|-------------|
| `SOURCE` | `TEXT` | Package source: local path, directory, or Git URL |

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--tool` | `-t` | `TEXT` | -- | Target AI tool(s). Repeatable. Auto-detects if not specified |
| `--no-ai` | -- | flag | `False` | Use file-copy mode instead of AI adaptation |
| `--conflict` | `-c` | `TEXT` | `prompt` | Conflict strategy: `prompt`, `skip`, `rename`, `overwrite` |
| `--project-dir` | `-p` | `PATH` | `.` | Target project directory |

```bash
# Install from local directory
devsync install ./team-standards

# Install from Git
devsync install https://github.com/company/standards

# Install to specific tools only
devsync install ./pkg --tool claude --tool cursor

# File-copy mode (no AI adaptation)
devsync install ./pkg --no-ai

# Auto-overwrite conflicts
devsync install ./pkg --conflict overwrite
```

---

## `devsync list`

List installed packages in the current project.

```
devsync list [OPTIONS]
```

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--tool` | `-t` | `TEXT` | -- | Filter by AI tool |
| `--json` | -- | flag | `False` | Output as JSON |

```bash
devsync list
devsync list --tool claude
devsync list --json
```

---

## `devsync uninstall`

Remove an installed package from the current project.

```
devsync uninstall NAME [OPTIONS]
```

| Argument | Type | Description |
|----------|------|-------------|
| `NAME` | `TEXT` | Package name to uninstall |

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--tool` | `-t` | `TEXT` | -- | Uninstall from specific AI tool only |
| `--force` | `-f` | flag | `False` | Skip confirmation prompt |

```bash
devsync uninstall team-standards
devsync uninstall team-standards --tool cursor
devsync uninstall team-standards --force
```

---

## `devsync version`

Show the installed DevSync version.

```
devsync version
```
