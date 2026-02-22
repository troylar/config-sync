---
name: triage
description: Set or reassess priority on issues against VISION.md
allowed-tools: Bash, Read, Grep, Glob, Task
---

# /triage Skill

Set priority on individual issues or reassess all open issues against VISION.md.

## Usage

```
/triage 83 high                          # Set priority on issue #83
/triage 83 critical                      # Set critical priority
/triage 83 medium                        # Set medium priority
/triage 83 low                           # Set low priority
/triage 83 blocked "waiting on #95"      # Mark as blocked with reason
/triage 83 unblock                       # Remove blocked label
/triage --reassess                       # Full reassessment of all open issues
```

## Workflow — Single Issue Mode

### Step 1: Ensure Labels Exist

Create all lifecycle labels idempotently (same as /next Step 1).

### Step 2: Fetch Issue Details

```bash
gh issue view <N> --json number,title,labels,body,state,assignees
```

### Step 3: Update Priority

Set/change priority labels or mark as blocked/unblocked.

### Step 4: Report Change

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🏷️ Triage: #<N> — <title>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Previous:  🟡 medium
  Updated:   🟠 high

────────────────────────────────────────────
  👉 Next: /next to see the updated queue
────────────────────────────────────────────
```

---

## Workflow — Reassess Mode (`--reassess`)

### Step 1: Ensure Labels Exist

Same as single issue mode.

### Step 2: Fetch All Data (parallel)

**A — All open issues:**
```bash
gh issue list --state open --limit 100 --json number,title,labels,body,assignees
```

**B — VISION.md:**
Read `VISION.md` and extract:
- Core principles
- Direction areas (AI Tool Integration, Package Management, MCP, CLI & UX, Docs & Quality)
- Negative guardrails ("What DevSync Is Not")

**C — Recent activity:**
```bash
gh issue list --state closed --limit 20 --json number,title,labels,closedAt
```

### Step 3: Evaluate Each Issue

Launch a Sonnet agent to evaluate all open issues against VISION.md. For each issue, determine:

1. **Vision alignment** — which direction area does it support?
2. **Type** — bug, enhancement, refactor, documentation, testing
3. **Impact** — how many users/use cases does this affect?
4. **Effort** — rough estimate (small/medium/large)
5. **Dependencies** — does it depend on or block other issues?
6. **Suggested priority:**
   - **Critical** — security bugs, data loss, blocking other work
   - **High** — bugs affecting core functionality, features in current sprint direction
   - **Medium** — enhancements aligned with vision, non-blocking improvements
   - **Low** — nice-to-haves, cosmetic, future-looking

### Step 4: Display Proposed Changes

Show table of all issues with current and proposed priorities.

### Step 5: Prompt for Action

Apply all / Pick / Skip

### Step 6: Apply Changes

Set priority labels as approved.

### Step 7: Update ROADMAP.md (optional)

Ask user if they want to regenerate ROADMAP.md based on current priorities.

### Step 8: Summary Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Triage Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔴 Critical:  N issues
  🟠 High:      N issues
  🟡 Medium:    N issues
  🟢 Low:       N issues
  📖 ROADMAP:   updated / skipped

────────────────────────────────────────────
  👉 Next: /next to see the prioritized queue
────────────────────────────────────────────
```

---

## ROADMAP.md Generation

When generating or updating `ROADMAP.md`, use this structure:

```markdown
# DevSync Roadmap

Aligned with [VISION.md](VISION.md). Updated YYYY-MM-DD.

## Critical
- [ ] #N — title

## AI Tool Integration

### High
- [ ] #N — title

### Medium
- [ ] #N — title

## Package Management

### High
- [ ] #N — title

## MCP Integration

### Medium
- [ ] #N — title

## CLI & UX

### Medium
- [ ] #N — title

## Docs & Quality

### Low
- [ ] #N — title

## Other

### Medium
- [ ] #N — title
```

Rules:
- Omit empty sections and subsections
- Critical issues go in a top-level section regardless of area
- Use checkbox format so progress is visible at a glance
- Only include OPEN issues

## Guidelines

- Always show `#N — title` for issue references
- Priority indicators: 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
- In reassess mode, be thorough but not over-triage — when in doubt, suggest medium
- Don't change priorities on `in-progress` issues unless the user specifically targets them
- Blocked issues keep their priority label — `blocked` is a status, not a priority
