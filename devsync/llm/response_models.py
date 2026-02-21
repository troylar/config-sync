"""Structured response types for LLM outputs."""

import json
from dataclasses import dataclass, field
from typing import Optional

from devsync.core.practice import MCPDeclaration, PracticeDeclaration


@dataclass
class ExtractionResult:
    """Result of AI-powered practice extraction.

    Attributes:
        practices: Extracted practice declarations.
        mcp_servers: Extracted MCP server declarations.
        source_files: Original files that were analyzed.
        ai_powered: Whether AI was used (False = fallback mode).
    """

    practices: list[PracticeDeclaration] = field(default_factory=list)
    mcp_servers: list[MCPDeclaration] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)
    ai_powered: bool = True

    def to_dict(self) -> dict:
        return {
            "practices": [p.to_dict() for p in self.practices],
            "mcp_servers": [m.to_dict() for m in self.mcp_servers],
            "source_files": self.source_files,
            "ai_powered": self.ai_powered,
        }


@dataclass
class AdaptationAction:
    """A single adaptation action for one practice/file.

    Attributes:
        action: One of 'install', 'merge', 'skip'.
        practice_name: Name of the practice being adapted.
        reason: Why this action was chosen.
        file_name: Target file name for installation.
        content: The content to write (original or merged).
    """

    action: str
    practice_name: str
    reason: str
    file_name: str = ""
    content: str = ""

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "practice_name": self.practice_name,
            "reason": self.reason,
            "file_name": self.file_name,
            "content": self.content,
        }


@dataclass
class AdaptationPlan:
    """Plan for adapting practices to a target project.

    Presented to the user for review before execution.

    Attributes:
        actions: List of adaptation actions.
        target_tools: AI tools to install to.
        ai_powered: Whether AI was used for adaptation.
    """

    actions: list[AdaptationAction] = field(default_factory=list)
    target_tools: list[str] = field(default_factory=list)
    ai_powered: bool = True

    @property
    def installs(self) -> list[AdaptationAction]:
        return [a for a in self.actions if a.action == "install"]

    @property
    def merges(self) -> list[AdaptationAction]:
        return [a for a in self.actions if a.action == "merge"]

    @property
    def skips(self) -> list[AdaptationAction]:
        return [a for a in self.actions if a.action == "skip"]

    def to_dict(self) -> dict:
        return {
            "actions": [a.to_dict() for a in self.actions],
            "target_tools": self.target_tools,
            "ai_powered": self.ai_powered,
        }


@dataclass
class MergeDecision:
    """Result of merging two instruction documents.

    Attributes:
        merged_content: The merged instruction text.
        changes_summary: Brief description of what changed.
    """

    merged_content: str
    changes_summary: str

    def to_dict(self) -> dict:
        return {
            "merged_content": self.merged_content,
            "changes_summary": self.changes_summary,
        }


def parse_extraction_response(raw_json: str) -> list[PracticeDeclaration]:
    """Parse LLM extraction response into PracticeDeclaration list.

    Args:
        raw_json: JSON string from LLM response.

    Returns:
        List of PracticeDeclaration objects.

    Raises:
        ValueError: If JSON is invalid or missing required fields.
    """
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in LLM response: {e}") from e

    practices = []
    for item in data.get("practices", []):
        practices.append(PracticeDeclaration.from_dict(item))
    return practices


def parse_adaptation_response(raw_json: str) -> AdaptationAction:
    """Parse LLM adaptation response into an AdaptationAction.

    Args:
        raw_json: JSON string from LLM response.

    Returns:
        AdaptationAction object.

    Raises:
        ValueError: If JSON is invalid or missing required fields.
    """
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in LLM response: {e}") from e

    return AdaptationAction(
        action=data.get("action", "skip"),
        practice_name="",
        reason=data.get("reason", ""),
        file_name=data.get("file_name", ""),
        content=data.get("merged_content", ""),
    )


def parse_merge_response(raw_json: str) -> MergeDecision:
    """Parse LLM merge response into a MergeDecision.

    Args:
        raw_json: JSON string from LLM response.

    Returns:
        MergeDecision object.

    Raises:
        ValueError: If JSON is invalid or missing required fields.
    """
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in LLM response: {e}") from e

    return MergeDecision(
        merged_content=data.get("merged_content", ""),
        changes_summary=data.get("changes_summary", ""),
    )
