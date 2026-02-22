# Test Requirements

> Vision principle: **"Lean over sprawling."** Tests prevent sprawl by catching regressions early. They're the safety net that lets the codebase stay lean — you can refactor aggressively when tests confirm nothing broke.

## New Code Must Have Tests

When adding or modifying code under `devsync/`:

1. **New modules** (`devsync/<name>.py` or `devsync/<dir>/<name>.py`) MUST have a corresponding test file at `tests/unit/test_<name>.py`
2. **New public functions/methods** MUST have at least one unit test covering the happy path
3. **Bug fixes** MUST include a regression test that would have caught the bug
4. **Modified functions** — if you change behavior, update or add tests to cover the change

## Test Conventions

- Test files: `tests/unit/test_<module>.py`
- Test functions: `test_<function_name>_<scenario>()`
- Mock all external dependencies (file I/O, Git operations, network) in unit tests
- Use `pytest` fixtures from `conftest.py`, not setUp/tearDown
- Integration tests go in `tests/integration/` and may use real file I/O and Git
- Minimum coverage target: 80%

## What Doesn't Need Tests

- Private helper functions (tested indirectly through public API)
- Type definitions and dataclasses (unless they have methods with logic)
- Configuration constants
- `__init__.py` re-exports

## Before Committing

Run `pytest tests/unit/ -v --tb=short` or `invoke test-unit` and confirm all tests pass. Do not commit with failing tests.
