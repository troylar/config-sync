# Smell Inventory

| ID | area_id | Title | Dimension | Sev | Conf | Effort | Scope | State | Movement | Measure (anchor+unit) | Current | Previous | First seen | Last run_id | Routing | Ever cleared |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SM-core-pipeline-001 | core-pipeline | `_detect_*` family re-implements one skeleton ×8 | duplication & change amplification | medium | high | M | subsystem | open | new | `grep -c "def _detect" devsync/core/component_detector.py` (methods on shared skeleton) | 8 | — | 2026-08-01 | 2026-08-01-core-pipeline | none | no |
| SM-core-pipeline-002 | core-pipeline | Tool knowledge hardcoded in core beside the registry | dependencies & coupling | high | high | M | suspected_cross_area | open | new | grep tool-name refs in devsync/core/*.py (count) | 25 | — | 2026-08-01 | 2026-08-01-core-pipeline | tracked_externally:devsync#86 | no |
| SM-core-pipeline-003 | core-pipeline | to_package_components: 110-line per-type enumeration | functions & control flow | low | high | S–M | local | open | new | function length (lines) | 110 | — | 2026-08-01 | 2026-08-01-core-pipeline | none | no |
| SM-core-pipeline-004 | core-pipeline | Detection failures invisible to CLI users | error handling & resilience | medium | high | S | subsystem | open | new | warn-continue sites surfaced to console (count of 11) | 0 | — | 2026-08-01 | 2026-08-01-core-pipeline | none | no |
| SM-core-pipeline-005 | core-pipeline | AI/non-AI extraction paths lack parity test | tests & testability | medium | medium | S | local | open | new | parity tests (count) | 0 | — | 2026-08-01 | 2026-08-01-core-pipeline | none | no |
