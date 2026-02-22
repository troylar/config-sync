# DevSync — Product Vision

## What DevSync Is

DevSync is a CLI tool for AI-powered config distribution across AI coding assistants. It uses LLM intelligence to extract practices from projects and adapt them to recipients' existing setups — across Cursor, Claude Code, Windsurf, GitHub Copilot, Kiro, Roo Code, Cline, Codex, and more.

**Install it with pip. Extract and install in two commands. No lock-in.**

Think of it as an AI-powered package manager for coding assistant configurations. Extract practices from any project, share them as packages, install them with intelligent merging into any of 23+ supported AI tools.

## Who It's For

### Primary: Teams standardizing AI tool configurations
Organizations that want consistent AI coding instructions across developers, tools, and projects — without manual copying or tool-specific formats.

### Secondary: Open-source instruction authors
Developers who create and share reusable AI coding instructions, MCP server configs, and development workflows via Git repositories.

### Tertiary: Individual developers
Power users who want to manage their own AI tool configurations across multiple projects and tools from a single library.

## Core Principles

These principles guide every feature decision. New features must align with at least one and violate none.

### 1. Zero-friction distribution
`pip install devsync && devsync tools` — that's it. No Docker, no external services, no accounts required. Download from any Git repo, install with one command. If a feature requires infrastructure to work, it doesn't belong.

### 2. IDE-agnostic
22+ tools, one package format, no lock-in. DevSync extracts from and installs to each tool's native format. Both extraction and installation must work across all supported tools — a user with only Cursor configs should be able to extract and share them just as easily as a Claude Code user. Adding a new AI tool should be a single file implementing the `AITool` base class. Users should never have to think about tool-specific file formats.

### 3. Git as distribution
No central server, no registry, no accounts. Any Git repository can be an instruction source. Version control is the distribution mechanism. If it works with `git clone`, it works with DevSync.

### 4. Lean CLI
Typer + Rich, no daemons, no services, no background processes. DevSync runs when you invoke it and exits. It doesn't watch files, it doesn't sync automatically, it doesn't phone home. Simple, predictable, fast.

### 5. Credential safety
Credentials never in repos, always prompted or from environment variables. MCP server configs can declare required credentials, but the values are never stored in package manifests or installation records. Secrets stay in the environment.

### 6. Standards-first
MCP protocol for server configs, conventional markdown for instructions, YAML manifests for packages. Standard formats over proprietary ones. Users can read, edit, and version-control everything DevSync creates.

## What's In Scope

- **AI-powered extraction**: Read a project's rules, MCP configs, and commands to produce abstract practice declarations — from any supported tool, not just one
- **AI-powered installation**: Adapt incoming practices to the recipient's existing setup with intelligent merging
- **Multi-tool support**: Extract from and install to 23+ AI coding assistants. Both sides of the pipeline must be tool-agnostic
- **Selective packaging**: Filter extractions by tool, component type (rules, MCP servers, commands, hooks), and scope (project vs global)
- **Package system**: v2 practice-based packages and v1 file-copy backward compatibility
- **MCP credential handling**: Prompt for credentials at install time, never store in repos
- **Project tracking**: Per-project installation records
- **Git integration**: Clone and install from any Git repository

## What DevSync Is Not

These aren't just out-of-scope items — they're identity statements.

### Not an IDE
DevSync manages configurations for AI tools. It doesn't provide AI assistance itself, doesn't run models, doesn't execute code. It's the plumbing, not the faucet.

### Not a cloud service
No hosted registry, no accounts, no SaaS tier. DevSync is a local CLI tool that talks to Git repos. The moment it requires a server to function, the design is wrong.

### Not a code generator
DevSync distributes instructions that humans or teams write. It doesn't generate, suggest, or modify instruction content. Creation is the author's job; distribution is DevSync's.

### Not a plugin framework
DevSync installs files to the right places in the right formats. It doesn't provide a runtime, an API, or an extension system. AI tools have their own extension mechanisms; DevSync just gets configs there.

### Not a package registry
There's no central registry, no publishing step, no approval process. Any Git repo with a manifest file is a valid source. Discovery happens through URLs, not through a catalog.

### Not a configuration burden
Zero configuration should always work. `devsync download <url>` and `devsync install` should work without any setup beyond `pip install`. Power users can customize, but defaults must be sensible.

## What's Out of Scope

These are explicit "no" decisions. Do not build features in these areas.

- **Cloud hosting / SaaS**: DevSync is always local. No managed version, no hosted tier.
- **AI model interaction beyond config distribution**: DevSync uses LLMs for extraction and adaptation of configs, but does not provide general AI assistance or generate application code.
- **IDE plugins / extensions**: DevSync is CLI-only. IDE integration happens through the files it installs, not through plugins.
- **Automatic syncing / file watching**: DevSync runs on demand. No daemons, no background processes.
- **Instruction content creation**: DevSync distributes; it doesn't author.
- **Complex deployment requirements**: If it needs more than `pip install`, it doesn't belong.

## Direction (Current)

The project is heading toward four areas:

1. **AI-Powered Distribution** — LLM-powered extraction and adaptation of practices, intelligent merging with existing configs, graceful degradation when no API key is available.

2. **AI Tool Integration** — Support for new and evolving AI coding assistants (23+ tools), improved translation between formats, better detection of installed tools.

3. **Package Ecosystem** — v2 practice-based packages, v1 backward compatibility, MCP server credential handling, Git-based distribution.

4. **Docs & Quality** — Documentation, test coverage, CI improvements, contributor experience.

## The Litmus Test

Before adding a feature, ask:

1. **Does it work with `pip install`?** If it adds heavy dependencies or external infrastructure, reconsider.
2. **Is it IDE-agnostic?** If it only works with one AI tool, it might not belong in core.
3. **Is it lean?** Could we do this with less code, fewer dependencies, simpler UX?
4. **Does it work offline?** DevSync should work without network access (for already-downloaded repos).
5. **Would the team use it?** If developers wouldn't reach for this feature regularly, it probably shouldn't exist.
