"""CLI command for installing MCP templates."""

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from aiconfigkit.core.mcp.manager import MCPManager
from aiconfigkit.core.models import InstallationScope

logger = logging.getLogger(__name__)
console = Console()


def mcp_install_command(
    source: str = typer.Argument(..., help="Source URL or local path to MCP template repository"),
    namespace: str = typer.Option(..., "--as", help="Namespace for this template (unique identifier)"),
    scope: str = typer.Option("project", "--scope", help="Installation scope: project or global"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing template if it exists"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
) -> int:
    """
    Install MCP server configurations from a template repository.

    This downloads and caches MCP server definitions from a Git repository or local
    directory into your local library. After installation, use 'devsync mcp configure'
    to set up credentials and 'devsync mcp sync' to apply to AI tools.

    Examples:

        # Install from GitHub repository
        devsync mcp install https://github.com/company/backend-tools --as backend

        # Install from local directory
        devsync mcp install ./my-mcp-configs --as local-tools

        # Install globally (available in all projects)
        devsync mcp install https://github.com/me/personal-tools --as personal --scope global

        # Force overwrite existing template
        devsync mcp install https://github.com/company/backend-tools --as backend --force
    """
    try:
        # Parse scope
        try:
            install_scope = InstallationScope(scope)
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid scope '{scope}'. Must be 'project' or 'global'")
            return 1

        # Get library root
        library_root = _get_library_root()

        # Create MCP manager
        manager = MCPManager(library_root)

        # Install template with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Installing MCP template '{namespace}'...", total=None)

            try:
                template = manager.install_template(
                    source=source,
                    namespace=namespace,
                    scope=install_scope,
                    force=force,
                )
            finally:
                progress.remove_task(task)

        # Output results
        if json_output:
            import json

            result = {
                "success": True,
                "namespace": template.namespace,
                "version": template.version,
                "servers": len(template.servers),
                "sets": len(template.sets),
                "scope": install_scope.value,
            }
            console.print(json.dumps(result, indent=2))
        else:
            console.print(f"[green]✓[/green] Installed MCP template: [bold]{namespace}[/bold]")
            console.print(f"  Version: {template.version}")
            console.print(f"  Description: {template.description}")
            console.print(f"  Servers: {len(template.servers)}")
            console.print(f"  Sets: {len(template.sets)}")
            console.print(f"  Scope: {install_scope.value}")

            # Show next steps
            console.print("\n[bold]Next steps:[/bold]")

            # Check which servers need configuration
            servers_needing_config = [s for s in template.servers if s.get_required_env_vars()]

            if servers_needing_config:
                console.print("  1. Configure credentials for servers:")
                for server in servers_needing_config[:3]:  # Show first 3
                    console.print(f"     [cyan]devsync mcp configure {namespace}.{server.name}[/cyan]")
                if len(servers_needing_config) > 3:
                    console.print(f"     ... and {len(servers_needing_config) - 3} more")
            else:
                console.print("  1. [dim]No credentials needed for servers[/dim]")

            console.print("  2. Sync to AI tools: [cyan]devsync mcp sync --tool all[/cyan]")

            if template.sets:
                set_name = template.sets[0].name
                console.print(f"  3. Or activate a set: [cyan]devsync mcp activate {namespace}.{set_name}[/cyan]")

        return 0

    except ValueError as e:
        if json_output:
            import json

            console.print(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error:[/red] {e}")
        return 1

    except FileNotFoundError as e:
        if json_output:
            import json

            console.print(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error:[/red] {e}")
        return 1

    except RuntimeError as e:
        if json_output:
            import json

            console.print(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error:[/red] {e}")
        return 1

    except Exception as e:
        logger.exception("Unexpected error during MCP template installation")
        if json_output:
            import json

            console.print(json.dumps({"success": False, "error": f"Unexpected error: {e}"}, indent=2))
        else:
            console.print(f"[red]Unexpected error:[/red] {e}")
        return 1


def _get_library_root() -> Path:
    """
    Get the library root directory.

    Returns:
        Path to library root (~/.instructionkit/library/)
    """
    return Path.home() / ".instructionkit" / "library"
