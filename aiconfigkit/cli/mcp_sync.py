"""CLI command for syncing MCP servers to AI tools."""

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from aiconfigkit.ai_tools.mcp_syncer import MCPSyncer
from aiconfigkit.core.models import InstallationScope

logger = logging.getLogger(__name__)
console = Console()


def mcp_sync_command(
    tool: str = typer.Option(
        "all",
        "--tool",
        "-t",
        help="AI tool to sync to (claude, cursor, windsurf, or all)",
    ),
    scope: str = typer.Option(
        "project",
        "--scope",
        help="Scope to load configurations from (project or global)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be synced without actually syncing",
    ),
    no_backup: bool = typer.Option(
        False,
        "--no-backup",
        help="Skip creating backup of config files before modifying",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
) -> int:
    """
    Sync configured MCP servers to AI tool configuration files.

    This command reads installed MCP servers from the library, resolves their
    environment variables from .instructionkit/.env, and writes them to AI
    tool configuration files (e.g., claude_desktop_config.json).

    Examples:

        # Sync to all detected AI tools
        devsync mcp sync --tool all

        # Sync to specific tool
        devsync mcp sync --tool claude

        # Dry run to see what would be synced
        devsync mcp sync --tool all --dry-run

        # Sync without creating backups
        devsync mcp sync --tool claude --no-backup

        # Sync global configurations
        devsync mcp sync --scope global
    """
    try:
        # Parse scope
        try:
            install_scope = InstallationScope(scope)
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid scope '{scope}'. Must be 'project' or 'global'")
            return 1

        # Create syncer
        syncer = MCPSyncer(
            library_root=Path.home() / ".instructionkit" / "library",
            project_root=Path.cwd(),
        )

        # Parse tool names
        tool_names = [tool] if tool != "all" else ["all"]

        # Show sync info
        if not json_output:
            console.print("\n[bold]Syncing MCP servers to AI tools[/bold]")
            console.print(f"Scope: {install_scope.value}")
            console.print(f"Tools: {tool}")
            if dry_run:
                console.print("[yellow]DRY RUN - no changes will be made[/yellow]")
            console.print()

        # Perform sync
        result = syncer.sync_all(
            tool_names=tool_names,
            scope=install_scope,
            create_backup=not no_backup,
            dry_run=dry_run,
        )

        # Output results
        if json_output:
            import json

            output = {
                "success": result.success,
                "synced_tools": result.synced_tools,
                "skipped_tools": [{"name": name, "reason": reason} for name, reason in result.skipped_tools],
                "synced_servers": result.synced_servers,
                "skipped_servers": [{"name": name, "reason": reason} for name, reason in result.skipped_servers],
            }
            console.print(json.dumps(output, indent=2))
        else:
            # Show synced tools
            if result.synced_tools:
                console.print(f"[green]✓[/green] Synced to {len(result.synced_tools)} tool(s):")
                for tool_name in result.synced_tools:
                    console.print(f"  • {tool_name}")
            else:
                console.print("[yellow]⚠[/yellow] No tools were synced")

            # Show skipped tools
            if result.skipped_tools:
                console.print(f"\n[yellow]⚠[/yellow] Skipped {len(result.skipped_tools)} tool(s):")
                for tool_name, reason in result.skipped_tools:
                    console.print(f"  • {tool_name}: {reason}")

            # Show server summary
            console.print("\n[bold]Server Summary:[/bold]")
            console.print(f"  Synced: {len(result.synced_servers)} server(s)")
            if result.skipped_servers:
                console.print(f"  Skipped: {len(result.skipped_servers)} server(s)")

            # Show skipped servers details
            if result.skipped_servers:
                console.print("\n[yellow]Skipped Servers:[/yellow]")
                table = Table(show_header=True)
                table.add_column("Server", style="cyan")
                table.add_column("Reason", style="yellow")

                for server_name, reason in result.skipped_servers:
                    table.add_row(server_name, reason)

                console.print(table)

                console.print(
                    "\n[dim]Tip: Run 'devsync mcp configure <namespace>' to configure missing credentials[/dim]"
                )

        if not result.success:
            return 1

        return 0

    except Exception as e:
        logger.exception("Unexpected error during MCP sync")
        if json_output:
            import json

            console.print(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
            console.print(f"[red]Unexpected error:[/red] {e}")
        return 1
