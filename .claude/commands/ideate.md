---
name: ideate
description: Explore and refine a feature idea before committing to an issue
allowed-tools: Bash, Read, Grep, Glob, Task
---

# /ideate Skill

Have a structured conversation about a feature idea before creating an issue. Explore feasibility, vision alignment, complexity, and alternative approaches — without committing to anything.

## Usage

```
/ideate version constraints for package dependencies
/ideate what if we added a central package registry
/ideate I want to make credential management more seamless
```

The argument is a rough idea — it can be vague, ambitious, or half-formed. That's the point.

## Workflow

### Step 1: Understand the Idea

Parse the user's input and restate it back clearly:
- What is the user trying to achieve?
- Who benefits from this?
- What problem does it solve?

Ask clarifying questions if the idea is too vague to evaluate. Keep it to 1-2 targeted questions, not an interrogation.

### Step 2: Vision Check

Read `VISION.md` and evaluate the idea against the product vision.

Check against **"What DevSync Is Not"** negative guardrails:
- Does this make DevSync an IDE?
- Does this make DevSync a cloud service?
- Does this make DevSync a code generator?
- Does this make DevSync a plugin framework?
- Does this make DevSync a package registry?
- Does this add configuration burden?

Check against **Out of Scope** (hard no): cloud/SaaS, AI model interaction, IDE plugins, auto-syncing, instruction content creation, complex deployment.

Run the **Litmus Test**:
- Does it work with `pip install`?
- Is it IDE-agnostic?
- Is it lean? Could we do this with less?
- Does it work offline?
- Would the team use this regularly?

Display the alignment:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎯 Vision Alignment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Supports:     <which core principles>
  Guardrails:   ✅ / ⚠️ <any "Is Not" concerns>
  Scope:        ✅ / ❌ <if it hits an out-of-scope area>
  Litmus test:  ✅ / ⚠️ <flag any concerns>

────────────────────────────────────────────
```

Do NOT stop here if there are warnings. This is ideation — explore the tension, don't block on it.

### Step 3: Explore Feasibility (parallel Sonnet agents)

Launch 2 parallel Sonnet agents:

**Agent A — Technical landscape:**
1. Read `CLAUDE.md` for architecture overview
2. Search the codebase for related modules, patterns, and existing infrastructure
3. Identify what exists, what's new, which parts are affected, rough complexity

**Agent B — Prior art and alternatives:**
1. Search existing GitHub issues: `gh issue list --search "<keywords>" --state all --limit 10`
2. Check if similar features exist in the codebase
3. Think about simpler alternatives that achieve 80% of the goal with 20% of the effort

### Step 4: Present the Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💡 Ideation: <idea summary>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📐 Feasibility
  Complexity:     Small / Medium / Large
  Builds on:      <existing modules/patterns>
  New code:       <what would be created>
  Affected files: <list of areas>
  Blockers:       <any technical blockers, or "none">

🔗 Related
  Existing issues: <list any related issues, or "none found">
  Existing code:   <anything in the codebase that helps>

💡 Approaches
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  A) <Lean approach>
     Complexity: <Small/Medium>
     Trade-offs: <what you give up>
     Vision fit: ✅ / ⚠️

  B) <Full approach>
     Complexity: <Medium/Large>
     Trade-offs: <what you gain vs. cost>
     Vision fit: ✅ / ⚠️

  C) <Alternative framing> (if applicable)
     Vision fit: ✅ / ⚠️

────────────────────────────────────────────
```

Always present at least 2 approaches — a lean version and a fuller version.

### Step 5: Open Discussion

```
────────────────────────────────────────────
  🗣️ What do you think?

  Options:
    → Discuss further — ask questions, refine the idea
    → Pick an approach — I'll draft as /new-issue
    → Park it — save the idea for later
    → Drop it — this isn't the right direction

────────────────────────────────────────────
```

### Step 6: Resolution

Based on the user's decision: hand off to `/new-issue`, create a `discussion` issue, or move on.

## Guidelines

- This is a **safe space for ideas** — don't shut things down, explore them
- Always present alternatives, even for well-aligned ideas
- Vision warnings are discussion points, not stop signs
- Be honest about complexity
- Keep the tone collaborative
