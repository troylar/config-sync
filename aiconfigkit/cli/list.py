"""List command implementation."""

from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from aiconfigkit.core.git_operations import GitOperations
from aiconfigkit.core.models import AIToolType
from aiconfigkit.core.repository import RepositoryParser
from aiconfigkit.storage.library import LibraryManager
from aiconfigkit.storage.tracker import InstallationTracker
from aiconfigkit.utils.project import find_project_root
from aiconfigkit.utils.ui import (
    format_installed_table,
    format_instructions_table,
    print_error,
    print_info,
)
from aiconfigkit.utils.validation import is_valid_git_url, normalize_repo_url

console = Console()


def list_available(
    repo: str,
    tag: Optional[str] = None,
    bundles_only: bool = False,
    instructions_only: bool = False,
) -> int:
    """
    List available instructions from a repository.

    Args:
        repo: Git repository URL
        tag: Filter by tag
        bundles_only: Show only bundles
        instructions_only: Show only instructions

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Validate repository URL
    if not is_valid_git_url(repo):
        print_error(f"Invalid Git repository URL: {repo}", console)
        return 1

    # Check Git is installed
    if not GitOperations.is_git_installed():
        print_error("Git is not installed. Please install Git and try again.", console)
        return 1

    # Clone repository or use local path
    git_ops = GitOperations()
    is_local = git_ops.is_local_path(repo)

    if is_local:
        # Use local directory directly
        try:
            repo_path = git_ops.clone_repository(repo)
        except Exception as e:
            print_error(f"Failed to access local directory: {e}", console)
            return 1
    else:
        # Clone remote repository
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Fetching repository...", total=None)

            try:
                repo_path = git_ops.clone_repository(repo)
            except Exception as e:
                print_error(f"Failed to clone repository: {e}", console)
                return 1

    try:
        # Parse repository
        parser = RepositoryParser(repo_path)
        repository = parser.parse()

        # Filter by tag if specified
        instructions = repository.instructions
        bundles = repository.bundles

        if tag:
            instructions = [i for i in instructions if tag in i.tags]
            bundles = [b for b in bundles if tag in b.tags]
            print_info(f"Filtered by tag: {tag}", console)

        # Apply filters
        if bundles_only:
            instructions = []
        if instructions_only:
            bundles = []

        # Check if anything to display
        if not instructions and not bundles:
            if tag:
                console.print(f"[yellow]No instructions or bundles found with tag '{tag}'[/yellow]")
            else:
                console.print("[yellow]No instructions or bundles found in repository[/yellow]")
            return 0

        # Display table
        table = format_instructions_table(instructions, bundles, show_bundles=not instructions_only)
        console.print()
        console.print(table)
        console.print()

        # Summary
        len(instructions) + len(bundles)
        console.print(f"Found {len(instructions)} instruction(s) and {len(bundles)} bundle(s)")

        return 0

    finally:
        # Clean up cloned repository (but not local directories)
        GitOperations.cleanup_repository(repo_path, is_temp=not is_local)


def list_installed(
    tool: Optional[str] = None,
    repo: Optional[str] = None,
) -> int:
    """
    List installed instructions.

    Args:
        tool: Filter by AI tool (cursor, copilot, etc.)
        repo: Filter by source repository URL

    Returns:
        Exit code (0 for success, 1 for error)
    """
    tracker = InstallationTracker()

    # Detect project root to include project-scoped installations
    project_root = find_project_root()

    # Get all installed instructions (both global and project)
    if tool:
        # Filter by specific tool
        try:
            ai_tool = AIToolType(tool.lower())
            records = tracker.get_installed_instructions(ai_tool, project_root=project_root)
        except ValueError:
            print_error(f"Invalid AI tool: {tool}. " f"Valid options: cursor, copilot, windsurf, claude", console)
            return 1
    else:
        records = tracker.get_installed_instructions(project_root=project_root)

    # Filter by repository if specified
    if repo:
        normalized_repo = normalize_repo_url(repo)
        records = [r for r in records if normalize_repo_url(r.source_repo) == normalized_repo]

    # Check if anything to display
    if not records:
        if tool and repo:
            console.print(f"[yellow]No instructions installed for {tool} from {repo}[/yellow]")
        elif tool:
            console.print(f"[yellow]No instructions installed for {tool}[/yellow]")
        elif repo:
            console.print(f"[yellow]No instructions installed from {repo}[/yellow]")
        else:
            console.print("[yellow]No instructions installed[/yellow]")
        return 0

    # Display table
    table = format_installed_table(records, group_by_tool=not bool(tool))
    console.print()
    console.print(table)
    console.print()

    # Summary
    console.print(f"Total: {len(records)} installed instruction(s)")

    return 0


def list_library(
    repo_filter: Optional[str] = None,
    show_instructions: bool = False,
) -> int:
    """
    List sources and instructions in the local library.

    Args:
        repo_filter: Filter by source alias or namespace
        show_instructions: Show individual instructions

    Returns:
        Exit code (0 for success)
    """
    library = LibraryManager()
    repositories = library.list_repositories()

    if not repositories:
        print_info("Library is empty. Use 'devsync download' to add sources.")
        return 0

    # Filter if specified (match against alias or namespace)
    if repo_filter:
        repositories = [
            r
            for r in repositories
            if repo_filter.lower() in (r.alias or "").lower() or repo_filter.lower() in r.namespace.lower()
        ]
        if not repositories:
            print_error(f"No sources matching: {repo_filter}")
            return 1

    # Show sources
    if not show_instructions:
        table = Table(title="Library Sources", show_header=True, header_style="bold cyan")
        table.add_column("Alias", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Version", style="yellow")
        table.add_column("Instructions", style="magenta")
        table.add_column("Downloaded", style="blue")

        for repo in sorted(repositories, key=lambda r: r.alias or r.name):
            table.add_row(
                repo.alias or repo.namespace,
                repo.name,
                repo.version,
                str(len(repo.instructions)),
                repo.downloaded_at.strftime("%Y-%m-%d"),
            )

        console.print()
        console.print(table)
        console.print()
        console.print(f"Total: {len(repositories)} source(s) in library")
        console.print()
        console.print("[dim]Use 'devsync install' to install instructions from library[/dim]")

    # Show instructions
    else:
        table = Table(title="Library Instructions", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        table.add_column("Repository", style="green")
        table.add_column("Version", style="yellow")
        table.add_column("Tags", style="magenta")

        all_instructions = []
        for repo in repositories:
            all_instructions.extend(repo.instructions)

        for inst in sorted(all_instructions, key=lambda i: i.name):
            tags_str = ", ".join(inst.tags[:3]) if inst.tags else "-"
            if len(inst.tags) > 3:
                tags_str += f" +{len(inst.tags) - 3}"

            table.add_row(
                inst.name,
                inst.description[:60] + "..." if len(inst.description) > 60 else inst.description,
                inst.repo_name,
                inst.version,
                tags_str,
            )

        console.print()
        console.print(table)
        console.print()
        console.print(f"Total: {len(all_instructions)} instruction(s) in library")
        console.print()
        console.print("[dim]Use 'devsync install' to install these instructions[/dim]")

    return 0
