---
name: next
description: Prioritized work queue sorted by priority labels and VISION.md alignment
allowed-tools: Bash, Read, Grep, Glob, Task
---

# /next Skill

Show a prioritized work queue of open issues, sorted by priority labels and grouped by VISION.md direction areas.

## Usage

```
/next                      # Prioritized queue (excludes in-progress/blocked)
/next --all                # Include in-progress and blocked issues
/next --area mcp           # Filter by vision direction area
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

### Step 2: Fetch Data (parallel)

**A — All open issues:**
```bash
gh issue list --state open --limit 100 --json number,title,labels,assignees,body
```

**B — VISION.md direction areas:**
Read `VISION.md` and extract the "Direction (Current)" section. Identify the 5 direction areas:
- AI Tool Integration
- Package Management
- MCP Integration
- CLI & UX
- Docs & Quality

**C — In-progress and blocked issues:**
```bash
gh issue list --label "in-progress" --state open --json number,title,labels,assignees
gh issue list --label "blocked" --state open --json number,title,labels,assignees
```

### Step 3: Categorize Each Issue

For each open issue:

1. **Priority** — from `priority:*` labels:
   - `priority:critical` -> Critical
   - `priority:high` -> High
   - `priority:medium` -> Medium
   - `priority:low` -> Low
   - No priority label -> Medium (default)

2. **Vision area** — keyword match the issue title and body against direction areas:
   - AI Tool Integration: ai tool, IDE, cursor, claude, windsurf, copilot, kiro, roo, cline, codex, translator, detection
   - Package Management: package, manifest, template, version, dependency, bundle, component
   - MCP Integration: MCP, server config, credential, sync
   - CLI & UX: CLI, command, TUI, Typer, Rich, output, error, UX
   - Docs & Quality: doc, test, CI, coverage, lint, quality, README
   - Other: anything that doesn't match

3. **Status:**
   - `in-progress` label -> In Progress
   - `blocked` label -> Blocked
   - `ready-for-review` label -> Ready for Review
   - None -> Ready

4. **Dependencies** — scan issue body for "depends on #N" / "blocked by #N"

### Step 4: Filter

- Default: exclude issues with `in-progress`, `blocked`, or `ready-for-review` labels
- With `--all`: include everything
- With `--area <area>`: only show issues matching that vision area

### Step 5: Display Queue

Sort by priority tier (critical -> high -> medium -> low), then by issue number.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📋 Work Queue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 AI Tool Integration
  🟡 #83 — Add Zed AI tool support
  🟢 #91 — Improve cursor rule translation

📋 Package Management
  🟡 #95 — Add version constraint support
  🟢 #110 — Template system for packages

📋 MCP Integration
  🟡 #88 — Credential sync improvements

📋 CLI & UX
  🟡 #102 — Better error messages for install failures

📋 Docs & Quality
  🟢 #115 — Increase test coverage

────────────────────────────────────────────

  🔴 Critical: 0  🟠 High: 0  🟡 Medium: 4  🟢 Low: 3
  📊 Total: 7 issues ready to work

────────────────────────────────────────────
```

### Step 6: Recommend Next Item

```
  ⭐ Recommended: #83 — Add Zed AI tool support
     Rationale: Highest priority in AI Tool Integration,
     no dependencies, aligns with IDE-agnostic principle.

────────────────────────────────────────────
  👉 Next: /start-work 83
────────────────────────────────────────────
```

## Guidelines

- Always show `#N — title` for issue references
- Default view should be actionable — only show issues you can start right now
- If there are 0 issues ready, say so and suggest `/triage --reassess` or `/new-issue`
- Priority indicators: 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
