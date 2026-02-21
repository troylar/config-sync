# CLI Reference

DevSync provides the `devsync` command for managing AI coding assistant configurations across your projects.

## Usage

```
$ devsync <command> [options]
```

## Commands

| Command | Description |
|---------|-------------|
| [`setup`](setup.md) | Configure LLM provider (one-time) |
| [`tools`](tools.md) | Detect installed AI coding tools |
| [`extract`](extract.md) | Extract practices from a project |
| [`install`](install.md) | Install a package with AI adaptation |
| [`list`](list.md) | Show installed packages |
| [`uninstall`](uninstall.md) | Remove an installed package |

## Typical Workflow

```bash
# 1. One-time setup
devsync setup

# 2. In your source project, extract practices
cd ~/team-project
devsync extract --output ./team-standards --name team-standards

# 3. In your target project, install
cd ~/new-project
devsync install ~/team-project/team-standards

# 4. Check what's installed
devsync list

# 5. Remove if needed
devsync uninstall team-standards
```

## Global Options

```
$ devsync --help       # Show help
$ devsync --version    # Show version
```

Every command supports `--help` for detailed usage:

```
$ devsync setup --help
$ devsync extract --help
$ devsync install --help
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOGLEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |
| `ANTHROPIC_API_KEY` | Anthropic API key (auto-detected by `devsync setup`) | -- |
| `OPENAI_API_KEY` | OpenAI API key (auto-detected by `devsync setup`) | -- |
| `OPENROUTER_API_KEY` | OpenRouter API key (auto-detected by `devsync setup`) | -- |

```
$ LOGLEVEL=DEBUG devsync install ./package
```
