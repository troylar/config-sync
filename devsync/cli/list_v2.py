"""Simplified list command for v2."""

import json as json_module
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from devsync.storage.package_tracker import PackageTracker
from devsync.utils.project import find_project_root

console = Console()


def list_v2_command(
    tool: Optional[str] = None,
    json: bool = False,
) -> int:
    """List installed packages and instructions.

    Args:
        tool: Filter by AI tool name.
        json: Output as JSON.

    Returns:
        Exit code (0 = success).
    """
    project_root = find_project_root(Path.cwd())
    if not project_root:
        project_root = Path.cwd()

    tracker = PackageTracker(project_root)

    try:
        packages = tracker.get_installed_packages()
    except Exception:
        packages = []

    if not packages:
        if json:
            console.print("[]")
        else:
            console.print("[dim]No packages installed in this project.[/dim]")
            console.print("Use [cyan]devsync install <source>[/cyan] to install packages.")
        return 0

    if tool:
        packages = [p for p in packages if _package_has_tool(p, tool)]

    if json:
        output = []
        for pkg in packages:
            pkg_dict = pkg.to_dict() if hasattr(pkg, "to_dict") else {"name": str(pkg)}
            output.append(pkg_dict)
        console.print(json_module.dumps(output, indent=2))
        return 0

    table = Table(title="Installed Packages")
    table.add_column("Package", style="cyan")
    table.add_column("Version")
    table.add_column("Components", justify="right")
    table.add_column("Status")

    for pkg in packages:
        name = getattr(pkg, "name", str(pkg))
        version = getattr(pkg, "version", "?")
        components = getattr(pkg, "components", [])
        component_count = len(components) if isinstance(components, list) else 0
        status = getattr(pkg, "status", "installed")
        status_style = "green" if status == "installed" or status == "COMPLETE" else "yellow"

        table.add_row(
            name,
            str(version),
            str(component_count),
            f"[{status_style}]{status}[/{status_style}]",
        )

    console.print(table)
    return 0


def _package_has_tool(pkg: object, tool_name: str) -> bool:
    """Check if a package has components for a specific tool."""
    components = getattr(pkg, "components", [])
    if isinstance(components, list):
        for comp in components:
            comp_tool = getattr(comp, "ai_tool", None) or getattr(comp, "tool", None)
            if comp_tool and str(comp_tool).lower() == tool_name.lower():
                return True
    return False
