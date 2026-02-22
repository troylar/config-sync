---
name: cleanup
description: Post-work cleanup — stale branches, orphaned worktrees, unclosed issues, stale labels
allowed-tools: Bash, Read, Grep, Glob, Task
---

# /cleanup Skill

Clean up stale branches, orphaned worktrees, unclosed issues, and stale labels after work is merged and deployed.

## Usage

```
/cleanup              # Show report and clean interactively
/cleanup --dry-run    # Show report only, no changes
```

## Workflow

### Step 1: Ensure Labels Exist

Create all lifecycle labels idempotently:

```bash
gh label create "priority:critical" --color "B60205" --description "Blocking other work" --force
gh label create "priority:high" --color "D93F0B" --description "Important, should be next" --force
gh label create "priority:medium" --color "FBCA04" --description "Standard priority" --force
gh label create "priority:low" --color "0E8A16" --description "Nice to have" --force
gh label create "in-progress" --color "6F42C1" --description "Actively being worked on" --force
gh label create "ready-for-review" --color "0075CA" --description "PR submitted" --force
gh label create "blocked" --color "9E9E9E" --description "Blocked by something" --force
```

### Step 2: Gather State (parallel)

Launch parallel operations to collect cleanup candidates:

**A — Stale local branches:**
```bash
git branch --list "issue-*"
```
For each branch, extract the issue number and check if the issue is CLOSED.

**B — Stale remote branches:**
```bash
git fetch --prune origin
git branch -r --list "origin/issue-*"
```
For each, check if there's a merged PR.

**C — Orphaned worktrees:**
```bash
git worktree list --porcelain
```
For each worktree (not the main one), check if the branch still exists and if the associated issue is CLOSED. Worktree paths follow the pattern `../devsync-<N>-<description>`.

**D — Issues with stale labels:**
```bash
gh issue list --label "in-progress" --state closed --json number,title
gh issue list --label "ready-for-review" --state closed --json number,title
```

**E — Open issues with stale in-progress label:**
```bash
gh issue list --label "in-progress" --state open --json number,title
```
Check if a corresponding branch exists locally or remotely.

### Step 3: Reconcile Merged PRs with Open Issues

Find merged PRs whose closing issues are still OPEN:
```bash
gh pr list --state merged --limit 20 --json number,title,closingIssuesReferences
```

### Step 4: Display Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🧹 Cleanup Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Local Branches to Delete
  issue-83-zed-tool-support        → #83 — Add Zed AI tool support (CLOSED)

📋 Remote Branches to Prune
  origin/issue-83-zed-tool-support → PR #100 — feat: zed tool support (merged)

📋 Worktrees to Remove
  ../devsync-83-zed-tool-support   → #83 — Add Zed AI tool support (CLOSED)

📋 Issues to Close
  #128 — Handle missing manifest    → merged via PR #135

📋 Stale Labels to Remove
  #91 — Install crash on empty lib  → remove `in-progress` (issue closed)

────────────────────────────────────────────
  📊 Summary: N branches, N worktrees, N issues, N labels
────────────────────────────────────────────
```

### Step 5: Check for Dry Run

If `--dry-run` was passed, stop here.

### Step 6: Prompt for Action

Options: Clean all / Pick categories / Abort

### Step 7: Execute Cleanup

For each approved category: delete branches, remove worktrees, close issues, clean labels.

### Step 8: Post-Cleanup Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Cleanup Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔀 Branches deleted:  N local, N remote
  📂 Worktrees removed: N
  📋 Issues closed:     N
  🏷️ Labels cleaned:    N

────────────────────────────────────────────
  👉 Next: /next to find your next task
────────────────────────────────────────────
```

## Guidelines

- Always show `#N — title` for issue references
- Always show `PR #N — title` for PR references
- Never delete branches or worktrees without user confirmation
- Be careful with `git worktree remove --force` — only use when the worktree's branch is confirmed gone
- If a worktree has uncommitted changes, warn the user and skip it
