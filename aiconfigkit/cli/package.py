"""Package CLI commands."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from aiconfigkit.cli.package_create import create_package_command
from aiconfigkit.cli.package_install import InstallationResult, install_package
from aiconfigkit.core.models import (
    AIToolType,
    ConflictResolution,
    InstallationScope,
    InstallationStatus,
)
from aiconfigkit.storage.package_tracker import PackageTracker
from aiconfigkit.utils.project import find_project_root

console = Console()
package_app = typer.Typer(help="Manage configuration packages")

# Register create command
package_app.command(name="create")(create_package_command)


@package_app.command(name="install")
def install_package_command(
    package_path: str = typer.Argument(
        ...,
        help="Path to package directory containing manifest",
    ),
    target_ide: str = typer.Option(
        "claude",
        "--ide",
        "-i",
        help="Target IDE (claude, cursor, windsurf, copilot)",
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project root directory (defaults to current directory)",
    ),
    conflict: str = typer.Option(
        "skip",
        "--conflict",
        "-c",
        help="Conflict resolution strategy (skip, overwrite, rename)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force reinstallation even if already installed",
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
    Install a configuration package to a project.

    Package must contain an ai-config-kit-package.yaml manifest.

    Example:
        devsync package install ./python-dev-setup --ide claude
        devsync package install ~/packages/my-package --ide cursor --conflict overwrite
    """
    try:
        # Parse target IDE
        try:
            ide_type = AIToolType(target_ide.lower())
        except ValueError:
            console.print(
                f"[red]Error: Invalid IDE '{target_ide}'. " f"Valid options: claude, cursor, windsurf, copilot[/red]"
            )
            raise typer.Exit(1)

        # Parse conflict resolution
        try:
            conflict_resolution = ConflictResolution(conflict.lower())
        except ValueError:
            console.print(
                f"[red]Error: Invalid conflict resolution '{conflict}'. "
                f"Valid options: skip, overwrite, rename[/red]"
            )
            raise typer.Exit(1)

        # Determine project root
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

        # Resolve package path
        pkg_path = Path(package_path).resolve()
        if not pkg_path.exists():
            console.print(f"[red]Error: Package directory not found: {package_path}[/red]")
            raise typer.Exit(1)

        if not quiet:
            console.print(f"[cyan]Installing package from {pkg_path}...[/cyan]")
            console.print(f"[cyan]Target IDE: {ide_type.value}[/cyan]")
            console.print(f"[cyan]Project root: {project_root}[/cyan]")

        # Install package
        result = install_package(
            package_path=pkg_path,
            project_root=project_root,
            target_ide=ide_type,
            scope=InstallationScope.PROJECT,
            conflict_resolution=conflict_resolution,
            force=force,
        )

        # Output results
        if json_output:
            import json

            output = {
                "success": result.success,
                "status": result.status.value,
                "package_name": result.package_name,
                "version": result.version,
                "installed_count": result.installed_count,
                "skipped_count": result.skipped_count,
                "failed_count": result.failed_count,
                "components_installed": {k.value: v for k, v in result.components_installed.items()},
                "is_reinstall": result.is_reinstall,
                "error_message": result.error_message,
            }
            console.print(json.dumps(output, indent=2))
        else:
            _display_installation_summary(result, quiet)

        # Exit with appropriate code
        if not result.success:
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Installation failed: {e}[/red]")
        raise typer.Exit(1)


def _display_installation_summary(result: InstallationResult, quiet: bool) -> None:
    """Display installation summary to user."""
    if result.success:
        # Success message
        if result.status == InstallationStatus.COMPLETE:
            console.print(f"\n[green]✓ Successfully installed {result.package_name} v{result.version}[/green]")
        elif result.status == InstallationStatus.PARTIAL:
            console.print(f"\n[yellow]⚠ Partially installed {result.package_name} v{result.version}[/yellow]")
        else:
            console.print(f"\n[red]✗ Installation failed for {result.package_name} v{result.version}[/red]")

        if result.is_reinstall:
            console.print("[cyan]  (Reinstalled existing package)[/cyan]")

        # Component summary table
        if not quiet:
            table = Table(title="Installation Summary", show_header=True)
            table.add_column("Component Type", style="cyan")
            table.add_column("Count", justify="right", style="green")

            for component_type, count in result.components_installed.items():
                table.add_row(component_type.value, str(count))

            console.print()
            console.print(table)

        # Statistics
        console.print(f"\n  Installed: {result.installed_count}")
        if result.skipped_count > 0:
            console.print(f"  Skipped: {result.skipped_count}")
        if result.failed_count > 0:
            console.print(f"  Failed: {result.failed_count}")

    else:
        # Failure message
        console.print(f"\n[red]✗ Installation failed for {result.package_name}[/red]")
        if result.error_message:
            console.print(f"[red]  Error: {result.error_message}[/red]")


@package_app.command(name="list")
def list_packages_command(
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project root directory (defaults to current directory)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
) -> None:
    """
    List installed packages in a project.

    Example:
        devsync package list
        devsync package list --project ~/my-project
    """
    try:
        # Determine project root
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

        # Get tracker
        tracker_file = project_root / ".ai-config-kit" / "packages.json"
        tracker = PackageTracker(tracker_file)

        # Get installed packages
        packages = tracker.get_installed_packages()

        if json_output:
            import json

            output = []
            for pkg in packages:
                output.append(
                    {
                        "name": pkg.package_name,
                        "namespace": pkg.namespace,
                        "version": pkg.version,
                        "status": pkg.status.value,
                        "scope": pkg.scope.value,
                        "installed_at": pkg.installed_at.isoformat(),
                        "updated_at": pkg.updated_at.isoformat(),
                        "component_count": len(pkg.components),
                    }
                )
            console.print(json.dumps(output, indent=2))
        else:
            if not packages:
                console.print("[yellow]No packages installed in this project.[/yellow]")
                return

            console.print(f"\n[cyan]Installed packages in {project_root}:[/cyan]\n")

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Package", style="green")
            table.add_column("Version", style="blue")
            table.add_column("Status", style="yellow")
            table.add_column("Components", justify="right", style="magenta")
            table.add_column("Installed", style="dim")

            for pkg in packages:
                status_icon = "✓" if pkg.status == InstallationStatus.COMPLETE else "⚠"
                table.add_row(
                    f"{pkg.namespace}/{pkg.package_name}",
                    pkg.version,
                    f"{status_icon} {pkg.status.value}",
                    str(len(pkg.components)),
                    pkg.installed_at.strftime("%Y-%m-%d %H:%M"),
                )

            console.print(table)
            console.print(f"\n[dim]Total: {len(packages)} package(s)[/dim]\n")

    except Exception as e:
        console.print(f"[red]Failed to list packages: {e}[/red]")
        raise typer.Exit(1)


@package_app.command(name="uninstall")
def uninstall_package_command(
    package_name: str = typer.Argument(
        ...,
        help="Package name to uninstall",
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project root directory (defaults to current directory)",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    Uninstall a package from a project.

    This removes the package's files and tracking record.

    Example:
        devsync package uninstall test-package
        devsync package uninstall my-org/my-package --yes
    """
    try:
        # Determine project root
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

        # Get tracker
        tracker_file = project_root / ".ai-config-kit" / "packages.json"
        tracker = PackageTracker(tracker_file)

        # Get package
        package = tracker.get_package(package_name, InstallationScope.PROJECT)
        if not package:
            console.print(f"[red]Error: Package '{package_name}' is not installed in this project.[/red]")
            raise typer.Exit(1)

        # Confirm uninstall
        if not yes:
            console.print("\n[yellow]Package to uninstall:[/yellow]")
            console.print(f"  Name: {package.package_name}")
            console.print(f"  Version: {package.version}")
            console.print(f"  Components: {len(package.components)}")

            confirm = typer.confirm("\nAre you sure you want to uninstall this package?")
            if not confirm:
                console.print("[yellow]Uninstall cancelled.[/yellow]")
                raise typer.Exit(0)

        # Remove component files
        removed_count = 0
        failed_count = 0
        for component in package.components:
            try:
                file_path = project_root / component.installed_path
                if file_path.exists():
                    file_path.unlink()
                    removed_count += 1
                    console.print(f"[dim]  Removed: {component.installed_path}[/dim]")
            except Exception as e:
                console.print(f"[yellow]  Warning: Failed to remove {component.installed_path}: {e}[/yellow]")
                failed_count += 1

        # Remove from tracker
        tracker.remove_package(package_name, InstallationScope.PROJECT)

        # Summary
        console.print(f"\n[green]✓ Uninstalled {package.package_name} v{package.version}[/green]")
        console.print(f"  Removed {removed_count} file(s)")
        if failed_count > 0:
            console.print(f"[yellow]  Failed to remove {failed_count} file(s)[/yellow]")

    except Exception as e:
        console.print(f"[red]Failed to uninstall package: {e}[/red]")
        raise typer.Exit(1)
