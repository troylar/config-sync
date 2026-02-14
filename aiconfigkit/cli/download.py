"""Download command for fetching instructions into the library."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from aiconfigkit.core.checksum import calculate_file_checksum
from aiconfigkit.core.git_operations import GitOperations, RepositoryOperationError
from aiconfigkit.core.models import LibraryInstruction
from aiconfigkit.core.repository import RepositoryParser
from aiconfigkit.storage.library import LibraryManager
from aiconfigkit.utils.ui import print_error, print_success

console = Console()

app = typer.Typer()


def download_instructions(
    repo: str,
    force: bool = False,
    alias: Optional[str] = None,
    ref: Optional[str] = None,
) -> int:
    """
    Download instructions from a repository into the local library.

    Args:
        repo: Repository URL or local path
        force: If True, re-download even if already in library
        alias: User-friendly alias for this source (auto-generated if not provided)
        ref: Git reference (tag, branch, or commit) to download

    Returns:
        Exit code (0 = success)
    """
    library = LibraryManager()

    # Display what we're downloading
    if ref:
        console.print(f"\n[bold]Downloading from:[/bold] {repo} [bold cyan]@{ref}[/bold cyan]\n")
    else:
        console.print(f"\n[bold]Downloading from:[/bold] {repo}\n")

    # Determine if local or remote
    is_local = GitOperations.is_local_path(repo)
    temp_repo_path = None  # Track temp directory for cleanup
    ref_type = None  # Track the reference type

    try:
        # Validate and detect ref type for remote repositories
        if ref and not is_local:
            try:
                validated_ref, ref_type = GitOperations.detect_ref_type(repo, ref)
                ref = validated_ref  # Use the validated reference
            except RepositoryOperationError as e:
                if e.error_type == "invalid_reference":
                    print_error(f"Invalid reference '{ref}': not found in repository")
                    return 1
                elif e.error_type == "network_error":
                    print_error("Network error: unable to access repository")
                    return 1
                else:
                    print_error(f"Failed to validate reference: {e}")
                    return 1

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            if is_local:
                if ref:
                    print_error("Version references (--ref) are not supported for local repositories")
                    return 1
                progress.add_task("Loading local repository...", total=None)
                repo_path = Path(repo).resolve()
            else:
                if ref:
                    task = progress.add_task(f"Cloning repository at {ref}...", total=None)
                else:
                    task = progress.add_task("Cloning repository...", total=None)

                # Use new clone_at_ref for versioned cloning
                import tempfile
                from pathlib import Path as PathlibPath

                temp_dir = PathlibPath(tempfile.mkdtemp(prefix="devsync-"))

                try:
                    GitOperations.clone_at_ref(repo, temp_dir, ref, ref_type)
                    repo_path = temp_dir
                    temp_repo_path = repo_path  # Save for cleanup
                except RepositoryOperationError as e:
                    if temp_dir.exists():
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    print_error(f"Failed to clone repository: {e}")
                    return 1

                progress.update(task, completed=True)

            # Parse repository
            task = progress.add_task("Parsing repository metadata...", total=None)
            parser = RepositoryParser(repo_path)
            repository = parser.parse()
            repository.url = repo
            progress.update(task, completed=True)

        # Generate versioned namespace if ref is specified
        repo_name = repository.metadata.get("name", "Unknown")
        if ref:
            repo_namespace = library.get_versioned_namespace(repo, ref)
        else:
            repo_namespace = library.get_repo_namespace(repo, repo_name)

        # Check if this specific version already exists
        existing_repo = library.get_repository(repo_namespace)

        if existing_repo and not force:
            if ref:
                print_error(
                    f"Version '{ref}' of '{repo_name}' already exists in library.\n" f"Use --force to re-download."
                )
            else:
                print_error(
                    f"Source '{existing_repo.alias or repo_name}' already exists in library.\n"
                    f"Use --force to re-download."
                )
            return 1

        # Prepare library instructions
        library_instructions = []
        library_repo_dir = library.library_dir / repo_namespace
        repo_dir = library_repo_dir / "instructions"
        repo_dir.mkdir(parents=True, exist_ok=True)

        console.print("\n[bold]Copying instructions to library...[/bold]\n")

        for instruction in repository.instructions:
            # Copy instruction file to library
            source_file = repo_path / instruction.file_path
            if not source_file.exists():
                print_error(f"Warning: File not found: {instruction.file_path}")
                continue

            dest_file = repo_dir / f"{instruction.name}.md"
            shutil.copy2(source_file, dest_file)

            # Calculate checksum
            checksum = calculate_file_checksum(str(dest_file))

            # Create library instruction
            lib_inst = LibraryInstruction(
                id=f"{repo_namespace}/{instruction.name}",
                name=instruction.name,
                description=instruction.description,
                repo_namespace=repo_namespace,
                repo_url=repo,
                repo_name=repo_name,
                author=repository.metadata.get("author", "Unknown"),
                version=repository.metadata.get("version", "1.0.0"),
                file_path=str(dest_file),
                tags=instruction.tags,
                downloaded_at=datetime.now(),
                checksum=checksum,
            )
            library_instructions.append(lib_inst)

            console.print(f"  ✓ {instruction.name}")

        # Preserve .git directory for Git sources to enable updates
        if not is_local:
            git_dir = repo_path / ".git"
            if git_dir.exists():
                dest_git_dir = library_repo_dir / ".git"
                if dest_git_dir.exists():
                    shutil.rmtree(dest_git_dir)
                shutil.copytree(git_dir, dest_git_dir)

        # Add to library
        library_repo = library.add_repository(
            repo_name=repo_name,
            repo_description=repository.metadata.get("description", ""),
            repo_url=repo,
            repo_author=repository.metadata.get("author", "Unknown"),
            repo_version=repository.metadata.get("version", "1.0.0"),
            instructions=library_instructions,
            alias=alias,
            namespace=repo_namespace,
        )

        # Build success message
        success_msg = f"\n✓ Downloaded {len(library_instructions)} instruction(s) from '{repo_name}'"
        if ref and ref_type:
            ref_type_badge = {"tag": "📌", "branch": "🌿", "commit": "📍"}.get(ref_type.value, "")
            success_msg += f" {ref_type_badge} {ref}"
        success_msg += f"\n  Alias: {library_repo.alias}\n" f"  Namespace: {repo_namespace}\n"
        if ref:
            ref_labels = {"tag": "Tag", "branch": "Branch", "commit": "Commit"}
            ref_label = ref_labels.get(ref_type.value if ref_type else "", "Ref")
            success_msg += f"  {ref_label}: {ref}\n"
        success_msg += (
            "  Use 'devsync list library' to see all downloaded instructions\n"
            "  Use 'devsync install' to install into your AI tools"
        )
        print_success(success_msg)

        return 0

    except FileNotFoundError as e:
        print_error(f"Repository metadata file not found: {e}")
        return 1
    except Exception as e:
        print_error(f"Failed to download: {e}")
        return 1
    finally:
        # Clean up temp directory if not local
        if temp_repo_path and not is_local:
            GitOperations.cleanup_repository(temp_repo_path, is_temp=True)


@app.command(name="download")
def download_command(
    repo: str = typer.Option(
        ...,
        "--repo",
        "-r",
        help="Repository URL or local path to download from",
    ),
    ref: Optional[str] = typer.Option(
        None,
        "--ref",
        help="Git reference (tag, branch, or commit) to download",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Re-download even if already in library",
    ),
) -> None:
    """
    Download instructions from a repository into your local library.

    This downloads and caches instructions locally without installing them.
    After downloading, use 'devsync install' to select and install
    instructions into your AI coding tools.

    Examples:
        # Download from GitHub (default branch)
        devsync download --repo https://github.com/company/instructions

        # Download specific tag version
        devsync download --repo https://github.com/company/instructions --ref v1.0.0

        # Download from specific branch
        devsync download --repo https://github.com/company/instructions --ref main

        # Download from specific commit
        devsync download --repo https://github.com/company/instructions --ref abc123def

        # Download from local folder (no --ref support)
        devsync download --repo ./my-instructions

        # Force re-download
        devsync download --repo https://github.com/company/instructions --force
    """
    exit_code = download_instructions(repo=repo, ref=ref, force=force)
    raise typer.Exit(code=exit_code)
