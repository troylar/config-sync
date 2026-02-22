---
name: pr-check
description: Validate an existing PR or remote branch without submitting
allowed-tools: Bash, Read, Edit, Grep, Glob, Task
---

# /pr-check Skill

Run the full validation suite on an **existing PR** or a **remote branch** — without creating or modifying anything. Use this to review someone else's work, or to re-check your own PR after updates.

For validating and submitting your own branch, use `/submit-pr` instead (which includes all these checks plus PR creation).

## Usage

```
/pr-check --pr 86                      # Check an existing GitHub PR by number
/pr-check --branch feature/foo         # Check a local branch (without switching)
/pr-check --worktree /path/to/wt       # Check code in an existing worktree
/pr-check --pr 86 develop              # Check PR #86 against develop (not main)
```

## When to Use

- **Reviewing a collaborator's PR** — run `/pr-check --pr 86` before approving
- **Re-checking after updates** — run `/pr-check --pr 86` after the author pushes fixes
- **Checking a branch without submitting** — run `/pr-check --branch feature/foo`
- **For your own work before submitting** — use `/submit-pr --checks-only` instead

## Workflow

### Step 0: Resolve Target

1. **Determine the base branch.** Use the bare positional argument if provided, otherwise default to `main`.
2. **Determine the working directory** based on the flags:

   | Flag | Action | Working directory |
   |------|--------|-------------------|
   | `--pr <N>` | `git fetch origin pull/<N>/head:pr-<N>-check`, create temp worktree | Temp worktree path |
   | `--branch <name>` | Create temp worktree from local branch | Temp worktree path |
   | `--worktree <path>` | Validate path exists and is a git worktree | Provided path |

3. **For temp worktrees:** create under `<repo-parent>/devsync-pr-check-<id>`.

### Steps 1–7: Full Validation Suite

Run the same validation steps as `/submit-pr` Steps 1–7, but with all commands prefixed with `cd $DIR &&`.

Quality commands for devsync:
- Lint: `ruff check devsync/ tests/` or `invoke lint`
- Format: `black --check devsync/ tests/` or `invoke format --check`
- Tests: `pytest tests/unit/ -v --tb=short` or `invoke test-unit`
- Types: `mypy devsync/` or `invoke typecheck`

### Step 8: Cleanup

If a temp worktree was created, remove it and its branch.

### Step 9: Recommendations

```
────────────────────────────────────────────
  👉 Next steps:
    - <if issues found> Request changes on the PR
    - <if clean> Approve and merge
    - <if docs stale> Suggest doc updates to the author
────────────────────────────────────────────
```
