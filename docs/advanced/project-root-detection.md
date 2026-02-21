# Project Root Detection

DevSync uses project root detection to determine where to install configurations and store tracking data. All installation paths are relative to the project root, so correct detection is essential.

## How It Works

When you run a `devsync` command, the tool searches **upward** from the current working directory, checking each directory for known project marker files and directories. The first directory containing any marker is treated as the project root.

```
/home/user/projects/my-app/src/utils/
  -> checks /home/user/projects/my-app/src/utils/
  -> checks /home/user/projects/my-app/src/
  -> checks /home/user/projects/my-app/         <- has .git/, FOUND
```

If no marker is found after reaching the filesystem root, detection returns `None` and DevSync falls back to the current working directory (for some commands) or reports an error.

## Recognized Markers

The following files and directories are recognized as project root indicators, checked in order:

| Marker | Ecosystem |
|--------|-----------|
| `.git/` | Git repository (any language) |
| `pyproject.toml` | Python (PEP 517/518) |
| `package.json` | Node.js / JavaScript |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pom.xml` | Java (Maven) |
| `build.gradle` | Java (Gradle) |
| `composer.json` | PHP |
| `Gemfile` | Ruby |
| `.project` | Eclipse |
| `Makefile` | General build systems |

The search stops at the **first match**. Since `.git/` is checked first, a Git repository root takes precedence over nested build files.

## Why This Matters

Project root detection affects several aspects of DevSync:

**Installation paths.** Instructions are installed relative to the project root. For example, a Claude Code instruction goes to `<project-root>/.claude/rules/name.md`.

**Tracking data.** Installation records are stored in `<project-root>/.devsync/installations.json`. The `installed_path` field in each record uses relative paths so that tracking files are portable across machines and safe to commit to version control.

**Package operations.** The `devsync install` and `devsync list` commands use the project root to locate `.devsync/packages.json`.

## Running from Subdirectories

You can run `devsync` commands from any subdirectory within a project. The upward search finds the project root automatically:

```bash
cd ~/projects/my-app/src/components
devsync install ./team-standards  # installs to ~/projects/my-app/.claude/rules/...
```

## Overriding the Project Root

Some commands accept a `--project-dir` flag to explicitly specify the project root, bypassing auto-detection:

```bash
devsync install ./my-package --project-dir ~/projects/my-app
devsync extract --project-dir ~/projects/my-app --output ./pkg --name my-pkg
```

## Edge Cases

**No markers found.** If detection reaches the filesystem root without finding any markers, the function returns `None`. Commands that require a project root will display an error:

```
Error: Could not find project root. Use --project to specify explicitly.
```

**Nested repositories.** If your project contains nested Git repositories (e.g., Git submodules), the innermost `.git/` directory wins when running from within the submodule. Running from the parent project directory resolves to the parent root.

**Home directory.** If your home directory contains a `Makefile` or `package.json`, DevSync might incorrectly identify it as the project root when running from a subdirectory that lacks its own markers. Use `--project` to override in such cases.

## Implementation

Project root detection is implemented in `devsync/utils/project.py`:

- `find_project_root(start_path)` -- Searches upward from the given path (defaults to `cwd`). Returns a `Path` or `None`.
- `is_in_project()` -- Returns `True` if the current directory is within a detectable project.
- `get_project_instructions_dir(project_root)` -- Returns the `.devsync/` directory for a project, creating it if necessary.
- `get_project_installation_tracker_path(project_root)` -- Returns the path to `installations.json` for the project.
