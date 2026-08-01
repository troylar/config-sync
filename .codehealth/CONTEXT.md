# Context

Scope: single-repo
Written: 2026-08-01 (PRE-context interview, confirmed by owner)

## What this system is and who depends on it
DevSync — OSS CLI on PyPI (v0.15.0), MIT. Extracts coding practices/configs from
a project via LLM and installs them into other projects, across 23+ AI coding
assistants. Small real user base (21 stars; pip installs unknown). No paying
customers, no SLA. Reputational stakes are real: publicly attached to the
owner's name and a candidate half of a two-product family (with
code-health-tracker: "one distributes your standards, one measures whether
they're holding").

## What debt competes against
Side-project time approaching zero (last push 2026-05-19). Debt work competes
with the project staying alive at all. Register policy: 2–3 items MAX, biased
toward what breaks a NEW USER'S TRUST over what slows development. Roadmap
(ROADMAP.md, updated 2026-02-22): P1 = extraction tool-agnosticism (#86),
Dependabot batch-merge (#84), pip MCP servers (#80), `devsync update` (#81);
P2 = e2e validation (#82), example repos (#59).

## Compliance scope
None regulatory. Trust-critical paths (treat as the money paths):
1. **Users' LLM API keys** — setup/storage/use (core/mcp/credentials.py,
   secret detection)
2. **Install-time writes into users' repos** — devsync modifies other
   people's projects; a destructive or secret-leaking install is the
   worst-case event
3. **Extraction leakage** — extract reads a project and sends content to an
   LLM provider; secrets in that payload = incident (core/secret_detector.py)

## Environment constraints
Full local access. Tests runnable (pytest). Git history available but noisy:
repo renamed from "instructionkit" — pre-rename churn attributes to old paths.
Issue tracker: GitHub Issues on troylar/devsync.

## Standing allocation
None. Debt earns time only by beating "ship a roadmap item" for user trust.
