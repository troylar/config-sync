---
name: dev-help
description: Show the developer workflow guide with all available skills and conventions
allowed-tools: Bash, Read, Grep, Glob
---

# /dev-help Skill

Display a comprehensive, visually formatted guide to DevSync's developer workflow for experienced developers who are new to the project's command structure.

## Workflow

### Step 1: Gather Context

Read the following to ensure the help is accurate:
1. List all skill files: `ls .claude/commands/`
2. Read `VISION.md` for the project tagline and core principles
3. Read the branch name: `git branch --show-current`
4. Check for open issues: `gh issue list --limit 5 --json number,title,state`

### Step 2: Display the Guide

Print the following formatted guide:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📦 DevSync Developer Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  DevSync distributes AI coding assistant configs across
  teams. pip install devsync — that's the whole pitch.

  📖 Read VISION.md for the full product vision.
  📖 Read CLAUDE.md for architecture and conventions.


🔄 Development Lifecycle
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  The workflow follows this order:

  📋 Prioritize    →  /next
  🏷️ Triage        →  /triage <issue#> <priority>
  💭 Explore idea  →  /ideate
  💡 Create issue  →  /new-issue
  🚀 Start coding  →  /start-work <issue#>
  💾 Save work     →  /commit
  📤 Submit + review → /submit-pr  (auto-runs /code-review)
  🔍 Review others →  /code-review <pr#>
  📦 Ship          →  /deploy
  🧹 Clean up      →  /cleanup


📋 Skills Reference
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  /ideate <rough idea>
    Explore a feature idea before committing to an issue.
    Checks vision, feasibility, and alternatives.
    Presents lean vs. full approaches for discussion.
    No issue created until you're ready.

  /new-issue <description>
    Turn a refined idea into a structured GitHub issue.
    Checks vision alignment before creating.
    Warns if the idea conflicts with product identity.

  /start-work <issue#> [--no-worktree]
    Create a worktree + branch, explore code, plan implementation.
    Worktree is the default — keeps your current branch clean.
    Use --no-worktree for a traditional branch instead.
    Runs 3 parallel agents for deep code exploration.

  /commit
    Stage, validate, and commit with enforced conventions.
    Auto-detects type/scope from changes.
    Runs lint + format + tests on staged files only.
    Format: type(scope): description (#issue)
    No co-author attribution lines.

  /submit-pr [--draft] [--checks-only] [--skip-checks]
    Full validation suite + PR creation + auto code review.
    Runs 5 parallel agents: test thoroughness,
    CLAUDE.md compliance, docs freshness, vision, security.
    After creating the PR, automatically runs /code-review.
    If issues found, offers to fix and re-review (max 2 rounds).

  /pr-check --pr <N>
    Validate someone else's PR in a temp worktree.
    Same checks as /submit-pr but read-only.

  /code-review [<pr#>]
    Deep review with up to 7 parallel agents using
    structured checklists (not open-ended scanning).
    Posts condensed results as a PR comment.

  /next [--all] [--area <area>]
    Prioritized work queue sorted by priority labels.
    Groups issues by VISION.md direction areas.
    Recommends next item with rationale.

  /triage <issue#> <priority> | --reassess
    Set priority on a single issue (critical/high/medium/low).
    --reassess: AI evaluates all open issues against VISION.md.
    Optionally updates ROADMAP.md.

  /cleanup [--dry-run]
    Post-work cleanup: stale branches, orphaned worktrees,
    unclosed issues, stale labels.

  /deploy [patch|minor|major]
    Merge PR, wait for CI, bump version, update CHANGELOG,
    create GitHub release (triggers automated PyPI publish).

  /write-docs <page-path>
    Write or update documentation pages.
    Cross-references source code for accuracy.


⚡ Rules (always active)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  These rules are enforced automatically in every session:

  📌 No code without a GitHub issue
     Every change must reference an issue. No exceptions.

  📌 Commit format: type(scope): description (#issue)
     No co-author attribution. Issue reference required.

  📌 Tests required for new code
     New modules need test files. Bug fixes need
     regression tests.

  📌 Security patterns
     Safe file operations, credential handling, input
     validation, no hardcoded secrets, no eval/exec.

  📌 Vision alignment
     Features are checked against VISION.md principles.
     "What DevSync Is Not" guardrails flag scope drift.

  📌 Consistent output formatting
     All skills use emoji + box-drawing for reports.


🎯 Vision Quick Reference
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Core principles:
    1. Zero-friction distribution (pip install && go)
    2. IDE-agnostic (8+ tools, one format)
    3. Git as distribution (no central server)
    4. Lean CLI (no daemons, no services)
    5. Credential safety (never in repos)
    6. Standards-first (MCP, markdown, YAML)

  What DevSync is NOT:
    ❌ An IDE                ❌ A cloud service
    ❌ A code generator      ❌ A plugin framework
    ❌ A package registry    ❌ A config burden


🛠️ Common Workflows
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Explore an idea:
    /ideate version constraints for packages

  Start a new feature:
    /new-issue add Zed AI tool support
    /start-work 92

  Save progress:
    /commit

  Ready to submit (includes auto code review):
    /submit-pr

  Review a teammate's PR:
    /pr-check --pr 86
    /code-review 86

  Ship a release:
    /deploy

  Find your next task:
    /next

  Triage after a sprint:
    /triage --reassess

  Post-deploy cleanup:
    /cleanup


📂 Project Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  devsync/
  ├── ai_tools/           # AI tool integrations
  │   ├── base.py        # AITool abstract base class
  │   ├── claude.py      # Claude Code integration
  │   ├── cursor.py      # Cursor integration
  │   └── detector.py    # Tool detection logic
  ├── cli/                # Typer CLI commands
  │   ├── main.py        # CLI app definition
  │   ├── install.py     # Install command
  │   └── package.py     # Package management
  ├── core/               # Core business logic
  │   ├── models.py      # Data models
  │   └── repository.py  # Manifest parsing
  ├── storage/            # Data persistence
  │   ├── library.py     # Library manager
  │   └── tracker.py     # Installation tracker
  ├── tui/                # Terminal UI
  │   └── installer.py   # Interactive browser
  └── utils/              # Utilities

  tests/unit/             # Fully mocked unit tests
  tests/integration/      # Real file I/O + Git tests


────────────────────────────────────────────────────────────
  💡 Tip: Run any skill with no arguments for usage help.
  📖 Full details: VISION.md, CLAUDE.md
────────────────────────────────────────────────────────────
```
