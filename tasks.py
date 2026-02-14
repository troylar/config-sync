"""
Invoke tasks for DevSync development.

Install invoke: pip install invoke
Usage: invoke <task-name>
List all tasks: invoke --list
"""

import sys
from pathlib import Path

from invoke import task

# Project paths
ROOT = Path(__file__).parent
SRC = ROOT / "aiconfigkit"
TESTS = ROOT / "tests"

# Check if pty is available (not available on Windows)
PTY_SUPPORTED = sys.platform != "win32"


# ============================================================================
# Testing Tasks
# ============================================================================

@task
def test(c, verbose=False, coverage=False, marker=None):
    """
    Run all tests.

    Options:
        -v, --verbose: Verbose output
        -c, --coverage: Generate coverage report
        -m, --marker: Run tests with specific marker (e.g., 'unit', 'integration')
    """
    cmd = "pytest tests/"

    if verbose:
        cmd += " -vv"
    else:
        cmd += " -q"

    if coverage:
        cmd += " --cov=aiconfigkit --cov-report=term-missing --cov-report=xml --cov-report=html"

    if marker:
        cmd += f" -m {marker}"

    c.run(cmd, pty=PTY_SUPPORTED)


@task
def test_unit(c, verbose=False):
    """Run unit tests only."""
    cmd = "pytest tests/unit/"
    if verbose:
        cmd += " -vv"
    else:
        cmd += " -q"
    c.run(cmd, pty=PTY_SUPPORTED)


@task
def test_integration(c, verbose=False):
    """Run integration tests only."""
    cmd = "pytest tests/integration/"
    if verbose:
        cmd += " -vv"
    else:
        cmd += " -q"
    c.run(cmd, pty=PTY_SUPPORTED)


@task
def test_watch(c):
    """Run tests in watch mode (requires pytest-watch)."""
    c.run("ptw tests/ -- -q", pty=PTY_SUPPORTED)


@task
def coverage(c, html=True):
    """
    Generate test coverage report.

    Options:
        --html: Generate HTML coverage report (default: True)
    """
    cmd = "pytest tests/ --cov=aiconfigkit --cov-report=term-missing --cov-report=xml"

    if html:
        cmd += " --cov-report=html"
        print("\n📊 HTML coverage report: htmlcov/index.html")

    print("📄 XML coverage report: coverage.xml")

    c.run(cmd, pty=PTY_SUPPORTED)


# ============================================================================
# Code Quality Tasks
# ============================================================================

@task
def lint(c, fix=False):
    """
    Run ruff linter.

    Options:
        -f, --fix: Automatically fix issues
    """
    cmd = "ruff check aiconfigkit/ tests/"

    if fix:
        cmd += " --fix"

    c.run(cmd, pty=PTY_SUPPORTED)


@task
def format(c, check=False):
    """
    Format code with black.

    Options:
        -c, --check: Check formatting without making changes
    """
    cmd = "black aiconfigkit/ tests/"

    if check:
        cmd += " --check"

    c.run(cmd, pty=PTY_SUPPORTED)


@task
def typecheck(c):
    """Run mypy type checking."""
    c.run("mypy aiconfigkit/", pty=PTY_SUPPORTED)


@task
def quality(c, fix=False):
    """
    Run all code quality checks.

    Options:
        -f, --fix: Automatically fix issues where possible
    """
    print("🔍 Running linter...")
    lint(c, fix=fix)

    print("\n🎨 Checking formatting...")
    format(c, check=not fix)

    print("\n📝 Type checking...")
    typecheck(c)

    print("\n✅ Quality checks complete!")


# ============================================================================
# Build & Installation Tasks
# ============================================================================

@task
def clean(c):
    """Clean build artifacts and caches."""
    patterns = [
        "build/",
        "dist/",
        "*.egg-info/",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        ".pytest_cache/",
        ".mypy_cache/",
        ".ruff_cache/",
        "htmlcov/",
        ".coverage",
        "*.log",
    ]

    for pattern in patterns:
        c.run(f"find . -type d -name '{pattern}' -exec rm -rf {{}} + 2>/dev/null || true")
        c.run(f"find . -type f -name '{pattern}' -delete 2>/dev/null || true")

    print("🧹 Cleaned all build artifacts and caches")


@task(pre=[clean])
def build(c):
    """Build the package."""
    c.run("python -m build", pty=PTY_SUPPORTED)
    print("\n📦 Package built successfully!")


@task
def install(c, dev=False, editable=True):
    """
    Install the package.

    Options:
        -d, --dev: Install with development dependencies
        -e, --editable: Install in editable mode (default: True)
    """
    if editable:
        cmd = "pip install -e ."
    else:
        cmd = "pip install ."

    if dev:
        cmd += "[dev]"

    c.run(cmd, pty=PTY_SUPPORTED)
    print("✅ Package installed successfully!")


@task
def uninstall(c):
    """Uninstall the package."""
    c.run("pip uninstall -y devsync", pty=PTY_SUPPORTED)
    print("✅ Package uninstalled successfully!")


# ============================================================================
# Development Tasks
# ============================================================================

@task
def dev_setup(c):
    """Set up development environment."""
    print("🔧 Setting up development environment...")

    print("\n📦 Installing package in editable mode with dev dependencies...")
    c.run("pip install -e .[dev]", pty=PTY_SUPPORTED)

    print("\n✅ Development environment ready!")
    print("\n💡 Quick commands:")
    print("  invoke test          - Run all tests")
    print("  invoke quality       - Run code quality checks")
    print("  invoke lint --fix    - Auto-fix linting issues")
    print("  invoke --list        - See all available tasks")


@task
def repl(c):
    """Start Python REPL with aiconfigkit imported."""
    c.run("python -i -c 'import aiconfigkit; print(\"DevSync imported\")'", pty=PTY_SUPPORTED)


# ============================================================================
# CLI Tasks
# ============================================================================

@task
def cli(c, args="--help"):
    """
    Run the aiconfigkit CLI.

    Usage: invoke cli --args="download --repo https://..."
    """
    c.run(f"aiconfig {args}", pty=PTY_SUPPORTED)


@task
def list_tools(c):
    """List detected AI tools."""
    c.run("aiconfig tools", pty=PTY_SUPPORTED)


@task
def list_library(c):
    """List instructions in library."""
    c.run("aiconfig list library", pty=PTY_SUPPORTED)


# ============================================================================
# Documentation Tasks
# ============================================================================

@task
def docs_serve(c, port=8000):
    """
    Serve documentation locally (if using MkDocs or similar).

    Options:
        -p, --port: Port to serve on (default: 8000)
    """
    print(f"📚 Serving documentation on http://localhost:{port}")
    # Placeholder - add when docs are set up
    print("⚠️  Documentation server not yet configured")


# ============================================================================
# Release Tasks
# ============================================================================

@task
def version(c):
    """Show current version."""
    result = c.run("grep 'version =' pyproject.toml | cut -d'\"' -f2", hide=True)
    version = result.stdout.strip()
    print(f"📌 Current version: {version}")
    return version


@task(pre=[clean, quality, test])
def release_check(c):
    """
    Run all checks before release.

    Runs: clean, quality checks, and full test suite
    """
    print("\n✅ All release checks passed!")
    print("\n📋 Next steps:")
    print("  1. Update version in pyproject.toml")
    print("  2. Update CHANGELOG")
    print("  3. Run: invoke build")
    print("  4. Run: git tag v<version>")
    print("  5. Run: git push --tags")


@task(pre=[build])
def publish(c, repository="pypi", skip_existing=True):
    """Publish the current build to PyPI using twine.

    Options:
        --repository: Target repository alias (default: "pypi")
        --skip-existing: Skip packages that already exist on the server (default: True)
    """

    dist_path = ROOT / "dist"

    if not dist_path.exists() or not any(dist_path.iterdir()):
        raise RuntimeError("No distributions found in dist/. Run 'invoke build' first.")

    skip_flag = " --skip-existing" if skip_existing else ""
    cmd = f"twine upload -r {repository}{skip_flag} dist/*"
    c.run(cmd, pty=PTY_SUPPORTED)

    print("\n🚀 Upload complete!")
    print("📦 Repository:", repository)
    print("📂 Uploaded artifacts from:", dist_path)


# ============================================================================
# Utility Tasks
# ============================================================================

@task
def count(c):
    """Count lines of code."""
    print("📊 Lines of Code:\n")

    # Source code
    result = c.run("find aiconfigkit -name '*.py' | xargs wc -l | tail -1", hide=True)
    src_lines = result.stdout.strip().split()[0]
    print(f"  Source:      {src_lines:>6} lines")

    # Test code
    result = c.run("find tests -name '*.py' | xargs wc -l | tail -1", hide=True)
    test_lines = result.stdout.strip().split()[0]
    print(f"  Tests:       {test_lines:>6} lines")

    # Total
    total = int(src_lines) + int(test_lines)
    print(f"  Total:       {total:>6} lines")


@task
def tree(c, level=2):
    """
    Show project structure.

    Options:
        -l, --level: Tree depth level (default: 2)
    """
    ignore = "__pycache__|*.pyc|*.egg-info|htmlcov|.pytest_cache|.mypy_cache|.ruff_cache"
    cmd = f"tree -L {level} -I '{ignore}'"
    c.run(cmd, pty=PTY_SUPPORTED)


@task(name="security-check")
def security_check(c):
    """Run security checks with bandit and safety."""
    print("🔒 Running security checks...\n")

    print("1. Checking for known vulnerabilities (safety)...")
    c.run("pip install safety", hide=True)
    c.run("safety check", warn=True)

    print("\n2. Checking for security issues in code (bandit)...")
    c.run("pip install bandit", hide=True)
    c.run("bandit -r aiconfigkit/ -ll", warn=True)

    print("\n✅ Security checks complete!")


# ============================================================================
# Aliases
# ============================================================================

@task
def t(c, verbose=False):
    """Alias for 'test'."""
    test(c, verbose=verbose)


@task
def cov(c):
    """Alias for 'coverage'."""
    coverage(c)


@task
def fmt(c, check=False):
    """Alias for 'format'."""
    format(c, check=check)


@task
def check(c):
    """Alias for 'quality'."""
    quality(c)
