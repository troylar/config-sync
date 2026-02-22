---
name: code-review
description: Code review a pull request with security audit and test verification
allowed-tools: Bash, Read, Edit, Grep, Glob, Task, WebFetch
---

# /code-review Skill

Review a pull request for bugs, security issues, CLAUDE.md compliance, and test results.

## Usage

```
/code-review 85        # Review PR #85
/code-review           # Review PR for current branch
```

## Workflow

### Step 1: Resolve PR Number

If a PR number is provided as an argument, use it. Otherwise, detect the PR for the current branch:
```bash
gh pr view --json number --jq '.number'
```

### Step 2: Eligibility and Context Detection

Check if the PR is eligible for review:
```bash
gh pr view <PR> --json state,isDraft,author,title,body,reviews
gh api repos/{owner}/{repo}/issues/<PR>/comments --jq '.[].body'
```

Do NOT proceed if: PR is closed/merged, is a draft, is automated, or already has a code review comment.

**Submit-PR detection:** Check if a `/submit-pr` validation comment exists. If found, set `submit_pr_ran = true`.

### Step 2b: PR Size Check

```bash
gh pr diff <PR> --stat | tail -1
```
If under 300 lines, set `small_pr = true`.

### Step 3: Gather Context (parallel Haiku agents)

**Agent A — CLAUDE.md paths:** Find all relevant CLAUDE.md files.

**Agent B — PR summary:** Run `gh pr view <PR>` and `gh pr diff <PR>`. Return summary.

**Agent C — Run unit tests:** Run `pytest tests/unit/ -v --tb=short 2>&1 | tail -80` or `invoke test-unit`.

### Step 4: Deep Review (conditional parallel agents)

| Condition | Agents to run |
|-----------|--------------|
| `submit_pr_ran = true` | #2 Bug scan, #4 Historical context, #5 Code comments |
| `small_pr = true` AND standalone | #2 Bug scan, #3 Security, #4 Historical context |
| Standalone, large PR | All 7 agents |

**Bug scan (#2) ALWAYS runs.**

**IMPORTANT:** Report ONLY failures. Do not report PASS or N/A items. Keep response under 500 words.

---

**Agent #1 — CLAUDE.md compliance (Sonnet):** *(skipped when `submit_pr_ran`)*

- [ ] New modules follow existing naming conventions
- [ ] New AI tools follow `AITool` base class pattern
- [ ] New CLI commands use Typer patterns
- [ ] No hardcoded paths or credentials
- [ ] Commits follow `type(scope): description (#issue)`
- [ ] No Co-Authored-By or Claude attribution lines

---

**Agent #2 — Bug scan (Sonnet):** *(ALWAYS runs)*

- [ ] **Return values**: Unchecked None returns?
- [ ] **Off-by-one**: Loop bounds, slice indices
- [ ] **Type mismatches**: Wrong types in YAML parsing, dict access
- [ ] **Null/empty handling**: Empty lists, missing dict keys, blank strings
- [ ] **Resource leaks**: Files/connections not closed? Missing `with`?
- [ ] **Exception handling**: Too broad? Swallowed silently?
- [ ] **String formatting**: Command concatenation with user input?
- [ ] **Import errors**: Missing or circular imports?
- [ ] **Logic inversion**: Negated conditions, `and`/`or` confusion?
- [ ] **Path handling**: Platform-specific paths? Unsanitized joins?

---

**Agent #3 — Security audit (Sonnet):** *(skipped when `submit_pr_ran`)*

- [ ] **Command injection**: `subprocess` with `shell=True` + user input?
- [ ] **Path traversal**: File ops with unsanitized `..`?
- [ ] **Hardcoded secrets**: API keys/passwords/tokens in source?
- [ ] **Insecure defaults**: Debug mode, disabled checks?
- [ ] **Input validation**: User input not validated?
- [ ] **Unsafe deserialization**: `pickle.loads`, `yaml.load()` without SafeLoader, `eval()`, `exec()`?
- [ ] **Credential safety**: Credentials stored in manifests or JSON trackers?
- [ ] **Git URL safety**: Credentials embedded in repo URLs?

---

**Agent #4 — Historical context (Haiku):** *(ALWAYS runs)*

Maximum 15 tool calls. Check:
- [ ] **Reverted fixes**: Does this undo a previous fix?
- [ ] **Recurring patterns**: Similar bugs in this file before?
- [ ] **TODO/FIXME regression**: TODOs addressed or ignored?
- [ ] **Breaking assumptions**: Violated documented assumptions?

---

**Agent #5 — Code comments and intent (Sonnet):** *(ALWAYS runs)*

- [ ] **Invariant violations**: "must be called after X" / "never modify without Y" — violated?
- [ ] **TODO completion**: TODOs this change should address but didn't?
- [ ] **Warning heeds**: `# WARNING:` / `# IMPORTANT:` — complied with?
- [ ] **Docstring accuracy**: Modified functions still match their docstrings?

---

**Agent #6 — Vision and scope alignment (Haiku):** *(skipped when `submit_pr_ran`)*

- [ ] Not an IDE / cloud service / code generator / plugin framework / package registry / config burden
- [ ] New dependencies justified
- [ ] New config options have sensible defaults
- [ ] Lean: could this be simpler?

---

**Agent #7 — Documentation freshness (Haiku):** *(skipped when `submit_pr_ran`)*

- [ ] New modules not in CLAUDE.md?
- [ ] Modified modules with stale CLAUDE.md descriptions?
- [ ] New CLI commands/flags missing from README?

### Step 5: Confidence Scoring (parallel Haiku agents)

For each FAIL item, independently verify and score confidence (0-100).

### Step 6: Filter

Keep only issues scoring 80+.

### Step 7-10: Report, Post Comment, Summary

Display local report, post condensed version as PR comment, show final summary.

### Link Format

```
https://github.com/troylar/devsync/blob/<full-40-char-sha>/path/to/file.py#L10-L15
```

## Notes

- Do NOT run builds or typechecks — CI handles those separately
- Use `gh` for all GitHub interactions
- Cite and link every issue
