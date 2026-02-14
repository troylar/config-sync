"""Git operations for cloning and managing instruction repositories."""

import re
import shutil
import subprocess
import tempfile
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any, Iterator, Optional

import git
from git import Repo
from git.exc import GitCommandError

from aiconfigkit.core.models import RefType
from aiconfigkit.utils.validation import is_valid_git_url


class GitOperationError(Exception):
    """Raised when a Git operation fails."""

    pass


class RepositoryOperationError(Exception):
    """Custom exception for repository operations with detailed error information."""

    def __init__(self, message: str, error_type: str, original_error: Optional[Exception] = None):
        """
        Initialize repository operation error.

        Args:
            message: Human-readable error message
            error_type: Error category (e.g., 'network_error', 'invalid_reference')
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error


class GitOperations:
    """Handle Git repository operations."""

    @staticmethod
    def is_local_path(repo_url: str) -> bool:
        """
        Check if the repository URL is a local file path.

        Args:
            repo_url: Repository URL or path

        Returns:
            True if it's a local path, False if it's a remote Git URL
        """
        # Remote URLs have protocols or SSH format
        if repo_url.startswith(("https://", "http://", "git://", "ssh://")):
            return False

        # SSH format (git@host:path)
        if "@" in repo_url and ":" in repo_url and not repo_url.startswith("/"):
            return False

        # Everything else is treated as a local path
        return True

    @staticmethod
    def clone_repository(
        repo_url: str, target_dir: Optional[Path] = None, branch: Optional[str] = None, depth: int = 1
    ) -> Path:
        """
        Clone a Git repository or use a local directory.

        Args:
            repo_url: URL of Git repository to clone or path to local directory
            target_dir: Directory to clone into (creates temp dir if None)
            branch: Specific branch to clone (defaults to default branch)
            depth: Clone depth (1 for shallow clone)

        Returns:
            Path to repository

        Raises:
            GitOperationError: If clone fails
            ValueError: If repo_url is invalid
        """
        # Validate URL
        if not is_valid_git_url(repo_url):
            raise ValueError(f"Invalid Git repository URL: {repo_url}")

        # Handle local directories
        if GitOperations.is_local_path(repo_url):
            local_path = Path(repo_url).resolve()
            if not local_path.exists():
                raise GitOperationError(f"Local directory does not exist: {local_path}")
            if not local_path.is_dir():
                raise GitOperationError(f"Path is not a directory: {local_path}")
            return local_path

        # Create target directory if not provided
        if target_dir is None:
            target_dir = Path(tempfile.mkdtemp(prefix="devsync-"))
        else:
            target_dir.mkdir(parents=True, exist_ok=True)

        # Build git clone command
        cmd = ["git", "clone"]

        # Add depth for shallow clone
        if depth > 0:
            cmd.extend(["--depth", str(depth)])

        # Add branch if specified
        if branch:
            cmd.extend(["--branch", branch])

        # Add URL and target directory
        cmd.extend([repo_url, str(target_dir)])

        try:
            # Execute git clone
            subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=300)  # 5 minute timeout

            return target_dir

        except subprocess.CalledProcessError as e:
            # Clean up target directory on failure
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)

            error_msg = e.stderr if e.stderr else str(e)
            raise GitOperationError(f"Failed to clone repository: {error_msg}")

        except subprocess.TimeoutExpired:
            # Clean up on timeout
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)

            raise GitOperationError("Repository clone timed out after 5 minutes")

        except Exception as e:
            # Clean up on any other error
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)

            raise GitOperationError(f"Unexpected error during clone: {str(e)}")

    @staticmethod
    def is_git_installed() -> bool:
        """
        Check if Git is installed and accessible.

        Returns:
            True if git command is available
        """
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @staticmethod
    def get_git_version() -> Optional[str]:
        """
        Get installed Git version.

        Returns:
            Git version string or None if not installed
        """
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Output format: "git version 2.x.x"
                return result.stdout.strip()
            return None
        except (subprocess.SubprocessError, FileNotFoundError):
            return None

    @staticmethod
    def cleanup_repository(repo_path: Path, is_temp: bool = True) -> None:
        """
        Clean up a cloned repository directory.

        Args:
            repo_path: Path to repository to clean up
            is_temp: Whether this is a temporary directory (safe to delete)
        """
        # Only delete if it's a temporary directory
        if is_temp and repo_path.exists() and repo_path.is_dir():
            # Safety check: only delete if it's in temp directory
            if "devsync-" in str(repo_path) or "/tmp/" in str(repo_path):
                shutil.rmtree(repo_path, ignore_errors=True)

    @staticmethod
    def detect_ref_type(repo_url: str, ref: Optional[str]) -> tuple[Optional[str], RefType]:
        """
        Detect and validate reference type for a remote repository.

        Args:
            repo_url: Git repository URL
            ref: Reference to check (None = default branch)

        Returns:
            Tuple of (validated_ref, ref_type)

        Raises:
            RepositoryOperationError: If reference validation fails
        """
        if ref is None:
            # Use default branch
            return (None, RefType.BRANCH)

        # Check if it looks like a commit hash (40-char hex or 7+ char hex)
        if re.match(r"^[0-9a-f]{7,40}$", ref.lower()):
            return (ref, RefType.COMMIT)

        # Check remote refs via ls-remote
        g = git.cmd.Git()
        try:
            remote_refs = {}
            for line in g.ls_remote(repo_url).split("\n"):
                if line and "\t" in line:
                    hash_ref = line.split("\t")
                    remote_refs[hash_ref[1]] = hash_ref[0]

            # Priority: tags > branches (Git's default behavior)
            tag_ref = f"refs/tags/{ref}"
            if tag_ref in remote_refs:
                return (ref, RefType.TAG)

            branch_ref = f"refs/heads/{ref}"
            if branch_ref in remote_refs:
                return (ref, RefType.BRANCH)

            raise RepositoryOperationError(f"Reference '{ref}' not found in repository", error_type="invalid_reference")

        except GitCommandError as e:
            raise RepositoryOperationError(
                f"Failed to access repository: {e}", error_type="network_error", original_error=e
            )

    @staticmethod
    def validate_remote_ref(repo_url: str, ref: str, ref_type: RefType) -> bool:
        """
        Validate that a specific reference exists on remote repository.

        Args:
            repo_url: Git repository URL
            ref: Reference name
            ref_type: Expected reference type ('tag' or 'branch')

        Returns:
            True if reference exists, False otherwise

        Raises:
            RepositoryOperationError: If validation fails due to network/access issues
        """
        g = git.cmd.Git()

        try:
            if ref_type == RefType.BRANCH:
                # Check for branch (heads)
                g.ls_remote("--exit-code", "--heads", repo_url, ref)
            elif ref_type == RefType.TAG:
                # Check for tag
                g.ls_remote("--exit-code", "--tags", repo_url, ref)
            elif ref_type == RefType.COMMIT:
                # Commits can't be validated via ls-remote
                # Will be validated during fetch/checkout
                return True
            return True
        except GitCommandError as e:
            # exit-code 2 means reference not found
            if e.status == 2:
                return False
            # Other errors are network/access issues
            raise RepositoryOperationError(
                f"Failed to validate reference: {e}", error_type="network_error", original_error=e
            )

    @staticmethod
    def clone_at_ref(
        repo_url: str, destination: Path, ref: Optional[str] = None, ref_type: Optional[RefType] = None, depth: int = 1
    ) -> Repo:
        """
        Clone repository at a specific reference.

        Args:
            repo_url: Git repository URL
            destination: Local directory to clone into
            ref: Reference to clone (tag, branch, or commit hash)
            ref_type: Type of reference (if known)
            depth: Clone depth (1 for shallow, 0 for full)

        Returns:
            GitPython Repo object

        Raises:
            RepositoryOperationError: If clone fails
        """
        # Create destination directory
        destination.mkdir(parents=True, exist_ok=True)

        # Handle default branch (no ref specified)
        if ref is None:
            try:
                return Repo.clone_from(url=repo_url, to_path=str(destination), depth=depth if depth > 0 else None)
            except GitCommandError as e:
                raise RepositoryOperationError(
                    f"Failed to clone repository: {e.stderr}", error_type="git_command_error", original_error=e
                )

        # Handle tags and branches (can use 'branch' parameter)
        if ref_type in (RefType.TAG, RefType.BRANCH, None):
            try:
                return Repo.clone_from(
                    url=repo_url,
                    to_path=str(destination),
                    branch=ref,
                    single_branch=True,
                    depth=depth if depth > 0 else None,
                )
            except GitCommandError as e:
                # If branch parameter fails and we haven't confirmed it's a commit, raise error
                if ref_type != RefType.COMMIT:
                    stderr = e.stderr.lower() if e.stderr else ""
                    if "remote branch" in stderr and "not found" in stderr:
                        raise RepositoryOperationError(
                            f"Reference '{ref}' not found in repository",
                            error_type="invalid_reference",
                            original_error=e,
                        )
                    raise RepositoryOperationError(
                        f"Failed to clone at ref '{ref}': {e.stderr}",
                        error_type="git_command_error",
                        original_error=e,
                    )

        # Handle commits (requires two-step process)
        if ref_type == RefType.COMMIT:
            try:
                # Step 1: Shallow clone default branch
                repo = Repo.clone_from(url=repo_url, to_path=str(destination), depth=depth if depth > 0 else None)

                # Step 2: Fetch and checkout specific commit
                try:
                    # Try shallow fetch first (requires server support)
                    repo.git.fetch("origin", ref, depth=1)
                    repo.git.checkout(ref)
                except GitCommandError:
                    # Fall back to full fetch if shallow fails
                    repo.git.fetch("origin", ref)
                    repo.git.checkout(ref)

                return repo

            except GitCommandError as e:
                raise RepositoryOperationError(
                    f"Failed to clone at commit '{ref}': {e.stderr}",
                    error_type="git_command_error",
                    original_error=e,
                )

        raise RepositoryOperationError(f"Unable to clone at ref '{ref}'", error_type="unknown_error")

    @staticmethod
    def get_repo_info(repo: Repo) -> dict[str, Any]:
        """
        Extract useful repository information.

        Args:
            repo: GitPython Repo object

        Returns:
            Dictionary with repository metadata
        """
        try:
            current_branch = repo.active_branch.name if not repo.head.is_detached else None
        except Exception:
            current_branch = None

        return {
            "url": repo.remotes.origin.url if repo.remotes else None,
            "current_branch": current_branch,
            "current_commit": repo.head.commit.hexsha,
            "is_dirty": repo.is_dirty(),
            "is_shallow": repo.git.rev_parse("--is-shallow-repository") == "true",
            "tags": [tag.name for tag in repo.tags],
            "branches": [branch.name for branch in repo.heads],
        }

    @staticmethod
    def check_for_updates(repo: Repo, branch: str = "main") -> bool:
        """
        Check if remote branch has new commits without pulling.

        Args:
            repo: GitPython Repo object
            branch: Branch name to check

        Returns:
            True if remote has updates, False otherwise

        Raises:
            RepositoryOperationError: If check fails
        """
        try:
            # Get current local commit
            local_commit = repo.head.commit.hexsha

            # Fetch remote refs (doesn't modify working tree)
            origin = repo.remotes.origin
            origin.fetch()

            # Get remote commit
            remote_commit = origin.refs[branch].commit.hexsha

            # Compare
            return local_commit != remote_commit
        except Exception as e:
            raise RepositoryOperationError(
                f"Failed to check for updates: {e}", error_type="network_error", original_error=e
            )

    @staticmethod
    def pull_repository_updates(repo: Repo, branch: str = "main") -> dict[str, Any]:
        """
        Pull updates with conflict detection.

        Args:
            repo: GitPython Repo object
            branch: Branch to pull

        Returns:
            Dictionary with pull result details

        Raises:
            RepositoryOperationError: If pull fails
        """
        try:
            origin = repo.remotes.origin

            # Check for local modifications
            if repo.is_dirty():
                return {
                    "success": False,
                    "error": "local_modifications",
                    "message": "Working directory has uncommitted changes",
                }

            # Pull
            pull_info = origin.pull(branch)

            # Check if any files were updated
            updated_files = []
            for info in pull_info:
                if info.flags & info.HEAD_UPTODATE:
                    # Already up to date
                    continue
                updated_files.append(str(info.ref))

            return {"success": True, "updated": len(updated_files) > 0, "files": updated_files}

        except GitCommandError as e:
            # Pull failed - likely due to conflicts
            stderr = e.stderr if e.stderr else ""
            if "CONFLICT" in stderr:
                return {"success": False, "error": "conflict", "message": str(e.stderr)}
            else:
                return {"success": False, "error": "unknown", "message": str(e)}

    @staticmethod
    def update_if_mutable(repo_path: Path, ref: str, ref_type: RefType) -> bool:
        """
        Update repository only if reference is mutable (branch).

        Args:
            repo_path: Path to repository
            ref: Reference name
            ref_type: Type of reference

        Returns:
            True if updated, False if skipped (immutable ref)

        Raises:
            RepositoryOperationError: If update fails
        """
        # Only update branches (mutable refs)
        if ref_type != RefType.BRANCH:
            return False

        try:
            repo = Repo(repo_path)

            # Check if updates available
            if not GitOperations.check_for_updates(repo, ref):
                return False

            # Pull updates
            result = GitOperations.pull_repository_updates(repo, ref)

            return bool(result.get("success", False) and result.get("updated", False))
        except Exception as e:
            raise RepositoryOperationError(
                f"Failed to update repository: {e}", error_type="git_error", original_error=e
            )


def with_temporary_clone(repo_url: str, branch: Optional[str] = None) -> AbstractContextManager[Path]:
    """
    Context manager for temporary repository clones.

    Usage:
        with with_temporary_clone(repo_url) as repo_path:
            # Use repo_path
            pass
        # Repository is automatically cleaned up

    Args:
        repo_url: URL of repository to clone
        branch: Optional branch to clone

    Yields:
        Path to cloned repository
    """
    from contextlib import contextmanager

    @contextmanager
    def _clone_context() -> Iterator[Path]:
        repo_path = None
        try:
            git_ops = GitOperations()
            repo_path = git_ops.clone_repository(repo_url, branch=branch)
            yield repo_path
        finally:
            if repo_path and repo_path.exists():
                GitOperations.cleanup_repository(repo_path)

    return _clone_context()
