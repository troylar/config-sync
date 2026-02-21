# Installation

DevSync requires Python 3.10+ and Git.

## Install from PyPI

```bash
$ pip install devsync
```

Verify the installation:

```bash
$ devsync version
DevSync version 2.0.0
```

!!! tip
    Use a virtual environment or `pipx` to avoid dependency conflicts:

    ```bash
    $ pipx install devsync
    ```

## Requirements

- **Python 3.10+** (3.10, 3.11, 3.12, 3.13 are tested)
- **Git** (for cloning instruction repositories)
- **One or more AI coding tools** (see [IDE Integrations](../ide-integrations/index.md))

## Configure LLM Provider

DevSync v2 uses an LLM to intelligently adapt practices to each IDE. Configure your provider once after installation:

```bash
$ devsync setup
```

This prompts for your LLM provider (Anthropic, OpenAI, or OpenRouter) and API key, stored in `~/.devsync/config.yaml`. Without a configured provider, DevSync falls back to file-copy mode.

## Check Detected IDEs

After installing, verify which AI tools DevSync detects on your system:

```bash
$ devsync tools
```

This scans for installed tools and shows their configuration paths. DevSync supports 23+ AI coding assistants -- see the [full list](../ide-integrations/index.md).

## Upgrading

```bash
$ pip install --upgrade devsync
```

## Development Install

To contribute or modify DevSync:

```bash
$ git clone https://github.com/troylar/devsync.git
$ cd devsync
$ pip install -e .[dev]
```

This installs DevSync in editable mode with development dependencies (pytest, black, ruff, mypy).

See [Contributing](../advanced/contributing.md) for the full development setup.

## Next Steps

- [Quickstart](quickstart.md) -- 5-minute guided walkthrough
- [Core Concepts](concepts.md) -- understand libraries, namespaces, and scopes
