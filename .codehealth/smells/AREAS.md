# Areas — canonical registry

One row per area. `area_id` is immutable — never renamed, never reissued.
IDs/metrics/reports use area_id, never paths.

| area_id | Display name | Repo | Current paths | Aliases | Status | Notes |
|---|---|---|---|---|---|---|
| core-pipeline | Extraction & packaging pipeline | devsync | devsync/core/{extractor,package_creator,component_detector,conflict_resolution,adapter}.py | — | active | split of core: whole core exceeds read budget |
| core-domain | Domain models & manifests | devsync | devsync/core/{models,package_manifest,package_manifest_v2,secret_detector}.py | — | active | split of core |
| core-infra | Git, repo, pip, MCP plumbing | devsync | devsync/core/{git_operations,repository,pip_utils}.py + devsync/core/mcp/ | — | active | split of core |
| cli | CLI commands & UX | devsync | devsync/cli/ | — | active | |
| ai-tools | Per-assistant adapters | devsync | devsync/ai_tools/ | — | active | 30 files behind a registry; per-run sampling strategy must be recorded |
| llm | LLM providers | devsync | devsync/llm/ | — | active | |
| support | Storage, utils | devsync | devsync/storage/ + devsync/utils/ | — | active | |

Excluded everywhere: tests/, docs/, .github/, __pycache__/, tasks.py (task runner).
