# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Config Kit** is a CLI tool for managing AI coding assistant instructions. It allows users to download instruction repositories to a local library, browse them with an interactive TUI, and install them to AI tools (Cursor, Claude Code, Windsurf, GitHub Copilot) at the project level.

**CLI entry point:** `aiconfig` (installed via `pip install ai-config-kit`)

## Architecture

### Core Concepts

1. **Library System**: Instructions are downloaded from Git repos or local folders to `~/.ai-config-kit/library/` organized by namespace
2. **Project-Level Installation**: All installations are project-specific, stored in tool-specific directories (`.cursor/rules/`, `.claude/rules/`, `.kiro/steering/`, etc.)
3. **Installation Tracking**: Tracked in `<project-root>/.ai-config-kit/installations.json` for each project (instructions) and `<project-root>/.ai-config-kit/packages.json` for packages
4. **Interactive TUI**: Terminal UI for browsing and selecting instructions from the library
5. **Configuration Packages**: Multi-component packages containing instructions, MCP servers, hooks, commands, and resources that can be installed as a unit

### Package Structure

```
ai-config-kit/
├── ai_tools/          # AI tool integrations and detection
│   ├── base.py       # Abstract AITool base class
│   ├── claude.py     # Claude Code (.claude/rules/*.md)
│   ├── cursor.py     # Cursor (.cursor/rules/*.mdc)
│   ├── cline.py      # Cline (.clinerules/*.md)
│   ├── kiro.py       # Kiro (.kiro/steering/*.md)
│   ├── roo.py        # Roo Code (.roo/rules/*.md)
│   ├── winsurf.py    # Windsurf (.windsurf/rules/*.md)
│   ├── copilot.py    # GitHub Copilot (.github/instructions/*.md)
│   └── detector.py   # Tool detection logic
├── cli/               # Typer CLI commands
│   ├── main.py       # CLI app definition
│   ├── download.py   # Download repos to library
│   ├── install.py    # Legacy install command
│   ├── install_new.py # New install with TUI
│   ├── list.py       # List library/installed/available
│   ├── update.py     # Update library repos
│   ├── delete.py     # Delete from library
│   ├── uninstall.py  # Uninstall from projects
│   ├── tools.py      # List detected AI tools
│   ├── package.py    # Package management commands (list, uninstall)
│   └── package_install.py # Package installation logic
├── core/              # Core business logic
│   ├── models.py     # Data models (Instruction, Repository, etc.)
│   ├── repository.py # Parse ai-config-kit.yaml
│   ├── git_operations.py # Git clone/pull operations
│   ├── checksum.py   # File integrity checking
│   └── conflict_resolution.py # Handle file conflicts
├── storage/           # Data persistence
│   ├── library.py    # LibraryManager for ~/.ai-config-kit/library/
│   ├── tracker.py    # InstallationTracker for installations.json
│   └── package_tracker.py # PackageTracker for packages.json
├── tui/               # Terminal UI
│   └── installer.py  # Textual-based interactive browser
└── utils/             # Utilities
    ├── project.py    # Project root detection
    └── logging.py    # Logging configuration
```

### Key Data Models

From `ai-config-kit/core/models.py`:

#### Instructions
- **Instruction**: Single instruction file with name, description, content, file_path, tags, checksum
- **InstructionBundle**: Group of related instructions
- **Repository**: Instruction repository with instructions and bundles
- **InstallationRecord**: Tracks installed instruction with ai_tool, source_repo, installed_path, scope
- **LibraryInstruction**: Instruction in library (downloaded but not installed)
- **LibraryRepository**: Downloaded repository in library

#### Packages
- **Package**: Configuration package containing multiple components (instructions, MCP servers, hooks, commands, resources)
- **PackageComponents**: Container for all components in a package with methods to count and manage them
- **ComponentType**: Enum for component types (INSTRUCTION, MCP_SERVER, HOOK, COMMAND, RESOURCE)
- **InstalledComponent**: Tracks installed component with type, name, path, checksum, and status
- **PackageInstallationRecord**: Tracks installed package with name, version, components, timestamps, scope, and status
- **InstallationStatus**: Enum for installation status (COMPLETE, PARTIAL, FAILED, PENDING_CREDENTIALS)
- **ConflictResolution**: Enum for conflict handling strategies (SKIP, OVERWRITE, RENAME)

### AI Tool Integration

Each AI tool integration (in `ai_tools/`) inherits from `AITool` base class:
- `name`: Tool identifier
- `install_path`: Where to install files (e.g., `.cursor/rules/`)
- `file_extension`: File extension (e.g., `.mdc` for Cursor, `.md` for others)
- `detect()`: Check if tool is installed
- `get_install_path(scope, project_root)`: Get installation directory
- `install(instruction, scope, project_root, conflict_strategy)`: Install instruction file

## Development Commands

### Setup
```bash
# Install in editable mode with dev dependencies
pip install -e .[dev]

# Or use invoke
invoke dev-setup
```

### Testing
```bash
# Run all tests (preferred)
invoke test

# Run with coverage
invoke test --coverage

# Run specific test types
invoke test-unit         # Unit tests only
invoke test-integration  # Integration tests only

# Manual pytest
pytest                        # All tests
pytest tests/unit/            # Unit tests
pytest tests/integration/     # Integration tests
pytest -k "test_name"         # Specific test pattern
```

### Code Quality
```bash
# Run all checks (lint, format, typecheck)
invoke quality

# Auto-fix issues
invoke quality --fix

# Individual checks
invoke lint              # Ruff linting
invoke lint --fix        # Auto-fix lint issues
invoke format            # Black formatting
invoke format --check    # Check without changes
invoke typecheck         # MyPy type checking
```

### Build & Install
```bash
invoke clean             # Clean build artifacts
invoke build             # Build package
invoke install           # Install package
invoke install --dev     # Install with dev dependencies
```

### Release
```bash
# Pre-release checks (runs clean, quality, test)
invoke release-check

# Build and publish to PyPI
invoke build
invoke publish           # Publish to PyPI
invoke publish --repository testpypi  # Test PyPI first
```

### Utilities
```bash
invoke count             # Count lines of code
invoke version           # Show current version
invoke tree              # Show project structure
invoke security-check    # Run security scans
```

## Testing Structure

```
tests/
├── conftest.py              # Shared fixtures (temp_dir, mock repos)
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_models.py      # Model validation
│   ├── test_checksum.py    # Checksum utilities
│   └── ...
└── integration/             # Integration tests (file I/O, Git)
    ├── test_library.py     # Library management
    ├── test_repository.py  # Repository parsing
    └── test_tracker.py     # Installation tracking
```

**Testing conventions:**
- Use fixtures from `conftest.py` (especially `temp_dir` for file operations)
- Integration tests may use actual Git operations and file I/O
- All tests should clean up after themselves
- Use `pytest -v` for verbose output, `pytest --cov` for coverage

## Code Style

- **Formatter**: Black (line length: 120)
- **Linter**: Ruff (select: E, F, I, N, W)
- **Type Checker**: MyPy (strict type hints required)
- **Python Version**: 3.10+ (using modern type hints like `list[str]`, not `List[str]`)

**Key conventions:**
- All functions must have type hints
- Use dataclasses for data models
- Use Enum for constants (AIToolType, ConflictResolution, InstallationScope)
- Docstrings for all public functions/classes (Google style)
- Line length: 120 characters

## Git & Commit Conventions

**Commit Message Format:**
```
<type>: <subject>

[optional issue reference]

<body>
```

**IMPORTANT:** Do NOT include Claude as a co-author in commit messages. Do NOT add:
- `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
- `Co-Authored-By: Claude <noreply@anthropic.com>`
- Any other Claude attribution lines

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Issue References:**
Always reference GitHub issues in commit messages to create automatic links and tracking:

- **Closing issues**: Use `Fixes #123`, `Closes #123`, or `Resolves #123` in the commit body to automatically close the issue when merged to main
  ```
  fix: remove duplicate installation confirmation prompt

  Fixes #1

  The aiconfig install command was prompting users twice...
  ```

- **Referencing issues**: Use `Refs #123` or `See #123` to reference related issues without closing them
  ```
  test: add unit tests for duplicate confirmation fix

  Refs #1

  Add comprehensive unit tests...
  ```

**Examples:**
```bash
# Bug fix that closes an issue
git commit -m "fix: handle empty library gracefully

Fixes #42

Previously the CLI would crash when the library was empty.
This commit adds proper error handling..."

# Test addition referencing an issue
git commit -m "test: add tests for library edge cases

Refs #42

Adds tests to verify empty library handling..."

# Feature with multiple issue references
git commit -m "feat: add batch installation support

Closes #15, Refs #12

Allows installing multiple instructions in one command..."
```

## Important Implementation Details

### Project Root Detection
The `utils/project.py` module detects project root by looking for markers like `.git/`, `pyproject.toml`, `package.json`, etc. This enables running `aiconfig` from any subdirectory within a project.

### Installation Workflow
1. **Download**: Clone/copy repo to `~/.ai-config-kit/library/<namespace>/`
2. **Browse**: TUI reads library, displays instructions
3. **Install**: Copy instruction file to project's tool-specific directory
4. **Track**: Record in `<project-root>/.ai-config-kit/installations.json`

### Conflict Resolution
When installing an instruction that already exists:
- **SKIP**: Don't install, leave existing
- **RENAME**: Install with suffix (e.g., `instruction-1.md`)
- **OVERWRITE**: Replace existing file

### Repository Format
Instruction repositories must have `ai-config-kit.yaml`:
```yaml
name: My Instructions
description: Description
version: 1.0.0

instructions:
  - name: my-instruction
    description: What it does
    file: instructions/my-instruction.md
    tags: [tag1, tag2]

bundles:
  - name: my-bundle
    description: Bundle description
    instructions: [instruction1, instruction2]
    tags: [tag]
```

### Package Management System

The package management system allows installing multi-component bundles that include instructions, MCP servers, hooks, commands, and resources.

#### Package Structure
Packages must contain an `ai-config-kit-package.yaml` manifest:
```yaml
name: package-name
version: 1.0.0
description: Package description
author: Author Name
license: MIT
namespace: org/repo

components:
  instructions:
    - name: instruction-name
      file: instructions/file.md
      description: Instruction description
      tags: [tag1, tag2]

  mcp_servers:
    - name: server-name
      file: mcp/config.json
      description: MCP server configuration
      credentials:
        - name: ENV_VAR
          description: Environment variable description
          required: true
          default: "default-value"

  hooks:
    - name: hook-name
      file: hooks/script.sh
      description: Hook description
      hook_type: pre-commit

  commands:
    - name: command-name
      file: commands/script.sh
      description: Command description
      command_type: shell

  resources:
    - name: resource-name
      file: resources/file.txt
      description: Resource file
      checksum: sha256:...
      size: 1234
```

#### Package Commands
```bash
# Install a package
aiconfig package install ./path/to/package --ide claude

# Install with conflict resolution
aiconfig package install ./package --ide cursor --conflict overwrite

# Force reinstall
aiconfig package install ./package --force

# List installed packages
aiconfig package list

# List with JSON output
aiconfig package list --json

# Uninstall a package
aiconfig package uninstall package-name

# Uninstall without confirmation
aiconfig package uninstall package-name --yes
```

#### Package Installation Workflow
1. **Parse Manifest**: Read and validate `ai-config-kit-package.yaml`
2. **Check Existing**: Detect if package already installed
3. **Filter Components**: Only install components supported by target IDE
4. **Translate Components**: Convert to IDE-specific formats
5. **Install Files**: Copy files with conflict resolution
6. **Track Installation**: Record in `.ai-config-kit/packages.json`

#### IDE Capability Filtering
Different IDEs support different component types:
- **Claude Code**: All components (instructions, MCP, hooks, commands, resources)
- **Cline**: Instructions and resources only
- **Cursor**: Instructions and resources only
- **Kiro**: Instructions and resources only
- **Roo Code**: Instructions, MCP, commands, and resources
- **Windsurf**: Instructions and resources only
- **GitHub Copilot**: Instructions only

Unsupported components are automatically skipped and counted separately.

#### Component Translation
Components are translated to IDE-specific formats:
- **Claude Code**: `.md` files in `.claude/rules/`, `.claude/hooks/`, `.claude/commands/`
- **Cline**: `.md` files in `.clinerules/`
- **Cursor**: `.mdc` files in `.cursor/rules/`
- **Roo Code**: `.md` files in `.roo/rules/`, `.roo/commands/`
- **Kiro**: `.md` files in `.kiro/steering/`
- **Windsurf**: `.md` files in `.windsurf/rules/`
- **GitHub Copilot**: `.md` files in `.github/instructions/`

#### Example Package
See `example-package/` directory for a complete example with all component types.

## CI/CD

GitHub Actions workflow at `.github/workflows/ci.yml`:
- Runs on Python 3.10, 3.11, 3.12, 3.13
- Matrix testing on ubuntu-latest, macos-latest, windows-latest
- Steps: lint, format check, typecheck, tests with coverage
- Coverage uploaded to Codecov

**Local pre-push hook** (`.githooks/pre-push`):
```bash
# Enable with:
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

## Common Tasks

### Adding a New AI Tool
1. Create `ai-config-kit/ai_tools/newtool.py` inheriting from `AITool`
2. Implement `detect()`, `get_install_path()`, and `install()` methods
3. Add to `AIToolType` enum in `models.py`
4. Register in `detector.py`
5. Add tests in `tests/unit/test_ai_tools.py`

### Adding a New CLI Command
1. Create command file in `ai-config-kit/cli/`
2. Define Typer command with `@app.command()`
3. Register in `cli/main.py`
4. Add tests in `tests/unit/test_cli.py`
5. Update README.md with usage examples

### Modifying Data Models
1. Update dataclass in `core/models.py`
2. Update `to_dict()` and `from_dict()` methods
3. Consider backwards compatibility for existing installations
4. Add tests in `tests/unit/test_models.py`

## Dependencies

**Core:**
- `typer[all]` - CLI framework
- `rich` - Terminal formatting
- `pyyaml` - YAML parsing
- `textual` - TUI framework

**Dev:**
- `pytest`, `pytest-cov` - Testing
- `black` - Formatting
- `ruff` - Linting
- `mypy` - Type checking
- `invoke` - Task automation

## Documentation Standards

Follow the `.cursor/rules/documentation-practices.mdc` guide:
- README-first approach
- Comprehensive docstrings (Google style)
- Explain WHY in comments, not WHAT
- Keep CHANGELOG.md updated
- Architecture decision records (ADRs) for major decisions

## Debugging

```bash
# Enable debug logging
LOGLEVEL=DEBUG aiconfig install

# Run specific test with output
pytest tests/unit/test_models.py -s -vv

# Use breakpoints
import pdb; pdb.set_trace()
# or
breakpoint()
```

## Release Workflow

**IMPORTANT:** When the user asks to "create a new release" or "make a release", follow this complete workflow.

This project uses **GitHub Actions with PyPI Trusted Publishing** for automated releases. Publishing to PyPI happens automatically when you create a GitHub release.

### PyPI Trusted Publishing Setup

**One-time setup** (if not already configured):

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher:
   - **PyPI Project Name**: `ai-config-kit`
   - **Owner**: `troylar`
   - **Repository**: `ai-config-kit`
   - **Workflow name**: `publish.yml`
   - **Environment**: (leave empty)
3. Save the trusted publisher

This allows GitHub Actions to publish without needing API tokens or passwords.

### Pre-Release Checklist

**IMPORTANT:** Before creating a release, you **must** run `invoke release-check` locally to ensure everything is working. This prevents CI failures and failed releases.

1. **Ensure you're on the main branch** (or merge feature branch PR first)
2. **Working directory must be clean** (no uncommitted changes)
3. **All checks must pass locally**: `invoke release-check`
4. **CI/CD pipeline must be green** on GitHub Actions (if PR was merged)

### Release Steps

Follow these steps in order when creating a new release:

#### 1. Check Current Branch and Status
```bash
# Check current branch
git branch --show-current

# If on feature branch with open PR, check PR status
gh pr status

# Check for uncommitted changes
git status
```

**Action:** If on a feature branch with an open PR:
- Ensure all CI checks are passing
- Merge the PR to main
- Then pull main locally

#### 2. Switch to Main and Pull Latest
```bash
git checkout main
git pull origin main
```

#### 3. Run Pre-Release Checks (REQUIRED)
```bash
# This runs clean, quality, and test
invoke release-check
```

**IMPORTANT:** This step is **required** before proceeding with the release. It verifies locally that:
- All tests pass
- Code quality checks pass (lint, format, typecheck)
- Build artifacts are clean

**Action:** Fix any failures before proceeding. Do NOT create a release if this command fails.

#### 4. Determine Version Bump

Version is in `pyproject.toml`:
```toml
[project]
version = "0.1.1"
```

**Semantic Versioning:**
- **Patch** (0.1.1 → 0.1.2): Bug fixes, minor changes
- **Minor** (0.1.1 → 0.2.0): New features, backwards compatible
- **Major** (0.1.1 → 1.0.0): Breaking changes

**Action:** Ask the user which version bump to apply if not specified.

#### 5. Update Version in pyproject.toml

Edit the version in `pyproject.toml`:
```toml
[project]
version = "0.2.0"  # New version
```

#### 6. Update CHANGELOG.md

Add a new version section at the top of CHANGELOG.md with changes since last release:
```markdown
## [0.2.0] - 2025-10-24

### Added
- New feature description

### Changed
- Modified behavior description

### Fixed
- Bug fix description
```

**Tip:** Review commits since last release:
```bash
git log v0.1.1..HEAD --oneline
```

#### 7. Commit Version Bump

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"
```

**IMPORTANT:** Do NOT include Claude co-author attribution.

#### 8. Create and Push Git Tag

```bash
# Create annotated tag
git tag -a v0.2.0 -m "Release version 0.2.0"

# Push commits and tags
git push origin main
git push origin v0.2.0
```

#### 9. Create GitHub Release (Triggers Automated Publishing)

```bash
# Create release from tag
gh release create v0.2.0 \
  --title "v0.2.0" \
  --notes "$(awk '/## \[0.2.0\]/,/## \[/' CHANGELOG.md | head -n -1)"
```

**Alternative:** Create release manually on GitHub:
1. Go to https://github.com/troylar/ai-config-kit/releases/new
2. Click "Choose a tag" and select `v0.2.0`
3. Title: `v0.2.0`
4. Copy the relevant section from CHANGELOG.md into the description
5. Click "Publish release"

**What happens next:** The `.github/workflows/publish.yml` workflow will automatically:
1. Run quality checks and tests
2. Build the package
3. Publish to PyPI using trusted publishing

#### 10. Monitor the Publish Workflow

```bash
# Watch workflow progress
gh run watch

# Or view in browser
gh run list --workflow=publish.yml
```

You can also monitor at: https://github.com/troylar/ai-config-kit/actions

### Post-Release Verification

Wait for the GitHub Actions workflow to complete (usually 2-5 minutes), then:

```bash
# Verify package on PyPI
pip install --upgrade ai-config-kit

# Check installed version
aiconfig --version

# Verify GitHub release
gh release view v0.2.0

# Check PyPI page
open https://pypi.org/project/ai-config-kit/
```

### Testing on TestPyPI (Optional)

To test the release process without publishing to production PyPI:

```bash
# Manually trigger workflow with TestPyPI option
gh workflow run publish.yml -f repository=testpypi

# Monitor the test run
gh run watch
```

Then verify on TestPyPI: https://test.pypi.org/project/ai-config-kit/

### Rollback (If Needed)

If issues are discovered after release:

1. **Yank release from PyPI** (marks as unavailable, doesn't delete):
   ```bash
   # Install twine if needed
   pip install twine

   # Yank the version
   twine upload --repository pypi --yank <version>
   ```

2. **Delete GitHub release**:
   ```bash
   gh release delete v0.2.0 --yes
   ```

3. **Optionally delete the tag**:
   ```bash
   git tag -d v0.2.0
   git push origin :refs/tags/v0.2.0
   ```

4. **Fix issues and create new patch release** (e.g., 0.2.1)

### Quick Reference

For a standard release from main branch:

```bash
# 1. Ensure clean state
git checkout main && git pull

# 2. REQUIRED: Run checks locally (DO NOT SKIP!)
invoke release-check

# 3. Update version in pyproject.toml and CHANGELOG.md

# 4. Commit and tag
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to X.Y.Z"
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin main && git push origin vX.Y.Z

# 5. Create GitHub release (triggers automated publish)
gh release create vX.Y.Z --title "vX.Y.Z" \
  --notes "$(awk '/## \[X.Y.Z\]/,/## \[/' CHANGELOG.md | head -n -1)"

# 6. Monitor workflow and verify
gh run watch
```

The GitHub Actions workflow (`.github/workflows/publish.yml`) handles building and publishing automatically.

## Active Technologies
- Markdown (instruction content) | Python 3.10+ (for AI Config Kit CLI - no changes needed) + Git (for repository hosting), existing AI Config Kit commands (no new dependencies) (001-example-instruction-repo)
- GitHub repository at `troylar/ai-config-kit-examples` | Git-based versioning (001-example-instruction-repo)
- Python 3.10+ (targeting 3.10-3.13) (002-template-sync-system)
- Filesystem-based (MCP definitions in `~/.ai-config-kit/library/<namespace>/`, credentials in `.ai-config-kit/.env`, AI tool configs at standard locations) (003-mcp-server-management)
- Python 3.10+ (minimum 3.10, support 3.10-3.13) + PyYAML (manifest parsing), Rich/Textual (TUI), Typer (CLI), existing ai-config-kit modules (004-config-package)
- JSON files (registry, package tracker) + YAML (manifests) + filesystem (.instructionkit/ structure) (004-config-package)

## Recent Changes
- 001-example-instruction-repo: Added Markdown (instruction content) | Python 3.10+ (for AI Config Kit CLI - no changes needed) + Git (for repository hosting), existing AI Config Kit commands (no new dependencies)
