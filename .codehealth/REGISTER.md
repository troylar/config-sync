# Register

Tracked debt items. Curated: registering here is a commitment. See CONTEXT.md
(register policy: 2–3 items max, trust-first).

---

## DEBT-001 — Extraction payload bypasses secret detection

- **Status:** resolved-pending-verify (fix landed 2026-08-01; both criteria pass — closes when they pass again at the next measurement, per the soak rule) · **Severity:** critical · **Registered:** 2026-08-01 · **Issue:** [#103](https://github.com/troylar/devsync/issues/103)
- **Statement:** `extractor.py` sends raw instruction-file text to the configured
  LLM provider with no secret scan. `SecretDetector` exists and is tested, but is
  wired only into MCP-config templating (`package_creator.py`). A user whose
  CLAUDE.md-class files contain keys ships them to a provider on first `extract`.
- **Why now:** extraction is the first command a new user runs; the product's
  pitch is safe practice-sharing. Trust-critical per CONTEXT.md path #3.
- **Done means (all criteria binary, exact commands):**
  1. Extraction payload passes through secret detection before ANY provider call.
     Measure: `grep -c "SecretDetector\|secret_detector" devsync/core/extractor.py`
     — baseline **0**, target **≥ 1** (and code review confirms it's on the payload path, both AI and non-AI persistence).
  2. A tripwire test plants a secret in a fixture instruction file and asserts it
     does not appear in the outbound payload.
     Measure: `grep -rln "secret" tests/unit/test_extractor.py | wc -l` — baseline
     **0**, target **≥ 1** (test must fail if detection is removed).
- **Effort:** S · **Blast radius of fix:** extraction output may template values
  that users expected verbatim — release-note it.

## DEBT-002 — `.instructionkit` residue in the storage/credentials layer

- **Status:** open · **Severity:** high · **Registered:** 2026-08-01 · **Issue:** [#104](https://github.com/troylar/devsync/issues/104)
- **Statement:** rename debt: credentials and storage still read/write
  `.instructionkit/` project and global paths across 5 modules. User-visible
  directories carry the dead product name; every contributor learns the alias.
- **Handle with care:** existing installs keep credentials at old paths —
  migration must write-new/read-old (alias) or migrate once, never strand keys.
- **Done means:**
  1. New writes land under `.devsync/`; old paths still readable.
     Measure: code review of `utils/paths.py` write-path + an alias test.
  2. Source refs to `instructionkit` trend to 0.
     Measure: `grep -rn "instructionkit" devsync/ --include="*.py" | wc -l` —
     baseline **11**, target **0** (excluding the read-alias constant + its test,
     which may retain the literal; adjust the count by explicit allowlist when
     the alias lands).
- **Effort:** S–M.

---

## Candidate decisions

- 2026-08-01 — "v1/v2 dual manifest architecture" — dismissed from register:
  below trust threshold for a solo project. Revisit if: any non-test import of
  package_manifest.py (v1) is found, or a v1-path bug ships.
- 2026-08-01 — "broad exception handling hides partial installs" — awaiting
  decision (quick-win #4, promote failure logs to console, may be enough).
  First surfaced 2026-08-01.
- 2026-08-01 — "models.py 43-class monolith" — dismissed: accept and monitor.
  Revisit if: `wc -l < devsync/core/models.py` exceeds 2,000.
