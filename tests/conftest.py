"""Pytest fixtures for DevSync tests."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_project_dir(temp_dir: Path) -> Path:
    """Create a mock project directory with Git."""
    project = temp_dir / "test-project"
    project.mkdir()

    # Create .git directory to mark as project root
    (project / ".git").mkdir()

    # Create a simple file
    (project / "README.md").write_text("# Test Project")

    return project


@pytest.fixture
def mock_instruction_repo(temp_dir: Path) -> Path:
    """Create a mock instruction repository."""
    repo = temp_dir / "test-instructions"
    repo.mkdir()

    # Create templatekit.yaml
    yaml_content = """name: Test Instructions
description: Test instruction repository
version: 1.0.0
author: Test Author

instructions:
  - name: python-style
    description: Python style guidelines
    file: instructions/python-style.md
    tags:
      - python
      - style

  - name: testing-guide
    description: Testing best practices
    file: instructions/testing-guide.md
    tags:
      - testing
      - quality

bundles:
  - name: python-stack
    description: Complete Python development setup
    instructions:
      - python-style
      - testing-guide
    tags:
      - python
"""
    (repo / "templatekit.yaml").write_text(yaml_content)

    # Create instructions directory
    instructions_dir = repo / "instructions"
    instructions_dir.mkdir()

    # Create instruction files
    (instructions_dir / "python-style.md").write_text("# Python Style Guide\n\nFollow PEP 8 standards.")
    (instructions_dir / "testing-guide.md").write_text("# Testing Guide\n\nWrite tests for all code.")

    return repo


@pytest.fixture
def mock_library_dir(temp_dir: Path) -> Path:
    """Create a mock library directory."""
    library = temp_dir / ".instructionkit" / "library"
    library.mkdir(parents=True)
    return library


@pytest.fixture
def mock_home_dir(temp_dir: Path, monkeypatch) -> Path:
    """Mock the home directory."""
    home = temp_dir / "home"
    home.mkdir()

    # Patch Path.home() to return our mock home
    monkeypatch.setattr(Path, "home", lambda: home)

    return home
