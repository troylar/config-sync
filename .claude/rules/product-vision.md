# Product Vision Alignment

Before creating issues, planning features, or starting work, check that the proposed work aligns with the product vision in `VISION.md`.

## Quick Reference — Core Principles

1. **Zero-friction distribution** — pip install and go. No Docker, no external services required.
2. **IDE-agnostic** — 8+ AI tools, one package format, no lock-in.
3. **Git as distribution** — no central server, any Git repo works.
4. **Lean CLI** — Typer + Rich, no daemons, no background processes.
5. **Credential safety** — credentials never in repos, always prompted or env vars.
6. **Standards-first** — MCP protocol, conventional markdown, YAML manifests.

## What DevSync Is Not (Negative Guardrails)

These are identity-level constraints. If a feature makes DevSync more like any of these, flag it.

- **Not an IDE** — DevSync manages configs, it doesn't provide AI assistance, run models, or execute code
- **Not a cloud service** — no hosted registry, no accounts, no SaaS tier. Local CLI only
- **Not a code generator** — distributes instructions, doesn't create or modify them
- **Not a plugin framework** — installs files to the right places, doesn't provide a runtime or API
- **Not a package registry** — no central registry, no publishing step, no approval process. Any Git repo is a valid source
- **Not a configuration burden** — zero configuration must always work. Every option needs a sensible default

## Out of Scope (Hard No)

Do not build or propose features in these areas:
- Cloud hosting or SaaS
- AI model interaction or content generation
- IDE plugins or extensions
- Automatic syncing or file watching (daemons)
- Instruction content creation or editing
- Complex deployment requirements

## The Litmus Test

When evaluating a feature idea, ask:
1. Does it work with `pip install`?
2. Is it IDE-agnostic?
3. Is it lean? Could we do this with less?
4. Does it work offline (for downloaded repos)?
5. Would the team use this regularly?

If the answer to any of these is "no," flag the concern before proceeding. Read `VISION.md` for the full product vision.

## When Ideas Don't Align

If a user proposes work that conflicts with the vision:
- Don't silently proceed — raise the concern directly
- Explain which principle it conflicts with
- Suggest an alternative approach that aligns, if one exists
- If the user wants to proceed despite the concern: go ahead, but:
  1. Add the `vision-review` label to the issue/PR
  2. Note the specific vision tension in the issue/PR description
  3. This ensures the project owner can batch-review vision-flagged work

## When Ideas Are Ambiguous

If alignment isn't clear:
- Ask the user how the feature relates to the core use cases (team config distribution, multi-tool support, package management)
- Check if the feature adds external dependencies or infrastructure requirements
- Consider whether it increases or decreases the "pip install to productive" time
