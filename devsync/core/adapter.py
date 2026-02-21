"""AI-powered practice adaptation engine."""

import json
import logging
from pathlib import Path
from typing import Optional

from devsync.core.practice import PracticeDeclaration
from devsync.llm.prompts import ADAPT_PRACTICE_PROMPT, SYSTEM_PROMPT
from devsync.llm.provider import LLMProvider, LLMProviderError
from devsync.llm.response_models import (
    AdaptationAction,
    AdaptationPlan,
    parse_adaptation_response,
)

logger = logging.getLogger(__name__)


class PracticeAdapter:
    """Adapts incoming practices to a target project's existing setup.

    Uses LLM intelligence for semantic merging when available,
    falls back to standard conflict resolution otherwise.
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self._llm = llm_provider

    def adapt(
        self,
        practices: list[PracticeDeclaration],
        project_path: Path,
        target_tools: list[str],
    ) -> AdaptationPlan:
        """Create an adaptation plan for installing practices.

        Args:
            practices: Practices to install.
            project_path: Target project root.
            target_tools: AI tools to install to.

        Returns:
            AdaptationPlan for user review before execution.
        """
        existing_rules = self._detect_existing_rules(project_path)

        if self._llm and existing_rules:
            return self._adapt_with_ai(practices, existing_rules, target_tools)
        return self._adapt_without_ai(practices, existing_rules, target_tools)

    def _detect_existing_rules(self, project_path: Path) -> dict[str, str]:
        """Detect existing instruction files in the target project."""
        rules: dict[str, str] = {}
        rule_dirs = [
            ".cursor/rules",
            ".claude/rules",
            ".windsurf/rules",
            ".github/instructions",
            ".kiro/steering",
            ".clinerules",
            ".roo/rules",
        ]
        for rule_dir in rule_dirs:
            dir_path = project_path / rule_dir
            if dir_path.is_dir():
                for f in dir_path.iterdir():
                    if f.is_file() and f.suffix in (".md", ".mdc"):
                        try:
                            content = f.read_text(encoding="utf-8")
                            rel_path = str(f.relative_to(project_path))
                            rules[rel_path] = content
                        except (OSError, UnicodeDecodeError):
                            pass
        return rules

    def _adapt_with_ai(
        self,
        practices: list[PracticeDeclaration],
        existing_rules: dict[str, str],
        target_tools: list[str],
    ) -> AdaptationPlan:
        """Use LLM to create semantic adaptation plan."""
        assert self._llm is not None
        actions: list[AdaptationAction] = []
        existing_summary = "\n".join(f"--- {path} ---\n{content[:500]}" for path, content in existing_rules.items())

        for practice in practices:
            try:
                prompt = ADAPT_PRACTICE_PROMPT.format(
                    practice_json=json.dumps(practice.to_dict(), indent=2),
                    existing_rules=existing_summary,
                    tool_name=", ".join(target_tools),
                )
                response = self._llm.complete(prompt, system=SYSTEM_PROMPT)
                action = parse_adaptation_response(response.content)
                action.practice_name = practice.name

                if action.action == "install" and not action.content:
                    action.content = self._render_practice(practice)
                if not action.file_name:
                    action.file_name = f"{practice.name}.md"

                actions.append(action)
            except (LLMProviderError, ValueError) as e:
                logger.warning("AI adaptation failed for %s: %s", practice.name, e)
                actions.append(
                    AdaptationAction(
                        action="install",
                        practice_name=practice.name,
                        reason="AI adaptation failed, installing as-is",
                        file_name=f"{practice.name}.md",
                        content=self._render_practice(practice),
                    )
                )

        return AdaptationPlan(actions=actions, target_tools=target_tools, ai_powered=True)

    def _adapt_without_ai(
        self,
        practices: list[PracticeDeclaration],
        existing_rules: dict[str, str],
        target_tools: list[str],
    ) -> AdaptationPlan:
        """Create adaptation plan without AI (standard conflict resolution)."""
        actions: list[AdaptationAction] = []
        existing_names = {Path(p).stem.lower() for p in existing_rules}

        for practice in practices:
            file_name = f"{practice.name}.md"
            if practice.name.lower() in existing_names:
                actions.append(
                    AdaptationAction(
                        action="skip",
                        practice_name=practice.name,
                        reason=f"File with name '{practice.name}' already exists",
                        file_name=file_name,
                    )
                )
            else:
                actions.append(
                    AdaptationAction(
                        action="install",
                        practice_name=practice.name,
                        reason="No conflict detected",
                        file_name=file_name,
                        content=self._render_practice(practice),
                    )
                )

        return AdaptationPlan(actions=actions, target_tools=target_tools, ai_powered=False)

    def _render_practice(self, practice: PracticeDeclaration) -> str:
        """Render a practice declaration as markdown instruction content."""
        if practice.raw_content:
            return practice.raw_content

        lines = [f"# {practice.name}", "", practice.intent, ""]

        if practice.principles:
            lines.append("## Principles")
            lines.append("")
            for p in practice.principles:
                lines.append(f"- {p}")
            lines.append("")

        if practice.enforcement_patterns:
            lines.append("## Enforcement")
            lines.append("")
            for e in practice.enforcement_patterns:
                lines.append(f"- {e}")
            lines.append("")

        if practice.examples:
            lines.append("## Examples")
            lines.append("")
            for ex in practice.examples:
                lines.append(f"```\n{ex}\n```")
                lines.append("")

        return "\n".join(lines)
