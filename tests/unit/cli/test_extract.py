"""Tests for extract CLI command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from devsync.cli.extract import extract_command
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
