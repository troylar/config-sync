"""Tests for v2 list command."""

from unittest.mock import MagicMock, patch

from devsync.cli.list_v2 import list_v2_command


class TestListV2Command:
    @patch("devsync.cli.list_v2.find_project_root", return_value=None)
    @patch("devsync.cli.list_v2.PackageTracker")
    def test_no_packages(self, mock_tracker_cls: MagicMock, mock_root: MagicMock) -> None:
        mock_tracker_cls.return_value.get_installed_packages.return_value = []
        result = list_v2_command()
        assert result == 0

    @patch("devsync.cli.list_v2.find_project_root", return_value=None)
    @patch("devsync.cli.list_v2.PackageTracker")
    def test_no_packages_json(self, mock_tracker_cls: MagicMock, mock_root: MagicMock) -> None:
        mock_tracker_cls.return_value.get_installed_packages.return_value = []
        result = list_v2_command(json=True)
        assert result == 0

    @patch("devsync.cli.list_v2.find_project_root", return_value=None)
    @patch("devsync.cli.list_v2.PackageTracker")
    def test_with_packages(self, mock_tracker_cls: MagicMock, mock_root: MagicMock) -> None:
        mock_pkg = MagicMock()
        mock_pkg.name = "test-pkg"
        mock_pkg.version = "1.0.0"
        mock_pkg.components = []
        mock_pkg.status = "COMPLETE"
        mock_tracker_cls.return_value.get_installed_packages.return_value = [mock_pkg]

        result = list_v2_command()
        assert result == 0

    @patch("devsync.cli.list_v2.find_project_root", return_value=None)
    @patch("devsync.cli.list_v2.PackageTracker")
    def test_tracker_exception(self, mock_tracker_cls: MagicMock, mock_root: MagicMock) -> None:
        mock_tracker_cls.return_value.get_installed_packages.side_effect = Exception("No file")
        result = list_v2_command()
        assert result == 0
