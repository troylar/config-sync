"""Tests for __main__ entry point."""

import subprocess
import sys


def test_main_module_execution() -> None:
    """Test that the module can be executed as python -m aiconfigkit."""
    result = subprocess.run(
        [sys.executable, "-m", "aiconfigkit", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert "devsync" in result.stdout.lower() or "aiconfigkit" in result.stdout.lower()


def test_main_module_version() -> None:
    """Test that version command works through module entry point."""
    result = subprocess.run(
        [sys.executable, "-m", "aiconfigkit", "version"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Should output version number (check both stdout and stderr)
    output = result.stdout + result.stderr
    assert any(
        char.isdigit() for char in output
    ), f"No version found in output. stdout: {result.stdout!r}, stderr: {result.stderr!r}"
