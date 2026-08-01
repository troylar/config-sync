# Baseline Health Scorecard — DevSync

Date: 2026-08-01 · v0.15.0 · single-repo · CONTEXT.md read

**Coverage note:** full read of the trust paths (extraction→LLM, credentials,
secret detection, git/install operations) and CLI entry points; structural
read + targeted sampling elsewhere (models, adapters, tests, CI). Per-tool
adapters were sampled, not exhaustively read.

## Vitals

| Dimension | Grade | Why |
|---|---|---|
| Architecture & coupling | B | Clean layering (cli/core/ai_tools/llm/storage); adapters isolate 23 tools behind a registry; marred by a 43-class, 1,702-line models.py and live v1/v2 manifest duplication |
| Correctness & data integrity | B- | Atomic writes and backups exist (utils/backup, test_atomic_write); conflict resolution tested; but 55 broad `except Exception` catches, several returning None/continue, can convert real failures into silent partial installs |
| Security posture | C | **Extraction payload bypasses secret detection entirely** (extractor.py sends raw instruction-file text to the LLM; SecretDetector guards only MCP-config templating). Credentials hygiene is otherwise good: .env-based, gitignore-enforced, non-interactive mode. Semgrep in CI (#91) |
| Performance & scalability | B | CLI workload; no hot loops found; unbounded `read_text` of instruction files is bounded in practice by what projects contain. SUSPECTED only — no profiling. Benchmark workflow exists but its assertions weren't reviewed |
| Observability: logging | B- | Real logging util (setup_logging, leveled, optional file) and logger use in core; but CLI paths mix `console.print` and logger, and most broad catches log at levels users never see — a failed install's *why* often isn't recoverable after the fact |
| Observability: metrics & alerting | N/A | Local CLI — no production surface. Not graded rather than graded F; TRACKER.md should drop this vital |
| Test safety net | B+ | ~22.8k test lines vs 17.5k source; money paths covered (extractor, install_v2, credential prompter, dotenv, git ops, conflict resolution); per-tool adapters each tested. Gap: no test asserts secrets DON'T reach the LLM payload — the exact regression that matters most has no tripwire |
| Dependency & platform health | A- | Dependabot on, Semgrep + dependency checks in CI, sane version floors, py3.10+; black pinned exact, rest ranged |
| Deployability & recoverability | A- | Full pipeline: CI, publish workflow, release drafter, docs build, PyPI. Rollback = pip install previous version; no migration surface |
| Change velocity friction | C+ | The rename debt bites here: **credential/config paths still write `.instructionkit/`** (5 modules, 11 refs) — every future contributor must learn the alias; v1/v2 manifest coexistence means two code paths to update; ROADMAP #86 itself says extraction is Claude-centric against the project's core principle |

## Overall verdict

For a solo side project this codebase is in genuinely good shape — the test
ratio, CI pipeline, and adapter architecture are better than most funded
projects'. If only ONE item gets funded this quarter it must be the
**secret-detection gap in the extraction payload**: this tool's entire pitch
is "safely move your practices between projects," extraction is the first
command a new user runs, and instruction files are exactly where people paste
keys. One leaked credential in an LLM request is the incident that ends a
trust-based tool. Everything else on this list is drag; that one is existential.

## Findings (candidates — nothing tracked until registered)

### 1. Extraction payload bypasses secret detection
- Repo: devsync · Severity: critical · Effort: S · **Verdict: fix before building on top of it**
- extractor.py `_read_instruction_files` reads raw file text; `_extract_with_ai`
  formats it into EXTRACT_PRACTICES_PROMPT and sends to the configured LLM
  provider. SecretDetector (a real, tested detector that exists 30 lines away
  in the same package) is applied only in package_creator.py's MCP-config
  templating — never to the extraction payload.
- Blast radius: any user whose CLAUDE.md/instruction files contain keys, tokens,
  or internal URLs ships them to OpenRouter/OpenAI/Anthropic on first `extract`.
- Interest: grows with every new user; silent by design.
- Cost of inaction: the single trust incident the project cannot survive.
- Evidence: devsync/core/extractor.py:74-118 · devsync/core/package_creator.py:27,103,328

### 2. Rename residue: `.instructionkit` paths live in the credential/storage layer
- Repo: devsync · Severity: high · Effort: S–M · **Verdict: schedule as roadmap item**
- credentials.py writes `.instructionkit/.env` (project) and
  `~/.instructionkit/global/.env`; utils/paths.py, utils/backup.py,
  utils/project.py, ai_tools/mcp_syncer.py carry the same prefix (11 refs).
- Blast radius: user-visible mystery directories under the OLD product name;
  support confusion; migration cost compounds the longer both names coexist.
  Migration needs care — existing users' credentials live at the old path.
- Evidence: devsync/core/mcp/credentials.py:31-32 · devsync/utils/paths.py ·
  devsync/utils/backup.py

### 3. v1/v2 dual architecture still resident
- Repo: devsync · Severity: medium · Effort: M · **Verdict: pay down opportunistically**
- package_manifest.py + package_manifest_v2.py; install_v2/list_v2 naming
  implies a v1 that no current import references (no non-test importer found —
  verify then delete). Dead-or-nearly-dead twin modules tax every reader.
- Evidence: devsync/core/package_manifest.py · package_manifest_v2.py ·
  cli/install_v2.py

### 4. Broad exception handling can hide partial-install failures
- Repo: devsync · Severity: medium · Effort: M (incremental) · **Verdict: pay down opportunistically**
- 55 `except Exception` sites; component_detector alone has 11, several
  continue/return-None. In detection that's arguably policy; in install/write
  paths it converts failures into "worked, mostly" — the user finds out later.
- Evidence: grep `except Exception` devsync/ · core/component_detector.py ·
  core/package_creator.py

### 5. models.py is a 43-class monolith
- Repo: devsync · Severity: low · Effort: M · **Verdict: accept and monitor**
- 1,702 lines, 43 classes, every layer imports it. Cohesion is actually fair
  (they're all models); the cost is merge friction and read time, not
  correctness. Not worth solo-project time now; watch its growth.

## Quick wins
1. Add a secret-detection pass + one test on the extraction payload (the tripwire for Finding 1's regression)
2. Alias-read old `.instructionkit` paths while writing new `.devsync` ones — 90% of Finding 2's user pain, one afternoon
3. Delete package_manifest.py (v1) after confirming zero non-test imports
4. Promote the failed-install log to console at WARN+ so users see the *why*
5. Fix ROADMAP.md link to VISION.md if VISION.md is absent (dangling reference)

## Suggested metrics
| Metric | Measures | Command | Direction |
|---|---|---|---|
| broad-catch count | exception hygiene | `grep -rc "except Exception" devsync/ --include='*.py' \| awk -F: '{s+=$2} END{print s}'` | down |
| instructionkit refs | rename debt burn-down | `grep -rn "instructionkit" devsync/ --include='*.py' \| wc -l` | down to 0 |
| coverage % | safety net | `pytest --cov=devsync -q` (term summary) | hold ≥ current |
| models.py lines | monolith growth | `wc -l < devsync/core/models.py` | not up |

## Handle with care
- **`.instructionkit` paths are load-bearing** — existing installs store
  credentials there; renaming without a read-alias strands users' keys.
- **`_extract_without_ai` fallback** exists and behaves differently from the
  AI path; changes to extraction must keep both paths in parity.
- **23 adapter modules share the capability_registry contract** — a registry
  change fans out to every tool; the per-tool tests are the safety net, run
  them all.

## Tracker-design notes
- Drop "Observability: metrics & alerting" from TRACKER.md's vitals (no prod surface).
- "instructionkit refs" is a vital-worth-tracking-as-number (change-velocity friction proxy).
