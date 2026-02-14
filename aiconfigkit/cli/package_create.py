"""CLI command for creating configuration packages."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from aiconfigkit.core.component_detector import ComponentDetector, DetectionResult
from aiconfigkit.core.package_creator import PackageCreationResult, PackageCreator, PackageMetadata, get_git_author
from aiconfigkit.utils.project import find_project_root

console = Console()


def create_package_command(
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Package name (lowercase, hyphens allowed)",
    ),
    version: str = typer.Option(
        "1.0.0",
        "--version",
        "-v",
        help="Package version (semantic versioning)",
    ),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        "-d",
        help="Package description",
    ),
    author: Optional[str] = typer.Option(
        None,
        "--author",
        "-a",
        help="Package author (defaults to git user.name)",
    ),
    license_: str = typer.Option(
        "MIT",
        "--license",
        "-l",
        help="Package license",
    ),
    output: str = typer.Option(
        ".",
        "--output",
        "-o",
        help="Output directory for package",
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project root directory (defaults to current directory)",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        help="Enable interactive mode for component selection",
    ),
    scrub_secrets: bool = typer.Option(
        True,
        "--scrub-secrets/--keep-secrets",
        help="Template secrets in MCP configs",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing package directory",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Minimal output",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
) -> None:
    """
    Create a shareable configuration package from project components.

    Scans the current project for AI coding assistant configurations
    (instructions, MCP servers, hooks, commands, resources) and creates
    a portable package that can be installed in other projects.

    Example:
        devsync package create --name my-package
        devsync package create --name dev-setup --no-interactive
        devsync package create --name my-pkg --output ~/packages
    """
    try:
        if project:
            project_root = Path(project).resolve()
            if not project_root.exists():
                console.print(f"[red]Error: Project directory not found: {project}[/red]")
                raise typer.Exit(1)
        else:
            project_root_maybe = find_project_root()
            if not project_root_maybe:
                console.print("[red]Error: Could not find project root. " "Use --project to specify explicitly.[/red]")
                raise typer.Exit(1)
            project_root = project_root_maybe

        output_dir = Path(output).resolve()
        if not output_dir.exists():
            console.print(f"[red]Error: Output directory not found: {output}[/red]")
            raise typer.Exit(1)

        if not quiet:
            console.print(f"[cyan]Scanning project: {project_root}[/cyan]")

        detector = ComponentDetector(project_root)
        detection_result = detector.detect_all()

        if detection_result.total_count == 0:
            console.print("[yellow]No packageable components found in this project.[/yellow]")
            console.print("\n[dim]Components are detected from:[/dim]")
            console.print("[dim]  - Instructions: .claude/rules/, .cursor/rules/, etc.[/dim]")
            console.print("[dim]  - MCP servers: .claude/settings.local.json[/dim]")
            console.print("[dim]  - Hooks: .claude/hooks/[/dim]")
            console.print("[dim]  - Commands: .claude/commands/[/dim]")
            console.print("[dim]  - Resources: .ai-config-kit/resources/[/dim]")
            raise typer.Exit(1)

        if not quiet:
            _display_detected_components(detection_result)

        if not name:
            if interactive:
                name = typer.prompt("Package name", default=project_root.name.lower().replace(" ", "-"))
            else:
                console.print("[red]Error: --name is required in non-interactive mode[/red]")
                raise typer.Exit(1)

        # At this point name is guaranteed to be a string (either from option or prompt)
        assert name is not None
        package_name: str = name.lower().replace(" ", "-")
        if not package_name.replace("-", "").replace("_", "").isalnum():
            console.print(
                f"[red]Error: Invalid package name '{package_name}'. "
                f"Use only lowercase letters, numbers, hyphens.[/red]"
            )
            raise typer.Exit(1)

        package_description: str
        if not description:
            if interactive:
                package_description = typer.prompt(
                    "Package description",
                    default=f"Configuration package for {project_root.name}",
                )
            else:
                package_description = f"Configuration package for {project_root.name}"
        else:
            package_description = description

        package_author: str
        if not author:
            git_author = get_git_author()
            if not git_author and interactive:
                package_author = typer.prompt("Author", default="Unknown")
            elif not git_author:
                package_author = "Unknown"
            else:
                package_author = git_author
        else:
            package_author = author

        package_dir = output_dir / f"package-{package_name}"
        if package_dir.exists():
            if force:
                if not quiet:
                    console.print(f"[yellow]Removing existing package directory: {package_dir}[/yellow]")
                import shutil

                shutil.rmtree(package_dir)
            else:
                console.print(f"[red]Error: Package directory already exists: {package_dir}[/red]")
                console.print("[dim]Use --force to overwrite[/dim]")
                raise typer.Exit(1)

        if interactive:
            console.print(f"\n[cyan]Creating package with {detection_result.total_count} components[/cyan]")
            if not typer.confirm("Proceed?", default=True):
                console.print("[yellow]Package creation cancelled.[/yellow]")
                raise typer.Exit(0)

        metadata = PackageMetadata(
            name=package_name,
            version=version,
            description=package_description,
            author=package_author,
            license=license_,
            namespace="local/local",
        )

        creator = PackageCreator(
            project_root=project_root,
            output_dir=output_dir,
            metadata=metadata,
            scrub_secrets=scrub_secrets,
        )

        result = creator.create(detection_result=detection_result)

        if json_output:
            output_data = {
                "success": result.success,
                "package_path": str(result.package_path) if result.package_path else None,
                "manifest_path": str(result.manifest_path) if result.manifest_path else None,
                "components_included": result.components_included,
                "secrets_templated": result.secrets_templated,
                "warnings": result.warnings,
                "error_message": result.error_message,
            }
            console.print(json.dumps(output_data, indent=2))
        else:
            _display_creation_result(result, quiet)

        if not result.success:
            raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Package creation failed: {e}[/red]")
        raise typer.Exit(1)


def _display_detected_components(detection_result: "DetectionResult") -> None:
    """Display summary of detected components."""
    console.print("\n[cyan]Detected components:[/cyan]")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Type", style="green")
    table.add_column("Count", justify="right", style="blue")
    table.add_column("Details", style="dim")

    if detection_result.instructions:
        names = ", ".join(i.name for i in detection_result.instructions[:3])
        if len(detection_result.instructions) > 3:
            names += f", +{len(detection_result.instructions) - 3} more"
        table.add_row("Instructions", str(len(detection_result.instructions)), names)

    if detection_result.mcp_servers:
        names = ", ".join(m.name for m in detection_result.mcp_servers[:3])
        if len(detection_result.mcp_servers) > 3:
            names += f", +{len(detection_result.mcp_servers) - 3} more"
        table.add_row("MCP Servers", str(len(detection_result.mcp_servers)), names)

    if detection_result.hooks:
        names = ", ".join(h.name for h in detection_result.hooks[:3])
        if len(detection_result.hooks) > 3:
            names += f", +{len(detection_result.hooks) - 3} more"
        table.add_row("Hooks", str(len(detection_result.hooks)), names)

    if detection_result.commands:
        names = ", ".join(c.name for c in detection_result.commands[:3])
        if len(detection_result.commands) > 3:
            names += f", +{len(detection_result.commands) - 3} more"
        table.add_row("Commands", str(len(detection_result.commands)), names)

    if detection_result.resources:
        names = ", ".join(r.name for r in detection_result.resources[:3])
        if len(detection_result.resources) > 3:
            names += f", +{len(detection_result.resources) - 3} more"
        table.add_row("Resources", str(len(detection_result.resources)), names)

    if detection_result.skills:
        names = ", ".join(s.name for s in detection_result.skills[:3])
        if len(detection_result.skills) > 3:
            names += f", +{len(detection_result.skills) - 3} more"
        table.add_row("Skills", str(len(detection_result.skills)), names)

    if detection_result.workflows:
        names = ", ".join(w.name for w in detection_result.workflows[:3])
        if len(detection_result.workflows) > 3:
            names += f", +{len(detection_result.workflows) - 3} more"
        table.add_row("Workflows", str(len(detection_result.workflows)), names)

    if detection_result.memory_files:
        names = ", ".join(m.name for m in detection_result.memory_files[:3])
        if len(detection_result.memory_files) > 3:
            names += f", +{len(detection_result.memory_files) - 3} more"
        table.add_row("Memory Files", str(len(detection_result.memory_files)), names)

    console.print(table)
    console.print(f"\n[dim]Total: {detection_result.total_count} component(s)[/dim]")


def _display_creation_result(result: PackageCreationResult, quiet: bool) -> None:
    """Display package creation result."""
    if result.success:
        console.print("\n[green]✓ Package created successfully![/green]")
        console.print(f"  Location: {result.package_path}")

        if not quiet:
            console.print(f"  Components: {result.components_included}")
            if result.secrets_templated > 0:
                console.print(f"  Secrets templated: {result.secrets_templated}")

            if result.warnings:
                console.print(f"\n[yellow]Warnings ({len(result.warnings)}):[/yellow]")
                for warning in result.warnings:
                    console.print(f"  - {warning}")

            console.print("\n[cyan]To install this package:[/cyan]")
            console.print(f"  devsync package install {result.package_path} --ide claude")

    else:
        console.print("\n[red]✗ Package creation failed[/red]")
        if result.error_message:
            console.print(f"  Error: {result.error_message}")
