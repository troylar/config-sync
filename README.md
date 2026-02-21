<div align="center">

# DevSync

**AI-powered config distribution for AI coding assistants**

[![CI](https://github.com/troylar/devsync/actions/workflows/ci.yml/badge.svg)](https://github.com/troylar/devsync/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/devsync/badge/?version=latest)](https://devsync.readthedocs.io)
[![PyPI version](https://img.shields.io/pypi/v/devsync.svg)](https://pypi.org/project/devsync/)
[![Coverage](https://codecov.io/gh/troylar/devsync/branch/main/graph/badge.svg)](https://codecov.io/gh/troylar/devsync)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Works with:** Aider | Amazon Q | Amp | Antigravity | Augment | Claude Code | Claude Desktop | Cline | Codex CLI | Continue.dev | Cursor | Gemini CLI | GitHub Copilot | JetBrains AI | Junie | Kiro | OpenCode | OpenHands | Roo Code | Tabnine | Trae | Windsurf | Zed

</div>

---

DevSync uses LLM intelligence to extract coding practices from projects and adapt them to recipients' existing setups -- across 23+ AI coding assistants. Two commands: `extract` and `install`.

## Quick Start

```bash
pip install devsync

# One-time: configure your LLM provider
devsync setup

# Check detected AI tools
devsync tools

# Extract practices from a project
devsync extract

# Install a package into another project
devsync install ./team-standards

# Install from Git
devsync install https://github.com/company/standards
```

No API key? DevSync works without one -- it falls back to file-copy mode. Add `--no-ai` to any command to force this.

## Features

- **AI-powered extraction** -- LLM reads your project's rules, MCP configs, and commands to produce abstract practice declarations
- **AI-powered installation** -- LLM adapts incoming practices to your existing setup with intelligent merging
- **23+ AI tool integrations** -- Claude Code, Cursor, Windsurf, GitHub Copilot, Kiro, Roo Code, Cline, Codex, and more
- **MCP credential handling** -- prompts for credentials at install time, never stores them in repos
- **v1 backward compatibility** -- old `ai-config-kit-package.yaml` packages still install via file-copy
- **Graceful degradation** -- works without an API key, `--no-ai` flag for explicit file-copy mode

## Commands

| Command | Description |
|---------|-------------|
| `devsync setup` | Configure LLM provider (Anthropic, OpenAI, OpenRouter) |
| `devsync tools` | Detect installed AI coding tools |
| `devsync extract` | Extract practices from current project into a shareable package |
| `devsync install <source>` | Install a package with AI-powered adaptation |
| `devsync list` | Show installed packages |
| `devsync uninstall <name>` | Remove an installed package |

## Migrating from v1

If you have v1 packages (`ai-config-kit-package.yaml`), they still work with `devsync install`. To upgrade them to v2 format:

```bash
devsync extract --upgrade ./old-package
```

## Documentation

Full documentation at **[devsync.readthedocs.io](https://devsync.readthedocs.io)**:

- [Getting Started](https://devsync.readthedocs.io/getting-started/installation/) -- installation, quickstart, core concepts
- [CLI Reference](https://devsync.readthedocs.io/cli/) -- all commands with examples
- [IDE Integrations](https://devsync.readthedocs.io/ide-integrations/) -- setup guides for each AI tool
- [Packages](https://devsync.readthedocs.io/packages/) -- creating and installing config packages
- [MCP Server](https://devsync.readthedocs.io/mcp-server/) -- MCP configuration management
- [Tutorials](https://devsync.readthedocs.io/tutorials/team-config-repo/) -- step-by-step walkthroughs

## Contributing

```bash
git clone https://github.com/troylar/devsync.git
cd devsync
pip install -e .[dev]
invoke test
```

See the [contributing guide](https://devsync.readthedocs.io/advanced/contributing/) for details.

## License

MIT -- see [LICENSE](LICENSE).
