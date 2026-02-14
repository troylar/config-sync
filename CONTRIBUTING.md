# Contributing to DevSync

Thanks for your interest in improving DevSync! This project thrives on community involvement. The guidelines below help you get started quickly and keep contributions consistent and high-quality.

## 🧭 Ways to Contribute

- Report bugs or suggest enhancements via GitHub issues
- Improve documentation or examples
- Add new instruction management features
- Help expand platform/tool support
- Review and test pull requests from other contributors

If you are unsure where to begin, check the **good first issue** label or ask in a discussion.

## ⚙️ Development Environment

DevSync uses [Invoke](https://www.pyinvoke.org/) to orchestrate common tasks. After cloning the repo:

```bash
pip install invoke
invoke dev-setup
```

This installs DevSync in editable mode with all development dependencies.

### Available Invoke Tasks

| Command | Purpose |
| --- | --- |
| `invoke test` | Run the full pytest suite |
| `invoke test-unit` / `invoke test-integration` | Target specific suites |
| `invoke quality` | Lint (ruff), format check (black), and type-check (mypy) |
| `invoke format --check` | Verify formatting only |
| `invoke typecheck` | Run mypy alone |
| `invoke security-check` | Run safety + bandit scans |
| `invoke build` | Build publishable distributions |
| `invoke release-check` | Full pre-release checklist |

## 🧱 Branching & Commit Style

- Fork the repository or create a topic branch from `main`
- Keep branches focused and small; group related changes together
- Write clear commit messages in the conventional style, e.g., `feat:`, `fix:`, `docs:`
- Rebase on the latest `main` to avoid merge commits when possible

## 🧼 Coding Standards

- Python 3.10+ with type annotations where practical
- Follow ruff and black defaults (`invoke quality` catches both)
- Keep functions small and intention-revealing, favoring pure logic where feasible
- Update or add tests alongside code changes to retain coverage expectations

## ✅ Testing Expectations

Before opening a pull request:

1. `invoke quality`
2. `invoke test`
3. For dependency or security updates, run `invoke security-check`

GitHub Actions will run the same tasks across multiple Python versions.

## 🔄 Pull Request Process

1. Ensure your branch is up to date with `main`
2. Open a PR with a concise summary and checklist of changes
3. Link related issues or discussions
4. Expect at least one maintainer review before merge
5. Address review feedback promptly; feel free to push follow-up commits

PRs that pass CI, include tests, and document user-facing changes are merged fastest.

## 🗣️ Communication

- Use GitHub Discussions or Issues for design proposals and questions
- Tag maintainers when feedback is blocking
- Be patient and respectful—maintainers are often volunteering their time

## 🚀 Releases

Releases are managed by maintainers. If you need a release:

1. Confirm `invoke release-check` passes
2. Update `pyproject.toml` with a new version
3. Document changes in the release notes / changelog
4. Request a maintainer to cut a release via the publish workflow
