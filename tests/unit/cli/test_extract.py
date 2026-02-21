"""Tests for extract CLI command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from devsync.cli.extract import _upgrade_v1_package, extract_command
from devsync.core.practice import PracticeDeclaration
from devsync.llm.response_models import ExtractionResult


class TestExtractCommand:
    def test_extract_invalid_path(self) -> None:
        result = extract_command(project_dir="/nonexistent/path")
        assert result == 1

    @patch("devsync.cli.extract.PracticeExtractor")
    @patch("devsync.cli.extract.load_config")
    def test_extract_no_ai(self, mock_config: MagicMock, mock_extractor_cls: MagicMock, tmp_path: Path) -> None:
        output_dir = tmp_path / "output"
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = ExtractionResult(
            practices=[PracticeDeclaration(name="test", intent="Test practice")],
            source_files=["rules/test.md"],
            ai_powered=False,
        )
        mock_extractor_cls.return_value = mock_extractor

        result = extract_command(
            output=str(output_dir),
            name="test-pkg",
            no_ai=True,
            project_dir=str(tmp_path),
        )

        assert result == 0
        manifest_path = output_dir / "devsync-package.yaml"
        assert manifest_path.exists()

        manifest = yaml.safe_load(manifest_path.read_text())
        assert manifest["name"] == "test-pkg"
        assert manifest["format_version"] == "2.0"

    @patch("devsync.cli.extract.resolve_provider", return_value=None)
    @patch("devsync.cli.extract.PracticeExtractor")
    @patch("devsync.cli.extract.load_config")
    def test_extract_no_api_key_fallback(
        self, mock_config: MagicMock, mock_extractor_cls: MagicMock, mock_resolve: MagicMock, tmp_path: Path
    ) -> None:
        output_dir = tmp_path / "output"
        mock_config.return_value = MagicMock(provider=None, model=None)
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = ExtractionResult(ai_powered=False)
        mock_extractor_cls.return_value = mock_extractor

        result = extract_command(output=str(output_dir), project_dir=str(tmp_path))

        assert result == 0
        mock_extractor_cls.assert_called_once_with(llm_provider=None)


class TestUpgradeV1Package:
    def test_upgrade_nonexistent_path(self) -> None:
        result = _upgrade_v1_package("/nonexistent/path")
        assert result == 1

    def test_upgrade_no_manifest(self, tmp_path: Path) -> None:
        result = _upgrade_v1_package(str(tmp_path))
        assert result == 1

    def test_upgrade_already_v2(self, tmp_path: Path) -> None:
        manifest = {"format_version": "2.0", "name": "test", "version": "1.0.0"}
        (tmp_path / "devsync-package.yaml").write_text(yaml.dump(manifest))
        result = _upgrade_v1_package(str(tmp_path))
        assert result == 0

    def test_upgrade_v1_no_ai(self, tmp_path: Path) -> None:
        instructions_dir = tmp_path / "instructions"
        instructions_dir.mkdir()
        (instructions_dir / "style.md").write_text("# Style\nUse black.")

        manifest = {
            "name": "old-pkg",
            "version": "1.0.0",
            "description": "Legacy package",
            "components": {
                "instructions": [{"name": "style", "file": "instructions/style.md"}],
            },
        }
        (tmp_path / "ai-config-kit-package.yaml").write_text(yaml.dump(manifest))

        output_dir = tmp_path / "output"
        result = _upgrade_v1_package(str(tmp_path), output=str(output_dir), no_ai=True)

        assert result == 0
        v2_manifest_path = output_dir / "devsync-package.yaml"
        assert v2_manifest_path.exists()

        v2 = yaml.safe_load(v2_manifest_path.read_text())
        assert v2["format_version"] == "2.0"
        assert v2["name"] == "old-pkg"
        assert v2["version"] == "1.0.0"
        assert len(v2.get("practices", [])) == 1

    def test_upgrade_dispatched_from_extract_command(self, tmp_path: Path) -> None:
        instructions_dir = tmp_path / "instructions"
        instructions_dir.mkdir()
        (instructions_dir / "rule.md").write_text("# Rule\nDo this.")

        manifest = {
            "name": "v1-pkg",
            "version": "0.5.0",
            "description": "Old",
            "components": {
                "instructions": [{"name": "rule", "file": "instructions/rule.md"}],
            },
        }
        (tmp_path / "ai-config-kit-package.yaml").write_text(yaml.dump(manifest))

        output_dir = tmp_path / "upgraded"
        result = extract_command(output=str(output_dir), no_ai=True, upgrade=str(tmp_path))

        assert result == 0
        assert (output_dir / "devsync-package.yaml").exists()
