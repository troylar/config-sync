# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
