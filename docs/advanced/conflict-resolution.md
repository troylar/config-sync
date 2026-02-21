# Conflict Resolution

In v2, DevSync uses AI-powered merging as the primary approach to conflict resolution. When a practice or instruction already exists in a target IDE's rule directory, the LLM reads both the incoming content and the existing content and produces a semantically merged result, preserving any local customizations while incorporating the new standards.

File-level strategies (skip, overwrite, rename) are still available as fallback modes -- used when running with `--no-ai`, when the LLM is unavailable, or when explicitly requested via the `--conflict` flag.

## When Conflicts Occur

A conflict is detected when:

- An instruction file already exists at the target path (e.g., `.cursor/rules/python-style.mdc` already exists)
- A section with the same name already exists in a single-file IDE (e.g., an `AGENTS.md` section with the same marker)
- A package component would overwrite an existing file

## Resolution Strategies

DevSync provides four conflict resolution strategies.

### AI Merge (Default in v2)

When an LLM provider is configured, the default behavior is to let the AI merge incoming practice content with the existing rule file. The LLM reads both versions and produces a unified result that preserves local customizations while incorporating the new standards.

To configure an LLM provider, run `devsync setup` before installing packages.

For non-AI fallback, DevSync displays a prompt:

```
Conflict: Instruction 'python-style' already exists.
How would you like to resolve this?
  [K]eep local version (ignore remote update)
  [O]verwrite with remote version (discard local changes)
  [R]ename local and install remote

Your choice [k/o/r]:
```

### Skip

Keeps the existing file unchanged. The new instruction is not installed.

```bash
devsync install python-style --conflict skip
```

Use this when you want to preserve any existing configurations without interruption.

### Overwrite

Replaces the existing file with the new content.

!!! warning "Automatic Backup"
    When using the overwrite strategy during template operations, DevSync automatically creates a timestamped backup of the existing file before overwriting it. Backups are stored in `.devsync/backups/<timestamp>/`.

    ```
    Backup created: 20260215_143052/python-style.md
    ```

```bash
devsync install python-style --conflict overwrite
```

### Rename

Installs the new instruction with an auto-incremented suffix to avoid overwriting the existing file. The existing file is left untouched.

```bash
devsync install python-style --conflict rename
```

This generates filenames like:

- `python-style-1.md`
- `python-style-2.md`

For template conflicts with the rename strategy, the existing local file is renamed (preserving local changes) and the new remote version is installed at the original path.

## Setting Strategy via CLI

### Instructions

Use the `--conflict` (or `-c`) flag with `devsync install`:

```bash
# Interactive prompt (default)
devsync install python-style

# Skip conflicts silently
devsync install python-style --conflict skip

# Overwrite existing files
devsync install python-style --conflict overwrite

# Rename to avoid conflicts
devsync install python-style --conflict rename
```

### Packages

Use the `--conflict` (or `-c`) flag with `devsync install`:

```bash
devsync install ./my-package --tool claude --conflict overwrite
```

## Upgrade Detection

When reinstalling an instruction from a newer version of a source repository, DevSync detects version changes and prompts for confirmation.

The upgrade detection workflow:

1. DevSync checks the installation tracker for existing records of the instruction
2. If the instruction exists and comes from the same source, it compares the `source_ref` (Git tag, branch, or commit)
3. If versions differ, it displays a side-by-side comparison:

```
Upgrade available: python-style
  Current: v1.0.0
  New:     v2.0.0

Proceed with upgrade? [y/N]:
```

This works across all AI tools and respects the configured conflict resolution strategy.

## Name Collision Handling

When an instruction with the same name exists from a **different** repository, DevSync treats this as a name collision rather than an upgrade.

The collision handling workflow:

1. DevSync queries the installation tracker with `find_instructions_by_name()` to find existing installations
2. If the instruction exists from a different source, it displays detailed information:

```
Name collision: 'python-style' already installed
  Existing source: github.com/team-a/instructions
  New source:      github.com/team-b/instructions

Options:
  1. Provide custom filename
  2. Skip installation
```

3. The user can provide an alternative filename to install both instructions without conflict, or skip the installation entirely.

## Checksum-Based Conflict Detection

For template operations, DevSync uses a three-way checksum comparison to determine the exact nature of a conflict:

| Current File | Original (at install) | New Template | Result |
|---|---|---|---|
| Unchanged | -- | Unchanged | No conflict |
| Unchanged | -- | Changed | No conflict (safe to update) |
| Changed | -- | Unchanged | `LOCAL_MODIFIED` |
| Changed | -- | Changed | `BOTH_MODIFIED` |

- **No conflict**: The file can be updated automatically
- **LOCAL_MODIFIED**: The user modified the file but the remote template has not changed. The prompt asks whether to keep local or overwrite.
- **BOTH_MODIFIED**: Both the local file and the remote template have changed. The prompt asks the user to choose which version to keep or to rename the local copy.

All checksums use SHA-256 for integrity verification.

## Batch Conflict Resolution

When installing a package with multiple practices, DevSync can apply the same strategy to all conflicts:

```bash
# Skip all conflicts in a batch install
devsync install ./team-standards --conflict skip

# Overwrite all existing files
devsync install ./team-standards --conflict overwrite
```

The `batch_resolve_conflicts()` function applies the chosen strategy uniformly to all detected conflicts in a single operation.

## Backup Integration

Backups are created automatically before any destructive overwrite operation. The backup system:

- Stores backups in `.devsync/backups/<YYYYMMDD_HHMMSS>/`
- Preserves the original filename
- Handles name collisions within the same timestamp directory by appending a counter suffix
