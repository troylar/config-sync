---
name: submit-pr
description: Validate, audit, and create a pull request with full pre-submission checks
allowed-tools: Bash, Read, Edit, Grep, Glob, Task
---

# /submit-pr Skill

Run a full validation suite on the current branch and create a pull request with a well-structured description. This is the single skill for "validate and submit my work."

## Usage

```
/submit-pr                          # Submit PR against main
/submit-pr develop                  # Submit PR against a specific base branch
/submit-pr --skip-checks            # Skip validation (not recommended)
/submit-pr --draft                  # Create as draft PR
/submit-pr --checks-only            # Run all checks but don't create the PR
```

## Workflow

### Step 1: Pre-flight (parallel)

**A — Branch status:**
```bash
git branch --show-current
git status --short
git log --oneline main..HEAD
```

**B — Remote status:**
```bash
git remote -v
git rev-list --left-right --count main...HEAD
```

**C — Merge conflicts:**
```bash
git merge-tree $(git merge-base main HEAD) main HEAD
```

Verify:
- We're on a feature branch (not main)
- There are commits ahead of the base branch
- No uncommitted changes (warn if present, suggest committing first)
- Branch can merge cleanly (if not, list conflicting files)

### Step 2: Extract Issue References

From the branch name and all commits, collect issue references:

```bash
git branch --show-current
git log --oneline main..HEAD
```

- Extract all `#N` references from commit messages
- Extract issue number from branch name (`issue-<N>-...`)
- Deduplicate
- Verify each issue exists:
  ```bash
  gh issue view <N> --json state,title --jq '"\(.state): \(.title)"'
  ```
- The primary issue (from branch name) gets `Closes #N` treatment
- Secondary issues get `Addresses #N` or `Related to #N`

If NO issue references are found, abort: "Every PR must reference at least one GitHub issue. Run `/new-issue` to create one."

### Step 3: Code Quality (parallel, unless --skip-checks)

If `--skip-checks` is passed, warn that this is not recommended and skip to Step 9.

Run all checks in parallel:

**A — Lint:**
```bash
ruff check devsync/ tests/ 2>&1 | tail -30
```

**B — Format:**
```bash
black --check devsync/ tests/ 2>&1 | tail -30
```

**C — Unit tests:**
```bash
pytest tests/unit/ -v --tb=short 2>&1 | tail -80
```

**D — Type check:**
```bash
mypy devsync/ --ignore-missing-imports 2>&1 | tail -30
```

These are **blocking** — if any fail, abort. The user must fix issues before submitting.

### Step 3b: Dependency Health (parallel with Steps 4 and 5)

Run these checks in parallel with Steps 4 and 5 — do not wait for 3b to complete before starting Step 4.

**E — Vulnerability audit:**
```bash
pip install pip-audit 2>/dev/null
pip-audit --desc on 2>&1 | tail -30
```
- If `pip-audit` is not installed, skip with warning (non-blocking)
- If vulnerabilities found: **blocking** — abort and show findings

**F — Outdated dependencies:**
```bash
pip list --outdated --format=json 2>/dev/null | python3 -c "
import json, sys
pkgs = json.load(sys.stdin)
for p in pkgs[:10]:
    print(f\"  {p['name']:30s} {p['version']:>10s} → {p['latest_version']}\")
if len(pkgs) > 10:
    print(f'  ... and {len(pkgs)-10} more')
"
```
- **Non-blocking** warning. Show top 10 outdated packages.

**G — New dependency review** (only if `pyproject.toml` changed):
```bash
git diff $BASE..HEAD -- pyproject.toml
```
For each new dependency added to `[project.dependencies]` or `[project.optional-dependencies]`:
1. Query PyPI JSON API: `curl -s --max-time 5 https://pypi.org/pypi/<package>/json`
2. Flag warnings:
   - Unknown or empty license
   - Last release older than 2 years
   - Missing summary/description
3. If PyPI query fails, skip that package (non-blocking)

**Non-blocking** — new deps are informational, not blocking.

**H — Semgrep security scan:**
```bash
pip install semgrep 2>/dev/null
semgrep scan --config p/python --config p/security-audit --config p/owasp-top-ten --error devsync/ 2>&1 | tail -40
```
- If `semgrep` is not installed, skip with warning (non-blocking)
- If Semgrep finds errors (`--error` flag): **blocking** — abort and show findings
- If Semgrep finds only warnings: non-blocking, show in report

### Step 4: Test Coverage for New Code

Check that new or modified Python source files have corresponding unit tests.

1. Get the list of added/modified Python files under `devsync/`:
   ```bash
   git diff --name-only --diff-filter=AM $BASE..HEAD -- 'devsync/**/*.py'
   ```
2. For each file (e.g., `devsync/ai_tools/zed.py`), check if a corresponding test file exists:
   - Expected location: `tests/unit/test_<module_name>.py` (e.g., `tests/unit/test_zed.py`)
   - Also check: `tests/unit/test_<parent>_<module>.py` (e.g., `tests/unit/test_ai_tools_zed.py`)
3. For modified files (not new), check if the test file was also modified — warn if source changed but tests didn't.
4. Flag any new Python modules under `devsync/` that have zero corresponding test files.

Report format:
```
🧪 Test Coverage:
  devsync/ai_tools/zed.py          -> ❌ MISSING (no test file found)
  devsync/cli/package.py           -> ⚠️ WARNING (source changed, tests unchanged)
  devsync/core/repository.py       -> ✅ OK (tests/unit/test_repository.py exists)
```

### Step 5: Deep Analysis (parallel agents, unless --skip-checks)

Launch 5 parallel agents. Use **Haiku** for Agents C and D (docs freshness, vision alignment — lightweight checks). Use **Sonnet** for Agents A, B, and E (test analysis, compliance, security — require deeper reasoning).

**IMPORTANT for ALL agents:** Report ONLY failures and warnings. Do not report passing checks. Keep response under 500 words.

**Agent A — Test Thoroughness (Sonnet):**

Read the new/modified source files and their corresponding test files. Check:
- [ ] Every public function/method has at least one test
- [ ] Both happy path and error paths covered
- [ ] Branching logic (if/else, try/except) has tests for each branch
- [ ] External dependencies (file I/O, Git, network) are mocked
- [ ] Input validation functions tested with valid and invalid inputs

Rate: GOOD (>80% paths), WEAK (50-80%), POOR (<50%).

**Agent B — CLAUDE.md Compliance (Sonnet):**

Get the diff (`git diff $BASE..HEAD`) and read `CLAUDE.md`. Check:
- [ ] Commit messages follow `type(scope): description (#issue)`
- [ ] Every commit references a GitHub issue
- [ ] New AI tools follow `AITool` base class pattern
- [ ] New CLI commands use Typer patterns
- [ ] No hardcoded paths or credentials

**Agent C — Documentation Freshness (Haiku, Authoritative):**

This is the authoritative doc review — identifies stale/missing docs AND applies fixes.

1. Get changed files: `git diff --name-only $BASE..HEAD`
2. Read `CLAUDE.md`, `README.md`, `VISION.md`
3. Check each surface — flag as MISSING or STALE:

**CLAUDE.md:** New modules not documented? Modified modules with stale descriptions? New config/model fields undocumented?

**README.md:** New CLI commands/flags missing? Feature descriptions stale? Install instructions accurate?

**VISION.md:** New capabilities not in "Direction"? Scope boundary changes?

4. **Apply fixes** for MISSING/STALE items directly.
5. Rate: UP TO DATE / FIXED (list files) / NEEDS MANUAL REVIEW.

**Agent D — Vision Alignment (Haiku):**

Read `VISION.md` and the diff (`git diff $BASE..HEAD`). Check:
- [ ] Not an IDE / cloud service / code generator / plugin framework / package registry / config burden
- [ ] New `pyproject.toml` dependencies justified
- [ ] New config options have sensible defaults
- [ ] Lean: could this be simpler? Unnecessary abstractions?

Flag only issues **introduced by this PR**, not pre-existing patterns.

**Agent E — Security Scan (Sonnet):**

Get the diff (`git diff $BASE..HEAD`) and read modified Python files. Check against OWASP ASVS Level 2:
- [ ] **Command injection**: No `subprocess` with `shell=True` + user input
- [ ] **Path traversal**: File ops validate paths (no unsanitized `..`)
- [ ] **Hardcoded secrets**: No API keys/passwords/tokens in source
- [ ] **Insecure defaults**: No debug mode, disabled checks
- [ ] **Input validation**: User input validated at boundaries
- [ ] **Unsafe deserialization**: No `pickle.loads`, `yaml.load()` without SafeLoader, `eval()`, `exec()` with external input
- [ ] **Credential safety**: No credentials stored in manifests or installation records
- [ ] **SQL injection**: Parameterized queries only (if applicable)
- [ ] **Cookie security**: HttpOnly, Secure, SameSite flags (if applicable)
- [ ] **Rate limiting**: Public endpoints rate-limited (if applicable)

Note: Semgrep runs automatically in Step 3b for pattern-based detection. This agent provides deeper semantic analysis that Semgrep cannot catch (data flow, business logic flaws, context-dependent vulnerabilities).

### Step 6: Commit Documentation Fixes

If Agent C in Step 5 flagged documentation as FIXED (it applied updates to CLAUDE.md, README.md, VISION.md):

1. Stage and commit the doc fixes. Extract the primary issue number from the branch name:
   ```bash
   git add CLAUDE.md README.md VISION.md
   git commit -m "docs: update documentation for current changes (#<primary issue>)"
   ```
2. Update the validation report to show docs as fixed rather than stale.

If Agent C rated docs as UP TO DATE, skip this step. If NEEDS MANUAL REVIEW, flag in the report but do not block PR creation.

### Step 7: GitHub Issue Check

Verify all commits reference a GitHub issue:
```bash
git log --oneline $BASE..HEAD
```

For each commit, check that it contains `(#N)` where N is a valid issue number.

### Step 8: Display Validation Report

Display the full validation results locally in the chat:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔍 PR Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔀 Target:   <branch> → main
  📊 Commits:  N commits, M files changed

📋 Branch Status
  Uncommitted:    ✅ / ⚠️ N files
  Merge:          ✅ / ⚠️ N conflicts
  Issues:         ✅ / ⚠️ N commits missing references

📋 Code Quality
  Lint:           ✅ / ❌ N errors
  Format:         ✅ / ❌ N files
  Tests:          ✅ / ❌ N passed, M failed
  Type Check:     ✅ / ❌ / ⏭️

🧪 Test Coverage
  Test Files:     ✅ / ❌ N new modules missing tests
  Thoroughness:   GOOD / WEAK / POOR

📦 Dependency Health
  Vulnerabilities: ✅ / ❌ N vulnerabilities found
  Outdated:        ✅ / ⚠️ N packages outdated
  New Deps:        ✅ / ⚠️ N new deps to review / ⏭️ no pyproject.toml changes
  Semgrep:         ✅ / ❌ N findings / ⏭️ not installed

📝 Compliance
  CLAUDE.md:      ✅ / ⚠️ N issues

🔒 Security
  Scan:           ✅ / ⚠️ N issues

📖 Documentation
  CLAUDE.md:      ✅ / ✅ fixed / ⚠️ needs manual review
  README.md:      ✅ / ✅ fixed / ⚠️ <details>
  VISION.md:      ✅ / ✅ fixed / ⚠️ <details>

🎯 Vision Alignment
  Guardrails:     ✅ / ⚠️ <details>
  Complexity:     ✅ / ⚠️ <new deps, config>
  Lean:           ✅ / ⚠️ <simplicity>

────────────────────────────────────────────
  ✅ Result: READY  /  ❌ Result: NOT READY
────────────────────────────────────────────
```

If `--checks-only` was passed, stop here. Do not create the PR.

If Result is NOT READY, abort and show what to fix.

### Step 9: Generate PR Description

Analyze all commits and changed files to generate the PR body:

```bash
git log --format='%s%n%b' main..HEAD
git diff --stat main..HEAD
git diff main..HEAD
```

Structure the PR body:

```markdown
## Summary

<2-4 bullet points describing what this PR does and why, written for a reviewer>

## Changes

<Grouped by area — ai_tools, cli, core, storage, tui, tests, etc.>

### <Area>
- `file.py` — <what changed and why>

## Issue References

Closes #<primary issue>
Addresses #<secondary issue>

## Test Plan

- [ ] Unit tests pass: `invoke test-unit`
- [ ] Lint passes: `invoke lint`
- [ ] <Specific test scenarios relevant to this PR>

## Security Considerations

<Only include if the PR touches credential handling, file operations, Git commands, or manifest parsing. Otherwise omit this section.>

## Vision Alignment

<Include a brief note on which core principles this PR supports. If the PR adds new dependencies, config options, or infrastructure requirements, note them here with justification. Omit this section for trivial changes.>

---
Generated with [Claude Code](https://claude.ai/code)
```

### Step 10: Push and Create PR

```bash
git push -u origin $(git branch --show-current)
```

Then create the PR:

```bash
gh pr create --title "<title>" --body "$(cat <<'EOF'
<generated body>
EOF
)" <--draft if requested>
```

**Title rules:**
- Under 70 characters
- Format: `<type>: <description> (#<primary issue>)`
- Examples: `feat: add zed ai tool support (#83)`, `fix: handle empty library in install (#91)`

### Step 10b: Transition Issue Labels

After the PR is created, transition the primary issue's label from `in-progress` to `ready-for-review`:

```bash
gh label create "ready-for-review" --color "0075CA" --description "PR submitted" --force
gh issue edit <N> --remove-label "in-progress" --add-label "ready-for-review"
```

### Step 11: Post-creation Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🚀 PR Created
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔗 PR:       #<N> — <title>
  🌐 URL:      <url>
  🔀 Base:     main ← <branch>
  📎 Issues:   Closes #<N>, Addresses #<N>
  📌 Status:   <ready | draft>
  🧪 Checks:   ✅ lint, format, tests, types
  📦 Deps:     ✅ / ⚠️ N vulnerabilities, M outdated
  🔒 Security: ✅ / ⚠️ N issues (Semgrep + agent)
  📖 Docs:     ✅ up to date / ✅ N fixes committed / ⚠️ N need manual review
  🎯 Vision:   ✅ supports <principles>

────────────────────────────────────────────
  🔍 Running code review automatically...
────────────────────────────────────────────
```

### Step 12: Automatic Code Review

Immediately after PR creation, run the full `/code-review` workflow on the new PR.

### Step 13: Fix Loop (if issues found)

If the code review finds issues (score 80+):

1. Display all issues with full context
2. Ask the user for action (Fix all / Fix specific / Skip)
3. If fixing: apply fixes, run checks, commit, push, re-review (max 2 rounds)

### Step 14: Final Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ PR Ready for Review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔗 PR:          #<N> — <title>
  🌐 URL:         <url>
  🔍 Code Review: ✅ clean / ⚠️ N issues remaining
  🔄 Fix Rounds:  <0-2> rounds applied

────────────────────────────────────────────
  👉 Next: wait for CI, or request human review
────────────────────────────────────────────
```

## Guidelines

- Never create a PR without at least one issue reference
- Never create a PR with failing tests (unless --skip-checks)
- Keep the PR title concise — details go in the body
- Group changes logically in the description
- If the PR is large (>500 lines changed), suggest breaking it up
- Security section only when relevant — don't add boilerplate

## Blocking vs Non-Blocking

**Blocking** (abort if failed):
- Lint, format, tests, type check (Step 3)
- pip-audit vulnerabilities (Step 3b-E)
- Semgrep errors (Step 3b-H)
- Missing test files for new modules (Step 4)
- POOR test thoroughness (Step 5-A)

**Non-blocking** (warn, continue):
- Outdated dependencies (Step 3b-F)
- New dependency metadata warnings (Step 3b-G)
- Tools not installed (pip-audit, semgrep — skip with warning)
- WEAK test thoroughness (Step 5-A)
- Documentation needing manual review (Step 5-C)
