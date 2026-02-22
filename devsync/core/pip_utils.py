"""Pip package validation, detection, and installation utilities.

All pip-related logic is isolated here for security audit. Functions validate
inputs, detect installed packages, resolve commands to pip packages, and
install packages with comprehensive error handling.
"""

import importlib.metadata
import logging
import os
import re
import shutil
import subprocess
import sys
from typing import Optional

logger = logging.getLogger(__name__)

# Allowlist pattern for pip package specs: name, name>=1.0, name[extra]==2.0, etc.
# Rejects URLs, paths, and shell metacharacters.
_PIP_SPEC_PATTERN = re.compile(
    r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?"  # package name
    r"(\[[A-Za-z0-9,._-]+\])?"  # optional extras
    r"([<>=!~]+[A-Za-z0-9.*]+)?"  # optional version constraint
    r"$"
)

_DANGEROUS_CHARS = set(";|&$`{}()\n\r")


def validate_pip_spec(spec: str) -> bool:
    """Validate a pip package specifier against an allowlist.

    Accepts: 'name', 'name>=1.0', 'name[extra]==2.0'
    Rejects: URLs, file paths, shell metacharacters, empty strings.

    Args:
        spec: Pip package specifier string.

    Returns:
        True if the spec is valid and safe.
    """
    if not spec or not spec.strip():
        return False

    spec = spec.strip()

    if any(c in spec for c in _DANGEROUS_CHARS):
        return False

    if "://" in spec or spec.startswith(("git+", "file:", "/", "\\", ".")):
        return False

    return bool(_PIP_SPEC_PATTERN.match(spec))


def _extract_base_name(spec: str) -> str:
    """Extract the base package name from a pip spec, stripping version/extras."""
    name = re.split(r"[<>=!~\[]", spec.strip())[0]
    return name


def is_pip_installed(package_name: str) -> bool:
    """Check if a pip package is installed.

    Args:
        package_name: Package name (version constraints are stripped).

    Returns:
        True if the package is installed.
    """
    base = _extract_base_name(package_name)
    try:
        importlib.metadata.version(base)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False


def get_installed_version(package_name: str) -> Optional[str]:
    """Get the installed version of a pip package.

    Args:
        package_name: Package name (version constraints are stripped).

    Returns:
        Version string or None if not installed.
    """
    base = _extract_base_name(package_name)
    try:
        return importlib.metadata.version(base)
    except importlib.metadata.PackageNotFoundError:
        return None


def installed_version_satisfies(spec: str) -> bool:
    """Check if the installed version of a package satisfies the spec.

    Args:
        spec: Pip package specifier (e.g., 'mcp-server>=1.0').

    Returns:
        True if the package is installed and satisfies the version constraint.
        False if not installed or version doesn't satisfy.
    """
    base = _extract_base_name(spec)
    installed = get_installed_version(base)
    if installed is None:
        return False

    # Extract version constraint from spec
    constraint_match = re.search(r"([<>=!~]+.+)$", spec.strip())
    if not constraint_match:
        return True

    constraint = constraint_match.group(1)

    try:
        from packaging.specifiers import SpecifierSet
        from packaging.version import Version

        specifier = SpecifierSet(constraint)
        return Version(installed) in specifier
    except ImportError:
        # packaging not available — fall back to simple presence check
        logger.debug("packaging library not available, skipping version constraint check")
        return True
    except Exception:
        # Invalid version/spec — assume satisfied to avoid blocking install
        return True


def resolve_pip_package_for_command(command: str, args: list[str]) -> Optional[str]:
    """Resolve a command/args pair to a pip package name if possible.

    Patterns detected:
    - command="python" (or python3), args contains "-m", "module_name"
    - command="uvx", first arg is package name
    - command is a console_script entry point

    Args:
        command: The executable command.
        args: Command arguments.

    Returns:
        Pip package name or None if unrecognized.
    """
    try:
        return _resolve_pip_package_for_command_inner(command, args)
    except Exception as e:
        logger.warning("Failed to resolve pip package for command %s: %s", command, e)
        return None


def _resolve_pip_package_for_command_inner(command: str, args: list[str]) -> Optional[str]:
    """Inner implementation of resolve_pip_package_for_command."""
    cmd_basename = os.path.basename(command)

    # Pattern 1: python -m module_name
    if cmd_basename == "python" or cmd_basename == "python3" or re.match(r"python3\.\d+$", cmd_basename):
        if "-m" in args:
            m_idx = args.index("-m")
            if m_idx + 1 < len(args):
                module_name = args[m_idx + 1]
                return _find_distribution_for_module(module_name)

    # Pattern 2: uvx package_name
    if cmd_basename == "uvx":
        if args:
            pkg_name = args[0]
            if not pkg_name.startswith("-") and validate_pip_spec(pkg_name):
                return pkg_name

    # Pattern 3: command is a console_script entry point
    dist = _find_distribution_for_script(cmd_basename)
    if dist:
        return dist

    return None


def _find_distribution_for_module(module_name: str) -> Optional[str]:
    """Find the distribution that provides a given top-level module.

    Compatible with Python 3.10+ (packages_distributions() is 3.11+).
    """
    # Try packages_distributions() (3.11+)
    try:
        pkg_dists = importlib.metadata.packages_distributions()  # type: ignore[attr-defined]
        dists = pkg_dists.get(module_name)
        if dists:
            return dists[0]
    except AttributeError:
        pass

    # Fallback for 3.10: iterate distributions
    for dist in importlib.metadata.distributions():
        top_level = dist.read_text("top_level.txt")
        if top_level:
            modules = [m.strip() for m in top_level.strip().split("\n") if m.strip()]
            if module_name in modules:
                return dist.metadata["Name"]

    return None


def _find_distribution_for_script(script_name: str) -> Optional[str]:
    """Find the distribution that provides a given console_script entry point.

    Compatible with Python 3.10+ (entry_points() API varies by version).
    """
    try:
        eps = importlib.metadata.entry_points()
        # Python 3.12+: eps.select()
        if hasattr(eps, "select"):
            console_scripts = eps.select(group="console_scripts")  # type: ignore[union-attr]
        elif isinstance(eps, dict):
            # Python 3.10-3.11: eps is a dict
            console_scripts = eps.get("console_scripts", [])  # type: ignore[arg-type]
        else:
            console_scripts = []

        for ep in console_scripts:
            if ep.name == script_name:
                # ep.dist may not exist on all versions
                if hasattr(ep, "dist") and ep.dist is not None:
                    return ep.dist.metadata["Name"]
                continue
    except Exception:
        pass

    return None


def find_pip_executable() -> Optional[str]:
    """Find a usable way to run pip.

    Prefers `sys.executable -m pip` (respects current venv),
    falls back to `shutil.which("pip")`.

    Returns:
        Python executable path (for `-m pip` usage) or standalone pip path,
        or None if pip is unavailable.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            return sys.executable
    except (OSError, subprocess.TimeoutExpired):
        pass

    pip_path = shutil.which("pip")
    if pip_path:
        return pip_path

    return None


def install_pip_package(spec: str, timeout: int = 120) -> tuple[bool, str]:
    """Install a pip package with comprehensive error handling.

    Validates the spec first, then runs pip install in a subprocess.

    Args:
        spec: Pip package specifier (e.g., 'mcp-server-github>=1.0').
        timeout: Maximum seconds to wait for install.

    Returns:
        Tuple of (success, message).
    """
    if not validate_pip_spec(spec):
        return (False, f"Invalid pip package spec: {spec}")

    pip_exe = find_pip_executable()
    if not pip_exe:
        return (False, "pip is not available. Install pip or use a virtual environment.")

    # Build command: either `python -m pip install` or `pip install`
    if pip_exe == sys.executable:
        cmd = [sys.executable, "-m", "pip", "install", spec]
    else:
        cmd = [pip_exe, "install", spec]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        if result.returncode == 0:
            return (True, f"Successfully installed {spec}")

        stderr = result.stderr.lower()
        if "no matching distribution" in stderr:
            return (False, f"Package not found: {spec}")
        if "could not find a version" in stderr:
            return (False, f"No compatible version found for {spec}")
        if "permission denied" in stderr or "permissionerror" in stderr:
            return (False, f"Permission denied installing {spec}. Try using a virtual environment.")

        return (False, f"pip install failed for {spec} (exit code {result.returncode})")

    except subprocess.TimeoutExpired:
        return (False, f"pip install timed out after {timeout}s for {spec}")
    except OSError as e:
        return (False, f"Failed to run pip: {e}")
