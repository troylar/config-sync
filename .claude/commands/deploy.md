---
name: deploy
description: Merge PR, verify CI, bump version, and publish via GitHub Actions
allowed-tools: Bash, Read, Edit, Grep, Glob, WebFetch
---

# /deploy Skill

Deploy the current branch by merging the PR, bumping the version, and triggering automated PyPI publishing via GitHub Actions.

## Usage

```
/deploy              # auto-detect PR and version bump
/deploy patch        # force patch bump
/deploy minor        # force minor bump
/deploy major        # force major bump
```

## Workflow

### Step 1: Pre-flight Checks

1. Confirm we're on a feature branch (not main)
2. Find the open PR for this branch: `gh pr view --json number,title,state,mergeable`
3. If no PR exists, abort with message
4. Show the PR title and number, confirm with user before proceeding
5. **Verify every commit references a GitHub issue.** Run:
   ```bash
   gh pr view --json commits --jq '.commits[].messageHeadline'
   ```
   Every commit message MUST contain a `(#NNN)` issue reference. If any commit is missing one, warn the user and ask them to fix it before proceeding.

### Step 1b: PR Queue Context

Show the user all other open PRs:

```bash
gh pr list --state open --json number,title,headRefName,mergeable --jq '.[] | "\(.number)\t\(.mergeable)\t\(.title)"'
```

### Step 2: Quick Documentation Check

Run a lightweight staleness check:

1. **New modules** — check for any new `.py` files under `devsync/` not documented in CLAUDE.md. Flag if any are missing.
2. **Version** — note the pre-bump version in `pyproject.toml` for reference.

If updates are needed, commit them before merging:
```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for vX.Y.Z release (#<primary issue>)"
git push
```

### Step 3: Rebase, Validate Freshness, and Merge

#### 3a. Check if main has moved

```bash
git fetch origin main
MERGE_BASE=$(git merge-base HEAD origin/main)
MAIN_HEAD=$(git rev-parse origin/main)
```

Report whether main is unchanged or has moved since branch was based.

#### 3b. Rebase

```bash
git rebase origin/main
git push --force-with-lease
```

#### 3c. Wait for CI

If main had moved, wait for CI to re-run. Poll every 15 seconds, up to 10 minutes:
```bash
gh pr checks <PR> --json name,state
```

#### 3d. Evaluate check results

- **All checks pass**: proceed to merge
- **Only non-required checks fail**: proceed with `--admin` — log which checks were bypassed
- **Required checks fail** (tests, lint): abort and show failure URL

#### 3e. Merge (worktree-aware)

```bash
gh pr merge <PR> --squash
```

Clean up worktree and branch if running from a worktree:
```bash
WORKTREE_PATH=$(git rev-parse --show-toplevel)
MAIN_WORKTREE=$(git worktree list --porcelain | grep -A0 'worktree ' | head -1 | sed 's/worktree //')
if [ "$WORKTREE_PATH" != "$MAIN_WORKTREE" ]; then
    BRANCH=$(git branch --show-current)
    cd "$MAIN_WORKTREE"
    git worktree remove "$WORKTREE_PATH"
    git branch -d "$BRANCH" 2>/dev/null || true
fi
```

Pull merged changes:
```bash
cd <main worktree path>
git checkout main && git pull
```

### Step 3f: Post-Merge Queue Check

Check whether other open PRs are affected by this merge.

### Step 4: Determine Version Bump

Read `pyproject.toml` to get current version.

If the user passed a bump level (patch/minor/major), use that.

Otherwise, determine from the merged PR:
- `feat:` or new files added -> **minor**
- `fix:`, `docs:`, `chore:`, `refactor:`, `test:` -> **patch**
- `BREAKING CHANGE` or `!:` in any commit -> **major**

### Step 5: Run Pre-Release Checks

```bash
invoke release-check
```

This runs clean, quality, and test. If it fails, abort.

### Step 6: Update Version and CHANGELOG

1. Bump version in `pyproject.toml`
2. Update `CHANGELOG.md` with changes since last release:
   ```bash
   git log <PREVIOUS_TAG>..HEAD --oneline
   ```
3. Commit:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: bump version to X.Y.Z"
   ```
4. Tag:
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   ```
5. Push:
   ```bash
   git push origin main --tags --no-verify
   ```

Note: `--no-verify` bypasses the pre-push hook that blocks direct pushes to main. This is intentional for the deploy skill.

### Step 7: Create GitHub Release (Triggers Automated Publishing)

Generate release notes from the PR and all referenced issues.

```bash
gh release create vX.Y.Z --title "vX.Y.Z" --notes "<generated notes>"
```

**What happens next:** The `.github/workflows/publish.yml` workflow will automatically:
1. Run quality checks and tests
2. Build the package
3. Publish to PyPI using trusted publishing

### Step 7b: Clean Up Issue Labels

For each issue closed by the merged PR, remove workflow labels:
```bash
gh issue edit <N> --remove-label "in-progress" --remove-label "ready-for-review"
```

### Step 7c: Suggest Cleanup

Check for stale local branches and suggest `/cleanup` if any exist.

### Step 8: Monitor and Verify

```bash
gh run watch
```

Wait for the workflow to complete, then verify:
```bash
pip install --upgrade devsync
devsync --version
```

## Error Handling

- If merge fails: show error, do not proceed
- If CI fails: show failure URL, do not proceed
- If release-check fails: show error, do not proceed
- If GitHub Actions publish fails: the tag and version commit are already pushed; show error and link to workflow run
- Never force-push or amend commits on main
- If commits are missing issue references: warn, do not proceed until fixed

## Output

On success:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📦 Deployed devsync vX.Y.Z
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔗 PR:       #NN (merged)
  🧪 CI:       ✅ passed
  🔄 Freshness: ✅ CI ran against current main / ⚠️ rebased and re-validated
  📖 Docs:     ✅ up to date / ⚠️ N updates committed
  📦 PyPI:     https://pypi.org/project/devsync/X.Y.Z/
  🏷️ Tag:      vX.Y.Z
  🏷️ Release:  https://github.com/troylar/devsync/releases/tag/vX.Y.Z
  📊 Version:  X.Y.Z-1 → X.Y.Z (<type> bump)
  📋 Queue:    N open PRs remaining (N mergeable, N conflicting)

────────────────────────────────────────────
  ✅ Deploy complete
────────────────────────────────────────────
```

On failure:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ❌ Deploy Failed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Step:    <which step failed>
  Error:   <error message>

────────────────────────────────────────────
  👉 Next: <what to do to fix it>
────────────────────────────────────────────
```
