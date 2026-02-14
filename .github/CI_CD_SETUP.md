# CI/CD Pipeline Documentation

## Overview

DevSync uses GitHub Actions for comprehensive CI/CD automation. This document describes all workflows, their purposes, and how to configure them.

## Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` branch
- Any pull request to any branch
- Manual trigger via workflow_dispatch

**Jobs:**

#### Code Quality
- **Linting** with ruff
- **Formatting** check with black
- **Type checking** with mypy
- Runs on: Ubuntu latest, Python 3.10

#### Tests
- **Matrix testing** across:
  - OS: Ubuntu, macOS, Windows
  - Python: 3.10, 3.11, 3.12, 3.13
- Coverage reporting to Codecov (Ubuntu + Python 3.10 only)
- Fails fast: No (all combinations run even if one fails)

#### Security Checks
- Runs `invoke security-check`
- Bandit security scanning
- Continue on error: Yes (won't block PR)

#### Dependency Review
- Reviews dependency changes in PRs
- Fails on moderate or higher severity vulnerabilities
- Only runs on PRs

#### All Checks Pass
- Meta-job that requires all other jobs to pass
- **Use this job as your branch protection requirement**
- Makes branch protection rules simpler

**Concurrency:** Cancels in-progress runs when new commits are pushed to the same ref.

---

### 2. PR Automation (`.github/workflows/pr-automation.yml`)

**Triggers:**
- PR opened, synchronized, reopened, labeled, unlabeled

**Jobs:**

#### Auto-label PR
- Automatically labels PRs based on changed files
- Configuration in `.github/labeler.yml`
- Labels: `type:`, `scope:`, etc.

#### PR Size
- Labels PR size based on lines changed
- Labels: `size/xs`, `size/s`, `size/m`, `size/l`, `size/xl`
- Thresholds:
  - XS: ≤10 lines
  - S: ≤100 lines
  - M: ≤500 lines
  - L: ≤1000 lines
  - XL: >1000 lines

#### Require Tests
- Checks if code changes include test changes
- Comments on PR if tests are missing
- Does not block PR (informational only)

#### Conventional Commits
- Validates PR title follows conventional commits format
- Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- Requires capitalized subject

---

### 3. Code Review (`.github/workflows/code-review.yml`)

**Triggers:**
- PR opened, synchronized, reopened

**Jobs:**

#### Coverage Report
- Runs tests with coverage
- Posts coverage report as PR comment
- Thresholds:
  - Green: ≥80%
  - Orange: ≥60%
  - Red: <60%

#### Complexity Check
- Analyzes code complexity with radon
- Reports:
  - Cyclomatic complexity (flags functions with CC > 10)
  - Maintainability index
- Results posted to job summary

#### Diff Quality
- Checks quality of changed lines only
- Runs ruff on diff
- Posts linting issues as PR comment

---

### 4. Performance Benchmarks (`.github/workflows/benchmark.yml`)

**Triggers:**
- Push to `main`
- PR to `main`
- Manual trigger

**Jobs:**

#### Benchmark
- Runs pytest benchmarks
- Stores results for main branch
- Compares PR results against main
- Alerts if performance degrades >150%
- Does not fail PR on performance regression

---

### 5. Publish to PyPI (`.github/workflows/publish.yml`)

**Triggers:**
- GitHub release created

**Jobs:**
- Runs quality checks and tests
- Builds package
- Publishes to Test PyPI (optional)
- Publishes to PyPI (production)

---

## Setup Instructions

### 1. Enable Workflows

All workflows are enabled by default. No additional setup needed.

### 2. Configure Branch Protection

Recommended settings for `main` branch:

1. Go to **Settings** → **Branches** → **Branch protection rules**
2. Add rule for `main`:
   - ✅ Require a pull request before merging
     - ✅ Require approvals: 1
     - ✅ Dismiss stale reviews
   - ✅ Require status checks to pass before merging
     - ✅ Require branches to be up to date
     - **Required checks:**
       - `All Checks Passed` (from CI workflow)
   - ✅ Require conversation resolution before merging
   - ✅ Do not allow bypassing the above settings

### 3. Configure Secrets

Required secrets (already configured):

- `CODECOV_TOKEN` - For coverage reporting
- `GITHUB_TOKEN` - Auto-provided by GitHub

### 4. Label Configuration

The following labels are auto-created by the labeler:

**Type labels:**
- `type: documentation`
- `type: tests`
- `type: ci/cd`
- `type: dependencies`

**Scope labels:**
- `scope: cli`
- `scope: core`
- `scope: storage`
- `scope: ai-tools`
- `scope: tui`
- `scope: utils`

**Size labels:**
- `size/xs`, `size/s`, `size/m`, `size/l`, `size/xl`

### 5. Codecov Integration

Coverage reports are automatically uploaded to Codecov. View reports at:
https://app.codecov.io/gh/troylar/devsync

## Workflow Status Badges

Add these to your README.md:

```markdown
[![CI](https://github.com/troylar/devsync/actions/workflows/ci.yml/badge.svg)](https://github.com/troylar/devsync/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/troylar/devsync/branch/main/graph/badge.svg)](https://codecov.io/gh/troylar/devsync)
[![PyPI version](https://badge.fury.io/py/devsync.svg)](https://badge.fury.io/py/devsync)
```

## Local Development

Before pushing, run the same checks locally:

```bash
# Run all quality checks
invoke quality

# Run tests with coverage
invoke test --coverage

# Run security checks
invoke security-check

# Or run everything
invoke release-check
```

## Troubleshooting

### PR Check Failures

**Quality check fails:**
```bash
# Fix locally
invoke quality --fix
git add .
git commit -m "fix: apply quality fixes"
git push
```

**Test failures:**
```bash
# Run tests locally
invoke test

# Run specific test
pytest tests/unit/test_specific.py -v

# Debug with output
pytest tests/unit/test_specific.py -s -vv
```

**Type checking fails:**
```bash
# Run mypy locally
invoke typecheck

# Fix type errors in the reported files
```

### Workflow Permissions

If workflows fail with permission errors, check:
1. **Settings** → **Actions** → **General**
2. Workflow permissions: Select "Read and write permissions"
3. Allow GitHub Actions to create pull requests: ✅

### Concurrency Issues

If jobs are being cancelled unexpectedly:
- Check the `concurrency` section in the workflow
- Multiple pushes to the same branch will cancel previous runs
- This is intentional to save CI time

## Cost Optimization

GitHub Actions provides 2,000 free minutes/month for private repos. To optimize:

1. **Use concurrency cancellation** (already configured)
2. **Matrix testing** only runs on PRs and main pushes
3. **Security checks** continue on error (non-blocking)
4. **Dependency review** only runs on PRs
5. **Benchmarks** only run on main and PRs to main

Current usage estimate:
- CI per PR: ~10-15 minutes (matrix: 3 OS × 4 Python versions)
- PR automation: ~1 minute
- Code review: ~3 minutes
- **Total per PR: ~15-20 minutes**

## Future Enhancements

Potential additions:

- [ ] Mutation testing with `mutmut`
- [ ] Docker image builds and publishing
- [ ] Automated changelog generation
- [ ] Auto-merge for dependabot PRs
- [ ] Nightly builds for dependency testing
- [ ] Integration testing with real AI tools
- [ ] Documentation preview deployment
