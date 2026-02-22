# All Work Requires a GitHub Issue

This is a non-negotiable project requirement. Before writing ANY code, modifying ANY file, or creating ANY branch:

1. **Confirm a GitHub issue exists** for the work being done
2. **If no issue exists**, create one before proceeding:
   ```bash
   gh issue create --title "<clear title>" --label "<type>" --body "<description with acceptance criteria>"
   ```
3. **Reference the issue** in the branch name: `issue-<N>-short-description`
4. **Reference the issue** in every commit: `type(scope): description (#N)`

## When This Applies

- Feature development
- Bug fixes
- Refactoring
- Documentation changes
- Test additions
- Configuration changes

## When This Does NOT Apply

- Reading/exploring code (research only, no changes)
- Running tests or linting (no commits)
- Reviewing PRs

## If the User Skips This

If the user asks to make code changes without mentioning an issue, ask:

> "Which GitHub issue does this work relate to? I can create one with `/new-issue`."

Use `/new-issue` to create issues — it includes vision alignment checks and proper formatting. Do not proceed with code changes until an issue is established.
