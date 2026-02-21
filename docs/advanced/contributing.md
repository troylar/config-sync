# Contributing

## Development Setup

### Prerequisites

- Python 3.10 or later (supports 3.10 - 3.13)
- Git
- [pyenv](https://github.com/pyenv/pyenv) (recommended for managing Python versions)

### Clone and Install

```bash
git clone https://github.com/troylar/devsync.git
cd devsync

# Install in editable mode with dev dependencies
pip install -e .[dev]
```

Or use the invoke task:

```bash
invoke dev-setup
```

This installs the `devsync` CLI in your current environment, along with all development dependencies (pytest, black, ruff, mypy, invoke).

## Running Tests

```bash
# Run all tests
invoke test

# Run with coverage report
invoke test --coverage

# Run only unit tests
invoke test-unit

# Run only integration tests
invoke test-integration

# Run a specific test file
pytest tests/unit/test_models.py -v

# Run tests matching a pattern
pytest -k "test_conflict" -v
```

### Test Structure

```
tests/
  conftest.py              # Shared fixtures (temp_dir, mock repos, etc.)
  unit/                    # Fast, isolated tests (no I/O, no network)
    test_models.py
    test_checksum.py
    test_ai_tools.py
    ...
  integration/             # Tests with file I/O and Git operations
    test_library.py
    test_repository.py
    test_tracker.py
    ...
```

**Conventions:**

- Use fixtures from `conftest.py`, especially `temp_dir` for any file operations
- Integration tests may perform actual Git operations and file I/O
- All tests must clean up temporary files
- Minimum 80% code coverage target

## Code Quality

```bash
# Run all checks (lint + format check + typecheck)
invoke quality

# Run all checks and auto-fix what can be fixed
invoke quality --fix

# Individual tools
invoke lint              # Ruff linting
invoke lint --fix        # Auto-fix lint issues
invoke format            # Black formatting
invoke format --check    # Check formatting without changes
invoke typecheck         # mypy type checking
```

### Code Style

| Tool | Configuration |
|------|--------------|
| **Black** | Line length: 120 characters |
| **Ruff** | Rules: E, F, I, N, W |
| **mypy** | Strict mode (`disallow_untyped_defs=true`) |
| **Python** | 3.10+ -- use `list[str]` not `List[str]`, use `X \| Y` not `Union[X, Y]` |

**Conventions:**

- All functions must have type hints
- Use dataclasses for data models
- Use `Enum` for constants (`AIToolType`, `ConflictResolution`, `InstallationScope`)
- Google-style docstrings for all public functions and classes
- Line length: 120 characters maximum

## Commit Conventions

### Format

```
type(scope): description
```

### Types

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `test` | Adding or updating tests |
| `refactor` | Code refactoring (no behavior change) |
| `docs` | Documentation changes |
| `chore` | Maintenance (version bumps, CI config, etc.) |
| `perf` | Performance improvement |

### Scope

Use the module name: `cli`, `core`, `storage`, `ai_tools`, `llm`, `utils`.

### Examples

```
feat(cli): add batch install command
fix(storage): handle missing tracker file on first run
test(ai_tools): add Codex section marker tests
refactor(core): extract checksum logic into utility module
docs: update CLI reference with new flags
chore: bump version to 0.11.0
```

### Issue References

Reference GitHub issues in commit messages:

```bash
# Closes an issue when merged
git commit -m "fix(cli): handle empty library gracefully

Fixes #42"

# References an issue without closing it
git commit -m "test(storage): add tracker edge case tests

Refs #42"
```

## Branch Strategy

- **`main`** -- Always deployable, protected branch
- **Feature branches** -- Named `issue-###-short-description`

```bash
git checkout -b issue-42-batch-install
```

## CI/CD

GitHub Actions runs on every push and pull request:

- **Python versions:** 3.10, 3.11, 3.12, 3.13
- **Platforms:** ubuntu-latest, macos-latest, windows-latest
- **Steps:** lint, format check, typecheck, tests with coverage
- **Coverage:** uploaded to Codecov

The workflow is defined in `.github/workflows/ci.yml`.

### Local Pre-Push Hook

Enable the pre-push hook to catch issues before pushing:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

## Pull Request Workflow

1. **Create a GitHub issue first.** All work must be tied to an issue.

    ```bash
    gh issue create --title "Add batch install command" --label "enhancement"
    ```

2. **Create a feature branch** from `main`:

    ```bash
    git checkout -b issue-42-batch-install
    ```

3. **Make your changes.** Write tests. Run quality checks:

    ```bash
    invoke quality
    invoke test
    ```

4. **Commit** with issue references:

    ```bash
    git commit -m "feat(cli): add batch install command

    Closes #42"
    ```

5. **Push and open a PR:**

    ```bash
    git push -u origin issue-42-batch-install
    gh pr create --title "Add batch install command" --body "Closes #42"
    ```

6. **Wait for CI** to pass, then request review.

## Adding a New AI Tool

1. Create `devsync/ai_tools/newtool.py` inheriting from `AITool`
2. Implement the required abstract methods: `tool_type`, `tool_name`, `is_installed()`, `get_instructions_directory()`, `get_instruction_file_extension()`, `get_project_instructions_directory()`
3. Add the tool to `AIToolType` enum in `devsync/core/models.py`
4. Register in `devsync/ai_tools/detector.py`
5. Add an `IDECapability` entry in `devsync/ai_tools/capability_registry.py`
6. Add a translator if the tool uses a non-standard format
7. Add tests in `tests/unit/test_ai_tools.py`

## Adding a New CLI Command

The v2 CLI has six commands: `setup`, `tools`, `extract`, `install`, `list`, `uninstall`. These are defined in the following files:

| Command | File |
|---------|------|
| `setup` | `devsync/cli/setup.py` |
| `tools` | `devsync/cli/tools.py` |
| `extract` | `devsync/cli/extract.py` |
| `install` | `devsync/cli/install_v2.py` |
| `list` | `devsync/cli/list_v2.py` |
| `uninstall` | `devsync/cli/uninstall.py` |

To add a new command:

1. Create a command file in `devsync/cli/` (e.g., `devsync/cli/my_command.py`)
2. Define the command function with Typer decorators
3. Register in `devsync/cli/main.py`
4. Add tests in `tests/unit/test_cli.py`

## Useful Commands

```bash
invoke count             # Count lines of code
invoke version           # Show current version
invoke tree              # Show project structure
invoke security-check    # Run security scans
invoke clean             # Clean build artifacts
invoke build             # Build distribution package
```
