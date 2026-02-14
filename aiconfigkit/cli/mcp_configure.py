"""CLI command for configuring MCP server credentials."""

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from aiconfigkit.core.mcp.credentials import CredentialManager
from aiconfigkit.core.mcp.manager import MCPManager
from aiconfigkit.core.models import InstallationScope

logger = logging.getLogger(__name__)
console = Console()


def mcp_configure_command(
    server_ref: str = typer.Argument(..., help="Server reference in format 'namespace.server' or just 'namespace'"),
    scope: str = typer.Option("project", "--scope", help="Installation scope: project or global"),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Read credentials from environment"),
    show_current: bool = typer.Option(False, "--show-current", help="Show current credential values (masked)"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
) -> int:
    """
    Configure credentials for MCP servers.

    This command helps you securely configure required environment variables for
    MCP servers. Credentials are stored in .instructionkit/.env (gitignored).

    Examples:

        # Configure specific server interactively
        devsync mcp configure backend.github

        # Configure all servers in a namespace
        devsync mcp configure backend

        # Configure with non-interactive mode (read from env)
        export GITHUB_TOKEN=ghp_xxxxx
        devsync mcp configure backend.github --non-interactive

        # Show current credentials (masked)
        devsync mcp configure backend.github --show-current

        # Configure globally (available in all projects)
        devsync mcp configure backend.github --scope global
    """
    try:
        # Parse scope
        try:
            install_scope = InstallationScope(scope)
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid scope '{scope}'. Must be 'project' or 'global'")
            return 1

        # Parse server reference
        if "." in server_ref:
            namespace, server_name = server_ref.rsplit(".", 1)
        else:
            namespace = server_ref
            server_name = None

        # Get library root and managers
        library_root = _get_library_root()
        mcp_manager = MCPManager(library_root)
        cred_manager = CredentialManager()

        # Load template
        template = mcp_manager.load_template(namespace, scope=install_scope)

        if not template:
            console.print(f"[red]Error:[/red] Template '{namespace}' not found in {install_scope.value} scope")
            console.print(f"\nInstall it first: [cyan]devsync mcp install <source> --as {namespace}[/cyan]")
            return 1

        # Get servers to configure
        if server_name:
            # Configure specific server
            server = template.get_server_by_name(server_name)
            if not server:
                console.print(f"[red]Error:[/red] Server '{server_name}' not found in template '{namespace}'")
                console.print(f"\nAvailable servers: {', '.join(s.name for s in template.servers)}")
                return 1
            servers = [server]
        else:
            # Configure all servers in namespace
            servers = template.servers

        if not servers:
            console.print(f"[yellow]Warning:[/yellow] No MCP servers found in template '{namespace}'")
            return 0

        # Show current credentials if requested
        if show_current:
            return _show_current_credentials(servers, cred_manager, install_scope, json_output)

        # Configure each server
        configured_count = 0
        skipped_count = 0

        for server in servers:
            required_vars = server.get_required_env_vars()

            if not required_vars:
                console.print(f"[dim]Server '{server.name}' requires no credentials[/dim]")
                skipped_count += 1
                continue

            try:
                cred_manager.configure_server(
                    server,
                    scope=install_scope,
                    non_interactive=non_interactive,
                )
                configured_count += 1

            except ValueError as e:
                console.print(f"[red]Error configuring '{server.name}':[/red] {e}")
                return 1

        # Output results
        if json_output:
            import json

            result = {
                "success": True,
                "namespace": namespace,
                "configured": configured_count,
                "skipped": skipped_count,
                "total": len(servers),
                "scope": install_scope.value,
            }
            console.print(json.dumps(result, indent=2))
        else:
            console.print("\n[green]✓[/green] Credential configuration complete!")
            console.print(f"  Configured: {configured_count} server(s)")
            if skipped_count > 0:
                console.print(f"  Skipped: {skipped_count} server(s) (no credentials needed)")

            # Show env file location
            if install_scope == InstallationScope.GLOBAL:
                env_path = Path.home() / ".instructionkit" / "global" / ".env"
            else:
                env_path = Path.cwd() / ".instructionkit" / ".env"

            console.print(f"\n[dim]Credentials saved to: {env_path}[/dim]")
            console.print("[dim](This file is automatically gitignored)[/dim]")

            # Show next steps
            console.print("\n[bold]Next step:[/bold]")
            console.print("  Sync to AI tools: [cyan]devsync mcp sync --tool all[/cyan]")

        return 0

    except Exception as e:
        logger.exception("Unexpected error during credential configuration")
        if json_output:
            import json

            console.print(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
            console.print(f"[red]Unexpected error:[/red] {e}")
        return 1


def _show_current_credentials(
    servers: list,
    cred_manager: CredentialManager,
    scope: InstallationScope,
    json_output: bool,
) -> int:
    """Show current credential values for servers."""
    if json_output:
        import json
        from typing import Any

        result: dict[str, Any] = {
            "scope": scope.value,
            "servers": [],
        }

        for server in servers:
            credentials = cred_manager.show_current_credentials(server, scope)
            is_valid, missing = cred_manager.validate_credentials(server, scope)

            result["servers"].append(
                {
                    "name": server.get_fully_qualified_name(),
                    "credentials": credentials,
                    "is_configured": is_valid,
                    "missing": missing,
                }
            )

        console.print(json.dumps(result, indent=2))
    else:
        table = Table(title=f"Current Credentials ({scope.value} scope)")
        table.add_column("Server", style="cyan")
        table.add_column("Variable", style="yellow")
        table.add_column("Value", style="dim")
        table.add_column("Status", style="green")

        for server in servers:
            credentials = cred_manager.show_current_credentials(server, scope)
            is_valid, missing = cred_manager.validate_credentials(server, scope)

            for i, (var_name, masked_value) in enumerate(credentials.items()):
                server_name = server.get_fully_qualified_name() if i == 0 else ""
                status = "✓" if var_name not in missing else "⚠ Missing"
                status_style = "green" if var_name not in missing else "yellow"

                table.add_row(
                    server_name,
                    var_name,
                    masked_value,
                    f"[{status_style}]{status}[/{status_style}]",
                )

        console.print(table)

    return 0


def _get_library_root() -> Path:
    """
    Get the library root directory.

    Returns:
        Path to library root (~/.instructionkit/library/)
    """
    return Path.home() / ".instructionkit" / "library"
