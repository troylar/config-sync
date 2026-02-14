"""Template uninstall command."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm

from aiconfigkit.storage.template_library import TemplateLibraryManager
from aiconfigkit.storage.template_tracker import TemplateInstallationTracker
from aiconfigkit.utils.project import find_project_root

console = Console()


def uninstall_command(
    repo_name: str = typer.Argument(..., help="Repository name or namespace to uninstall"),
    scope: str = typer.Option(
        "project",
        "--scope",
        "-s",
        help="Which installation to remove (project or global)",
    ),
    template: Optional[str] = typer.Option(
        None,
        "--template",
        "-t",
        help="Uninstall specific template (not entire repository)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
    keep_files: bool = typer.Option(
        False,
        "--keep-files",
        "-k",
        help="Remove from tracking but keep files on disk",
    ),
) -> None:
    """
    Remove installed templates.

    Example:
        devsync template uninstall acme-templates
        devsync template uninstall acme-templates --force
        devsync template uninstall acme-templates --template test-command
        devsync template uninstall acme-templates --keep-files
    """
    try:
        # Validate scope
        if scope not in ["project", "global"]:
            console.print(f"[red]Error: Invalid scope '{scope}'. Must be 'project' or 'global'[/red]")
            raise typer.Exit(1)

        # Get tracker
        if scope == "project":
            try:
                project_root = find_project_root()
                if not project_root:
                    console.print("[red]Error: Not in a project directory[/red]")
                    raise typer.Exit(1)
            except Exception:
                console.print("[red]Error: Not in a project directory[/red]")
                raise typer.Exit(1)
            tracker = TemplateInstallationTracker.for_project(project_root)
        else:
            tracker = TemplateInstallationTracker.for_global()

        # Load records
        all_records = tracker.load_installation_records()

        # Filter by repository name or namespace
        repo_records = [r for r in all_records if r.source_repo == repo_name or r.namespace == repo_name]

        if not repo_records:
            console.print(f"[red]Error: Repository '{repo_name}' not found in {scope} installations[/red]")
            console.print("\nInstalled repositories:")
            repos = set(f"{r.source_repo} ({r.namespace})" for r in all_records)
            for repo in sorted(repos):
                console.print(f"  - {repo}")
            raise typer.Exit(1)

        # Filter by specific template if requested
        if template:
            repo_records = [r for r in repo_records if r.template_name == template]
            if not repo_records:
                console.print(f"[red]Error: Template '{template}' not found in repository '{repo_name}'[/red]")
                raise typer.Exit(1)

        # Show what will be removed
        console.print("\n[bold]The following templates will be removed:[/bold]")
        for record in repo_records:
            console.print(f"  - {record.namespace}.{record.template_name} ({record.ide_type.value})")

        # Confirm unless --force
        if not force:
            confirm_msg = f"Remove {len(repo_records)} template(s) from {repo_name}?"
            if not Confirm.ask(confirm_msg, default=False):
                console.print("[yellow]Uninstall cancelled[/yellow]")
                raise typer.Exit(0)

        # Remove templates
        removed_count = 0
        for record in repo_records:
            console.print(f"Removing [cyan]{record.namespace}.{record.template_name}[/cyan]...", end=" ")

            # Delete file if not keeping
            if not keep_files:
                try:
                    file_path = Path(record.installed_path)
                    if file_path.exists():
                        file_path.unlink()
                except Exception as e:
                    console.print(f"[yellow]⚠️  (failed to delete file: {e})[/yellow]")
                    continue

            # Remove from tracking
            tracker.remove_installation(record.id)
            removed_count += 1
            console.print("[green]✓[/green]")

        # Clean up library if removing entire repository and no templates remain
        if not template:
            remaining = tracker.get_installations_by_namespace(repo_records[0].namespace)
            if not remaining:
                try:
                    library_manager = TemplateLibraryManager()
                    library_manager.remove_repository(repo_records[0].namespace)
                    console.print(f"\n[dim]Removed repository from library: {repo_records[0].namespace}[/dim]")
                except Exception:
                    pass  # Library removal is optional

        console.print(f"\n[green]✓ Uninstalled {removed_count} template(s)[/green]")

    except typer.Exit:
        raise
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)
