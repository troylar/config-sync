"""Delete command for removing instructions from library."""

import typer
from rich.console import Console
from rich.prompt import Confirm

from aiconfigkit.storage.library import LibraryManager
from aiconfigkit.storage.tracker import InstallationTracker
from aiconfigkit.utils.ui import print_error, print_success, print_warning

console = Console()

app = typer.Typer()


def delete_from_library(
    namespace: str,
    force: bool = False,
) -> int:
    """
    Delete a repository from the library.

    Args:
        namespace: Repository namespace to delete
        force: Skip confirmation

    Returns:
        Exit code (0 = success)
    """
    library = LibraryManager()
    tracker = InstallationTracker()

    # Check if repository exists
    repo = library.get_repository(namespace)
    if not repo:
        print_error(f"Repository not found: {namespace}")
        print_error("Use 'devsync list library' to see available repositories")
        return 1

    # Check if any instructions from this repo are currently installed
    installed_records = tracker.list_installations()
    installed_from_repo = [
        record for record in installed_records if any(inst.repo_namespace == namespace for inst in repo.instructions)
    ]

    if installed_from_repo and not force:
        print_warning(
            f"\n⚠️  Warning: {len(installed_from_repo)} instruction(s) from this repository are currently installed:"
        )
        for record in installed_from_repo[:5]:  # Show first 5
            console.print(f"  - {record.instruction_name} ({record.ai_tool.value})")
        if len(installed_from_repo) > 5:
            console.print(f"  ... and {len(installed_from_repo) - 5} more")
        console.print()
        print_warning("Deleting from library will not uninstall them from your AI tools.\n")

    # Confirm deletion
    if not force:
        console.print(f"\n[bold]Repository:[/bold] {repo.name}")
        console.print(f"[bold]Namespace:[/bold] {repo.namespace}")
        console.print(f"[bold]Instructions:[/bold] {len(repo.instructions)}\n")

        confirmed = Confirm.ask("[yellow]Are you sure you want to delete this repository from your library?[/yellow]")

        if not confirmed:
            console.print("[dim]Cancelled[/dim]")
            return 0

    # Delete repository
    success = library.remove_repository(namespace)

    if success:
        print_success(
            f"✓ Deleted repository '{repo.name}' from library\n"
            f"  {len(repo.instructions)} instruction(s) removed from library"
        )
        if installed_from_repo:
            print_warning(
                f"\n  Note: {len(installed_from_repo)} instruction(s) are still installed in your AI tools.\n"
                f"  Use 'devsync uninstall <name>' to remove them."
            )
        return 0
    else:
        print_error(f"Failed to delete repository: {namespace}")
        return 1


@app.command(name="delete")
def delete_command(
    namespace: str = typer.Argument(
        ...,
        help="Repository namespace to delete from library",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    Delete a repository from your local library.

    This removes the downloaded instructions from your library but does NOT
    uninstall them from your AI tools. To uninstall, use 'devsync uninstall'.

    Examples:
        # Delete a repository
        devsync delete github.com_company_instructions

        # Skip confirmation
        devsync delete github.com_company_instructions --force

        # List repositories to find namespace
        devsync list library
    """
    exit_code = delete_from_library(namespace=namespace, force=force)
    raise typer.Exit(code=exit_code)
