"""AI-powered practice extraction engine."""

import json
import logging
import re
from pathlib import Path
from typing import Optional

from devsync.core.practice import MCPDeclaration, PracticeDeclaration
from devsync.llm.prompts import (
    EXTRACT_MCP_PROMPT,
    EXTRACT_PRACTICES_PROMPT,
    SYSTEM_PROMPT,
    format_files_for_extraction,
)
from devsync.llm.provider import LLMProvider, LLMProviderError
from devsync.llm.response_models import ExtractionResult, parse_extraction_response

logger = logging.getLogger(__name__)


class PracticeExtractor:
    """Extracts practice declarations from a project's AI configs.

    Uses LLM intelligence when available, falls back to file-copy mode.
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self._llm = llm_provider

    def extract(self, project_path: Path) -> ExtractionResult:
        """Extract practices from a project directory.

        Args:
            project_path: Root directory of the project to analyze.

        Returns:
            ExtractionResult with extracted practices and MCP servers.
        """
        from devsync.core.component_detector import ComponentDetector

        detector = ComponentDetector(project_path)
        detection = detector.detect_all()

        instruction_files = self._read_instruction_files(project_path, detection)
        mcp_configs = self._read_mcp_configs(detection)

        if self._llm:
            return self._extract_with_ai(instruction_files, mcp_configs)
        return self._extract_without_ai(instruction_files, mcp_configs)

    def _read_instruction_files(self, project_path: Path, detection: object) -> dict[str, str]:
        """Read instruction file contents from detected components."""
        files: dict[str, str] = {}
        for instr in getattr(detection, "instructions", []):
            file_path = getattr(instr, "file_path", None) or getattr(instr, "path", None)
            if not file_path:
                continue
            path = Path(file_path)
            if not path.is_absolute():
                path = project_path / path
            if path.exists() and path.stat().st_size < 100_000:
                try:
                    content = path.read_text(encoding="utf-8")
                    rel_path = str(path.relative_to(project_path))
                    files[rel_path] = content
                except (OSError, UnicodeDecodeError):
                    logger.warning("Could not read %s", path)
        return files

    def _read_mcp_configs(self, detection: object) -> list[dict]:
        """Read MCP server configurations from detected components."""
        configs = []
        for server in getattr(detection, "mcp_servers", []):
            config: dict = {}
            for attr in ("name", "command", "args", "env", "pip_package"):
                val = getattr(server, attr, None)
                if val is not None:
                    config[attr] = val
            if config:
                configs.append(config)
        return configs

    def _extract_with_ai(self, files: dict[str, str], mcp_configs: list[dict]) -> ExtractionResult:
        """Extract practices using LLM intelligence."""
        assert self._llm is not None

        practices: list[PracticeDeclaration] = []
        mcp_servers: list[MCPDeclaration] = []

        if files:
            files_content = format_files_for_extraction(files)
            prompt = EXTRACT_PRACTICES_PROMPT.format(files_content=files_content)
            try:
                response = self._llm.complete(prompt, system=SYSTEM_PROMPT)
                practices = parse_extraction_response(response.content)
                for i, p in enumerate(practices):
                    source_files = list(files.keys())
                    if i < len(source_files):
                        practices[i] = PracticeDeclaration(
                            name=p.name,
                            intent=p.intent,
                            principles=p.principles,
                            enforcement_patterns=p.enforcement_patterns,
                            examples=p.examples,
                            tags=p.tags,
                            source_file=source_files[i] if i < len(source_files) else None,
                        )
            except (LLMProviderError, ValueError) as e:
                logger.warning("AI extraction failed, falling back: %s", e)
                practices = self._practices_from_files(files)

        for mcp_config in mcp_configs:
            try:
                prompt = EXTRACT_MCP_PROMPT.format(mcp_config=json.dumps(mcp_config, indent=2))
                response = self._llm.complete(prompt, system=SYSTEM_PROMPT)
                content = _strip_markdown_fences(response.content)
                data = json.loads(content)
                mcp_servers.append(MCPDeclaration.from_dict(data))
            except (LLMProviderError, ValueError, json.JSONDecodeError) as e:
                logger.warning("MCP extraction failed for %s: %s", mcp_config.get("name", "unknown"), e)

        return ExtractionResult(
            practices=practices,
            mcp_servers=mcp_servers,
            source_files=list(files.keys()),
            ai_powered=True,
        )

    def _extract_without_ai(self, files: dict[str, str], mcp_configs: list[dict]) -> ExtractionResult:
        """Extract practices as literal file copies (no AI)."""
        practices = self._practices_from_files(files)

        mcp_servers = []
        for config in mcp_configs:
            name = config.get("name", "unknown-mcp")
            mcp_servers.append(
                MCPDeclaration(
                    name=name,
                    description=f"MCP server: {name}",
                    command=config.get("command", ""),
                    args=config.get("args", []),
                    pip_package=config.get("pip_package"),
                )
            )

        return ExtractionResult(
            practices=practices,
            mcp_servers=mcp_servers,
            source_files=list(files.keys()),
            ai_powered=False,
        )

    def _practices_from_files(self, files: dict[str, str]) -> list[PracticeDeclaration]:
        """Create literal practice declarations from file contents."""
        practices = []
        for path, content in files.items():
            name = Path(path).stem
            practices.append(
                PracticeDeclaration(
                    name=name,
                    intent=f"Instructions from {path}",
                    source_file=path,
                    raw_content=content,
                )
            )
        return practices


def _strip_markdown_fences(text: str) -> str:
    """Strip markdown code fences from LLM response text.

    LLMs sometimes wrap JSON output in ```json ... ``` fences.
    This extracts the content inside the fences if present.
    """
    match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()
