# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.12.0] - 2026-02-21

### Added
- **DevSync v2.0 — AI-Powered Config Distribution** (#63)
  - 6 streamlined CLI commands replacing 20+: `setup`, `tools`, `extract`, `install`, `list`, `uninstall`
  - AI-powered practice extraction: LLM reads project rules and produces abstract practice declarations
  - AI-powered installation: LLM adapts incoming practices to recipient's existing setup with intelligent merging
  - LLM provider abstraction layer (Anthropic, OpenAI, OpenRouter) via HTTP — no SDK dependencies
  - Graceful degradation: works without API key using file-copy mode (`--no-ai` flag)
  - v2 package format (`devsync-package.yaml`) with `practices` section
  - Backward compatibility with v1 `ai-config-kit-package.yaml` packages
  - MCP credential prompting with masked input during installation
  - `devsync setup` — interactive LLM provider configuration
  - `devsync extract` — extract practices from any project with AI or file-copy mode
  - `devsync install` — install packages from Git URLs, local paths, or directories
  - `devsync list` — show installed packages with tool filtering and JSON output
  - v1 package upgrade via `devsync extract --upgrade`

### Fixed
- Temp directory leak when cloning Git repos during install
- LLM JSON responses wrapped in markdown fences now parsed correctly
- `parse_adaptation_response` now reads `practice_name` from JSON instead of defaulting to empty
- `--conflict` flag now properly honored (skip/overwrite/rename strategies)
- `extract --upgrade` returns correct exit code when no instruction files found
- Path traversal protection uses `Path.relative_to()` instead of string prefix check
- Windows path separator handling in tests (use Path objects instead of string comparison)
- Removed stale `tui.installer` import that caused mypy failures

### Security
- MCP credential input now masked with `password=True`
- Path traversal guard added to both install and extract commands

### Documentation
- Complete ReadTheDocs rewrite for v2 architecture (47 files updated)
- New CLI pages: `setup.md`, `extract.md`
- Rewritten: `install.md`, `list.md`, quickstart, concepts, CLI reference
- Updated tutorials, IDE integrations, and package documentation
- Removed obsolete v1 pages (download, update, delete, MCP server section)

## [0.11.0] - 2026-02-21

### Added
- **Anteroom AI Tool Support** (#60) - Single-file instructions in `ANTEROOM.md` with section markers
  - Detection via `aroom` binary or `~/.anteroom/` config directory
  - Full package system support (translator, capability registry, component detector)
  - 20 unit tests covering all tool methods

### Fixed
- Replace `aiconfig` with `devsync` CLI name in tutorials
- Fix `os.uname()` compatibility on Windows (use `sys.platform` instead)

### Documentation
- Add 3 example repos (starter-templates, python-package, fullstack-package)
- Add 3 new tutorials (CI/CD integration, multi-IDE workflow, migration guide)
- Add unified MkDocs Material documentation with ReadTheDocs deployment
- Slim down README and point to ReadTheDocs

## [0.10.0] - 2026-02-15

### Added
- **12 New IDE Integrations** - Expanded from 10 to 22 supported AI coding tools
  - **Amazon Q** (#33) - Multi-file instructions in `.amazonq/rules/`, MCP support
  - **JetBrains AI** (#34) - Multi-file instructions in `.aiassistant/rules/`, MCP support
  - **Junie** (#35) - Single-file instructions in `.junie/guidelines.md` with section markers
  - **Zed** (#36) - Single-file instructions in `.rules` with section markers, MCP support
  - **Continue.dev** (#39) - Multi-file instructions in `.continue/rules/`, MCP support
  - **Aider** (#40) - Single-file instructions in `CONVENTIONS.md` with section markers
  - **Trae** (#41) - Multi-file instructions in `.trae/rules/`, MCP support
  - **Augment** (#42) - Multi-file instructions in `.augment/rules/`, MCP support
  - **Tabnine** (#43) - Multi-file instructions in `.tabnine/guidelines/`, MCP support
  - **OpenHands** (#44) - Multi-file instructions in `.openhands/microagents/`, MCP support
  - **Amp** (#45) - Single-file instructions in `AGENTS.md` with section markers
  - **OpenCode** (#47) - Single-file instructions in `AGENTS.md` with section markers
- Full package system support (translators, capability registry) for all 12 new IDEs
- Comprehensive test coverage for all new tools (200+ new tests)

## [0.9.0] - 2026-02-15

### Added
- **Gemini CLI / Code Assist Support** - Added support for Google Gemini CLI and Gemini Code Assist (#38, #46)
  - Instructions managed via section markers in `GEMINI.md` at project root
  - Section-based install/uninstall using HTML comment markers
  - Detection via `gemini` binary on PATH or `~/.gemini/` directory
  - MCP configuration via `~/.gemini/settings.json`
  - Package system support for instructions and resources
- **Antigravity IDE Support** - Added support for Google's Antigravity IDE (#52)
  - Instructions stored in `.agent/rules/*.md` (multi-file pattern)
  - Detection via `antigravity` binary on PATH or `~/.gemini/antigravity/` directory
  - MCP configuration via `.mcp.json` at project root
  - Package system support for instructions, MCP servers, and resources
- **Snyk Security Scanning** - Added Snyk vulnerability scanning to CI pipeline (#53)
  - Dependency scanning with high severity threshold
  - `.snyk` policy file to suppress false positive findings (#54)

## [0.8.0] - 2026-02-14

### Added
- **OpenAI Codex CLI Support** - Added support for the OpenAI Codex CLI (#37)
  - Instructions managed via section markers in `AGENTS.md` at project root
  - Section-based install/uninstall using HTML comment markers (`<!-- devsync:start:name -->`)
  - Multiple instructions coexist in a single file without conflicts
  - Detection via `codex` binary on PATH
  - Package system support for instructions and resources
  - IDE capability registry entry for Codex CLI
  - Component detector recognizes `AGENTS.md` files

## [0.7.0] - 2026-02-14

### Changed
- **BREAKING: Module renamed** - Python module `aiconfigkit` renamed to `devsync`
  - All imports changed from `from aiconfigkit...` to `from devsync...`
- **Data directories consolidated** - All data directories unified to `.devsync`
  - Global: `~/.instructionkit/` -> `~/.devsync/` (with fallback to old path)
  - Project: `.instructionkit/` and `.ai-config-kit/` -> `.devsync/` (with fallback)
  - Existing installations automatically detected via fallback logic

## [0.6.0] - 2026-02-14

### Changed
- **CLI Renamed** - CLI command changed from `aiconfig` to `devsync`
  - All CLI examples, help text, and documentation updated
  - `pip install devsync` now provides the `devsync` command
- **Full rebrand to DevSync** - Removed all legacy "InstructionKit", "inskit", and "AI Config Kit" references
- Cleaned up old build artifacts

## [0.5.7] - 2026-02-14

### Changed
- **Project Rename** - Renamed project to "DevSync", GitHub repo to `troylar/devsync`
- All documentation, URLs, and references updated

## [0.5.6] - 2026-02-14

### Changed
- **Project Rename** - Renamed from "AI Config Kit" to "DevSync"
- All documentation and references updated

## [0.5.5] - 2026-02-14

### Changed
- **PyPI Package Rename** - Package renamed from `ai-config-kit` to `devsync`
  - Install with `pip install devsync` (CLI command is now `devsync`)
  - Previous package name was quarantined by PyPI's anti-typosquatting filters

## [0.5.4] - 2026-02-14

### Added
- **Roo Code IDE Support** - Added support for the Roo Code VS Code extension (#32)
  - Instructions installed to `.roo/rules/*.md`
  - Cross-platform detection via VS Code globalStorage (`rooveterinaryinc.roo-cline`)
  - Package system support for instructions, MCP servers, commands, and resources
  - Project-level MCP config at `.roo/mcp.json`
  - Slash commands at `.roo/commands/`
  - Global and project scope support
  - IDE capability registry entry for Roo Code
  - Component detector recognizes `.roo/rules/` directories

## [0.5.2] - 2026-02-13

### Added
- **Cline IDE Support** - Added support for the Cline VS Code extension (#31)
  - Instructions installed to `.clinerules/*.md`
  - Cross-platform detection via VS Code globalStorage (`saoudrizwan.claude-dev`)
  - Package system support for instructions and resources
  - IDE capability registry entry for Cline
  - Component detector recognizes `.clinerules/` directories

## [0.5.1] - 2026-02-13

### Added
- **Kiro IDE Support** - Added support for Amazon's Kiro AI-powered IDE (#29)
  - Instructions installed to `.kiro/steering/*.md`
  - Cross-platform detection (macOS, Linux, Windows)
  - Package system support for instructions and resources
  - IDE capability registry entry for Kiro
  - Component detector recognizes `.kiro/steering/` directories

## [0.5.0] - 2026-01-30

### Added
- **Package Creation Command** - Generate shareable packages from existing configurations (#24)
  - `aiconfig package create` - Create packages from project configurations
  - Automatic component detection for instructions, MCP servers, hooks, commands, resources
  - Secret detection and templating for secure distribution
  - Support for new component types: skills, workflows, memory files
- **Enhanced IDE Capability Support** - All IDEs now support MCP servers
  - Claude Code: Full support (skills, memory files, hooks, commands, resources)
  - Cursor: MCP via `.cursor/mcp.json` (40 tool limit)
  - Windsurf: MCP via `~/.codeium/windsurf/mcp_config.json` (100 tool limit)
  - GitHub Copilot: MCP via `.vscode/mcp.json` (128 tool limit)
- New component types in IDE capability registry:
  - Skills (`.claude/skills/*/SKILL.md`)
  - Workflows (`.windsurf/workflows/*.md`)
  - Memory files (`CLAUDE.md`)
- Updated copilot instruction detection for `.github/copilot-instructions.md` pattern

### Changed
- Updated MCP translators for Cursor and Copilot to support MCP installation
- IDE capability registry now accurately reflects current MCP support across all tools

## [0.4.0] - 2025-11-09

### Added
- **Template Sync System** - Repository-based distribution of IDE artifacts (instructions, commands, hooks) (#17)
  - Install templates with namespace isolation using dot notation (e.g., `acme.security-rules`)
  - Support for instructions, slash commands, and prompt hooks
  - Cross-IDE compatibility (Claude Code, Cursor, Windsurf, GitHub Copilot)
  - Template library management with `aiconfig template` commands
  - Installation tracking with checksum verification
- **Template Validation** - Health checking system for installed templates
  - `aiconfig template validate` command with severity-based reporting (error/warning/info)
  - Detects missing files, local modifications, and outdated versions
  - Checksum-based verification using SHA-256 hashing
  - Validates template integrity across project and global scopes
  - `--fix` flag for automatic remediation of issues
  - `--verbose` flag for detailed diagnostic output
- **Automatic Backup System** - Protection against accidental data loss
  - Automatic timestamped backups before any template overwrite
  - Backups stored in `.ai-config-kit/backups/<timestamp>/`
  - `aiconfig template backup list` - View available backups
  - `aiconfig template backup restore` - Restore files from backups
  - `aiconfig template backup cleanup` - Remove old backups (default: 30 days)
  - Support for both project and global scopes
- **Interactive Conflict Resolution** - User prompts for template conflicts
  - Rich terminal UI for conflict resolution choices
  - Three strategies: Keep local, Overwrite (with backup), or Rename
  - Side-by-side conflict information display
  - Prevents accidental overwrites of modified templates
- **Template Repository Scaffolding** - Create new template repositories with one command
  - `aiconfig template init` - Generate scaffolded template repository
  - Pre-configured `templatekit.yaml` with examples
  - Example templates with comprehensive documentation
  - Ready-to-use directory structure for all template types
  - Automatic README and .gitignore generation
- Template-specific CLI commands:
  - `aiconfig template init` - Create new template repository
  - `aiconfig template install` - Install templates from library
  - `aiconfig template list` - List available templates
  - `aiconfig template update` - Update installed templates
  - `aiconfig template uninstall` - Remove installed templates

### Changed
- Default conflict resolution strategy changed from `skip` to `prompt` for template operations
  - Users are now interactively prompted when conflicts are detected
  - Provides better visibility and control over file operations
- Enhanced README.md with comprehensive template sync documentation
  - Added validation command reference with examples
  - Documented backup management workflow
  - Updated features section with safety improvements
  - Added template system architecture documentation

### Fixed
- Templates with local modifications are now safely detected before updates
- Conflict resolution now creates backups before destructive operations

## [0.3.1] - 2025-10-27

### Fixed
- Git repository updates now work correctly - `.git` directory is preserved during download (#16)
  - Previously, downloading from Git URLs would skip the `.git` directory, preventing `aiconfig update --all` from working
  - Update command would show "Not a Git repository (local source)" for all Git-based repositories
  - Now the entire `.git` directory is copied to the library alongside instruction files
  - Enables proper Git-based updates via `aiconfig update --all` and `aiconfig update --namespace`
  - Local (non-Git) sources continue to work as before

## [0.3.0] - 2025-10-27

### Breaking Changes
- **GitHub Copilot file extension**: Instructions now use `.instructions.md` extension (was `.md`) (#15)
  - Required by GitHub Copilot's [official specification](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
  - Previous installations with `.md` extension will not be recognized by Copilot
  - **Action required** if you have existing Copilot instructions:
    ```bash
    aiconfig uninstall <instruction-name> --tool copilot
    aiconfig install <instruction-name>
    ```
  - Affects: GitHub Copilot only (Cursor, Claude Code, Windsurf unchanged)

### Added
- Git-based repository versioning support - download and manage multiple versions of instruction repositories
  - `aiconfig download --ref <tag|branch|commit>` to download specific Git references
  - Support for tags (e.g., `v1.0.0`), branches (e.g., `main`), and commit hashes
  - Multiple versions of the same repository can coexist in the library
  - Version information tracked in installation records (`source_ref` and `source_ref_type`)
  - Automatic update behavior: branch-based installs auto-update, tag/commit-based installs remain pinned
  - `aiconfig update` intelligently updates only mutable references (branches)
  - Version display in TUI installer and `aiconfig list` commands
- **Upgrade detection and prompts** - when installing a newer version of an existing instruction:
  - Automatically detects version changes (e.g., v1.0.0 → v2.0.0)
  - Displays side-by-side version comparison with old and new versions
  - Prompts for user confirmation before upgrading
  - Works across all AI tools (Cursor, Claude Code, Copilot, Windsurf)
- **Name collision handling** - when installing instructions with duplicate names from different repositories:
  - Detects when instruction name already exists from a different repository
  - Displays detailed information about existing and new installations
  - Allows users to provide custom filename to avoid conflicts
  - Option to skip installation if collision cannot be resolved
  - `find_instructions_by_name()` method in `InstallationTracker` for collision detection
- New `RefType` enum for tracking Git reference types (tag, branch, commit)
- `GitOperations` class with functions for:
  - `detect_ref_type()` - automatically determine if a reference is a tag, branch, or commit
  - `validate_remote_ref()` - verify Git references exist on remote before cloning
  - `clone_at_ref()` - clone repository at a specific Git reference
  - `check_for_updates()` - check if updates are available for branch-based repos
  - `pull_repository_updates()` - pull latest changes with conflict detection
- Versioned namespace generation in `LibraryManager`:
  - `get_versioned_namespace()` - creates unique namespaces like `repo@v1.0.0`
  - `list_repository_versions()` - lists all downloaded versions of a repository
- Enhanced update command with progress bars and detailed status reporting
- Comprehensive unit tests: 72 new tests, improving coverage from 46% to 57%

### Changed
- `InstallationRecord` now includes `source_ref` and `source_ref_type` fields for version tracking
- Library organization now supports version-specific namespaces (e.g., `github_com_user_repo@v1.0.0`)
- Update workflow now filters installations by ref mutability (only updates branches)
- Installation workflow now includes upgrade and collision checks before file operations

## [0.2.0] - 2025-10-24

### Changed
- Project-scoped installations now use relative paths in `installations.json` for version control compatibility (#8, #9)
- Removed `project_root` field from `InstallationRecord` model
- Installation tracking files are now safe to commit to version control across different machines

### Added
- Comprehensive release workflow documentation in CLAUDE.md with GitHub Actions automation
- Unit tests for relative path functionality in installation tracking
- Automatic migration from absolute to relative paths on save

### Fixed
- PyPI trusted publishing workflow configuration

## [0.1.2] - 2025-10-24

### Fixed
- Fixed duplicate installation confirmation prompt in `aiconfig install` command (#1)
- Improved path assertions for cross-platform compatibility (Windows support)

### Changed
- Added CODECOV_TOKEN to codecov upload step in CI workflow

### Added
- Comprehensive unit tests for installation confirmation workflow
- Git and commit message conventions documentation in CLAUDE.md

## [0.1.1] - 2025-10-21

### Added
- Initial release with core functionality
- CLI commands: download, install, list, update, delete, uninstall, tools
- Support for Claude Code, Cursor, Windsurf, and GitHub Copilot
- Interactive TUI for browsing and installing instructions
- Library management system for instruction repositories
- Installation tracking and conflict resolution
