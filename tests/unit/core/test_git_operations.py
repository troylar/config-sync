"""Unit tests for git_operations module."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
from git import Repo
from git.exc import GitCommandError

from aiconfigkit.core.git_operations import (
    GitOperationError,
    GitOperations,
    RepositoryOperationError,
    with_temporary_clone,
)
from aiconfigkit.core.models import RefType


class TestGitOperationError:
    """Test GitOperationError exception."""

    def test_exception_creation(self) -> None:
        """Test creating GitOperationError."""
        error = GitOperationError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)


class TestRepositoryOperationError:
    """Test RepositoryOperationError exception."""

    def test_exception_with_type(self) -> None:
        """Test creating RepositoryOperationError with error type."""
        error = RepositoryOperationError("Test error", "network_error")
        assert str(error) == "Test error"
        assert error.error_type == "network_error"
        assert error.original_error is None

    def test_exception_with_original_error(self) -> None:
        """Test RepositoryOperationError with original exception."""
        original = ValueError("Original error")
        error = RepositoryOperationError("Test error", "invalid_reference", original)
        assert str(error) == "Test error"
        assert error.error_type == "invalid_reference"
        assert error.original_error == original


class TestIsLocalPath:
    """Test is_local_path static method."""

    def test_https_url(self) -> None:
        """Test HTTPS URL is not local."""
        assert GitOperations.is_local_path("https://github.com/user/repo.git") is False

    def test_http_url(self) -> None:
        """Test HTTP URL is not local."""
        assert GitOperations.is_local_path("http://github.com/user/repo.git") is False

    def test_git_protocol_url(self) -> None:
        """Test git:// protocol URL is not local."""
        assert GitOperations.is_local_path("git://github.com/user/repo.git") is False

    def test_ssh_protocol_url(self) -> None:
        """Test ssh:// protocol URL is not local."""
        assert GitOperations.is_local_path("ssh://git@github.com/user/repo.git") is False

    def test_ssh_format_url(self) -> None:
        """Test SSH format (git@host:path) is not local."""
        assert GitOperations.is_local_path("git@github.com:user/repo.git") is False

    def test_absolute_local_path(self) -> None:
        """Test absolute local path is local."""
        assert GitOperations.is_local_path("/home/user/repos/project") is True

    def test_relative_local_path(self) -> None:
        """Test relative local path is local."""
        assert GitOperations.is_local_path("./repos/project") is True

    def test_simple_directory_name(self) -> None:
        """Test simple directory name is local."""
        assert GitOperations.is_local_path("my-repo") is True


class TestIsGitInstalled:
    """Test is_git_installed static method."""

    @patch("subprocess.run")
    def test_git_is_installed(self, mock_run: MagicMock) -> None:
        """Test when Git is installed."""
        mock_run.return_value = Mock(returncode=0)
        assert GitOperations.is_git_installed() is True
        mock_run.assert_called_once_with(["git", "--version"], capture_output=True, timeout=5)

    @patch("subprocess.run")
    def test_git_not_installed(self, mock_run: MagicMock) -> None:
        """Test when Git is not installed."""
        mock_run.return_value = Mock(returncode=1)
        assert GitOperations.is_git_installed() is False

    @patch("subprocess.run")
    def test_git_command_not_found(self, mock_run: MagicMock) -> None:
        """Test when git command not found."""
        mock_run.side_effect = FileNotFoundError()
        assert GitOperations.is_git_installed() is False

    @patch("subprocess.run")
    def test_subprocess_error(self, mock_run: MagicMock) -> None:
        """Test when subprocess error occurs."""
        mock_run.side_effect = subprocess.SubprocessError()
        assert GitOperations.is_git_installed() is False


class TestGetGitVersion:
    """Test get_git_version static method."""

    @patch("subprocess.run")
    def test_get_version_success(self, mock_run: MagicMock) -> None:
        """Test getting Git version successfully."""
        mock_run.return_value = Mock(returncode=0, stdout="git version 2.39.0\n")
        version = GitOperations.get_git_version()
        assert version == "git version 2.39.0"

    @patch("subprocess.run")
    def test_get_version_failure(self, mock_run: MagicMock) -> None:
        """Test when Git version check fails."""
        mock_run.return_value = Mock(returncode=1, stdout="")
        version = GitOperations.get_git_version()
        assert version is None

    @patch("subprocess.run")
    def test_get_version_not_found(self, mock_run: MagicMock) -> None:
        """Test when git command not found."""
        mock_run.side_effect = FileNotFoundError()
        version = GitOperations.get_git_version()
        assert version is None


class TestCleanupRepository:
    """Test cleanup_repository static method."""

    def test_cleanup_temp_directory(self, tmp_path: Path) -> None:
        """Test cleaning up temporary directory."""
        temp_dir = tmp_path / "devsync-abc123"
        temp_dir.mkdir()
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        GitOperations.cleanup_repository(temp_dir, is_temp=True)

        assert not temp_dir.exists()

    def test_cleanup_non_temp_directory_skipped(self, tmp_path: Path) -> None:
        """Test that non-temp directories outside /tmp are not cleaned up."""
        # Create a directory outside /tmp that doesn't match temp patterns
        from unittest.mock import patch

        # Mock a path that's not in /tmp and doesn't have instructionkit- prefix
        regular_dir = Path("/home/user/my-repo")

        # Mock exists() and is_dir() to return True
        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "is_dir", return_value=True),
            patch("shutil.rmtree") as mock_rmtree,
        ):

            GitOperations.cleanup_repository(regular_dir, is_temp=True)

            # Should NOT call rmtree because path doesn't match temp patterns
            mock_rmtree.assert_not_called()

    def test_cleanup_non_temp_flag(self, tmp_path: Path) -> None:
        """Test cleanup with is_temp=False doesn't delete."""
        temp_dir = tmp_path / "devsync-abc123"
        temp_dir.mkdir()
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        GitOperations.cleanup_repository(temp_dir, is_temp=False)

        # Should not be deleted because is_temp=False
        assert temp_dir.exists()

    def test_cleanup_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test cleanup of nonexistent directory doesn't raise error."""
        nonexistent = tmp_path / "does-not-exist"
        GitOperations.cleanup_repository(nonexistent, is_temp=True)
        # Should not raise error


class TestCloneRepository:
    """Test clone_repository static method."""

    @patch("aiconfigkit.core.git_operations.is_valid_git_url", return_value=False)
    def test_clone_invalid_url(self, mock_valid: MagicMock) -> None:
        """Test cloning with invalid URL raises error."""
        with pytest.raises(ValueError, match="Invalid Git repository URL"):
            GitOperations.clone_repository("invalid-url")

    @patch("aiconfigkit.utils.validation.is_valid_git_url")
    def test_clone_local_path_exists(self, mock_valid: MagicMock, tmp_path: Path) -> None:
        """Test cloning local path that exists."""
        mock_valid.return_value = True
        local_dir = tmp_path / "local-repo"
        local_dir.mkdir()

        result = GitOperations.clone_repository(str(local_dir))

        assert result == local_dir.resolve()

    @patch("aiconfigkit.utils.validation.is_valid_git_url")
    def test_clone_local_path_not_exists(self, mock_valid: MagicMock, tmp_path: Path) -> None:
        """Test cloning local path that doesn't exist."""
        mock_valid.return_value = True
        local_dir = tmp_path / "nonexistent"

        with pytest.raises(GitOperationError, match="Local directory does not exist"):
            GitOperations.clone_repository(str(local_dir))

    @patch("aiconfigkit.utils.validation.is_valid_git_url")
    def test_clone_local_path_not_directory(self, mock_valid: MagicMock, tmp_path: Path) -> None:
        """Test cloning local path that is a file."""
        mock_valid.return_value = True
        local_file = tmp_path / "file.txt"
        local_file.write_text("test")

        with pytest.raises(GitOperationError, match="Path is not a directory"):
            GitOperations.clone_repository(str(local_file))

    @patch("subprocess.run")
    @patch("aiconfigkit.utils.validation.is_valid_git_url")
    def test_clone_remote_success(self, mock_valid: MagicMock, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test successful remote clone."""
        mock_valid.return_value = True
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="")

        target_dir = tmp_path / "target"
        result = GitOperations.clone_repository("https://github.com/user/repo.git", target_dir=target_dir)

        assert result == target_dir
        assert target_dir.exists()
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[:2] == ["git", "clone"]
        assert "https://github.com/user/repo.git" in cmd

    @patch("subprocess.run")
    @patch("aiconfigkit.utils.validation.is_valid_git_url")
    def test_clone_with_branch(self, mock_valid: MagicMock, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test cloning with specific branch."""
        mock_valid.return_value = True
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="")

        target_dir = tmp_path / "target"
        GitOperations.clone_repository("https://github.com/user/repo.git", target_dir=target_dir, branch="develop")

        cmd = mock_run.call_args[0][0]
        assert "--branch" in cmd
        assert "develop" in cmd

    @patch("subprocess.run")
    @patch("aiconfigkit.utils.validation.is_valid_git_url")
    def test_clone_with_depth(self, mock_valid: MagicMock, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test cloning with depth."""
        mock_valid.return_value = True
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="")

        target_dir = tmp_path / "target"
        GitOperations.clone_repository("https://github.com/user/repo.git", target_dir=target_dir, depth=5)

        cmd = mock_run.call_args[0][0]
        assert "--depth" in cmd
        assert "5" in cmd

    @patch("subprocess.run")
    @patch("shutil.rmtree")
    @patch("aiconfigkit.utils.validation.is_valid_git_url")
    def test_clone_failure_cleanup(
        self, mock_valid: MagicMock, mock_rmtree: MagicMock, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        """Test that failed clone cleans up target directory."""
        mock_valid.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="Clone failed")

        target_dir = tmp_path / "target"
        target_dir.mkdir()

        with pytest.raises(GitOperationError, match="Failed to clone repository"):
            GitOperations.clone_repository("https://github.com/user/repo.git", target_dir=target_dir)

    @patch("subprocess.run")
    @patch("shutil.rmtree")
    @patch("aiconfigkit.utils.validation.is_valid_git_url")
    def test_clone_timeout_cleanup(
        self, mock_valid: MagicMock, mock_rmtree: MagicMock, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        """Test that timed out clone cleans up."""
        mock_valid.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired("git", 300)

        target_dir = tmp_path / "target"
        target_dir.mkdir()

        with pytest.raises(GitOperationError, match="Repository clone timed out"):
            GitOperations.clone_repository("https://github.com/user/repo.git", target_dir=target_dir)


class TestDetectRefType:
    """Test detect_ref_type static method."""

    def test_detect_none_ref(self) -> None:
        """Test detecting None ref (default branch)."""
        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo.git", None)
        assert ref is None
        assert ref_type == RefType.BRANCH

    def test_detect_commit_40_chars(self) -> None:
        """Test detecting 40-char commit hash."""
        commit = "a" * 40
        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo.git", commit)
        assert ref == commit
        assert ref_type == RefType.COMMIT

    def test_detect_commit_7_chars(self) -> None:
        """Test detecting 7-char commit hash."""
        commit = "abc1234"
        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo.git", commit)
        assert ref == commit
        assert ref_type == RefType.COMMIT

    @patch("git.cmd.Git")
    def test_detect_tag(self, mock_git_cls: MagicMock) -> None:
        """Test detecting tag reference."""
        mock_git = MagicMock()
        mock_git.ls_remote.return_value = "abc123\trefs/tags/v1.0.0\n"
        mock_git_cls.return_value = mock_git

        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo.git", "v1.0.0")
        assert ref == "v1.0.0"
        assert ref_type == RefType.TAG

    @patch("git.cmd.Git")
    def test_detect_branch(self, mock_git_cls: MagicMock) -> None:
        """Test detecting branch reference."""
        mock_git = MagicMock()
        mock_git.ls_remote.return_value = "abc123\trefs/heads/main\n"
        mock_git_cls.return_value = mock_git

        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo.git", "main")
        assert ref == "main"
        assert ref_type == RefType.BRANCH

    @patch("git.cmd.Git")
    def test_detect_tag_priority_over_branch(self, mock_git_cls: MagicMock) -> None:
        """Test that tags have priority over branches."""
        mock_git = MagicMock()
        # Both tag and branch with same name
        mock_git.ls_remote.return_value = "abc123\trefs/tags/release\ndef456\trefs/heads/release\n"
        mock_git_cls.return_value = mock_git

        ref, ref_type = GitOperations.detect_ref_type("https://github.com/user/repo.git", "release")
        assert ref == "release"
        assert ref_type == RefType.TAG  # Tag has priority

    @patch("git.cmd.Git")
    def test_detect_invalid_ref(self, mock_git_cls: MagicMock) -> None:
        """Test detecting invalid reference raises error."""
        mock_git = MagicMock()
        mock_git.ls_remote.return_value = "abc123\trefs/heads/main\n"
        mock_git_cls.return_value = mock_git

        with pytest.raises(RepositoryOperationError, match="Reference 'nonexistent' not found"):
            GitOperations.detect_ref_type("https://github.com/user/repo.git", "nonexistent")

    @patch("git.cmd.Git")
    def test_detect_network_error(self, mock_git_cls: MagicMock) -> None:
        """Test detecting ref with network error."""
        mock_git = MagicMock()
        mock_git.ls_remote.side_effect = GitCommandError("ls-remote", 128, stderr="Network error")
        mock_git_cls.return_value = mock_git

        with pytest.raises(RepositoryOperationError, match="Failed to access repository"):
            GitOperations.detect_ref_type("https://github.com/user/repo.git", "main")


class TestValidateRemoteRef:
    """Test validate_remote_ref static method."""

    @patch("git.cmd.Git")
    def test_validate_branch_exists(self, mock_git_cls: MagicMock) -> None:
        """Test validating existing branch."""
        mock_git = MagicMock()
        mock_git.ls_remote.return_value = ""
        mock_git_cls.return_value = mock_git

        result = GitOperations.validate_remote_ref("https://github.com/user/repo.git", "main", RefType.BRANCH)
        assert result is True
        mock_git.ls_remote.assert_called_once_with("--exit-code", "--heads", "https://github.com/user/repo.git", "main")

    @patch("git.cmd.Git")
    def test_validate_tag_exists(self, mock_git_cls: MagicMock) -> None:
        """Test validating existing tag."""
        mock_git = MagicMock()
        mock_git.ls_remote.return_value = ""
        mock_git_cls.return_value = mock_git

        result = GitOperations.validate_remote_ref("https://github.com/user/repo.git", "v1.0.0", RefType.TAG)
        assert result is True
        mock_git.ls_remote.assert_called_once_with(
            "--exit-code", "--tags", "https://github.com/user/repo.git", "v1.0.0"
        )

    @patch("git.cmd.Git")
    def test_validate_commit_always_true(self, mock_git_cls: MagicMock) -> None:
        """Test validating commit always returns True."""
        mock_git = MagicMock()
        mock_git_cls.return_value = mock_git

        result = GitOperations.validate_remote_ref("https://github.com/user/repo.git", "abc123", RefType.COMMIT)
        assert result is True
        # ls-remote should not be called for commits
        mock_git.ls_remote.assert_not_called()

    @patch("git.cmd.Git")
    def test_validate_ref_not_found(self, mock_git_cls: MagicMock) -> None:
        """Test validating non-existent ref."""
        mock_git = MagicMock()
        error = GitCommandError("ls-remote", 2, stderr="Not found")
        error.status = 2
        mock_git.ls_remote.side_effect = error
        mock_git_cls.return_value = mock_git

        result = GitOperations.validate_remote_ref("https://github.com/user/repo.git", "nonexistent", RefType.BRANCH)
        assert result is False

    @patch("git.cmd.Git")
    def test_validate_network_error(self, mock_git_cls: MagicMock) -> None:
        """Test validation with network error."""
        mock_git = MagicMock()
        error = GitCommandError("ls-remote", 128, stderr="Network error")
        error.status = 128
        mock_git.ls_remote.side_effect = error
        mock_git_cls.return_value = mock_git

        with pytest.raises(RepositoryOperationError, match="Failed to validate reference"):
            GitOperations.validate_remote_ref("https://github.com/user/repo.git", "main", RefType.BRANCH)


class TestGetRepoInfo:
    """Test get_repo_info static method."""

    def test_get_repo_info_normal_branch(self) -> None:
        """Test getting repo info for normal branch checkout."""
        mock_repo = MagicMock(spec=Repo)
        mock_repo.head.is_detached = False
        mock_repo.active_branch.name = "main"
        mock_repo.head.commit.hexsha = "abc123"
        mock_repo.is_dirty.return_value = False
        mock_repo.git.rev_parse.return_value = "false"

        # Mock remotes properly - needs to be truthy and have origin attribute
        mock_origin = MagicMock()
        mock_origin.url = "https://github.com/user/repo.git"
        mock_repo.remotes = MagicMock()
        mock_repo.remotes.origin = mock_origin
        mock_repo.remotes.__bool__ = lambda self: True  # Make remotes truthy

        # Mock tags and heads
        tag1, tag2 = MagicMock(), MagicMock()
        tag1.name, tag2.name = "v1.0.0", "v1.1.0"
        branch1, branch2 = MagicMock(), MagicMock()
        branch1.name, branch2.name = "main", "develop"
        mock_repo.tags = [tag1, tag2]
        mock_repo.heads = [branch1, branch2]

        info = GitOperations.get_repo_info(mock_repo)

        assert info["url"] == "https://github.com/user/repo.git"
        assert info["current_branch"] == "main"
        assert info["current_commit"] == "abc123"
        assert info["is_dirty"] is False
        assert info["is_shallow"] is False
        assert info["tags"] == ["v1.0.0", "v1.1.0"]
        assert info["branches"] == ["main", "develop"]

    def test_get_repo_info_detached_head(self) -> None:
        """Test getting repo info for detached HEAD."""
        mock_repo = MagicMock(spec=Repo)
        mock_repo.head.is_detached = True
        mock_repo.head.commit.hexsha = "abc123"
        mock_repo.is_dirty.return_value = False
        mock_repo.git.rev_parse.return_value = "true"

        # Mock remotes properly
        mock_origin = MagicMock()
        mock_origin.url = "https://github.com/user/repo.git"
        mock_repo.remotes = MagicMock()
        mock_repo.remotes.origin = mock_origin
        mock_repo.remotes.__bool__ = lambda self: True

        # Mock tags and heads
        mock_repo.tags = []
        branch1 = MagicMock()
        branch1.name = "main"
        mock_repo.heads = [branch1]

        info = GitOperations.get_repo_info(mock_repo)

        assert info["current_branch"] is None  # Detached HEAD
        assert info["is_shallow"] is True

    def test_get_repo_info_no_remotes(self) -> None:
        """Test getting repo info with no remotes."""
        mock_repo = MagicMock(spec=Repo)
        mock_repo.head.is_detached = False
        mock_repo.active_branch.name = "main"
        mock_repo.head.commit.hexsha = "abc123"
        mock_repo.is_dirty.return_value = False
        mock_repo.git.rev_parse.return_value = "false"
        mock_repo.remotes = []
        mock_repo.tags = []
        mock_repo.heads = [MagicMock(name="main")]

        info = GitOperations.get_repo_info(mock_repo)

        assert info["url"] is None


class TestCheckForUpdates:
    """Test check_for_updates static method."""

    def test_check_updates_available(self) -> None:
        """Test checking when updates are available."""
        mock_repo = MagicMock(spec=Repo)
        mock_repo.head.commit.hexsha = "abc123"
        mock_origin = MagicMock()
        mock_origin.refs = {"main": MagicMock(commit=MagicMock(hexsha="def456"))}
        mock_repo.remotes.origin = mock_origin

        result = GitOperations.check_for_updates(mock_repo, "main")

        assert result is True
        mock_origin.fetch.assert_called_once()

    def test_check_no_updates(self) -> None:
        """Test checking when no updates available."""
        mock_repo = MagicMock(spec=Repo)
        mock_repo.head.commit.hexsha = "abc123"
        mock_origin = MagicMock()
        mock_origin.refs = {"main": MagicMock(commit=MagicMock(hexsha="abc123"))}
        mock_repo.remotes.origin = mock_origin

        result = GitOperations.check_for_updates(mock_repo, "main")

        assert result is False

    def test_check_updates_network_error(self) -> None:
        """Test checking for updates with network error."""
        mock_repo = MagicMock(spec=Repo)
        mock_origin = MagicMock()
        mock_origin.fetch.side_effect = Exception("Network error")
        mock_repo.remotes.origin = mock_origin

        with pytest.raises(RepositoryOperationError, match="Failed to check for updates"):
            GitOperations.check_for_updates(mock_repo, "main")


class TestPullRepositoryUpdates:
    """Test pull_repository_updates static method."""

    def test_pull_success_with_updates(self) -> None:
        """Test successful pull with updates."""
        mock_repo = MagicMock(spec=Repo)
        mock_repo.is_dirty.return_value = False
        mock_origin = MagicMock()

        # Mock pull info with updates
        mock_pull_info = MagicMock()
        mock_pull_info.flags = 0  # Not HEAD_UPTODATE
        mock_pull_info.HEAD_UPTODATE = 4
        mock_pull_info.ref = "refs/heads/main"
        mock_origin.pull.return_value = [mock_pull_info]
        mock_repo.remotes.origin = mock_origin

        result = GitOperations.pull_repository_updates(mock_repo, "main")

        assert result["success"] is True
        assert result["updated"] is True
        assert len(result["files"]) == 1

    def test_pull_already_up_to_date(self) -> None:
        """Test pull when already up to date."""
        mock_repo = MagicMock(spec=Repo)
        mock_repo.is_dirty.return_value = False
        mock_origin = MagicMock()

        # Mock pull info with HEAD_UPTODATE flag
        mock_pull_info = MagicMock()
        mock_pull_info.flags = 4  # HEAD_UPTODATE
        mock_pull_info.HEAD_UPTODATE = 4
        mock_origin.pull.return_value = [mock_pull_info]
        mock_repo.remotes.origin = mock_origin

        result = GitOperations.pull_repository_updates(mock_repo, "main")

        assert result["success"] is True
        assert result["updated"] is False
        assert len(result["files"]) == 0

    def test_pull_with_local_modifications(self) -> None:
        """Test pull with uncommitted local changes."""
        mock_repo = MagicMock(spec=Repo)
        mock_repo.is_dirty.return_value = True

        result = GitOperations.pull_repository_updates(mock_repo, "main")

        assert result["success"] is False
        assert result["error"] == "local_modifications"

    def test_pull_with_conflicts(self) -> None:
        """Test pull with merge conflicts."""
        mock_repo = MagicMock(spec=Repo)
        mock_repo.is_dirty.return_value = False
        mock_origin = MagicMock()
        mock_origin.pull.side_effect = GitCommandError("pull", stderr="CONFLICT (content): Merge conflict")
        mock_repo.remotes.origin = mock_origin

        result = GitOperations.pull_repository_updates(mock_repo, "main")

        assert result["success"] is False
        assert result["error"] == "conflict"

    def test_pull_with_unknown_error(self) -> None:
        """Test pull with unknown error."""
        mock_repo = MagicMock(spec=Repo)
        mock_repo.is_dirty.return_value = False
        mock_origin = MagicMock()
        mock_origin.pull.side_effect = GitCommandError("pull", stderr="Unknown error")
        mock_repo.remotes.origin = mock_origin

        result = GitOperations.pull_repository_updates(mock_repo, "main")

        assert result["success"] is False
        assert result["error"] == "unknown"


class TestUpdateIfMutable:
    """Test update_if_mutable static method."""

    def test_update_immutable_tag(self, tmp_path: Path) -> None:
        """Test update skipped for immutable tag."""
        result = GitOperations.update_if_mutable(tmp_path, "v1.0.0", RefType.TAG)
        assert result is False

    def test_update_immutable_commit(self, tmp_path: Path) -> None:
        """Test update skipped for immutable commit."""
        result = GitOperations.update_if_mutable(tmp_path, "abc123", RefType.COMMIT)
        assert result is False

    @patch.object(GitOperations, "check_for_updates")
    @patch("aiconfigkit.core.git_operations.Repo")
    def test_update_branch_no_updates(self, mock_repo_cls: MagicMock, mock_check: MagicMock, tmp_path: Path) -> None:
        """Test update branch with no updates available."""
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_check.return_value = False

        result = GitOperations.update_if_mutable(tmp_path, "main", RefType.BRANCH)

        assert result is False
        mock_repo_cls.assert_called_once_with(tmp_path)

    @patch.object(GitOperations, "pull_repository_updates")
    @patch.object(GitOperations, "check_for_updates")
    @patch("aiconfigkit.core.git_operations.Repo")
    def test_update_branch_with_updates(
        self, mock_repo_cls: MagicMock, mock_check: MagicMock, mock_pull: MagicMock, tmp_path: Path
    ) -> None:
        """Test successful update of branch."""
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_check.return_value = True
        mock_pull.return_value = {"success": True, "updated": True}

        result = GitOperations.update_if_mutable(tmp_path, "main", RefType.BRANCH)

        assert result is True

    @patch.object(GitOperations, "pull_repository_updates")
    @patch.object(GitOperations, "check_for_updates")
    @patch("aiconfigkit.core.git_operations.Repo")
    def test_update_branch_pull_failed(
        self, mock_repo_cls: MagicMock, mock_check: MagicMock, mock_pull: MagicMock, tmp_path: Path
    ) -> None:
        """Test update branch when pull fails."""
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_check.return_value = True
        mock_pull.return_value = {"success": False}

        result = GitOperations.update_if_mutable(tmp_path, "main", RefType.BRANCH)

        assert result is False


class TestWithTemporaryClone:
    """Test with_temporary_clone context manager."""

    @patch.object(GitOperations, "clone_repository")
    @patch.object(GitOperations, "cleanup_repository")
    def test_temporary_clone_success(self, mock_cleanup: MagicMock, mock_clone: MagicMock, tmp_path: Path) -> None:
        """Test successful temporary clone."""
        clone_path = tmp_path / "clone"
        clone_path.mkdir()
        mock_clone.return_value = clone_path

        with with_temporary_clone("https://github.com/user/repo.git") as repo_path:
            assert repo_path == clone_path

        mock_clone.assert_called_once()
        mock_cleanup.assert_called_once_with(clone_path)

    @patch.object(GitOperations, "clone_repository")
    @patch.object(GitOperations, "cleanup_repository")
    def test_temporary_clone_cleanup_on_error(
        self, mock_cleanup: MagicMock, mock_clone: MagicMock, tmp_path: Path
    ) -> None:
        """Test cleanup happens even on error."""
        clone_path = tmp_path / "clone"
        clone_path.mkdir()
        mock_clone.return_value = clone_path

        with pytest.raises(RuntimeError):
            with with_temporary_clone("https://github.com/user/repo.git") as _repo_path:
                raise RuntimeError("Test error")

        # Cleanup should still happen
        mock_cleanup.assert_called_once_with(clone_path)


class TestCloneRepositoryEdgeCases:
    """Test edge cases in clone_repository."""

    @patch("subprocess.run")
    @patch("aiconfigkit.utils.validation.is_valid_git_url")
    @patch("tempfile.mkdtemp")
    def test_clone_without_target_dir_creates_tempdir(
        self, mock_mkdtemp: MagicMock, mock_valid: MagicMock, mock_run: MagicMock
    ) -> None:
        """Test cloning without target_dir creates temporary directory."""
        mock_valid.return_value = True
        mock_mkdtemp.return_value = "/tmp/devsync-abc123"
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="")

        _result = GitOperations.clone_repository("https://github.com/user/repo.git")

        mock_mkdtemp.assert_called_once()
        assert "devsync-" in mock_mkdtemp.call_args[1]["prefix"]

    @patch("subprocess.run")
    @patch("shutil.rmtree")
    @patch("aiconfigkit.utils.validation.is_valid_git_url")
    def test_clone_generic_exception_cleanup(
        self, mock_valid: MagicMock, mock_rmtree: MagicMock, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        """Test that generic exception in clone triggers cleanup."""
        mock_valid.return_value = True
        mock_run.side_effect = Exception("Unexpected error")

        target_dir = tmp_path / "target"
        target_dir.mkdir()

        with pytest.raises(GitOperationError, match="Unexpected error during clone"):
            GitOperations.clone_repository("https://github.com/user/repo.git", target_dir=target_dir)


class TestGetRepoInfoEdgeCases:
    """Test edge cases in get_repo_info."""

    @patch("git.Repo")
    def test_get_repo_info_exception_getting_branch(self, mock_repo_class: MagicMock) -> None:
        """Test get_repo_info handles exception when getting active branch."""
        mock_repo = MagicMock()
        mock_repo.head.is_detached = False
        # Simulate exception when accessing active_branch property
        type(mock_repo).active_branch = PropertyMock(side_effect=Exception("Branch error"))
        mock_repo.remotes = []
        mock_repo.head.commit.hexsha = "abc123"
        mock_repo.is_dirty.return_value = False
        mock_repo.git.rev_parse.return_value = "false"
        mock_repo.tags = []
        mock_repo.heads = []

        info = GitOperations.get_repo_info(mock_repo)

        # Should handle exception gracefully, set current_branch to None
        assert info["current_branch"] is None
