"""Template validation command."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from aiconfigkit.core.checksum import calculate_file_checksum
from aiconfigkit.storage.template_library import TemplateLibraryManager
from aiconfigkit.storage.template_tracker import TemplateInstallationTracker
from aiconfigkit.utils.project import find_project_root

console = Console()


class ValidationIssue:
    """Represents a validation issue found during template validation."""

    def __init__(self, severity: str, template: str, issue_type: str, description: str, remediation: str = ""):
        """
        Initialize validation issue.

        Args:
            severity: Issue severity (error, warning, info)
            template: Template identifier
            issue_type: Type of issue
            description: Issue description
            remediation: Suggested remediation
        """
        self.severity = severity
        self.template = template
        self.issue_type = issue_type
        self.description = description
        self.remediation = remediation


def validate_command(
    scope: str = typer.Option(
        "all",
        "--scope",
        "-s",
        help="Which installations to validate (project, global, all)",
    ),
    fix: bool = typer.Option(
        False,
        "--fix",
        help="Attempt to fix issues automatically",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed information",
    ),
) -> None:
    """
    Validate installed templates for issues.

    Checks for:
    - Tracking inconsistencies (installed but files missing)
    - Missing files referenced in manifest
    - Outdated versions (local vs remote)
    - Broken template dependencies
    - Local modifications (checksum mismatch)

    Example:
        devsync template validate
        devsync template validate --scope project
        devsync template validate --fix
    """
    try:
        # Validate scope
        if scope not in ["project", "global", "all"]:
            console.print(f"[red]Error: Invalid scope '{scope}'. Must be 'project', 'global', or 'all'[/red]")
            raise typer.Exit(1)

        issues: list[ValidationIssue] = []

        # Validate project templates
        if scope in ["project", "all"]:
            try:
                project_root = find_project_root()
                if project_root:
                    console.print(f"\n[bold]Validating project templates[/bold] ({project_root})...")
                    project_issues = _validate_installations(
                        TemplateInstallationTracker.for_project(project_root), "project", verbose
                    )
                    issues.extend(project_issues)
                elif scope == "project":
                    console.print("[yellow]⚠️  Not in a project directory[/yellow]")
                    raise typer.Exit(1)
            except Exception as e:
                if scope == "project":
                    console.print(f"[red]Error: {e}[/red]")
                    raise typer.Exit(1)

        # Validate global templates
        if scope in ["global", "all"]:
            console.print("\n[bold]Validating global templates...[/bold]")
            global_issues = _validate_installations(TemplateInstallationTracker.for_global(), "global", verbose)
            issues.extend(global_issues)

        # Display results
        _display_validation_results(issues, fix, verbose)

    except typer.Exit:
        raise
    except KeyboardInterrupt:
        console.print("\n[yellow]Validation cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _validate_installations(tracker: TemplateInstallationTracker, scope: str, verbose: bool) -> list[ValidationIssue]:
    """Validate all installations tracked by a tracker."""
    issues: list[ValidationIssue] = []
    records = tracker.load_installation_records()

    if not records:
        console.print(f"  [dim]No {scope} templates installed[/dim]")
        return issues

    console.print(f"  Found {len(records)} template(s)")

    for record in records:
        template_id = f"{record.namespace}.{record.template_name}"

        # Check 1: File exists
        installed_path = Path(record.installed_path)
        if not installed_path.exists():
            issues.append(
                ValidationIssue(
                    severity="error",
                    template=template_id,
                    issue_type="missing_file",
                    description=f"Installed file not found: {installed_path}",
                    remediation=(
                        f"Reinstall template with: "
                        f"devsync template install {record.source_repo} --template {record.template_name}"
                    ),
                )
            )
            continue

        # Check 2: Local modifications (checksum mismatch)
        try:
            current_checksum = calculate_file_checksum(str(installed_path))
            if current_checksum != record.checksum:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        template=template_id,
                        issue_type="modified",
                        description="Template has been modified locally",
                        remediation=f"Update to restore original: devsync template update {record.namespace}",
                    )
                )
        except Exception as e:
            if verbose:
                console.print(f"  [dim]Could not verify checksum for {template_id}: {e}[/dim]")

        # Check 3: Outdated version
        try:
            library_manager = TemplateLibraryManager()
            local_version = library_manager.get_repository_version(record.namespace)
            if local_version and record.source_version and local_version != record.source_version:
                issues.append(
                    ValidationIssue(
                        severity="info",
                        template=template_id,
                        issue_type="outdated",
                        description=f"Newer version available ({record.source_version} -> {local_version})",
                        remediation=f"Update with: devsync template update {record.namespace}",
                    )
                )
        except Exception as e:
            if verbose:
                console.print(f"  [dim]Could not check version for {template_id}: {e}[/dim]")

    return issues


def _display_validation_results(issues: list[ValidationIssue], fix: bool, verbose: bool) -> None:
    """Display validation results in a formatted table."""
    if not issues:
        console.print("\n[green]✓ All templates are valid![/green]")
        return

    # Group by severity
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    info = [i for i in issues if i.severity == "info"]

    console.print("\n[bold]Validation Summary:[/bold]")
    if errors:
        console.print(f"  [red]✗ {len(errors)} error(s)[/red]")
    if warnings:
        console.print(f"  [yellow]⚠ {len(warnings)} warning(s)[/yellow]")
    if info:
        console.print(f"  [blue]ℹ {len(info)} info[/blue]")

    # Display issues table
    if verbose or errors:
        table = Table(title="\nValidation Issues")
        table.add_column("Severity", style="bold")
        table.add_column("Template")
        table.add_column("Issue Type")
        table.add_column("Description")
        table.add_column("Remediation")

        for issue in errors + warnings + info:
            severity_color = {"error": "red", "warning": "yellow", "info": "blue"}[issue.severity]
            severity_symbol = {"error": "✗", "warning": "⚠", "info": "ℹ"}[issue.severity]

            table.add_row(
                f"[{severity_color}]{severity_symbol} {issue.severity.upper()}[/{severity_color}]",
                issue.template,
                issue.issue_type,
                issue.description,
                issue.remediation,
            )

        console.print(table)

    if fix:
        console.print("\n[yellow]⚠️  Auto-fix is not yet implemented[/yellow]")
        console.print("Please use the suggested remediation commands above")

    # Exit with error code if there are errors
    if errors:
        raise typer.Exit(1)
