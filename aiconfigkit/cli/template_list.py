"""Template list command."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from aiconfigkit.storage.template_tracker import TemplateInstallationTracker
from aiconfigkit.utils.project import find_project_root

console = Console()


def list_command(
    scope: str = typer.Option(
        "all",
        "--scope",
        "-s",
        help="Which installations to list (project, global, all)",
    ),
    repo: Optional[str] = typer.Option(
        None,
        "--repo",
        "-r",
        help="Filter by repository name",
    ),
    format_type: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (table, json, simple)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed information",
    ),
) -> None:
    """
    List installed templates.

    Example:
        devsync template list
        devsync template list --scope project
        devsync template list --repo acme-templates
        devsync template list --format json
    """
    try:
        # Validate scope
        if scope not in ["project", "global", "all"]:
            console.print(f"[red]Error: Invalid scope '{scope}'. Must be 'project', 'global', or 'all'[/red]")
            raise typer.Exit(1)

        # Validate format
        if format_type not in ["table", "json", "simple"]:
            console.print(f"[red]Error: Invalid format '{format_type}'. Must be 'table', 'json', or 'simple'[/red]")
            raise typer.Exit(1)

        # Load installation records
        project_records: list = []
        global_records: list = []

        if scope in ["project", "all"]:
            try:
                project_root = find_project_root()
                if project_root:
                    tracker = TemplateInstallationTracker.for_project(project_root)
                    project_records = tracker.load_installation_records()
            except Exception:
                if scope == "project":
                    console.print("[yellow]⚠️  Not in a project directory[/yellow]")
                    raise typer.Exit(1)

        if scope in ["global", "all"]:
            tracker = TemplateInstallationTracker.for_global()
            global_records = tracker.load_installation_records()

        # Combine records
        all_records = []
        if project_records:
            all_records.extend(project_records)
        if global_records:
            all_records.extend(global_records)

        # Filter by repository if specified
        if repo:
            all_records = [r for r in all_records if r.source_repo == repo or r.namespace == repo]

        # Check if empty
        if not all_records:
            if repo:
                console.print(f"[yellow]No templates installed from repository '{repo}'[/yellow]")
            else:
                console.print("[yellow]No templates installed.[/yellow]")
                console.print("\nTo install templates:")
                console.print("  devsync template install <repo-url>")
            raise typer.Exit(0)

        # Output based on format
        if format_type == "json":

            output = {
                "installations": [r.to_dict() for r in all_records],
                "count": len(all_records),
                "repositories": len(set(r.source_repo for r in all_records)),
            }
            console.print_json(data=output)

        elif format_type == "simple":
            for record in all_records:
                console.print(f"{record.namespace}.{record.template_name}")

        else:  # table format
            # Group by repository
            repos: dict = {}
            for record in all_records:
                repo_key = record.source_repo
                if repo_key not in repos:
                    repos[repo_key] = {
                        "version": record.source_version,
                        "namespace": record.namespace,
                        "records": [],
                    }
                repos[repo_key]["records"].append(record)

            # Display each repository
            for repo_name, repo_data in repos.items():
                console.print(f"\n[bold]Repository: {repo_name}[/bold] (v{repo_data['version']})")
                console.print(f"[dim]Namespace: {repo_data['namespace']}[/dim]\n")

                table = Table()
                table.add_column("Template", style="cyan")
                table.add_column("IDE", style="green")
                table.add_column("Scope", style="yellow")
                table.add_column("Installed", style="magenta")

                if verbose:
                    table.add_column("Path", style="dim")
                    table.add_column("Checksum", style="dim")

                for record in repo_data["records"]:
                    installed_date = record.installed_at.strftime("%Y-%m-%d")
                    row = [
                        record.template_name,
                        record.ide_type.value,
                        record.scope.value,
                        installed_date,
                    ]

                    if verbose:
                        row.append(str(record.installed_path))
                        row.append(record.checksum[:8] + "...")

                    table.add_row(*row)

                console.print(table)

            # Summary
            total_repos = len(repos)
            total_templates = len(all_records)
            console.print(f"\n[bold]Total:[/bold] {total_templates} templates from {total_repos} repository(ies)")

    except typer.Exit:
        raise
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)
