"""Tools command to show detected AI coding tools."""

from rich.console import Console
from rich.table import Table

from devsync.ai_tools.detector import get_detector

console = Console()

# Map ComponentType enum values to user-facing filter names
_COMPONENT_TYPE_LABELS: dict[str, str] = {
    "instruction": "rules",
    "mcp_server": "mcp",
    "hook": "hooks",
    "command": "commands",
    "skill": "skills",
    "workflow": "workflows",
    "resource": "resources",
    "memory_file": "memory",
}


def show_tools(verbose: bool = False) -> int:
    """Show detected AI coding tools.

    Args:
        verbose: Show capabilities column and valid filter names.

    Returns:
        Exit code (0 for success)
    """
    from devsync.ai_tools.capability_registry import CAPABILITY_REGISTRY

    detector = get_detector()

    table = Table(title="AI Coding Tools", show_header=True, header_style="bold cyan")
    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    if verbose:
        table.add_column("Capabilities", style="dim")

    for tool_type, tool in detector.tools.items():
        is_installed = tool.is_installed()
        status = "[green]✓ Installed[/green]" if is_installed else "[red]✗ Not found[/red]"

        if verbose:
            cap = CAPABILITY_REGISTRY.get(tool_type)
            if cap:
                labels = sorted(_COMPONENT_TYPE_LABELS.get(ct.value, ct.value) for ct in cap.supported_components)
                caps_str = ", ".join(labels)
            else:
                caps_str = ""
            table.add_row(tool.tool_name, status, caps_str)
        else:
            table.add_row(tool.tool_name, status)

    console.print()
    console.print(table)
    console.print()

    installed = detector.detect_installed_tools()
    if installed:
        tool_names = ", ".join([t.tool_name for t in installed])
        console.print(f"[green]Found {len(installed)} installed tool(s):[/green] {tool_names}")
    else:
        console.print("[yellow]No AI coding tools detected[/yellow]")
        console.print("\nSupported tools: Cursor, GitHub Copilot, Winsurf, Claude Code")

    if verbose:
        all_labels = sorted(set(_COMPONENT_TYPE_LABELS.values()))
        console.print(f"\nValid --component names: {', '.join(all_labels)}")

    console.print()
    return 0
