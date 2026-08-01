# Smell Audit — core-pipeline · run 2026-08-01-core-pipeline

Area: core-pipeline (extractor, package_creator, component_detector,
conflict_resolution, adapter — ~3,850 lines). First audit; no prior inventory
for this area. Preflight: read end-to-end except adapter.py (skimmed) and the
long tail of conflict_resolution (sampled); recorded here per the honesty rule.

## Findings (all NEW — first run)

### SM-core-pipeline-001 — The `_detect_*` family re-implements one skeleton eight times
- dimension: duplication & change amplification · severity: medium · confidence: high · scope: subsystem · effort: M
- Eight methods (`_detect_instructions`, `_mcp_servers`, `_hooks`, `_commands`,
  `_resources`, `_skills`, `_workflows`, `_memory_files`; component_detector.py:382–950)
  share the same walk-locations → filter-by-tool → read → catch-warn-continue
  skeleton with per-type variations inline. Adding a component type means
  copying the skeleton; changing the walk policy means eight edits. This is the
  same KNOWLEDGE (how detection traverses a project) written eight times.
- Measure: `grep -c "def _detect" devsync/core/component_detector.py` — **8**
  sharing the skeleton (target after extraction of a shared walker: methods
  remain, skeleton lives once).
- Smallest safe step: extract the location-walk + tool-filter + safe-read into
  one helper; port ONE detector to it with its existing tests green.

### SM-core-pipeline-002 — Tool-specific knowledge hardcoded in core, beside the registry built to own it
- dimension: dependencies & coupling · severity: high · confidence: high · scope: suspected_cross_area · effort: M
- component_detector special-cases tools by name (`if ide_name == "copilot":
  rglob(...)`; location dicts naming claude/cursor/windsurf/copilot — 14 refs)
  and core/*.py carries 11 more, while `ai_tools/capability_registry.py`
  exists precisely to own per-tool capability knowledge. The project's own
  ROADMAP (#86) names the consequence: "extraction is currently Claude-centric,
  which undermines the IDE-agnostic principle."
- Cross-area: evidence spans core-pipeline ↔ ai-tools; scope stays
  suspected_cross_area until the ai-tools audit + validation step confirms.
- Measure: `grep -rn '"claude"\|"cursor"\|"copilot"\|CLAUDE.md\|cursorrules'
  devsync/core/*.py | wc -l` — baseline **25**, direction down (tool knowledge
  migrates behind the registry).
- Routing note: NOT proposed as a register candidate — this is existing
  roadmap issue [#86](https://github.com/troylar/devsync/issues/86); a DEBT
  item would double-track it. Recorded here so the inventory trends it anyway.

### SM-core-pipeline-003 — `to_package_components`: 110 lines of parallel per-type mapping
- dimension: functions & control flow · severity: low · confidence: high · scope: local · effort: S–M
- component_detector.py:~250–360. One function maps eight detected-component
  types to eight component models in sequence — not complex per se, but it is
  the ninth place the "component types" concept is enumerated (see SM-001),
  so every new type touches it too. Length is a symptom; the enumeration is
  the smell.
- Measure: function length — **110** lines (falls out naturally if SM-001's
  extraction gives types a shared mapping seam).

### SM-core-pipeline-004 — Failures during detection/extraction are logged where CLI users don't look
- dimension: error handling & resilience · severity: medium · confidence: high · scope: subsystem · effort: S
- 11 catch-warn-continue sites in component_detector alone (e.g. :438, :464,
  :528, :554, :722) log to `logger.warning` while the CLI's user-facing
  surface is rich `console`. A file that fails to read is silently absent
  from the extraction from the user's point of view — "worked, mostly."
  The catch-and-continue policy itself is defensible for detection; the
  invisibility is the smell.
- Measure: warn-continue sites whose message reaches the console — **0 of 11**.
- Smallest safe step: count skipped files during a run and print one summary
  line ("3 files skipped — run with --verbose for details").

### SM-core-pipeline-005 — AI and non-AI extraction paths have no parity tripwire
- dimension: tests & testability · severity: medium · confidence: medium · scope: local · effort: S
- extractor.py maintains `_extract_with_ai` and `_extract_without_ai` as
  alternative pipelines (fallback on provider absence/failure). No test runs
  the same fixture through both and compares the shape of the results, so the
  paths can drift silently — already flagged as handle-with-care in the
  baseline scorecard; this is its measurable form.
- Measure: parity tests — **0** (target ≥ 1).

## Appears healthy
- Broad catches in this area are uniformly logged (no bare `pass` anywhere) —
  the hygiene is real; visibility is the gap (SM-004).
- conflict_resolution has both a unit and a "full" test module; sampled logic
  is cohesive.
- Atomic-write + backup discipline holds on the write paths sampled.

## Investigated but not substantiated
- Temporal coupling between package_creator steps: constructor takes detector
  output cleanly; no undocumented call-order requirement found.
- Exception-driven control flow: `except` blocks skip-and-continue but none
  were found steering normal logic.

## Routing
- Register candidates: none this run (SM-002 is existing roadmap #86 —
  double-tracking declined; SM-004/005 are below the CONTEXT.md trust
  threshold, quick-win-sized).
- Quick wins: SM-004's skip-summary line · SM-005's one parity test ·
  fold the copilot rglob special case into the locations config.
