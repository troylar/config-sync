"""Tests for PracticeAdapter."""

import json
from pathlib import Path
from unittest.mock import MagicMock

from devsync.core.adapter import PracticeAdapter
from devsync.core.practice import PracticeDeclaration
from devsync.llm.provider import LLMProviderError, LLMResponse


class TestPracticeAdapterNoAI:
    def test_adapt_no_conflicts(self, tmp_path: Path) -> None:
        practices = [
            PracticeDeclaration(name="type-safety", intent="Enforce types", principles=["Use type hints"]),
        ]
        adapter = PracticeAdapter(llm_provider=None)
        plan = adapter.adapt(practices, tmp_path, ["claude"])

        assert plan.ai_powered is False
        assert len(plan.installs) == 1
        assert plan.installs[0].practice_name == "type-safety"
        assert "type-safety" in plan.installs[0].content

    def test_adapt_with_existing_rule_skips(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "type-safety.md").write_text("# Existing type rules")

        practices = [
            PracticeDeclaration(name="type-safety", intent="Enforce types"),
        ]
        adapter = PracticeAdapter(llm_provider=None)
        plan = adapter.adapt(practices, tmp_path, ["claude"])

        assert len(plan.skips) == 1
        assert plan.skips[0].practice_name == "type-safety"

    def test_adapt_mixed_conflicts(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "style.mdc").write_text("# Style rules")

        practices = [
            PracticeDeclaration(name="style", intent="Code style"),
            PracticeDeclaration(name="testing", intent="Test coverage"),
        ]
        adapter = PracticeAdapter(llm_provider=None)
        plan = adapter.adapt(practices, tmp_path, ["cursor"])

        assert len(plan.skips) == 1
        assert len(plan.installs) == 1

    def test_render_practice_with_raw_content(self, tmp_path: Path) -> None:
        practices = [
            PracticeDeclaration(name="custom", intent="Custom rule", raw_content="# My Custom Rule\nDo this."),
        ]
        adapter = PracticeAdapter(llm_provider=None)
        plan = adapter.adapt(practices, tmp_path, ["claude"])

        assert plan.installs[0].content == "# My Custom Rule\nDo this."


class TestPracticeAdapterWithAI:
    def test_adapt_install_action(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "existing.md").write_text("# Existing rule")

        practices = [
            PracticeDeclaration(name="security", intent="Security patterns", principles=["No eval()"]),
        ]

        llm_response = LLMResponse(
            content=json.dumps(
                {
                    "action": "install",
                    "reason": "No overlap with existing rules",
                    "file_name": "security.md",
                }
            ),
            model="test",
        )
        mock_provider = MagicMock()
        mock_provider.complete.return_value = llm_response

        adapter = PracticeAdapter(llm_provider=mock_provider)
        plan = adapter.adapt(practices, tmp_path, ["claude"])

        assert plan.ai_powered is True
        assert len(plan.installs) == 1
        assert plan.installs[0].practice_name == "security"

    def test_adapt_merge_action(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "style.md").write_text("# Old style")

        practices = [
            PracticeDeclaration(name="style", intent="Code style"),
        ]

        llm_response = LLMResponse(
            content=json.dumps(
                {
                    "action": "merge",
                    "reason": "Overlapping style rules",
                    "merged_content": "# Merged Style\nOld + new rules",
                    "file_name": "style.md",
                }
            ),
            model="test",
        )
        mock_provider = MagicMock()
        mock_provider.complete.return_value = llm_response

        adapter = PracticeAdapter(llm_provider=mock_provider)
        plan = adapter.adapt(practices, tmp_path, ["claude"])

        assert len(plan.merges) == 1
        assert "Merged Style" in plan.merges[0].content

    def test_ai_failure_falls_back_to_install(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "existing.md").write_text("# Existing")

        practices = [
            PracticeDeclaration(name="testing", intent="Test rules"),
        ]

        mock_provider = MagicMock()
        mock_provider.complete.side_effect = LLMProviderError("API error")

        adapter = PracticeAdapter(llm_provider=mock_provider)
        plan = adapter.adapt(practices, tmp_path, ["claude"])

        assert len(plan.installs) == 1
        assert "failed" in plan.installs[0].reason.lower()
