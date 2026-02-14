# Tutorial: Small Team - Shared Coding Standards

**⏱️ Time**: 20 minutes (team lead), 2 minutes (team members)
**👥 Team Size**: 2-10 developers
**🎯 Goal**: Everyone's AI assistant follows the same team conventions

---

## 🎬 The Scenario

Your 5-person startup has inconsistent code:
- **Alice** writes verbose comments
- **Bob** prefers minimal comments
- **Carol** uses different error handling patterns
- **David** has unique naming conventions

Code reviews waste time debating style instead of logic. You need team-wide standards that AI assistants enforce automatically.

---

## 🎭 Team Roles

This tutorial has two paths:

| Role | Time | What You'll Do |
|------|------|----------------|
| **🏗️ Team Lead** (you) | 20 min | Create team package, set up repository |
| **👥 Team Members** | 2 min | Install package, start using it |

Choose your role below ⬇️

---

## 🏗️ Part 1: Team Lead Setup (20 minutes)

You'll create a team coding standards package and publish it to GitHub.

### Step 1.1: Create Team Standards Repository

**What**: Create GitHub repo to host your team's coding standards
**Why**: Centralized source of truth that everyone can pull from
**How**:

```bash
# Navigate to where you keep your projects/packages
cd ~/projects  # Or your preferred location (e.g., ~/code, ~/workspace)

# Create local directory for team standards
mkdir team-coding-standards
cd team-coding-standards
git init

# Create package structure
mkdir -p instructions mcp hooks commands

# Initialize Git
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
gh repo create yourcompany/coding-standards --public --source=. --remote=origin
git push -u origin main
```

**📤 Expected Output**:
```
✓ Created repository yourcompany/coding-standards on GitHub
✓ Added remote https://github.com/yourcompany/coding-standards.git
```

**✅ What you created**: A version-controlled home for your team's AI configuration.

---

### Step 1.2: Define Team Standards

**What**: Document your team's agreed-upon conventions
**Why**: AI assistants will enforce these automatically

**How**:

**First, hold a 30-minute team meeting to decide**:
- Error handling patterns
- Comment style
- Testing requirements
- Code review checklist

**Then, create the package**:

```bash
cd team-coding-standards

# Create manifest
cat > ai-config-kit-package.yaml << 'EOF'
name: acme-coding-standards
version: 1.0.0
description: ACME Corp coding standards for all projects
author: ACME Engineering Team
namespace: yourcompany/coding-standards
license: MIT

components:
  instructions:
    - name: error-handling
      description: Team error handling conventions
      file: instructions/error-handling.md
      tags: [errors, exceptions, logging]

    - name: testing-guide
      description: Unit testing requirements
      file: instructions/testing-guide.md
      tags: [testing, quality]

    - name: code-review-checklist
      description: What to check in code reviews
      file: instructions/code-review-checklist.md
      tags: [review, quality]

  commands:
    - name: run-tests
      description: Run test suite with coverage
      file: commands/run-tests.sh
      command_type: shell
      tags: [testing, automation]
EOF

# Create error-handling instruction
cat > instructions/error-handling.md << 'EOF'
# ACME Team Error Handling Standards

## Exception Types

✅ **DO**: Use specific exception types
```python
# Good
if not user:
    raise ValueError(f"User {user_id} not found")

# Good
try:
    data = api.fetch_data()
except requests.Timeout as e:
    logger.error(f"API timeout: {e}")
    raise
```

❌ **DON'T**: Use generic exceptions
```python
# Bad
raise Exception("Something went wrong")

# Bad
except Exception:
    pass  # Silently swallowing errors
```

## Logging Before Re-raising

✅ **ALWAYS log before re-raising**:
```python
import logging

logger = logging.getLogger(__name__)

try:
    process_payment(order_id)
except PaymentError as e:
    logger.error(
        "Payment failed",
        extra={
            "order_id": order_id,
            "error": str(e),
            "user_id": user.id
        }
    )
    raise  # Re-raise for caller to handle
```

## Error Messages

✅ **Include context**:
```python
raise ValueError(
    f"Invalid email format: '{email}'. "
    f"Must match pattern: {EMAIL_REGEX}"
)
```

❌ **Don't be vague**:
```python
raise ValueError("Invalid input")  # What input? Why invalid?
```

## When helping with error handling:

1. Use specific exception types (ValueError, TypeError, etc.)
2. Always log errors with context before re-raising
3. Include relevant IDs (user_id, order_id) in log context
4. Don't silently swallow exceptions
5. Error messages should explain WHAT failed and WHY
EOF

# Create testing-guide instruction
cat > instructions/testing-guide.md << 'EOF'
# ACME Team Testing Standards

## Test Coverage Requirements

- **Minimum coverage**: 80% for all new code
- **Required tests**: All public functions must have at least one test
- **Run before commit**: `pytest` must pass locally

## Test Structure

```python
import pytest
from myapp.services import UserService

class TestUserService:
    """Tests for UserService."""

    @pytest.fixture
    def user_service(self):
        """Create UserService instance for testing."""
        return UserService(db=mock_db)

    def test_create_user_success(self, user_service):
        """Test successful user creation."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "name": "Test User"
        }

        # Act
        user = user_service.create_user(user_data)

        # Assert
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.id is not None

    def test_create_user_duplicate_email(self, user_service):
        """Test that duplicate email raises error."""
        # Arrange
        user_data = {"email": "existing@example.com"}
        user_service.create_user(user_data)  # Create first user

        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            user_service.create_user(user_data)

    def test_create_user_invalid_email(self, user_service):
        """Test that invalid email raises error."""
        user_data = {"email": "not-an-email"}

        with pytest.raises(ValueError, match="Invalid email"):
            user_service.create_user(user_data)
```

## Test Naming

- Use `test_<function>_<scenario>` pattern
- Scenarios: `success`, `failure`, `invalid_input`, `edge_case`
- Examples:
  - `test_create_user_success`
  - `test_create_user_duplicate_email`
  - `test_get_user_not_found`

## When writing tests:

1. Use Arrange-Act-Assert pattern
2. One assertion per test (or closely related assertions)
3. Test both success and failure cases
4. Use descriptive test names
5. Include docstrings explaining what's being tested
6. Use fixtures for setup
EOF

# Create code-review checklist
cat > instructions/code-review-checklist.md << 'EOF'
# ACME Code Review Checklist

When reviewing code, verify:

## Functionality
- [ ] Code does what the PR description says
- [ ] Edge cases are handled
- [ ] No obvious bugs

## Testing
- [ ] Tests cover new functionality
- [ ] Tests cover error cases
- [ ] All tests pass locally
- [ ] Coverage is >= 80%

## Error Handling
- [ ] Specific exceptions (not generic `Exception`)
- [ ] Errors are logged before re-raising
- [ ] Error messages include context

## Code Quality
- [ ] Functions are < 50 lines
- [ ] Descriptive variable/function names
- [ ] Comments explain WHY, not WHAT
- [ ] No commented-out code

## Documentation
- [ ] Docstrings for all public functions
- [ ] README updated if behavior changed
- [ ] Breaking changes highlighted

## Security
- [ ] No sensitive data in logs
- [ ] Input validation for user data
- [ ] No SQL injection vulnerabilities

## Performance
- [ ] No obvious performance issues
- [ ] Database queries are optimized
- [ ] No N+1 queries

## When reviewing AI-generated code:

Ask AI to verify each checklist item, then verify yourself.
EOF

# Create test runner command
mkdir -p commands
cat > commands/run-tests.sh << 'EOF'
#!/usr/bin/env bash
# ACME team test runner with coverage

set -e  # Exit on error

echo "🧪 Running test suite..."

# Run tests with coverage
pytest \
  --cov=. \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=80 \
  -v

echo "✅ All tests passed with sufficient coverage!"
EOF
chmod +x commands/run-tests.sh
```

**✅ What you created**:
- Error handling standards everyone follows
- Testing requirements for all code
- Code review checklist (saves 10 min/review)
- Automated test runner

---

### Step 1.3: Tag and Push

**What**: Create versioned release
**Why**: Team members can install specific versions
**How**:

```bash
git add .
git commit -m "v1.0.0: Initial team coding standards"
git tag v1.0.0
git push origin main --tags
```

**📤 Expected Output**:
```
[main abc1234] v1.0.0: Initial team coding standards
 6 files changed, 250 insertions(+)
 * [new tag]         v1.0.0 -> v1.0.0
```

**✅ What happened**: Team standards are now published at `github.com/yourcompany/coding-standards@v1.0.0`.

---

### Step 1.4: Announce to Team

**What**: Send message to team Slack/email
**Why**: Everyone needs to install the package
**How**:

```markdown
📢 **New: Team Coding Standards Package**

We've created a DevSync package with our team's coding standards!

**What**: AI assistants will now automatically follow our conventions
**Who**: Everyone should install this
**When**: Before your next PR
**How**: 2 minutes - see instructions below

👉 Installation Guide: [link to Part 2 below]

This will ensure:
- ✅ Consistent error handling
- ✅ Proper test coverage
- ✅ Faster code reviews (less nitpicking)

Questions? Ask in #engineering
```

---

## 👥 Part 2: Team Member Installation (2 minutes)

You're a team member. Your lead just shared the team standards package. Here's how to install it:

### Step 2.1: Navigate to Your Project

```bash
# Navigate to your actual project (replace with your project path)
cd ~/projects/acme-webapp  # Replace with your actual project directory
```

---

### Step 2.2: Install Team Package

**What**: Install team standards from GitHub
**Why**: Your AI assistant will follow team conventions
**How**:

```bash
# Install from GitHub
aiconfig package install github:yourcompany/coding-standards@v1.0.0 --ide claude

# Or if you have it cloned locally:
aiconfig package install ~/code/team-coding-standards --ide claude
```

**📤 Expected Output**:
```
📦 Installing package: acme-coding-standards v1.0.0

Installed components:
  ✓ error-handling (instruction)
  ✓ testing-guide (instruction)
  ✓ code-review-checklist (instruction)
  ✓ run-tests (command)

4/4 components installed to .claude/

✅ Package 'acme-coding-standards' installed successfully
```

**✅ What happened**: Team standards are now in `.claude/rules/`. Your AI knows them.

---

### Step 2.3: Commit AI Config (Optional but Recommended)

**What**: Add AI config to your project's Git
**Why**: New team members get it automatically
**How**:

```bash
git add .claude/ .ai-config-kit/
git commit -m "Add team coding standards package"
git push
```

**📤 Expected Output**:
```
[main def5678] Add team coding standards package
 4 files changed, 180 insertions(+)
```

**✅ What happened**: Next person who clones your project gets team standards automatically.

---

### Step 2.4: Test It Out

**What**: Verify AI follows team standards
**Why**: Make sure it works before relying on it
**How**:

```bash
# Ask your AI assistant:
claude "Write a function to fetch user data from an API. Handle errors."
```

**✅ What to expect**:
- ✅ Specific exceptions (not generic `Exception`)
- ✅ Logging before re-raising
- ✅ Error messages with context
- ✅ Tests included (if you asked for them)

---

## 🔄 Updating Team Standards

### When Team Decides on New Convention

**Team Lead**:

```bash
cd team-coding-standards

# Update instructions
vim instructions/error-handling.md

# Commit and tag new version
git add .
git commit -m "v1.1.0: Add database error handling guidelines"
git tag v1.1.0
git push origin main --tags

# Announce in Slack
```

**Team Members**:

```bash
# Update to latest version
cd ~/projects/acme-webapp
aiconfig package install github:yourcompany/coding-standards@v1.1.0 --ide claude --force

# The --force flag updates existing installation
```

---

## 📊 Measuring Impact

### Before Team Standards Package

**Code Review Comments (per PR)**:
- "Use ValueError here, not Exception" - 3 times
- "Add logging before re-raising" - 2 times
- "Need more test coverage" - 4 times
- "Improve error message" - 2 times

**Average PR review time**: 45 minutes

---

### After Team Standards Package

**Code Review Comments (per PR)**:
- Style/convention issues: ~90% reduction
- Focus on: Logic, architecture, edge cases

**Average PR review time**: 15 minutes

**Time saved**: 30 minutes × 20 PRs/week = **10 hours/week**

---

## 🐛 Troubleshooting

### ❌ Problem: Team member's AI not following standards

**Diagnosis**:
```bash
# Check if package is installed
aiconfig package list
# Should show: acme-coding-standards v1.0.0

# Check if files exist
ls .claude/rules/error-handling.md
```

**Fix**:
```bash
# If not installed:
aiconfig package install github:yourcompany/coding-standards@v1.0.0 --ide claude

# If installed but not working, reinstall:
aiconfig package uninstall acme-coding-standards
aiconfig package install github:yourcompany/coding-standards@v1.0.0 --ide claude
```

---

### ❌ Problem: Different team members have different versions

**Why**: Some haven't updated to latest release
**Fix**: Use version pinning in project

```bash
# Create .ai-config-kit.yaml in project root
cat > .ai-config-kit.yaml << 'EOF'
required_packages:
  - name: acme-coding-standards
    source: github:yourcompany/coding-standards
    version: "1.1.0"  # Specific version
EOF

# Add to Git
git add .ai-config-kit.yaml
git commit -m "Pin team standards to v1.1.0"
```

Now CI can verify everyone has correct version.

---

### ❌ Problem: Standards conflicts between team package and personal preferences

**Why**: You have personal preferences that conflict with team standards
**Fix**: Team standards take precedence

```bash
# Remove conflicting personal configs
rm .claude/rules/my-personal-error-handling.md

# Or namespace them
mv .claude/rules/my-style.md .claude/rules/personal-my-style.md
# Then add to .gitignore
echo ".claude/rules/personal-*.md" >> .gitignore
```

**Best Practice**: Personal configs should extend, not override, team configs.

---

## 💡 Pro Tips

### Tip 1: Gradual Rollout

Don't implement all standards at once:

**Week 1**: Error handling only
**Week 2**: Add testing requirements
**Week 3**: Add code review checklist
**Week 4**: Full standards

Each week, create new version:
- v1.0.0: Error handling
- v1.1.0: + Testing
- v1.2.0: + Code review

---

### Tip 2: Team-Specific vs Project-Specific

```
Team Standards (all projects):
  - Error handling
  - Testing requirements
  - Code review checklist

Project Standards (one project):
  - API endpoint conventions
  - Database migration checklist
  - Deployment procedures
```

Install both:
```bash
aiconfig package install github:yourcompany/coding-standards --ide claude  # Team
aiconfig package install ./project-specific-rules --ide claude              # Project
```

---

### Tip 3: Make It Enforceable with CI

Add to `.github/workflows/ci.yml`:

```yaml
- name: Verify team standards installed
  run: |
    aiconfig package list | grep "acme-coding-standards v1.1.0" || (
      echo "❌ Team coding standards not installed or wrong version"
      echo "Run: aiconfig package install github:yourcompany/coding-standards@v1.1.0"
      exit 1
    )
```

---

## ✅ Success Metrics

Track these metrics before/after:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| PR review time | 45 min | 15 min | **67% faster** |
| Style-related comments | 11/PR | 1/PR | **91% reduction** |
| Test coverage | 60% | 85% | **+25%** |
| Bug escape rate | 8/month | 2/month | **75% reduction** |

---

## 🎓 What Your Team Learned

**Team Lead**:
1. How to create and version team standards packages
2. How to publish packages to GitHub
3. How to communicate changes to the team

**Team Members**:
1. How to install team packages
2. How to verify installation
3. How to update when standards change

**Whole Team**:
1. Consistent coding standards across the team
2. Faster code reviews
3. Higher code quality
4. Less time debating style, more time building features

---

## 🚀 Next Steps

- **Add more standards**: Testing, documentation, security
- **Multiple teams**: See [Multi-Team Tutorial](multi-team-standards.md)
- **Enforcement with CI**: [CI/CD Integration Guide](cicd-integration.md)
- **Custom standards**: [Creating Advanced Packages](advanced-packages.md)

---

## 📚 Additional Resources

- [Example Team Standards Repo](https://github.com/ai-config-kit/examples/team-standards)
- [Community Standards Library](https://github.com/ai-config-kit/community)
- [Best Practices Guide](../guides/team-best-practices.md)
