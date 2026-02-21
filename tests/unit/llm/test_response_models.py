"""Tests for LLM response models and parsers."""

import json

import pytest

from devsync.core.practice import PracticeDeclaration
from devsync.llm.response_models import (
    AdaptationAction,
    AdaptationPlan,
    ExtractionResult,
    parse_adaptation_response,
    parse_extraction_response,
    parse_merge_response,
)


class TestExtractionResult:
    def test_empty(self) -> None:
        result = ExtractionResult()
        assert result.practices == []
        assert result.mcp_servers == []
        assert result.ai_powered is True

    def test_to_dict(self) -> None:
        result = ExtractionResult(
            practices=[PracticeDeclaration(name="test", intent="Test")],
            source_files=["rules/test.md"],
            ai_powered=True,
        )
        d = result.to_dict()
        assert len(d["practices"]) == 1
        assert d["source_files"] == ["rules/test.md"]


class TestAdaptationPlan:
    def test_action_filters(self) -> None:
        plan = AdaptationPlan(
            actions=[
                AdaptationAction(action="install", practice_name="a", reason="new"),
                AdaptationAction(action="merge", practice_name="b", reason="overlap"),
                AdaptationAction(action="skip", practice_name="c", reason="exists"),
                AdaptationAction(action="install", practice_name="d", reason="new"),
            ]
        )
        assert len(plan.installs) == 2
        assert len(plan.merges) == 1
        assert len(plan.skips) == 1


class TestParseExtractionResponse:
    def test_valid_response(self) -> None:
        response = json.dumps(
            {
                "practices": [
                    {
                        "name": "type-safety",
                        "intent": "Enforce type hints",
                        "principles": ["Use type hints everywhere"],
                        "tags": ["python"],
                    }
                ]
            }
        )
        practices = parse_extraction_response(response)
        assert len(practices) == 1
        assert practices[0].name == "type-safety"

    def test_empty_practices(self) -> None:
        response = json.dumps({"practices": []})
        practices = parse_extraction_response(response)
        assert practices == []

    def test_invalid_json(self) -> None:
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_extraction_response("not json")

    def test_missing_practices_key(self) -> None:
        response = json.dumps({"other": "data"})
        practices = parse_extraction_response(response)
        assert practices == []


class TestParseAdaptationResponse:
    def test_install_action(self) -> None:
        response = json.dumps(
            {
                "action": "install",
                "reason": "No conflicts found",
                "file_name": "type-safety.md",
            }
        )
        action = parse_adaptation_response(response)
        assert action.action == "install"
        assert action.file_name == "type-safety.md"

    def test_merge_action(self) -> None:
        response = json.dumps(
            {
                "action": "merge",
                "reason": "Overlapping rules",
                "merged_content": "# Merged\nRule 1\nRule 2",
                "file_name": "style.md",
            }
        )
        action = parse_adaptation_response(response)
        assert action.action == "merge"
        assert "Merged" in action.content

    def test_invalid_json(self) -> None:
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_adaptation_response("{bad")


class TestParseMergeResponse:
    def test_valid(self) -> None:
        response = json.dumps(
            {
                "merged_content": "# Combined\nAll rules here",
                "changes_summary": "Added 3 new rules from incoming",
            }
        )
        decision = parse_merge_response(response)
        assert "Combined" in decision.merged_content
        assert "3 new rules" in decision.changes_summary

    def test_invalid_json(self) -> None:
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_merge_response("nope")
