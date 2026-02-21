# devsync uninstall

Remove an installed package from your project's AI tools.

## Usage

```
$ devsync uninstall <name> [OPTIONS]
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `name` | Package name to uninstall | Yes |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--tool` | `-t` | Uninstall from a specific AI tool only |
| `--force` | `-f` | Skip the confirmation prompt |

## How It Works

The `uninstall` command removes files installed by a package from your project's AI tool configuration directories and updates the installation tracker (`.devsync/packages.json`). It only affects project-level installations.

Before removing, DevSync shows what will be uninstalled and asks for confirmation (unless `--force` is used).

## Examples

### Uninstall from all tools

```
$ devsync uninstall team-standards
```

This removes all files installed by the package from every AI tool in the current project.

### Uninstall from a specific tool

```
$ devsync uninstall team-standards --tool cursor
```

Only removes from Cursor, leaving other tools untouched.

### Uninstall without confirmation

```
$ devsync uninstall team-standards --force
```

### Typical workflow

```
$ devsync list                           # See what's installed
$ devsync uninstall team-standards       # Remove it
$ devsync list                           # Verify removal
```

!!! tip
    Uninstalling removes files from your AI tool directories (e.g., `.cursor/rules/`, `.claude/rules/`) and updates the tracking in `.devsync/packages.json`. You can reinstall the package later with `devsync install`.
