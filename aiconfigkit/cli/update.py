"""Update command for refreshing library instructions."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from git import Repo
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from aiconfigkit.core.checksum import calculate_file_checksum
from aiconfigkit.core.git_operations import GitOperations, RepositoryOperationError
from aiconfigkit.core.models import LibraryInstruction, RefType
from aiconfigkit.core.repository import RepositoryParser
from aiconfigkit.storage.library import LibraryManager
from aiconfigkit.storage.tracker import InstallationTracker
from aiconfigkit.utils.project import find_project_root
from aiconfigkit.utils.ui import print_error, print_info, print_success

console = Console()

app = typer.Typer()


def update_repository(
    namespace: Optional[str] = None,
    all_repos: bool = False,
) -> int:
    """
    Update instructions from their source repositories.

    Only updates mutable references (branches). Tags and commits are immutable and will be skipped.

    Args:
        namespace: Specific repository namespace to update
        all_repos: Update all repositories

    Returns:
        Exit code (0 = success)
    """
    library = LibraryManager()
    tracker = InstallationTracker()

    if not all_repos and not namespace:
        print_error("Must specify either --namespace or --all")
        return 1

    # Get repositories to update
    if all_repos:
        repositories = library.list_repositories()
        if not repositories:
            print_info("No repositories in library to update")
            return 0
    else:
        assert namespace is not None, "namespace should not be None here"
        repo = library.get_repository(namespace)
        if not repo:
            print_error(f"Repository not found: {namespace}")
            print_info("Use 'devsync list library' to see available repositories")
            return 1
        repositories = [repo]

    console.print(f"\n[bold]Updating {len(repositories)} repository(ies)...[/bold]\n")

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for repo in repositories:
        # Extract ref info from namespace
        ref, ref_type = _extract_ref_from_namespace(repo.namespace)

        # Skip immutable refs (tags and commits)
        if ref and ref_type in (RefType.TAG, RefType.COMMIT):
            ref_type_name = "tag" if ref_type == RefType.TAG else "commit"
            console.print(
                f"[yellow]⊘ Skipped:[/yellow] {repo.name} " f"({ref_type_name} [cyan]{ref}[/cyan] is immutable)"
            )
            skipped_count += 1
            continue

        # Update branch-based or non-versioned repositories
        console.print(f"[cyan]Updating:[/cyan] {repo.name} ", end="")
        if ref:
            console.print(f"(branch [green]{ref}[/green])")
        else:
            console.print("(default branch)")

        try:
            # Get the repository directory
            repo_dir = library.library_dir / repo.namespace

            if not repo_dir.exists():
                print_error(f"  Repository directory not found: {repo_dir}")
                error_count += 1
                continue

            # Check if it's a git repository (skip local non-git repos)
            git_dir = repo_dir / ".git"
            if not git_dir.exists():
                console.print("  [yellow]⊘ Skipped:[/yellow] Not a Git repository (local source)")
                skipped_count += 1
                continue

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("  Checking for updates...", total=None)

                # Open repository and check for updates
                git_repo = Repo(repo_dir)
                branch_name = ref if ref else git_repo.active_branch.name

                # Check if updates are available
                has_updates = GitOperations.check_for_updates(git_repo, branch_name)

                if not has_updates:
                    console.print("  [green]✓[/green] Already up to date")
                    continue

                # Pull updates
                progress.update(task, description="  Pulling updates...")
                result = GitOperations.pull_repository_updates(git_repo, branch_name)

                if not result.get("success"):
                    error_type = result.get("error", "unknown")
                    if error_type == "local_modifications":
                        console.print(f"  [red]✗[/red] {result.get('message')}")
                    elif error_type == "conflict":
                        console.print("  [red]✗[/red] Merge conflict detected")
                    else:
                        console.print(f"  [red]✗[/red] Update failed: {result.get('message')}")
                    error_count += 1
                    continue

            # Re-parse repository to update library index
            parser = RepositoryParser(repo_dir)
            repository = parser.parse()

            # Update library instructions
            library_instructions = []
            instructions_dir = repo_dir / "instructions"

            for instruction in repository.instructions:
                source_file = repo_dir / instruction.file_path
                if not source_file.exists():
                    continue

                dest_file = instructions_dir / f"{instruction.name}.md"
                if source_file != dest_file:
                    shutil.copy2(source_file, dest_file)

                checksum = calculate_file_checksum(str(dest_file))

                lib_inst = LibraryInstruction(
                    id=f"{repo.namespace}/{instruction.name}",
                    name=instruction.name,
                    description=instruction.description,
                    repo_namespace=repo.namespace,
                    repo_url=repo.url,
                    repo_name=repo.name,
                    author=repository.metadata.get("author", "Unknown"),
                    version=repository.metadata.get("version", "1.0.0"),
                    file_path=str(dest_file),
                    tags=instruction.tags,
                    downloaded_at=datetime.now(),
                    checksum=checksum,
                )
                library_instructions.append(lib_inst)

            # Update library index
            library.add_repository(
                repo_name=repo.name,
                repo_description=repository.metadata.get("description", ""),
                repo_url=repo.url,
                repo_author=repository.metadata.get("author", "Unknown"),
                repo_version=repository.metadata.get("version", "1.0.0"),
                instructions=library_instructions,
                alias=repo.alias,
            )

            # Update installed instructions
            _update_installed_instructions(repo.namespace, library_instructions, tracker)

            console.print(f"  [green]✓[/green] Updated successfully ({len(library_instructions)} instructions)")
            updated_count += 1

        except RepositoryOperationError as e:
            console.print(f"  [red]✗[/red] Failed: {e}")
            error_count += 1
        except Exception as e:
            console.print(f"  [red]✗[/red] Unexpected error: {e}")
            error_count += 1

    # Summary
    console.print()
    if updated_count > 0:
        print_success(f"✓ Updated: {updated_count} repository(ies)")
    if skipped_count > 0:
        print_info(f"⊘ Skipped: {skipped_count} immutable reference(s)")
    if error_count > 0:
        print_error(f"✗ Failed: {error_count} repository(ies)")

    return 0 if error_count == 0 else 1


def _extract_ref_from_namespace(namespace: str) -> tuple[Optional[str], Optional[RefType]]:
    """Extract Git reference from versioned namespace."""
    if "@" not in namespace:
        return (None, None)

    ref = namespace.split("@", 1)[1]

    import re

    # Tags typically start with 'v' followed by numbers
    if re.match(r"^v?\d+\.\d+", ref):
        return (ref, RefType.TAG)
    # Commit hashes are hex strings
    elif re.match(r"^[0-9a-f]{7,40}$", ref):
        return (ref, RefType.COMMIT)
    # Everything else is likely a branch
    else:
        return (ref, RefType.BRANCH)


def _update_installed_instructions(
    repo_namespace: str, library_instructions: list[LibraryInstruction], tracker: InstallationTracker
) -> None:
    """Update files for installed instructions from this repository."""
    project_root = find_project_root()

    # Get all installed instructions from this repository
    all_records = tracker.get_installed_instructions(project_root=project_root)
    repo_records = [r for r in all_records if repo_namespace in r.source_repo or repo_namespace in r.instruction_name]

    if not repo_records:
        return

    # Update each installed instruction file
    for record in repo_records:
        # Find matching library instruction
        matching_inst = None
        for lib_inst in library_instructions:
            if lib_inst.name in record.instruction_name or record.instruction_name in lib_inst.id:
                matching_inst = lib_inst
                break

        if not matching_inst:
            continue

        # Update the installed file
        try:
            source_path = Path(matching_inst.file_path)
            if not source_path.exists():
                continue

            installed_path = Path(record.installed_path)
            # Handle relative paths for project-scoped installations
            if not installed_path.is_absolute() and project_root:
                installed_path = project_root / installed_path

            if installed_path.exists():
                # Read new content and write to installed location
                content = source_path.read_text(encoding="utf-8")
                installed_path.write_text(content, encoding="utf-8")
        except Exception:
            # Silently skip if update fails (file might have been manually removed)
            continue


@app.command(name="update")
def update_command(
    namespace: Optional[str] = typer.Option(
        None,
        "--namespace",
        "-n",
        help="Repository namespace to update",
    ),
    all_repos: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Update all repositories in library",
    ),
) -> None:
    """
    Update downloaded instructions to their latest versions.

    This re-downloads instructions from their source repositories,
    ensuring you have the latest versions in your library.

    Examples:
        # Update a specific repository
        devsync update --namespace github.com_company_instructions

        # Update all repositories
        devsync update --all

        # List repositories to find namespace
        devsync list library
    """
    exit_code = update_repository(namespace=namespace, all_repos=all_repos)
    raise typer.Exit(code=exit_code)
