"""Tests for extract CLI command."""

import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from devsync.cli.extract import (
    _display_detection_summary,
    _get_detection_rows,
    _upgrade_v1_package,
    extract_command,
)
from devsync.core.component_detector import (
    DetectedInstruction,
    DetectedMCPServer,
    DetectionResult,
)
from devsync.core.practice import PracticeDeclaration
from devsync.llm.response_models import ExtractionResult


def _make_detection(
    instructions: list[DetectedInstruction] | None = None,
    mcp_servers: list[DetectedMCPServer] | None = None,
) -> DetectionResult:
    """Build a DetectionResult for testing."""
    return DetectionResult(
        instructions=instructions or [],
        mcp_servers=mcp_servers or [],
    )


def _make_project_with_rules(tmp_path: Path) -> Path:
    """Create a project dir with a Claude rule file so detection finds something."""
    rules_dir = tmp_path / ".claude" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "test-rule.md").write_text("# Test\nA test rule.")
    return tmp_path


class TestExtractCommand:
    def test_extract_invalid_path(self) -> None:
        result = extract_command(project_dir="/nonexistent/path")
        assert result == 1

    @patch("devsync.cli.extract.PracticeExtractor")
    @patch("devsync.cli.extract.load_config")
    def test_extract_no_ai(self, mock_config: MagicMock, mock_extractor_cls: MagicMock, tmp_path: Path) -> None:
        project_dir = _make_project_with_rules(tmp_path)
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
            project_dir=str(project_dir),
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
        project_dir = _make_project_with_rules(tmp_path)
        output_dir = tmp_path / "output"
        mock_config.return_value = MagicMock(provider=None, model=None)
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = ExtractionResult(ai_powered=False)
        mock_extractor_cls.return_value = mock_extractor

        result = extract_command(output=str(output_dir), project_dir=str(project_dir))

        assert result == 0
        mock_extractor_cls.assert_called_once_with(llm_provider=None)


class TestExtractFilterValidation:
    """Test validation of --tool, --component, --scope options."""

    def test_invalid_tool_rejected(self, tmp_path: Path) -> None:
        result = extract_command(project_dir=str(tmp_path), no_ai=True, tool=["nonexistent-tool"])
        assert result == 1

    def test_invalid_component_rejected(self, tmp_path: Path) -> None:
        result = extract_command(project_dir=str(tmp_path), no_ai=True, component=["nonexistent-component"])
        assert result == 1

    def test_invalid_scope_rejected(self, tmp_path: Path) -> None:
        result = extract_command(project_dir=str(tmp_path), no_ai=True, scope="invalid")
        assert result == 1

    def test_valid_tool_accepted(self, tmp_path: Path) -> None:
        result = extract_command(
            project_dir=str(tmp_path),
            no_ai=True,
            tool=["claude"],
            output=str(tmp_path / "out"),
        )
        # Returns 0 even with zero results (zero-result is not an error)
        assert result == 0

    def test_valid_component_accepted(self, tmp_path: Path) -> None:
        result = extract_command(
            project_dir=str(tmp_path),
            no_ai=True,
            component=["mcp"],
            output=str(tmp_path / "out"),
        )
        assert result == 0

    @patch("devsync.cli.extract.PracticeExtractor")
    @patch("devsync.cli.extract.load_config")
    def test_filters_pass_to_extractor(
        self, mock_config: MagicMock, mock_extractor_cls: MagicMock, tmp_path: Path
    ) -> None:
        """Detection is done in extract_command; extractor receives pre-computed DetectionResult."""
        project_dir = _make_project_with_rules(tmp_path)
        output_dir = tmp_path / "output"
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = ExtractionResult(ai_powered=False)
        mock_extractor_cls.return_value = mock_extractor

        extract_command(
            output=str(output_dir),
            no_ai=True,
            project_dir=str(project_dir),
            tool=["claude"],
        )

        mock_extractor.extract.assert_called_once()
        call_kwargs = mock_extractor.extract.call_args
        # Extractor now receives a pre-computed DetectionResult via detection kwarg
        assert "detection" in call_kwargs.kwargs
        assert call_kwargs.kwargs["detection"] is not None


class TestExtractDryRun:
    """Test --dry-run flag behaviour."""

    def test_dry_run_shows_detection_no_files_written(self, tmp_path: Path) -> None:
        """Dry run should return 0 and not create output directory."""
        project_dir = _make_project_with_rules(tmp_path)
        output_dir = tmp_path / "output"

        result = extract_command(
            output=str(output_dir),
            no_ai=True,
            project_dir=str(project_dir),
            dry_run=True,
        )

        assert result == 0
        assert not output_dir.exists()

    def test_dry_run_with_tool_filter(self, tmp_path: Path) -> None:
        """Dry run with a tool filter that matches something."""
        project_dir = _make_project_with_rules(tmp_path)

        result = extract_command(
            no_ai=True,
            project_dir=str(project_dir),
            tool=["claude"],
            dry_run=True,
        )

        assert result == 0

    def test_dry_run_zero_results(self, tmp_path: Path) -> None:
        """Dry run with filters that match nothing returns 0."""
        result = extract_command(
            no_ai=True,
            project_dir=str(tmp_path),
            tool=["claude"],
            component=["hooks"],
            dry_run=True,
        )

        assert result == 0


class TestExtractIncludeGlobal:
    """Test --include-global flag and deprecated --scope behaviour."""

    def test_include_global_maps_to_scope_all(self, tmp_path: Path) -> None:
        """--include-global should use scope 'all' internally."""
        project_dir = _make_project_with_rules(tmp_path)

        with patch("devsync.cli.extract.ComponentDetector") as mock_cd_cls:
            mock_cd = MagicMock()
            mock_cd.detect_all.return_value = DetectionResult(
                instructions=[
                    DetectedInstruction(
                        name="test",
                        file_path=project_dir / ".claude" / "rules" / "test-rule.md",
                        relative_path=".claude/rules/test-rule.md",
                        source_ide="claude",
                    )
                ]
            )
            mock_cd_cls.return_value = mock_cd

            with patch("devsync.cli.extract.PracticeExtractor") as mock_ext_cls:
                mock_ext = MagicMock()
                mock_ext.extract.return_value = ExtractionResult(ai_powered=False)
                mock_ext_cls.return_value = mock_ext

                extract_command(
                    output=str(tmp_path / "out"),
                    no_ai=True,
                    project_dir=str(project_dir),
                    include_global=True,
                )

            mock_cd_cls.assert_called_once()
            call_kwargs = mock_cd_cls.call_args
            assert call_kwargs.kwargs.get("scope") == "all"

    def test_deprecated_scope_still_works(self, tmp_path: Path) -> None:
        """--scope all should still work but trigger deprecation warning."""
        project_dir = _make_project_with_rules(tmp_path)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = extract_command(
                output=str(tmp_path / "out"),
                no_ai=True,
                project_dir=str(project_dir),
                scope="all",
            )

        assert result == 0
        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert len(deprecation_warnings) >= 1


class TestExtractZeroResult:
    """Test zero-result warning behaviour."""

    def test_zero_result_returns_zero(self, tmp_path: Path) -> None:
        """Empty project with filters should return 0, not error."""
        result = extract_command(
            no_ai=True,
            project_dir=str(tmp_path),
            tool=["cursor"],
            component=["hooks"],
        )

        assert result == 0

    def test_zero_result_no_output_dir_created(self, tmp_path: Path) -> None:
        """No output directory when zero components found."""
        output_dir = tmp_path / "output"

        extract_command(
            output=str(output_dir),
            no_ai=True,
            project_dir=str(tmp_path),
            tool=["cursor"],
            component=["hooks"],
        )

        assert not output_dir.exists()


class TestDetectionSummaryHelpers:
    """Test the detection summary display helpers."""

    def test_get_detection_rows_empty(self) -> None:
        rows = _get_detection_rows(DetectionResult())
        assert rows == []

    def test_get_detection_rows_with_instructions(self) -> None:
        detection = _make_detection(
            instructions=[
                DetectedInstruction(
                    name="rule1",
                    file_path=Path("/tmp/r1.md"),
                    relative_path=".claude/rules/r1.md",
                    source_ide="claude",
                ),
                DetectedInstruction(
                    name="rule2",
                    file_path=Path("/tmp/r2.md"),
                    relative_path=".cursor/rules/r2.mdc",
                    source_ide="cursor",
                ),
            ]
        )
        rows = _get_detection_rows(detection)
        assert len(rows) == 2
        labels = {r[0] for r in rows}
        assert "Rules" in labels

    def test_get_detection_rows_groups_by_source(self) -> None:
        detection = _make_detection(
            instructions=[
                DetectedInstruction(name="r1", file_path=Path("/t/r1.md"), relative_path="r1.md", source_ide="claude"),
                DetectedInstruction(name="r2", file_path=Path("/t/r2.md"), relative_path="r2.md", source_ide="claude"),
            ]
        )
        rows = _get_detection_rows(detection)
        # Both claude instructions grouped into one row
        assert len(rows) == 1
        assert rows[0] == ("Rules", "claude", 2)

    def test_display_detection_summary_no_crash_on_empty(self) -> None:
        """Should not crash when detection is empty."""
        _display_detection_summary(DetectionResult())


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
