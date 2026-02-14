# Development Guide

This guide covers development workflows, tools, and best practices for contributing to DevSync.

---

## 🚀 Quick Start

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/devsync.git
cd devsync

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
invoke dev-setup
# Or manually:
pip install -e .[dev]
```

---

## 📋 Using Invoke Tasks

DevSync uses [Invoke](https://www.pyinvoke.org/) for task automation. All common development operations are available as invoke tasks.

### List All Available Tasks

```bash
invoke --list
```

### Common Tasks

#### Testing

```bash
# Run all tests
invoke test

# Run tests with verbose output
invoke test --verbose

# Run tests with coverage report
invoke test --coverage

# Run only unit tests
invoke test-unit

# Run only integration tests
invoke test-integration

# Generate coverage report
invoke coverage

# Run tests in watch mode (requires pytest-watch)
invoke test-watch
```

#### Code Quality

```bash
# Run linter (ruff)
invoke lint

# Auto-fix linting issues
invoke lint --fix

# Format code (black)
invoke format

# Check formatting without changes
invoke format --check

# Run type checking (mypy)
invoke typecheck

# Run all quality checks
invoke quality

# Auto-fix all fixable issues
invoke quality --fix
```

#### Build & Installation

```bash
# Clean build artifacts and caches
invoke clean

# Build the package
invoke build

# Install package in editable mode
invoke install

# Install with dev dependencies
invoke install --dev

# Uninstall package
invoke uninstall
```

#### CLI Operations

```bash
# Run CLI with custom arguments
invoke cli --args="download --repo https://github.com/example/repo"

# List detected AI tools
invoke list-tools

# List instructions in library
invoke list-library
```

#### Utilities

```bash
# Count lines of code
invoke count

# Show project structure
invoke tree

# Show current version
invoke version

# Run security checks
invoke security-check

# Pre-release checks (quality + tests)
invoke release-check
```

#### Aliases

```bash
invoke t              # Alias for 'test'
invoke cov            # Alias for 'coverage'
invoke fmt            # Alias for 'format'
invoke check          # Alias for 'quality'
```

---

## 🧪 Testing

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── integration/             # Integration tests
│   ├── test_library.py
│   ├── test_repository.py
│   └── test_tracker.py
└── unit/                    # Unit tests
    ├── test_checksum.py
    ├── test_models.py
    └── ...
```

### Running Specific Tests

```bash
# Run a specific test file
pytest tests/unit/test_models.py

# Run a specific test class
pytest tests/unit/test_models.py::TestInstruction

# Run a specific test function
pytest tests/unit/test_models.py::TestInstruction::test_create_valid_instruction

# Run tests matching a pattern
pytest -k "repository"

# Run with specific marker
pytest -m unit
```

### Test Coverage

```bash
# Generate coverage report
invoke coverage

# View HTML coverage report
open htmlcov/index.html
```

### Writing Tests

**Example Unit Test:**

```python
def test_parse_conflict_strategy():
    """Test conflict strategy parsing."""
    from ai-config-kit.cli.install_new import _parse_conflict_strategy
    from ai-config-kit.core.models import ConflictResolution
    
    result = _parse_conflict_strategy("skip")
    assert result == ConflictResolution.SKIP
    
    result = _parse_conflict_strategy("invalid")
    assert result is None
```

**Example Integration Test:**

```python
def test_add_repository(temp_dir: Path):
    """Test adding a repository to library."""
    from ai-config-kit.storage.library import LibraryManager
    
    manager = LibraryManager(temp_dir / "library")
    repo = manager.add_repository(
        repo_name="Test Repo",
        repo_description="Test",
        repo_url="https://github.com/test/repo",
        repo_author="Author",
        repo_version="1.0.0",
        instructions=[],
    )
    
    assert repo.name == "Test Repo"
```

---

## 🎨 Code Style

### Formatting & Linting

DevSync uses:
- **Black** for code formatting (line length: 100)
- **Ruff** for fast Python linting
- **MyPy** for type checking

```bash
# Format all code
invoke format

# Check formatting
invoke format --check

# Lint all code
invoke lint

# Auto-fix lint issues
invoke lint --fix

# Run type checking
invoke typecheck

# Run all checks
invoke quality --fix
```

### Code Style Guidelines

1. **Use type hints**
   ```python
   def process_instruction(name: str, tags: list[str]) -> Optional[Instruction]:
       ...
   ```

2. **Descriptive names**
   ```python
   # Good
   def get_project_root_for_installation() -> Optional[Path]:
       ...
   
   # Bad
   def get_pr() -> Path:
       ...
   ```

3. **Docstrings**
   ```python
   def parse_repository(repo_path: Path) -> Repository:
       """
       Parse instruction repository metadata and files.
       
       Args:
           repo_path: Path to cloned repository
           
       Returns:
           Repository object with instructions loaded
           
       Raises:
           FileNotFoundError: If metadata file not found
       """
       ...
   ```

4. **Small, focused functions**
   - Keep functions under 50 lines when possible
   - Single responsibility principle
   - Extract helper functions for clarity

---

## 📦 Project Structure

```
ai-config-kit/
├── ai_tools/           # AI tool integrations
│   ├── base.py        # Abstract base class
│   ├── claude.py      # Claude integration
│   ├── cursor.py      # Cursor integration
│   └── detector.py    # Tool detection
├── cli/               # CLI commands
│   ├── main.py        # Main CLI entry
│   ├── install.py     # Install command
│   └── ...
├── core/              # Core business logic
│   ├── models.py      # Data models
│   ├── repository.py  # Repository parsing
│   └── ...
├── storage/           # Data persistence
│   ├── library.py     # Library management
│   └── tracker.py     # Installation tracking
├── tui/               # Terminal UI
│   └── installer.py   # TUI installer
└── utils/             # Utilities
    ├── logging.py     # Logging setup
    ├── project.py     # Project detection
    └── ...
```

---

## 🔄 Development Workflow

### Feature Development

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests first** (TDD approach)
   ```bash
   # Create test file
   touch tests/unit/test_your_feature.py
   
   # Write failing tests
   invoke test
   ```

3. **Implement feature**
   ```python
   # Write implementation
   ```

4. **Run quality checks**
   ```bash
   invoke quality --fix
   invoke test --coverage
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Enforcing CI Locally Before Pushing to `main`

To mirror GitHub Actions checks locally, install the provided Git hooks:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

The `pre-push` hook runs `invoke lint`, `invoke format --check`, `invoke typecheck`, and `invoke test --coverage` whenever you push to `main`. The push is blocked if any step fails. Ensure `invoke` is available (`pip install -e .[dev]`).

### Bug Fixes

1. **Create test reproducing the bug**
   ```python
   def test_bug_reproduction():
       """Test that reproduces issue #123."""
       # Code that fails with the bug
       ...
   ```

2. **Fix the bug**
   ```python
   # Implement fix
   ```

3. **Verify test passes**
   ```bash
   invoke test
   ```

4. **Run quality checks**
   ```bash
   invoke quality
   ```

---

## 🐛 Debugging

### Debug Logging

```python
import logging

logger = logging.getLogger(__name__)

# Set debug level
logging.basicConfig(level=logging.DEBUG)

# Add debug statements
logger.debug(f"Processing instruction: {instruction.name}")
```

### Interactive Debugging

```python
# Add breakpoint
breakpoint()

# Or use pdb
import pdb; pdb.set_trace()
```

### Running with Debug Output

```bash
# Run with debug logging
LOGLEVEL=DEBUG aiconfig install

# Run specific test with output
pytest tests/unit/test_models.py -s
```

---

## 📊 Performance Testing

### Profiling

```python
import cProfile
import pstats

def profile_function():
    with cProfile.Profile() as pr:
        # Your code here
        result = expensive_operation()
    
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### Benchmarking

```bash
# Time command execution
time aiconfig install test-instruction

# Memory profiling (requires memory_profiler)
python -m memory_profiler script.py
```

---

## 🔐 Security

### Security Checks

```bash
# Run security checks
invoke security-check

# Check dependencies for vulnerabilities
pip install safety
safety check

# Scan code for security issues
pip install bandit
bandit -r ai-config-kit/
```

### Security Best Practices

1. **Never commit secrets**
   - Use environment variables
   - Add to `.gitignore`

2. **Validate all inputs**
   ```python
   def validate_instruction_name(name: str) -> bool:
       # Validate against pattern
       return bool(re.match(r'^[a-z0-9\-]+$', name))
   ```

3. **Safe file operations**
   ```python
   # Check for path traversal
   def is_safe_path(path: Path) -> bool:
       try:
           path.resolve().relative_to(ROOT)
           return True
       except ValueError:
           return False
   ```

---

## 📝 Documentation

### Docstring Format

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description.
    
    Longer description explaining what the function does,
    any important details, and edge cases.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        FileNotFoundError: When file doesn't exist
        
    Example:
        >>> function_name("test", 42)
        True
    """
    ...
```

### Adding Documentation

1. Update docstrings in code
2. Update README.md for user-facing features
3. Update this DEVELOPMENT.md for dev workflows
4. Create ADRs (Architecture Decision Records) for major decisions

---

## 🚢 Release Process

### Pre-Release Checklist

```bash
# 1. Run all checks
invoke release-check

# 2. Update version in pyproject.toml
# Edit pyproject.toml: version = "x.y.z"

# 3. Update CHANGELOG.md
# Add release notes

# 4. Commit changes
git add .
git commit -m "chore: release v0.2.0"

# 5. Tag release
git tag v0.2.0

# 6. Push
git push origin main --tags

# 7. Build package
invoke build

# 8. Publish to PyPI (manual for now)
# twine upload dist/*
```

---

## 🛠️ Troubleshooting

### Common Issues

**Tests failing after refactoring:**
```bash
# Clear caches
invoke clean

# Reinstall in editable mode
invoke install --dev

# Run tests
invoke test
```

**Import errors:**
```bash
# Ensure package is installed
pip install -e .[dev]

# Check Python path
python -c "import sys; print(sys.path)"
```

**Linting errors:**
```bash
# Auto-fix what's possible
invoke lint --fix

# Format code
invoke format

# Check remaining issues
invoke quality
```

---

## 💡 Tips & Tricks

### Faster Test Development

```bash
# Run specific test in watch mode
ptw tests/unit/test_models.py -- -vv

# Run with last failed tests only
pytest --lf
```

### Quick Checks

```bash
# Before committing
invoke quality && invoke test

# Alias for convenience
alias qa="invoke quality && invoke test"
```

### IDE Configuration

**VS Code settings.json:**
```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

---

## 📚 Resources

### Documentation
- [Python Packaging Guide](https://packaging.python.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Invoke Documentation](https://www.pyinvoke.org/)

### Code Style
- [PEP 8](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints (PEP 484)](https://peps.python.org/pep-0484/)

### Tools
- [Black](https://black.readthedocs.io/)
- [Ruff](https://docs.astral.sh/ruff/)
- [MyPy](https://mypy.readthedocs.io/)

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

### Quick Contribution Checklist

- [ ] Tests added/updated
- [ ] Code formatted (`invoke format`)
- [ ] Linting passes (`invoke lint`)
- [ ] Type checking passes (`invoke typecheck`)
- [ ] All tests pass (`invoke test`)
- [ ] Documentation updated
- [ ] Commit messages follow convention

---

## 📞 Getting Help

- **Issues**: https://github.com/troylar/devsync/issues
- **Discussions**: https://github.com/troylar/devsync/discussions
- **Documentation**: See README.md and docs/

---

**Happy coding! 🎉**
