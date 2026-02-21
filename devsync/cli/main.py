"""Main CLI application entry point — v2 command surface."""

from typing import Optional

import typer

from devsync.cli.tools import show_tools

app = typer.Typer(
    name="devsync",
    help="AI-powered config distribution for AI coding tools.",
    add_completion=False,
)


@app.command()
def setup() -> None:
    """Configure LLM provider for AI-powered features.

    Interactive setup to select provider (Anthropic, OpenAI, OpenRouter),
    validate API key, and save preferences.

    Example:
      devsync setup
    """
    from devsync.cli.setup import setup_command

    exit_code = setup_command()
    raise typer.Exit(code=exit_code)


@app.command()
def tools() -> None:
    """Show detected AI coding tools.

    Display which AI coding tools are installed on your system
    and where their configuration directories are located.
    """
    exit_code = show_tools()
    raise typer.Exit(code=exit_code)


@app.command()
def extract(
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for the package (default: ./devsync-package/)",
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Package name (default: project directory name)",
    ),
    no_ai: bool = typer.Option(
        False,
        "--no-ai",
        help="Force file-copy mode (no LLM calls)",
    ),
    project_dir: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project directory to extract from (default: current directory)",
    ),
    upgrade: Optional[str] = typer.Option(
        None,
        "--upgrade",
        help="Convert a v1 package to v2 format",
    ),
) -> None:
    """Extract practices from a project into a shareable package.

    Reads your project's AI tool configs (rules, MCP servers, hooks, commands)
    and produces a devsync-package.yaml with abstract practice declarations.

    Examples:
      # AI-powered extraction
      devsync extract

      # File-copy mode (no AI)
      devsync extract --no-ai

      # Custom output and name
      devsync extract --output ./my-package --name team-standards

      # Upgrade v1 package to v2
      devsync extract --upgrade ./old-package
    """
    from devsync.cli.extract import extract_command

    exit_code = extract_command(
        output=output,
        name=name,
        no_ai=no_ai,
        project_dir=project_dir,
        upgrade=upgrade,
    )
    raise typer.Exit(code=exit_code)


@app.command()
def install(
    source: str = typer.Argument(
        ...,
        help="Package source: Git URL, local path, or package directory",
    ),
    tool: Optional[list[str]] = typer.Option(
        None,
        "--tool",
        "-t",
        help="Target AI tool(s). Auto-detects if not specified.",
    ),
    no_ai: bool = typer.Option(
        False,
        "--no-ai",
        help="Disable AI-powered adaptation",
    ),
    conflict: str = typer.Option(
        "prompt",
        "--conflict",
        "-c",
        help="Conflict strategy: prompt, skip, overwrite, rename",
    ),
    project_dir: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Target project directory (default: current directory)",
    ),
) -> None:
    """Install a package into the current project.

    Accepts Git URLs, local paths, or extracted package directories.
    AI-powered adaptation merges incoming practices with existing rules.

    Examples:
      # Install from local package
      devsync install ./team-standards

      # Install from Git
      devsync install https://github.com/company/standards

      # Install to specific tools
      devsync install ./package --tool claude --tool cursor

      # File-copy mode (no AI)
      devsync install ./package --no-ai

      # Skip conflicts
      devsync install ./package --conflict skip
    """
    from devsync.cli.install_v2 import install_v2_command

    exit_code = install_v2_command(
        source=source,
        tool=tool,
        no_ai=no_ai,
        conflict=conflict,
        project_dir=project_dir,
    )
    raise typer.Exit(code=exit_code)


@app.command(name="list")
def list_cmd(
    tool: Optional[str] = typer.Option(
        None,
        "--tool",
        "-t",
        help="Filter by AI tool name",
    ),
    json: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON",
    ),
) -> None:
    """List installed packages and instructions.

    Shows all packages installed in the current project with component breakdown.

    Examples:
      devsync list
      devsync list --tool claude
      devsync list --json
    """
    from devsync.cli.list_v2 import list_v2_command

    exit_code = list_v2_command(tool=tool, json=json)
    raise typer.Exit(code=exit_code)


@app.command()
def uninstall(
    name: str = typer.Argument(..., help="Package name to uninstall"),
    tool: Optional[str] = typer.Option(
        None,
        "--tool",
        "-t",
        help="AI tool to uninstall from",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Uninstall a package from the current project.

    Examples:
      devsync uninstall team-standards
      devsync uninstall team-standards --tool cursor
      devsync uninstall team-standards --force
    """
    from devsync.cli.uninstall import uninstall_instruction

    exit_code = uninstall_instruction(name=name, tool=tool, force=force)
    raise typer.Exit(code=exit_code)


@app.command()
def version() -> None:
    """Show DevSync version."""
    from importlib.metadata import version as get_version

    try:
        ver = get_version("devsync")
    except Exception:
        ver = "unknown"

    typer.echo(f"DevSync version {ver}")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """DevSync — AI-powered config distribution for AI coding tools.

    Extract practices from your project, share them as packages,
    and install them into any supported AI coding tool.
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


if __name__ == "__main__":
    app()
