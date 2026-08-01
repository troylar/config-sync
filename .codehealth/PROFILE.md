# Profile

Recorded: 2026-08-01 · v0.15.0 · Python 3.10+ · MIT

## Shape
- **CLI**: typer + rich + textual (devsync/cli/ — main.py, extract.py,
  install_v2.py, tools, setup)
- **Core**: devsync/core/ — models.py (1,702 ln), component_detector.py
  (1,050 ln), package_creator.py, git_operations.py, conflict_resolution.py,
  secret_detector.py, repository.py, pip_utils.py, package_manifest.py AND
  package_manifest_v2.py (both live)
- **AI-tool adapters**: devsync/ai_tools/ — translator.py (937 ln),
  capability_registry.py, mcp_syncer.py, per-tool support for 23+ assistants
- **MCP**: core/mcp/ — manager.py, credentials.py
- **Storage**: storage/tracker.py (install tracking)
- **LLM access**: httpx-based; provider configured via `devsync setup`

## Size & tests
175 .py files · ~17.5k source lines · ~22.8k test lines (unit-heavy;
per-tool adapter tests dominate). CI: ci.yml, benchmark, docs, publish,
release-drafter, code-review (Semgrep + dependency checks added #91).

## Entry points
`devsync` console script → cli/main.py. Critical flows: setup (keys) →
extract (read project + LLM) → install (write into user repo).

## History quirks
Renamed instructionkit → devsync; v2 rewrite landed ~v0.12.0 (LLM-powered
pipeline). Some v1 artifacts remain alongside v2 (_v2 suffixes).
