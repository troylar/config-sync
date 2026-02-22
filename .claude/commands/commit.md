---
name: commit
description: Create a well-formatted commit with enforced conventions
allowed-tools: Bash, Read, Grep, Glob
---

# /commit Skill

Create a commit that follows this project's conventions. Validates format, issue references, and test status before committing.

## Usage

```
/commit                              # Auto-detect type, scope, and message from changes
/commit fix(core): handle empty manifest gracefully (#91)
/commit --amend                      # Amend the last commit (use sparingly)
```

If a message is provided, validate and use it. If no message is provided, generate one from the staged/unstaged changes.

## Workflow

### Step 1: Assess Changes

Run in parallel:
```bash
git status --short
git diff --cached --stat
git diff --stat
```

- If nothing is staged and nothing is modified, abort: "Nothing to commit."
- If nothing is staged but files are modified, show the modified files and ask what to stage.

### Step 2: Determine the Issue Number

The current branch should be named `issue-<N>-...`. Extract the issue number:
```bash
git branch --show-current
```

If the branch name doesn't contain an issue number:
1. Check recent commits for an issue reference
2. If still not found, ask the user: "Which GitHub issue does this commit relate to?"

Verify the issue exists:
```bash
gh issue view <N> --json state,title --jq '"\(.state): \(.title)"' 2>&1
```

### Step 3: Generate or Validate Message

**If a message was provided:** Validate it matches `type(scope): description (#N)`:
- Correct type (feat/fix/docs/refactor/test/chore)
- Scope matches a known module (cli, core, storage, ai_tools, tui, utils)
- Issue reference present and matches the branch issue
- Description is lowercase, imperative, no trailing period

If validation fails, show what's wrong and suggest a corrected version.

**If no message was provided:** Generate one:
1. Analyze the diff to determine:
   - **type**: new files/functions -> `feat`, bug fix -> `fix`, tests only -> `test`, docs only -> `docs`, restructuring -> `refactor`, everything else -> `chore`
   - **scope**: primary module being changed (by file count or significance)
   - **description**: concise summary of what changed, imperative mood
2. Draft: `type(scope): description (#N)`

### Step 4: Stage Files

If files aren't staged yet:
1. Show the list of modified/untracked files
2. Stage the relevant files (not `.env`, credentials, or large binaries):
   ```bash
   git add <specific files>
   ```
3. Never use `git add -A` or `git add .` — always add specific files

### Step 5: Pre-commit Checks

Get the list of staged Python files first:
```bash
git diff --cached --name-only --diff-filter=ACMR -- '*.py'
```

Run checks scoped to staged files:
```bash
ruff check <staged files> 2>&1 | tail -20
black --check <staged files> 2>&1 | tail -20
```

Run tests:
```bash
pytest tests/unit/ -x -q 2>&1 | tail -20
```

- If lint fails: auto-fix with `ruff check --fix <staged files>`, then re-stage only those files
- If format fails: auto-fix with `black <staged files>`, re-stage only those files, continue
- If tests fail: abort and show failures. Do not commit with failing tests.
- Never auto-fix or re-stage files that aren't already staged

### Step 5b: Complexity Check

Scan the staged diff for vision-relevant changes:

1. **New dependencies**: Check if `pyproject.toml` is staged and has new entries in `dependencies` or `dev` dependencies. If so, note them.
2. **New config options**: Check if config-related files are staged with new user-facing settings. Flag if a default would suffice.
3. **New infrastructure**: Check for Docker files, external service integrations, or daemon-like patterns.

If any are found, report them briefly:
```
  [WARN] New dependency: <package> — is this justified?
  [WARN] New config option: <option> — could a default work?
```

This is informational, not blocking — but the warnings should prompt the developer to reconsider if the addition is necessary.

### Step 6: Commit

**IMPORTANT:** Do NOT include any Co-Authored-By line or Claude attribution.

```bash
git commit -m "type(scope): description (#N)"
```

### Step 7: Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Committed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  💬 Message:  type(scope): description (#N)
  🔑 SHA:      <short sha>
  📁 Files:    <N> changed, <N> insertions(+), <N> deletions(-)
  🔗 Issue:    #<N> — <issue title>

  🧪 Checks:   ✅ lint, format, tests (<N> passed)
  ⚠️ Warnings: <any complexity warnings, or "none">

────────────────────────────────────────────
  👉 Next: <context-aware suggestion>
────────────────────────────────────────────
```

To determine the next step suggestion, check for an existing PR:
```bash
gh pr list --head "$(git branch --show-current)" --json number,url --jq '.[0]' 2>/dev/null
```

- **If a PR exists**: `👉 Next: push to update PR #<N>, or continue working`
- **If no PR exists**: `👉 Next: /submit-pr when ready, or continue working`

## Amend Mode

If `--amend` is passed:
1. Show the current HEAD commit message and changes
2. Confirm with the user before amending
3. Use `git commit --amend` instead of `git commit`
4. Warn if the commit has already been pushed

## Guidelines

- Never commit without a passing test suite
- Never commit secrets, `.env` files, or credentials
- Never use `git add -A` or `git add .`
- Never include Co-Authored-By or Claude attribution lines
- If in doubt about the scope, prefer the more specific module name
- One logical change per commit — if the staged changes span unrelated work, suggest splitting into multiple commits
