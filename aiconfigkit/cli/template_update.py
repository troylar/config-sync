"""Template update command."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from aiconfigkit.core.checksum import sha256_string
from aiconfigkit.core.conflict_resolution import (
    apply_resolution,
    detect_conflict,
    prompt_conflict_resolution_template,
)
from aiconfigkit.core.models import ConflictResolution, ConflictType
from aiconfigkit.storage.template_library import TemplateLibraryManager
from aiconfigkit.storage.template_tracker import TemplateInstallationTracker
from aiconfigkit.utils.git_helpers import TemplateNetworkError, update_template_repo
from aiconfigkit.utils.project import find_project_root

console = Console()


def update_command(
    repo_name: Optional[str] = typer.Argument(None, help="Repository name to update (omit for --all)"),
    all_repos: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Update all installed template repositories",
    ),
    scope: str = typer.Option(
        "project",
        "--scope",
        "-s",
        help="Which installations to update (project, global, both)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite local changes without prompting",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what would be updated without making changes",
    ),
) -> None:
    """
    Update installed templates to latest version.

    Example:
        devsync template update acme-templates
        devsync template update --all
        devsync template update acme-templates --dry-run
        devsync template update --all --force
    """
    try:
        # Validate arguments
        if not repo_name and not all_repos:
            console.print("[red]Error: Must specify repo-name or --all[/red]")
            console.print("Usage: devsync template update <repo-name> or devsync template update --all")
            raise typer.Exit(2)

        if scope not in ["project", "global", "both"]:
            console.print(f"[red]Error: Invalid scope '{scope}'. Must be 'project', 'global', or 'both'[/red]")
            raise typer.Exit(1)

        # Determine which trackers to use
        trackers: list[tuple[str, TemplateInstallationTracker]] = []
        if scope in ["project", "both"]:
            try:
                project_root = find_project_root()
                if project_root:
                    trackers.append(("project", TemplateInstallationTracker.for_project(project_root)))
            except Exception:
                if scope == "project":
                    console.print("[red]Error: Not in a project directory[/red]")
                    raise typer.Exit(1)

        if scope in ["global", "both"]:
            trackers.append(("global", TemplateInstallationTracker.for_global()))

        # Collect repositories to update
        repos_to_update: set[str] = set()
        for scope_name, tracker in trackers:
            records = tracker.load_installation_records()
            if all_repos:
                repos_to_update.update(r.namespace for r in records)
            elif repo_name:
                matching = [r for r in records if r.source_repo == repo_name or r.namespace == repo_name]
                if matching:
                    repos_to_update.add(matching[0].namespace)

        if not repos_to_update:
            if repo_name:
                console.print(f"[yellow]Repository '{repo_name}' not found in {scope} installations[/yellow]")
            else:
                console.print(f"[yellow]No repositories found in {scope} installations[/yellow]")
            raise typer.Exit(0)

        # Update each repository
        library_manager = TemplateLibraryManager()
        total_updated = 0

        for namespace in sorted(repos_to_update):
            console.print(f"\n[bold]Checking {namespace} for updates...[/bold]")

            # Get repository path
            try:
                repo_path, old_manifest = library_manager.get_template_repository(namespace)
            except FileNotFoundError:
                console.print("[yellow]⚠️  Repository not found in library, skipping[/yellow]")
                continue

            # Check for updates
            try:
                with Progress(
                    SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
                ) as progress:
                    task = progress.add_task("Fetching updates...", total=None)
                    has_updates = update_template_repo(repo_path)
                    progress.update(task, completed=True)

                if not has_updates:
                    console.print("[green]✓ Already up-to-date[/green]")
                    continue

            except TemplateNetworkError as e:
                console.print(f"[red]❌ Failed to check for updates: {e}[/red]")
                continue

            # Load new manifest
            from aiconfigkit.core.template_manifest import load_manifest

            new_manifest = load_manifest(repo_path / "templatekit.yaml")

            console.print(f"[green]Found updates[/green] (v{old_manifest.version} → v{new_manifest.version})\n")

            if dry_run:
                console.print("[dim]Dry run - no changes will be made[/dim]")
                # Show what would be updated
                for template in new_manifest.templates:
                    console.print(f"  Would update: {namespace}.{template.name}")
                continue

            # Update templates
            updated_count = 0
            skipped_count = 0

            for scope_name, tracker in trackers:
                records = tracker.get_installations_by_namespace(namespace)

                for record in records:
                    # Find matching template in new manifest
                    matching_template = next(
                        (t for t in new_manifest.templates if t.name == record.template_name), None
                    )
                    if not matching_template:
                        console.print(
                            f"[yellow]⚠️  Template {record.template_name} no longer in repository, skipping[/yellow]"
                        )
                        continue

                    # Read new template content
                    template_file = matching_template.files[0]
                    source_file = repo_path / template_file.path
                    new_content = source_file.read_text(encoding="utf-8")

                    # Check for conflicts
                    installed_path = Path(record.installed_path)
                    conflict_type = detect_conflict(installed_path, new_content, record)

                    if conflict_type != ConflictType.NONE and not force:
                        # Prompt for resolution
                        resolution = prompt_conflict_resolution_template(
                            f"{namespace}.{record.template_name}", conflict_type
                        )

                        if resolution == ConflictResolution.SKIP:
                            console.print(f"Skipping [cyan]{namespace}.{record.template_name}[/cyan]")
                            skipped_count += 1
                            continue

                        # Apply resolution
                        apply_resolution(installed_path, new_content, resolution)
                    else:
                        # Safe to update or force mode
                        console.print(f"Updating [cyan]{namespace}.{record.template_name}[/cyan]...", end=" ")
                        installed_path.write_text(new_content, encoding="utf-8")

                    # Update installation record
                    record.source_version = new_manifest.version
                    record.checksum = sha256_string(new_content)
                    record.installed_at = datetime.now()
                    tracker.update_installation(record.id, record)

                    console.print("[green]✓[/green]")
                    updated_count += 1

            if updated_count > 0:
                console.print(f"\n[green]✓ Updated {updated_count} template(s)[/green]")
                total_updated += updated_count
            if skipped_count > 0:
                console.print(f"[yellow]Skipped {skipped_count} template(s) due to conflicts[/yellow]")

        if dry_run:
            console.print("\n[dim]Dry run complete - no changes were made[/dim]")
        elif total_updated > 0:
            console.print(f"\n[green]✓ Total updated: {total_updated} template(s)[/green]")
        else:
            console.print("\n[yellow]No templates were updated[/yellow]")

    except typer.Exit:
        raise
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)
