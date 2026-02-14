"""Template installation command."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from aiconfigkit.ai_tools.detector import get_detector
from aiconfigkit.core.checksum import sha256_string
from aiconfigkit.core.models import AIToolType, InstallationScope, TemplateInstallationRecord
from aiconfigkit.core.template_manifest import validate_dependencies, validate_manifest_size
from aiconfigkit.storage.template_library import TemplateLibraryManager
from aiconfigkit.storage.template_tracker import TemplateInstallationTracker
from aiconfigkit.utils.git_helpers import TemplateAuthError, TemplateNetworkError
from aiconfigkit.utils.namespace import derive_namespace, get_install_path
from aiconfigkit.utils.project import find_project_root

console = Console()


def install_command(
    repo_url: str = typer.Argument(..., help="Git repository URL (https:// or git@)"),
    scope: str = typer.Option(
        "project",
        "--scope",
        "-s",
        help="Installation scope (project or global)",
    ),
    namespace_override: Optional[str] = typer.Option(
        None,
        "--as",
        help="Override namespace (default: derived from repository name)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing templates without prompting",
    ),
) -> None:
    """
    Install templates from a repository.

    Example:
        devsync template install https://github.com/acme/templates
        devsync template install https://github.com/acme/templates --scope global
        devsync template install https://github.com/acme/templates --as acme
    """
    try:
        # Validate scope
        if scope not in ["project", "global"]:
            console.print(f"[red]Error: Invalid scope '{scope}'. Must be 'project' or 'global'[/red]")
            raise typer.Exit(1)

        installation_scope = InstallationScope.PROJECT if scope == "project" else InstallationScope.GLOBAL

        # Derive namespace
        try:
            namespace = derive_namespace(repo_url, namespace_override)
            if namespace_override:
                console.print(f"Using custom namespace: [cyan]{namespace}[/cyan]")
            else:
                console.print(f"Deriving namespace from repository: [cyan]{namespace}[/cyan]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

        # Clone repository
        library_manager = TemplateLibraryManager()

        console.print(f"\n[bold]Cloning repository from {repo_url}...[/bold]")

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Cloning repository...", total=None)

            try:
                repo_path, manifest = library_manager.clone_repository(repo_url, namespace_override)
                progress.update(task, completed=True)

            except TemplateAuthError as e:
                progress.stop()
                console.print(f"\n[red]❌ {e}[/red]")
                raise typer.Exit(3)

            except TemplateNetworkError as e:
                progress.stop()
                console.print(f"\n[red]❌ {e}[/red]")
                raise typer.Exit(4)

            except Exception as e:
                progress.stop()
                console.print(f"\n[red]❌ Failed to clone repository: {e}[/red]")
                raise typer.Exit(1)

        console.print("[green]✓ Repository cloned[/green]\n")

        # Validate manifest
        warnings = validate_manifest_size(repo_path / "templatekit.yaml", len(manifest.templates))
        for warning in warnings:
            console.print(warning)

        dep_errors = validate_dependencies(manifest.templates)
        if dep_errors:
            console.print("[red]❌ Manifest validation errors:[/red]")
            for error in dep_errors:
                console.print(f"  - {error}")
            raise typer.Exit(5)

        # Detect IDEs
        if installation_scope == InstallationScope.PROJECT:
            try:
                project_root = find_project_root()
            except Exception:
                console.print("[red]Error: Could not detect project root. Ensure you're in a project directory.[/red]")
                raise typer.Exit(1)
        else:
            project_root = None

        detector = get_detector()
        detected_tool_instances = detector.detect_installed_tools() if project_root else []
        detected_tools = [tool.tool_type for tool in detected_tool_instances]

        if not detected_tools and installation_scope == InstallationScope.PROJECT:
            console.print("[yellow]⚠️  No AI coding tools detected in project.[/yellow]")
            console.print("Templates will be installed but may not be accessible until IDE is configured.")

        if not detected_tools and installation_scope == InstallationScope.GLOBAL:
            # For global, use a default set
            detected_tools = [AIToolType.CURSOR, AIToolType.CLAUDE, AIToolType.WINSURF, AIToolType.COPILOT]

        # Install templates
        console.print(f"[bold]Installing {len(manifest.templates)} templates...[/bold]\n")

        # Initialize tracker
        if installation_scope == InstallationScope.PROJECT:
            if project_root is None:
                console.print("[red]Error: Project root not found[/red]")
                raise typer.Exit(1)
            tracker = TemplateInstallationTracker.for_project(project_root)
        else:
            tracker = TemplateInstallationTracker.for_global()

        installed_count = 0
        skipped_count = 0
        failed_count = 0

        for template in manifest.templates:
            template_display_name = f"{namespace}.{template.name}"

            try:
                console.print(f"Installing [cyan]{template_display_name}[/cyan]...", end=" ")

                # Get template file
                template_file = template.files[0]  # Use first file for now
                source_file = repo_path / template_file.path
                content = source_file.read_text(encoding="utf-8")

                # Calculate checksum
                checksum = sha256_string(content)

                # Install for each detected IDE
                for ide_type in detected_tools:
                    # Get IDE-specific paths
                    if installation_scope == InstallationScope.PROJECT:
                        tool = detector.get_tool_by_type(ide_type)
                        if tool is None or project_root is None:
                            continue

                        ide_base_path = tool.get_project_instructions_directory(project_root)
                        extension = tool.get_instruction_file_extension().lstrip(".")
                    else:
                        # Global installation
                        global_base = Path.home() / ".instructionkit" / "global-templates" / ide_type.value
                        global_base.mkdir(parents=True, exist_ok=True)
                        ide_base_path = global_base
                        extension = "md"  # Default

                    # Get install path with namespace
                    install_path = get_install_path(namespace, template.name, ide_base_path, extension)

                    # Check for conflicts
                    if install_path.exists() and not force:
                        console.print("[yellow]⚠️  (already exists, skipping)[/yellow]")
                        skipped_count += 1
                        continue

                    # Create parent directory
                    install_path.parent.mkdir(parents=True, exist_ok=True)

                    # Write template file
                    install_path.write_text(content, encoding="utf-8")

                    # Create installation record
                    record = TemplateInstallationRecord(
                        id=str(uuid.uuid4()),
                        template_name=template.name,
                        source_repo=manifest.name,
                        source_version=manifest.version,
                        namespace=namespace,
                        installed_path=str(install_path),
                        scope=installation_scope,
                        installed_at=datetime.now(),
                        checksum=checksum,
                        ide_type=ide_type,
                    )

                    tracker.add_installation(record)

                console.print("[green]✓[/green]")
                installed_count += 1

            except Exception as e:
                console.print(f"[red]✗ {e}[/red]")
                failed_count += 1

        # Display summary
        console.print()
        table = Table(title="Installation Summary")
        table.add_column("Status", style="cyan")
        table.add_column("Count", style="magenta")
        table.add_column("Templates", style="green")

        if installed_count > 0:
            template_names = ", ".join([t.name for t in manifest.templates[:3]])
            if len(manifest.templates) > 3:
                template_names += f", ... ({len(manifest.templates)} total)"
            table.add_row("✓ Installed", str(installed_count), template_names)

        if skipped_count > 0:
            table.add_row("⊘ Skipped", str(skipped_count), "(already exists)")

        if failed_count > 0:
            table.add_row("✗ Failed", str(failed_count), "(see errors above)")

        console.print(table)

        # Show available commands
        if installed_count > 0:
            console.print("\n[bold]Commands available:[/bold]")
            for template in manifest.templates[:5]:
                console.print(f"  /{namespace}.{template.name}")
            if len(manifest.templates) > 5:
                console.print(f"  ... and {len(manifest.templates) - 5} more")

        console.print("\n[green]✓ Installation complete[/green]")

    except typer.Exit:
        raise
    except KeyboardInterrupt:
        console.print("\n[yellow]Installation cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)
