---
name: start-work
description: Begin work on a GitHub issue — create branch, explore code, plan implementation
allowed-tools: Bash, Read, Edit, Grep, Glob, Task
---

# /start-work Skill

Set up everything needed to begin implementing a GitHub issue.

## Usage

```
/start-work 83                  # Start work on issue #83 (worktree, default)
/start-work 83 --no-worktree    # Start on a branch in the current tree instead
/start-work 83 --plan-only      # Just create the plan, don't create a branch or worktree
```

The argument is a GitHub issue number.

By default, work is set up in a **git worktree** — a separate working directory linked to the same repo. This keeps your current branch clean and lets you work on multiple features simultaneously without stashing. Use `--no-worktree` if you prefer a traditional branch in the current tree.

## Workflow

### Step 1: Fetch and Validate the Issue

```bash
gh issue view <N> --json number,title,body,labels,state,assignees
```

- If the issue is closed, warn the user and ask if they want to proceed
- If the issue is assigned to someone else, warn the user

### Step 1c: Check Assignment and Status

Ensure lifecycle labels exist (idempotent):
```bash
gh label create "in-progress" --color "6F42C1" --description "Actively being worked on" --force
gh label create "ready-for-review" --color "0075CA" --description "PR submitted" --force
gh label create "blocked" --color "9E9E9E" --description "Blocked by something" --force
```

Check if the issue is already being worked on:

1. **Assignment check:** If the issue is assigned to someone else, warn:
   ```
   ⚠️ #<N> — <title> is assigned to @<user>. Continue anyway?
   ```

2. **Double-up check:** If the issue has the `in-progress` label, warn:
   ```
   ⚠️ #<N> — <title> is already marked as in-progress. Continue anyway?
   ```

3. If the user confirms, assign the issue and add the label:
   ```bash
   gh issue edit <N> --add-assignee @me --add-label "in-progress"
   ```

### Step 1d: Vision Alignment Check

Read `VISION.md` and evaluate the issue against the product vision.

1. Check against the **"What DevSync Is Not"** negative guardrails:
   - Does this make DevSync an IDE? (providing AI assistance, running models)
   - Does this make DevSync a cloud service? (hosted registry, accounts, SaaS)
   - Does this make DevSync a code generator? (creating or modifying instruction content)
   - Does this add a plugin framework? (providing a runtime or API)
   - Does this add configuration burden? (feature that doesn't work without configuration)
   - Does this make DevSync a package registry? (central catalog, approval process)

2. Check against **Out of Scope** (hard no): cloud/SaaS, AI model interaction, IDE plugins, auto-syncing, instruction content creation, complex deployment

3. Run the **Litmus Test**:
   - Does it work with `pip install`?
   - Is it IDE-agnostic?
   - Is it lean?
   - Does it work offline?
   - Would the team use this regularly?

4. Check for **complexity creep**: Does this issue add new dependencies, new config options, or new infrastructure requirements? If so, is each one justified?

**Report:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎯 Vision Alignment: #<N>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Supports:     <which core principles this advances>
  Guardrails:   ✅ / ⚠️ <any "Is Not" concerns>
  Litmus test:  ✅ / ⚠️ <any concerns>
  Scope:        ✅ / ❌
  Complexity:   ✅ / ⚠️ <new deps, config, or infra>

────────────────────────────────────────────
```

- If **[FAIL]**: explain the conflict, suggest alternatives, ask the user how to proceed. Do not create a branch.
- If **[WARN]**: show the concern, ask the user to confirm before proceeding.
- If all **[PASS]**: continue to Step 2.

### Step 2: Check for Existing Work

Check if work has already started on this issue:

```bash
git branch --list "issue-<N>-*"
gh pr list --search "head:issue-<N>" --json number,title,state,headRefName
```

If a branch or PR already exists, show it and ask the user how to proceed:
- Continue on the existing branch
- Start fresh (new branch)
- Abort

### Step 3: Create Branch and Workspace

Generate a branch name from the issue:
- Format: `issue-<N>-<short-description>`
- `<short-description>`: 2-4 words from the issue title, kebab-case, max 50 chars total
- Example: issue #83 "Add Zed AI tool support" -> `issue-83-zed-tool-support`

If `--plan-only` was passed, skip branch/workspace creation.

#### Default: Worktree

Create a branch and set up a worktree in a sibling directory:

```bash
git fetch origin main
git branch issue-<N>-<description> origin/main
git worktree add ../devsync-<N>-<short-description> issue-<N>-<description>
```

Install dev dependencies in the worktree:
```bash
cd ../devsync-<N>-<short-description> && pip install -e ".[dev]" -q
```

The worktree path follows the pattern: `../devsync-<N>-<short-description>` (sibling to the main repo directory).

#### With `--no-worktree`: Traditional Branch

```bash
git checkout main && git pull origin main
git checkout -b issue-<N>-<short-description>
```

### Step 4: Deep Code Exploration (parallel agents)

Launch parallel agents to understand the codebase context for this issue:

**Agent A — Architecture context (Sonnet):**
1. Read `CLAUDE.md` for architecture overview
2. Identify which layer(s) this issue touches (ai_tools, cli, core, storage, tui, utils)
3. List the key files and patterns relevant to this change

**Agent B — Existing implementation (Sonnet):**
1. Based on the issue description and affected files, read the current code
2. Understand existing patterns: how similar features are implemented
3. Identify integration points and dependencies
4. Note any TODOs, FIXMEs, or comments related to this work

**Agent C — Test landscape (Sonnet):**
1. Find test files related to the affected modules
2. Understand testing patterns: fixtures, mocking approach
3. Identify what new tests will be needed

### Step 5: Create Implementation Plan

Based on the exploration, create a structured plan:

```markdown
## Implementation Plan: #<N> — <title>

### Summary
<1-2 sentences on what this change does>

### Files to Create
- `devsync/<path>` — <purpose>
- `tests/unit/test_<name>.py` — <what it tests>

### Files to Modify
- `devsync/<path>` — <what changes and why>
- `devsync/<path>` — <what changes and why>

### Implementation Steps
1. <First thing to do — be specific about what code to write/change>
2. <Next step>
3. <Continue...>
N. Run tests: `invoke test-unit`
N+1. Run lint: `invoke lint`

### Testing Strategy
- <What to test, how to test it>
- <Edge cases to cover>
- <Integration points to verify>

### Risks & Considerations
- <Anything tricky, breaking changes, migration needs>
```

### Step 6: Report

Print:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🚀 Ready to Work: #<N> — <title>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔀 Branch:     issue-<N>-<description>
  📂 Worktree:   ../devsync-<N>-<description>  (or "current directory" if --no-worktree)
  👤 Assigned:   @<user>
  🏷️ Status:     in-progress
  📋 Plan:       <number> steps across <number> files
  🧪 Tests:      <number> existing, <number> new needed
  🎯 Vision:     ✅ supports <principles>

<The implementation plan from Step 5>

────────────────────────────────────────────
  👉 Next: cd ../devsync-<N>-<description> and say "go",
           or adjust the plan
────────────────────────────────────────────
```

## Guidelines

- The plan should be detailed enough that another developer (or Claude session) could follow it
- Don't start coding — this skill only sets up the context and plan
- If the issue description is vague or missing acceptance criteria, flag what's unclear and suggest criteria
- If the issue touches security-sensitive code (credential handling, file operations, Git commands), note security requirements
