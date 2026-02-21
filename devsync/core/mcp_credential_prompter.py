"""MCP credential prompting for package installation."""

import logging
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt

from devsync.core.practice import CredentialSpec, MCPDeclaration

logger = logging.getLogger(__name__)
console = Console()


def prompt_mcp_credentials(
    mcp_servers: list[MCPDeclaration],
    env_path: Optional[Path] = None,
) -> dict[str, dict[str, str]]:
    """Prompt the user for MCP server credentials.

    Args:
        mcp_servers: MCP server declarations with credential specs.
        env_path: Path to write .env file. If None, returns values without writing.

    Returns:
        Dict mapping server name → {env_var_name: value}.
    """
    all_credentials: dict[str, dict[str, str]] = {}

    for server in mcp_servers:
        if not server.credentials:
            continue

        console.print(f"\n[bold]MCP Server: {server.name}[/bold]")
        console.print(f"  {server.description}")

        server_creds: dict[str, str] = {}
        for cred in server.credentials:
            value = _prompt_single_credential(cred)
            if value:
                server_creds[cred.name] = value

        if server_creds:
            all_credentials[server.name] = server_creds

    if env_path and all_credentials:
        _write_env_file(env_path, all_credentials)

    return all_credentials


def _prompt_single_credential(cred: CredentialSpec) -> str:
    """Prompt for a single credential value.

    Args:
        cred: Credential specification.

    Returns:
        The credential value entered by the user (empty string if skipped).
    """
    required_label = "[red](required)[/red]" if cred.required else "[dim](optional)[/dim]"
    console.print(f"\n  {required_label} {cred.name}")
    console.print(f"  [dim]{cred.description}[/dim]")

    default = cred.default or ""
    if cred.required:
        while True:
            value = Prompt.ask(f"  Enter {cred.name}", default=default if default else None, password=True)
            if value and value.strip():
                return value.strip()
            console.print("  [red]This credential is required. Please enter a value.[/red]")
    else:
        value = Prompt.ask(f"  Enter {cred.name}", default=default, password=True)
        return value or ""


def _write_env_file(env_path: Path, credentials: dict[str, dict[str, str]]) -> None:
    """Write credentials to a .env file.

    Args:
        env_path: Path to the .env file.
        credentials: Server name → {env_var: value} mapping.
    """
    env_path.parent.mkdir(parents=True, exist_ok=True)

    from devsync.utils.dotenv import ensure_env_gitignored, set_env_variable

    ensure_env_gitignored(env_path)

    for server_name, creds in credentials.items():
        for var_name, value in creds.items():
            if value:
                set_env_variable(env_path, var_name, value)
                logger.info("Wrote %s to %s", var_name, env_path)

    console.print(f"\n[green]Credentials saved to {env_path}[/green]")


def build_mcp_config(
    server: MCPDeclaration,
    credentials: dict[str, str],
) -> dict:
    """Build a tool-native MCP server config dict.

    Args:
        server: MCP server declaration.
        credentials: Resolved credential values {env_var: value}.

    Returns:
        Dict suitable for writing to tool-specific MCP config.
    """
    config: dict = {
        "command": server.command,
        "args": server.args,
    }

    env: dict[str, str] = {}
    env.update(server.env_vars)

    for cred in server.credentials:
        value = credentials.get(cred.name, "")
        if value:
            env[cred.name] = value

    if env:
        config["env"] = env

    return config
