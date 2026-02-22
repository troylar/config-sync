"""Prompt templates for LLM-powered extraction and adaptation."""

SYSTEM_PROMPT = """\
You are a coding standards expert. You analyze AI coding assistant configurations \
and extract structured practice declarations. Always respond with valid JSON."""

EXTRACT_PRACTICES_PROMPT = """\
Analyze the following instruction files from a software project and extract abstract \
coding practice declarations.

For each distinct practice found, produce a JSON object with:
- "name": short kebab-case identifier
- "intent": one-line description of what this practice enforces
- "principles": list of specific rules/guidelines
- "enforcement_patterns": how to enforce (CI checks, linting config, etc.)
- "examples": code examples if present
- "tags": categorization tags

Input files:
{files_content}

Respond with a JSON object:
{{
  "practices": [
    {{
      "name": "...",
      "intent": "...",
      "principles": ["..."],
      "enforcement_patterns": ["..."],
      "examples": ["..."],
      "tags": ["..."]
    }}
  ]
}}"""

EXTRACT_MCP_PROMPT = """\
Analyze the following MCP server configuration and extract a structured declaration.

Strip all credential VALUES but keep credential NAMES and descriptions.

Input configuration:
{mcp_config}

If the MCP server command suggests a pip-installable package (e.g., uvx, python -m),
include the pip_package field with the package name and optional version constraint.

Respond with a JSON object:
{{
  "name": "server-name",
  "description": "what this server provides",
  "protocol": "stdio",
  "command": "executable",
  "args": ["arg1", "arg2"],
  "env_vars": {{"NON_SECRET_VAR": "value"}},
  "credentials": [
    {{
      "name": "ENV_VAR_NAME",
      "description": "what this credential is for",
      "required": true
    }}
  ],
  "pip_package": "package-name>=1.0 (if pip-installable, null otherwise)"
}}"""

ADAPT_PRACTICE_PROMPT = """\
You are adapting a coding practice for installation into a project that already has \
existing rules.

Incoming practice:
{practice_json}

Existing rules in the target project:
{existing_rules}

Target AI tool: {tool_name}

Determine the best adaptation strategy:
1. "install" — no conflict, install as-is
2. "merge" — overlapping content, produce merged version
3. "skip" — existing rules already cover this practice

Respond with a JSON object:
{{
  "action": "install|merge|skip",
  "reason": "explanation",
  "merged_content": "merged instruction text (only if action=merge)",
  "file_name": "suggested-filename.md"
}}"""

MERGE_PRACTICES_PROMPT = """\
Merge the following two instruction documents into a single coherent document.
Preserve all unique rules from both. Remove duplicates. Resolve contradictions \
by preferring the incoming practice (it represents the team's latest standards).

Existing document:
{existing_content}

Incoming practice:
{incoming_content}

Respond with a JSON object:
{{
  "merged_content": "the merged instruction text",
  "changes_summary": "brief description of what was merged/changed"
}}"""


def format_files_for_extraction(files: dict[str, str]) -> str:
    """Format a dict of {filename: content} for the extraction prompt.

    Args:
        files: Mapping of file paths to their content.

    Returns:
        Formatted string with file separators.
    """
    parts = []
    for path, content in files.items():
        parts.append(f"--- {path} ---\n{content}\n")
    return "\n".join(parts)
