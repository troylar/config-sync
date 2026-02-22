# Commit Message Format

Every commit in this repository MUST follow this format:

```
type(scope): description (#issue)
```

## Rules

- **type** must be one of: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- **scope** must be a module name: `cli`, `core`, `storage`, `ai_tools`, `tui`, `utils`
- **description** is lowercase, imperative mood, no period
- **#issue** is a valid GitHub issue number — every commit MUST reference one

**IMPORTANT:** Do NOT include Claude as a co-author in commit messages. Do NOT add:
- `Co-Authored-By: Claude <noreply@anthropic.com>`
- `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
- Any other Claude attribution lines
- `Generated with [Claude Code]` lines

## Examples

Good:
- `feat(ai_tools): add kiro tool support (#83)`
- `fix(storage): handle missing installations.json (#91)`
- `test(core): add package model validation tests (#88)`
- `docs: update CLAUDE.md architecture section (#95)`

Bad:
- `fixed bug` (no type, scope, or issue)
- `feat: add new feature` (missing issue reference)
- `feat(ai_tools): Add Kiro Support (#83)` (capitalized description)

## Scope Exception

`docs` type may omit scope when the change is project-wide (e.g., README, CLAUDE.md).

## When Creating Commits

Before running `git commit`, verify:
1. The message matches `type(scope): description (#issue)` format
2. The issue number exists: `gh issue view <N> --json state`
3. The scope matches the primary module being changed
4. The type accurately reflects the change (feat = new, fix = bug, etc.)
5. There is NO co-author attribution line

If the user provides a commit message that doesn't match this format, reformat it. If no issue number is provided, ask for one — do not commit without it.
