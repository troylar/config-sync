"""Tests for PracticeExtractor."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from devsync.core.extractor import PracticeExtractor
from devsync.llm.provider import LLMProviderError, LLMResponse


def _make_detection_result(instructions: list | None = None, mcp_servers: list | None = None) -> MagicMock:
    result = MagicMock()
    result.instructions = instructions or []
    result.mcp_servers = mcp_servers or []
    return result


class TestPracticeExtractorNoAI:
    def test_extract_empty_project(self, tmp_path: Path) -> None:
        with patch("devsync.core.component_detector.ComponentDetector") as mock_cls:
            mock_cls.return_value.detect_all.return_value = _make_detection_result()
            extractor = PracticeExtractor(llm_provider=None)
            result = extractor.extract(tmp_path)

        assert result.ai_powered is False
        assert result.practices == []
        assert result.mcp_servers == []

    def test_extract_with_instruction_files(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)
        rule_file = rules_dir / "style.md"
        rule_file.write_text("# Style Guide\nUse black.")

        mock_instr = MagicMock()
        mock_instr.file_path = str(rule_file)
        mock_instr.path = None

        with patch("devsync.core.component_detector.ComponentDetector") as mock_cls:
            mock_cls.return_value.detect_all.return_value = _make_detection_result(instructions=[mock_instr])
            extractor = PracticeExtractor(llm_provider=None)
            result = extractor.extract(tmp_path)

        assert result.ai_powered is False
        assert len(result.practices) == 1
        assert result.practices[0].name == "style"
        assert "Use black" in (result.practices[0].raw_content or "")

    def test_extract_with_mcp_servers(self, tmp_path: Path) -> None:
        mock_server = MagicMock()
        mock_server.name = "github"
        mock_server.command = "npx"
        mock_server.args = ["-y", "server"]
        mock_server.env = None
        mock_server.pip_package = None

        with patch("devsync.core.component_detector.ComponentDetector") as mock_cls:
            mock_cls.return_value.detect_all.return_value = _make_detection_result(mcp_servers=[mock_server])
            extractor = PracticeExtractor(llm_provider=None)
            result = extractor.extract(tmp_path)

        assert len(result.mcp_servers) == 1
        assert result.mcp_servers[0].name == "github"
        assert result.mcp_servers[0].command == "npx"


class TestPracticeExtractorPipPackage:
    def test_extract_propagates_pip_package(self, tmp_path: Path) -> None:
        mock_server = MagicMock()
        mock_server.name = "fetch"
        mock_server.command = "python"
        mock_server.args = ["-m", "mcp_server_fetch"]
        mock_server.env = None
        mock_server.pip_package = "mcp-server-fetch>=0.5"

        with patch("devsync.core.component_detector.ComponentDetector") as mock_cls:
            mock_cls.return_value.detect_all.return_value = _make_detection_result(mcp_servers=[mock_server])
            extractor = PracticeExtractor(llm_provider=None)
            result = extractor.extract(tmp_path)

        assert len(result.mcp_servers) == 1
        assert result.mcp_servers[0].pip_package == "mcp-server-fetch>=0.5"

    def test_extract_pip_package_none_when_absent(self, tmp_path: Path) -> None:
        mock_server = MagicMock()
        mock_server.name = "github"
        mock_server.command = "npx"
        mock_server.args = ["-y", "server"]
        mock_server.env = None
        mock_server.pip_package = None

        with patch("devsync.core.component_detector.ComponentDetector") as mock_cls:
            mock_cls.return_value.detect_all.return_value = _make_detection_result(mcp_servers=[mock_server])
            extractor = PracticeExtractor(llm_provider=None)
            result = extractor.extract(tmp_path)

        assert len(result.mcp_servers) == 1
        assert result.mcp_servers[0].pip_package is None


class TestPracticeExtractorWithAI:
    def test_extract_with_ai(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        rule_file = rules_dir / "types.md"
        rule_file.write_text("# Type Safety\nAll functions need type hints.")

        mock_instr = MagicMock()
        mock_instr.file_path = str(rule_file)
        mock_instr.path = None

        llm_response = LLMResponse(
            content=json.dumps(
                {
                    "practices": [
                        {
                            "name": "type-safety",
                            "intent": "Enforce strict type hints",
                            "principles": ["All functions must have type hints"],
                            "tags": ["python", "typing"],
                        }
                    ]
                }
            ),
            model="test",
        )
        mock_provider = MagicMock()
        mock_provider.complete.return_value = llm_response

        with patch("devsync.core.component_detector.ComponentDetector") as mock_cls:
            mock_cls.return_value.detect_all.return_value = _make_detection_result(instructions=[mock_instr])
            extractor = PracticeExtractor(llm_provider=mock_provider)
            result = extractor.extract(tmp_path)

        assert result.ai_powered is True
        assert len(result.practices) == 1
        assert result.practices[0].name == "type-safety"

    def test_ai_fallback_on_error(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "test.md").write_text("# Test")

        mock_instr = MagicMock()
        mock_instr.file_path = str(rules_dir / "test.md")
        mock_instr.path = None

        mock_provider = MagicMock()
        mock_provider.complete.side_effect = LLMProviderError("API error")

        with patch("devsync.core.component_detector.ComponentDetector") as mock_cls:
            mock_cls.return_value.detect_all.return_value = _make_detection_result(instructions=[mock_instr])
            extractor = PracticeExtractor(llm_provider=mock_provider)
            result = extractor.extract(tmp_path)

        assert len(result.practices) == 1
        assert result.practices[0].raw_content == "# Test"


class TestSecretRedactionTripwire:
    """DEBT-001 tripwire: planted secrets must never reach the LLM payload.

    If secret detection is removed from the extraction path, these fail.
    """

    def _detection_for(self, rule_file: Path) -> MagicMock:
        mock_instr = MagicMock()
        mock_instr.file_path = str(rule_file)
        mock_instr.path = None
        return _make_detection_result(instructions=[mock_instr])

    def test_planted_secret_never_reaches_llm_payload(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)
        rule_file = rules_dir / "deploy.md"
        rule_file.write_text(
            "# Deploy\n"
            'export OPENAI_API_KEY="sk-plantedsecret1234567890abcdef"\n'
            "AWS_SECRET_ACCESS_KEY: plantedAWSsecretValue99\n"
            "Use PORT=8080 for local runs.\n"
        )

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLMResponse(
            content=json.dumps({"practices": []}), model="test", usage={}
        )

        with patch("devsync.core.component_detector.ComponentDetector") as mock_cls:
            mock_cls.return_value.detect_all.return_value = self._detection_for(rule_file)
            extractor = PracticeExtractor(llm_provider=mock_llm)
            extractor.extract(tmp_path)

        assert mock_llm.complete.called
        all_payloads = " ".join(
            str(call.args) + str(call.kwargs) for call in mock_llm.complete.call_args_list
        )
        assert "sk-plantedsecret1234567890abcdef" not in all_payloads
        assert "plantedAWSsecretValue99" not in all_payloads
        # Non-secret content must survive redaction (no over-scrubbing)
        assert "8080" in all_payloads

    def test_planted_secret_never_persisted_in_file_copy_path(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        rule_file = rules_dir / "ci.md"
        rule_file.write_text("token: ghp_ABCdefGHIjklMNOpqrSTUvwx12345678\n")

        with patch("devsync.core.component_detector.ComponentDetector") as mock_cls:
            mock_cls.return_value.detect_all.return_value = self._detection_for(rule_file)
            extractor = PracticeExtractor(llm_provider=None)
            result = extractor.extract(tmp_path)

        assert len(result.practices) == 1
        assert "ghp_ABCdefGHIjklMNOpqrSTUvwx12345678" not in (result.practices[0].raw_content or "")
