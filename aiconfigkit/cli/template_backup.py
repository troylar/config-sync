"""Template backup management commands."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from aiconfigkit.utils.backup import cleanup_old_backups, list_backups, restore_backup
from aiconfigkit.utils.project import find_project_root

console = Console()


def backup_list_command(
    scope: str = typer.Option(
        "project",
        "--scope",
        "-s",
        help="Which backups to list (project, global)",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        help="Maximum number of backups to show",
    ),
) -> None:
    """
    List available template backups.

    Backups are created automatically before overwriting templates
    during update operations.

    Example:
        devsync template backup list
        devsync template backup list --scope global
        devsync template backup list --limit 20
    """
    try:
        # Determine backup directory
        if scope == "project":
            project_root = find_project_root()
            if not project_root:
                console.print("[red]Error: Not in a project directory[/red]")
                raise typer.Exit(1)
            backup_dir = project_root / ".instructionkit" / "backups"
        elif scope == "global":
            backup_dir = Path.home() / ".instructionkit" / "backups"
        else:
            console.print(f"[red]Error: Invalid scope '{scope}'. Must be 'project' or 'global'[/red]")
            raise typer.Exit(1)

        # Get backups
        backups = list_backups(backup_dir)

        if not backups:
            console.print(f"[yellow]No backups found in {scope} scope[/yellow]")
            console.print(f"[dim]Backup directory: {backup_dir}[/dim]")
            return

        # Limit results
        backups = backups[:limit]

        # Display table
        table = Table(title=f"\n{scope.capitalize()} Template Backups")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Backup Directory", style="green")
        table.add_column("Files", justify="right")

        for timestamp, backup_path in backups:
            file_count = len(list(backup_path.iterdir()))
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            table.add_row(timestamp_str, str(backup_path.relative_to(backup_dir.parent)), str(file_count))

        console.print(table)
        console.print(f"\n[dim]Showing {len(backups)} most recent backup(s)[/dim]")

        if len(backups) >= limit:
            console.print("[dim]Use --limit to see more backups[/dim]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)


def backup_cleanup_command(
    days: int = typer.Option(
        30,
        "--days",
        "-d",
        help="Remove backups older than this many days",
    ),
    scope: str = typer.Option(
        "project",
        "--scope",
        "-s",
        help="Which backups to clean up (project, global)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    Remove old template backups to free up space.

    Example:
        devsync template backup cleanup --days 30
        devsync template backup cleanup --days 7 --force
        devsync template backup cleanup --scope global --days 90
    """
    try:
        # Determine backup directory
        if scope == "project":
            project_root = find_project_root()
            if not project_root:
                console.print("[red]Error: Not in a project directory[/red]")
                raise typer.Exit(1)
            backup_dir = project_root / ".instructionkit" / "backups"
        elif scope == "global":
            backup_dir = Path.home() / ".instructionkit" / "backups"
        else:
            console.print(f"[red]Error: Invalid scope '{scope}'. Must be 'project' or 'global'[/red]")
            raise typer.Exit(1)

        # Get backups that will be removed
        backups = list_backups(backup_dir)
        from datetime import datetime

        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        old_backups = [b for timestamp, b in backups if timestamp.timestamp() < cutoff_date]

        if not old_backups:
            console.print(f"[green]No backups older than {days} days found[/green]")
            return

        # Confirm deletion
        if not force:
            console.print(f"[yellow]Found {len(old_backups)} backup(s) older than {days} days:[/yellow]")
            for backup_path in old_backups[:5]:  # Show first 5
                console.print(f"  - {backup_path.name}")
            if len(old_backups) > 5:
                console.print(f"  ... and {len(old_backups) - 5} more")

            confirm = typer.confirm(f"\nRemove {len(old_backups)} old backup(s)?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        # Clean up
        removed = cleanup_old_backups(days, backup_dir)
        console.print(f"[green]✓ Removed {removed} old backup(s)[/green]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)


def backup_restore_command(
    backup_timestamp: str = typer.Argument(..., help="Timestamp of backup to restore (YYYYMMDD_HHMMSS)"),
    file_name: str = typer.Argument(..., help="Name of file to restore"),
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Target path (default: original location)",
    ),
    scope: str = typer.Option(
        "project",
        "--scope",
        "-s",
        help="Where backup is located (project, global)",
    ),
) -> None:
    """
    Restore a file from a backup.

    Example:
        # List backups first
        devsync template backup list

        # Restore specific file
        devsync template backup restore 20251109_143052 company.test.md

        # Restore to different location
        devsync template backup restore 20251109_143052 company.test.md --target .claude/rules/company.test-restored.md
    """
    try:
        # Determine backup directory
        if scope == "project":
            project_root = find_project_root()
            if not project_root:
                console.print("[red]Error: Not in a project directory[/red]")
                raise typer.Exit(1)
            backup_dir = project_root / ".instructionkit" / "backups"
        elif scope == "global":
            backup_dir = Path.home() / ".instructionkit" / "backups"
        else:
            console.print(f"[red]Error: Invalid scope '{scope}'. Must be 'project' or 'global'[/red]")
            raise typer.Exit(1)

        # Find backup
        backup_path = backup_dir / backup_timestamp / file_name
        if not backup_path.exists():
            console.print(f"[red]Error: Backup not found: {backup_path}[/red]")
            console.print("\n[yellow]Available backups:[/yellow]")
            # Show available backups for this timestamp
            timestamp_dir = backup_dir / backup_timestamp
            if timestamp_dir.exists():
                for f in timestamp_dir.iterdir():
                    console.print(f"  - {f.name}")
            else:
                console.print(f"[red]Backup directory not found: {timestamp_dir}[/red]")
                console.print("\nUse 'devsync template backup list' to see available backups")
            raise typer.Exit(1)

        # Determine target path
        if target:
            target_path = Path(target)
        else:
            # Try to restore to original location based on file name
            # Assume structure like .claude/rules/company.test.md
            parts = file_name.split(".")
            if len(parts) >= 3:
                # namespace.template-name.ext format
                # Default to .claude/rules as restore location
                target_path = Path(f".claude/rules/{file_name}")
            else:
                console.print("[yellow]Could not determine original location[/yellow]")
                console.print("Please specify --target path")
                raise typer.Exit(1)

        # Confirm restore
        console.print("[yellow]Restore file:[/yellow]")
        console.print(f"  From: {backup_path}")
        console.print(f"  To: {target_path}")

        if target_path.exists():
            console.print("\n[red]⚠️  Target file exists and will be overwritten[/red]")

        confirm = typer.confirm("\nProceed with restore?")
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

        # Restore
        restore_backup(backup_path, target_path)
        console.print(f"[green]✓ File restored to {target_path}[/green]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)
