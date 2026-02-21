# Installing Packages

## Basic Installation

```bash
devsync install <source>
```

The `<source>` can be a local directory path or a Git URL.

```bash
# Local directory
devsync install ./team-standards

# Absolute path
devsync install /home/user/packages/team-standards

# Git URL
devsync install https://github.com/company/team-standards
```

## Command Options

```bash
devsync install <source> \
  [--tool <tool-name>] \
  [--no-ai] \
  [--conflict <strategy>] \
  [--project-dir <path>]
```

### `--tool, -t` (optional, repeatable)

Target specific AI tools. If omitted, DevSync auto-detects all installed tools.

```bash
# Install to Claude Code only
devsync install ./pkg --tool claude

# Install to Claude Code and Cursor
devsync install ./pkg --tool claude --tool cursor
```

### `--no-ai` (optional)

Skip AI adaptation and copy files directly:

```bash
devsync install ./pkg --no-ai
```

Useful when you don't have an LLM configured or want exact file copies.

### `--conflict, -c` (optional)

Conflict resolution strategy when files already exist. Default: `prompt`.

```bash
--conflict prompt      # Ask what to do (default)
--conflict skip        # Keep existing files
--conflict overwrite   # Replace existing files
--conflict rename      # Install with numbered suffix
```

See [Conflict Resolution](#conflict-resolution) below for detailed behavior.

### `--project-dir, -p` (optional)

Override the target project directory:

```bash
devsync install ./pkg --project-dir ~/other-project
```

## AI Adaptation

With AI enabled (default), DevSync intelligently merges practices with existing rules:

```bash
$ devsync install ./team-standards

Installing team-standards...

  Detected tools: Claude Code, Cursor

  Claude Code:
    Created: .claude/rules/type-safety.md
    Merged:  .claude/rules/code-style.md (adapted to existing)
    Created: .claude/rules/testing.md

  Cursor:
    Created: .cursor/rules/type-safety.mdc
    Merged:  .cursor/rules/code-style.mdc (adapted to existing)
    Created: .cursor/rules/testing.mdc

  MCP: Configured 1 server (1 credential prompted)

Installation complete.
```

The AI reads existing rules in the target project and:

- **Creates** new files for practices that don't exist
- **Merges** overlapping practices into existing files, avoiding duplication
- **Adapts** content to match the project's conventions

## Conflict Resolution

When an installed component targets a file that already exists:

### Prompt (Default)

Asks what to do for each conflict.

### Skip

Existing files are preserved. Conflicting components are not installed.

```bash
devsync install ./pkg --conflict skip
```

### Overwrite

Existing files are replaced with the package version.

```bash
devsync install ./pkg --conflict overwrite
```

!!! warning
    Overwrite permanently replaces local changes. Consider committing your changes to version control first.

### Rename

Both versions are kept. The new file receives a numbered suffix.

```bash
devsync install ./pkg --conflict rename
```

```
.claude/rules/code-quality.md      # original, untouched
.claude/rules/code-quality-1.md    # from package
```

## MCP Credential Prompting

If a package includes MCP servers that require credentials, DevSync prompts during installation:

```
MCP server "github" requires credentials:

  GITHUB_TOKEN (required): GitHub personal access token
  > [enter value]

  ALLOWED_DIRECTORIES (optional, default: "."): Directories to expose
  > [enter value or press Enter for default]
```

Credentials are set as environment variables -- never written to tracked files.

## IDE Filtering

Packages install different components per IDE based on capability:

=== "Claude Code"

    Gets all component types: practices, MCP servers, hooks, commands, resources.

=== "Cursor"

    Gets practices (as `.mdc` files), MCP servers, and resources. Hooks and commands are skipped.

=== "Windsurf"

    Gets practices, MCP servers, and resources. Hooks and commands are skipped.

=== "Other IDEs"

    Each IDE receives only the component types it supports. Run `devsync tools` to check support.

## Listing Installed Packages

```bash
$ devsync list
```

```
Installed packages in /home/user/my-project:

  team-standards     v1.0.0    4 practices, 1 MCP server    Claude Code, Cursor
  security-rules     v2.1.0    3 practices                  Claude Code

Total: 2 package(s)
```

### JSON output

```bash
devsync list --json
```

## Uninstalling Packages

```bash
devsync uninstall team-standards
```

This removes all files installed by the package and deletes the tracking record from `.devsync/packages.json`.

```bash
# Skip confirmation
devsync uninstall team-standards --force

# Uninstall from specific tool only
devsync uninstall team-standards --tool cursor
```

## Troubleshooting

### "Manifest not found"

Point to the package directory, not the YAML file:

```bash
# Correct
devsync install ./my-package

# Wrong
devsync install ./my-package/devsync-package.yaml
```

### Components not appearing in IDE

1. Verify the IDE supports the component type (see [IDE Compatibility](index.md#ide-compatibility))
2. Some IDEs require a restart to load new configuration files
3. Check that files were installed to the expected paths:

```bash
ls -la .claude/rules/     # Claude Code
ls -la .cursor/rules/     # Cursor
ls -la .windsurf/rules/   # Windsurf
```

### AI adaptation not working

1. Run `devsync setup` to configure your LLM provider
2. Ensure your API key environment variable is set
3. Use `--no-ai` as a fallback for file-copy mode
