# Creating Packages

**Complete guide to building, testing, and sharing your own configuration packages**

This guide walks you through creating custom packages from scratch, from basic structure to advanced multi-component packages.

## Table of Contents

- [Package Basics](#package-basics)
- [Step-by-Step Tutorial](#step-by-step-tutorial)
- [Component Types](#component-types)
- [Manifest Schema](#manifest-schema)
- [Testing Your Package](#testing-your-package)
- [Best Practices](#best-practices)
- [Publishing and Sharing](#publishing-and-sharing)

## Package Basics

### What Is a Package?

A package is a directory containing:
1. **Manifest file**: `ai-config-kit-package.yaml` (required)
2. **Component directories**: Instructions, MCP servers, hooks, commands, resources (optional)

### Minimum Package Structure

```
my-package/
├── ai-config-kit-package.yaml    # Required manifest
└── instructions/                  # At least one component
    └── my-instruction.md
```

### Complete Package Structure

```
my-package/
├── ai-config-kit-package.yaml    # Package manifest
├── README.md                     # Usage documentation (recommended)
├── instructions/                 # Instruction files
│   ├── code-style.md
│   └── best-practices.md
├── mcp/                         # MCP server configs
│   └── custom-server.json
├── hooks/                       # Hook scripts
│   └── pre-commit.sh
├── commands/                    # Command scripts
│   └── lint.sh
└── resources/                   # Additional files
    └── .editorconfig
```

## Step-by-Step Tutorial

Let's create a Python development package from scratch.

### Step 1: Create Package Directory

```bash
mkdir python-dev-package
cd python-dev-package
```

### Step 2: Create the Manifest

Create `ai-config-kit-package.yaml`:

```yaml
name: python-dev-package
version: 1.0.0
description: Python development best practices and tooling
author: Your Name
author_email: your.email@example.com
namespace: your-org/packages

components:
  instructions:
    - name: python-style
      description: PEP 8 style guidelines
      file: instructions/python-style.md
      tags: [python, style, pep8]

  hooks:
    - name: pre-commit
      description: Run black and ruff before commits
      file: hooks/pre-commit.sh
      tags: [python, linting]

  commands:
    - name: test
      description: Run pytest with coverage
      file: commands/test.sh
      tags: [python, testing]
```

### Step 3: Create Component Directories

```bash
mkdir -p instructions hooks commands
```

### Step 4: Write Your First Instruction

Create `instructions/python-style.md`:

```markdown
# Python Style Guidelines

Follow PEP 8 style guidelines for all Python code.

## Key Rules

1. **Line Length**: Maximum 120 characters
2. **Indentation**: 4 spaces (no tabs)
3. **Imports**: Group in order: standard library, third-party, local
4. **Naming**:
   - Functions/variables: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPER_CASE`

## Tools

Use these tools to enforce style:
- **black**: Auto-formatter
- **ruff**: Fast linter
- **mypy**: Type checker

## Examples

Good:
```python
def calculate_total(items: list[dict]) -> float:
    """Calculate total price from items."""
    return sum(item["price"] for item in items)
```

Bad:
```python
def calculateTotal(items):
    total = 0
    for i in items:
        total = total + i["price"]
    return total
```
```

### Step 5: Create a Pre-Commit Hook

Create `hooks/pre-commit.sh`:

```bash
#!/usr/bin/env bash
# Pre-commit hook for Python projects

set -e

echo "Running pre-commit checks..."

# Run black formatter
echo "→ Running black..."
if command -v black &> /dev/null; then
    black --check . || {
        echo "❌ Black formatting issues found. Run 'black .' to fix."
        exit 1
    }
else
    echo "⚠️  Black not installed, skipping"
fi

# Run ruff linter
echo "→ Running ruff..."
if command -v ruff &> /dev/null; then
    ruff check . || {
        echo "❌ Ruff linting issues found. Run 'ruff check --fix .' to fix."
        exit 1
    }
else
    echo "⚠️  Ruff not installed, skipping"
fi

echo "✓ All pre-commit checks passed!"
```

Make it executable:
```bash
chmod +x hooks/pre-commit.sh
```

### Step 6: Create a Test Command

Create `commands/test.sh`:

```bash
#!/usr/bin/env bash
# Run pytest with coverage

set -e

echo "Running test suite..."

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not installed. Install with: pip install pytest pytest-cov"
    exit 1
fi

# Run tests with coverage
pytest \
    --cov=. \
    --cov-report=html \
    --cov-report=term \
    -v

echo ""
echo "✓ All tests passed!"
echo "Coverage report: htmlcov/index.html"
```

Make it executable:
```bash
chmod +x commands/test.sh
```

### Step 7: Add a README

Create `README.md`:

```markdown
# Python Development Package

Complete Python development configuration for AI coding assistants.

## What's Included

- **python-style**: PEP 8 style guidelines
- **pre-commit**: Automatic linting with black and ruff
- **test**: Run pytest with coverage reporting

## Installation

```bash
aiconfig package install python-dev-package --ide claude
```

## Requirements

This package works best with:
- Python 3.10+
- black (formatter)
- ruff (linter)
- pytest & pytest-cov (testing)

Install with:
```bash
pip install black ruff pytest pytest-cov
```

## Usage

After installation:
- **Style guidelines**: Your AI assistant will follow PEP 8 automatically
- **Pre-commit hook**: Runs automatically before each commit
- **Test command**: Run `.claude/commands/test.sh` (or equivalent for your IDE)
```

### Step 8: Test the Package Locally

```bash
# Navigate to a test project
cd ~/test-project

# Install your package
aiconfig package install /path/to/python-dev-package --ide claude

# Verify installation
aiconfig package list
```

**Expected output:**
```
Installed packages in /Users/you/test-project:

┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Package                ┃ Version ┃ Status    ┃ Components ┃ Installed      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ python-dev-package     │ 1.0.0   │ ✓ complete│          3 │ 2025-01-14 ... │
└────────────────────────┴─────────┴───────────┴────────────┴────────────────┘
```

Congratulations! You've created your first package.

## Component Types

Packages can include five types of components. Here's how to create each.

### Instructions

**Purpose**: Guidelines and rules for the AI assistant

**Location**: `instructions/` directory

**Format**: Markdown (`.md`)

**Example manifest entry:**
```yaml
components:
  instructions:
    - name: code-review
      description: Code review checklist
      file: instructions/code-review.md
      tags: [review, quality]
```

**File content example:**
```markdown
# Code Review Checklist

When reviewing code, check:

1. **Correctness**: Does it solve the problem?
2. **Tests**: Are there adequate tests?
3. **Readability**: Is it easy to understand?
4. **Performance**: Are there obvious inefficiencies?

## Common Issues

- Magic numbers without explanation
- Missing error handling
- Inconsistent naming
```

**Best practices:**
- Be specific and actionable
- Include examples of good/bad code
- Link to external resources when relevant
- Use clear section headings
- Keep focused (one instruction per concern)

### MCP Servers

**Purpose**: Model Context Protocol server configurations

**Location**: `mcp/` directory

**Format**: JSON configuration files

**Compatibility**: Claude Code only

**Example manifest entry:**
```yaml
components:
  mcp_servers:
    - name: filesystem
      description: Filesystem access for reading/writing files
      file: mcp/filesystem.json
      tags: [filesystem, io]
      requires_credentials:
        - ALLOWED_DIRECTORIES
```

**File content example (`mcp/filesystem.json`):**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${ALLOWED_DIRECTORIES}"
      ],
      "env": {}
    }
  }
}
```

**Best practices:**
- Use environment variables for sensitive config
- Document required credentials in `requires_credentials`
- Test MCP server works before packaging
- Provide setup instructions in README

### Hooks

**Purpose**: Scripts that run automatically at specific points

**Location**: `hooks/` directory

**Format**: Executable shell scripts (`.sh`, `.bash`)

**Compatibility**: Claude Code only

**Example manifest entry:**
```yaml
components:
  hooks:
    - name: pre-push
      description: Run tests before pushing
      file: hooks/pre-push.sh
      tags: [git, testing]
```

**File content example (`hooks/pre-push.sh`):**
```bash
#!/usr/bin/env bash
# Pre-push hook: ensure tests pass

set -e

echo "Running tests before push..."

# Run test suite
pytest || {
    echo "❌ Tests failed. Fix before pushing."
    exit 1
}

echo "✓ Tests passed, proceeding with push"
```

**Best practices:**
- Always include shebang (`#!/usr/bin/env bash`)
- Use `set -e` to exit on errors
- Provide clear error messages
- Make scripts executable (`chmod +x`)
- Keep hooks fast (< 10 seconds)
- Allow skipping with environment variable if needed

### Commands

**Purpose**: Reusable scripts for common tasks

**Location**: `commands/` directory

**Format**: Executable shell scripts (`.sh`, `.bash`)

**Compatibility**: Claude Code only

**Example manifest entry:**
```yaml
components:
  commands:
    - name: deploy
      description: Deploy to staging environment
      file: commands/deploy.sh
      tags: [deployment, automation]
```

**File content example (`commands/deploy.sh`):**
```bash
#!/usr/bin/env bash
# Deploy to staging

set -e

ENVIRONMENT="${1:-staging}"

echo "Deploying to $ENVIRONMENT..."

# Build
echo "→ Building application..."
npm run build

# Run tests
echo "→ Running tests..."
npm test

# Deploy
echo "→ Deploying..."
aws s3 sync ./dist s3://my-app-$ENVIRONMENT/

echo "✓ Deployed successfully to $ENVIRONMENT"
echo "URL: https://$ENVIRONMENT.myapp.com"
```

**Best practices:**
- Accept parameters for flexibility
- Provide sensible defaults
- Include verbose output
- Handle errors gracefully
- Document usage in comments

### Resources

**Purpose**: Configuration files, templates, or other assets

**Location**: `resources/` directory

**Format**: Any file type

**Compatibility**: Claude Code, Cursor, Windsurf

**Example manifest entry:**
```yaml
components:
  resources:
    - name: gitignore
      description: Standard Python .gitignore
      file: resources/.gitignore
      install_path: .gitignore  # Where to install in project
      tags: [git, python]
```

**File content example (`resources/.gitignore`):**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# IDEs
.vscode/
.idea/
*.swp

# Testing
.coverage
htmlcov/
.pytest_cache/
```

**Best practices:**
- Use `install_path` to specify where file should go
- Don't include sensitive data
- Keep files generic and reusable
- Document customization in README

## Manifest Schema

### Required Fields

```yaml
name: package-name              # Lowercase, hyphens (not underscores)
version: 1.0.0                  # Semantic versioning (major.minor.patch)
description: Package description # Brief, clear description
author: Your Name               # Your name or organization
namespace: org/category         # Unique namespace (e.g., "mycompany/python")
```

### Optional Fields

```yaml
author_email: email@example.com  # Contact email
license: MIT                     # License identifier
homepage: https://example.com    # Project homepage
repository: https://github.com/user/repo  # Source repository
keywords: [python, django, web]  # Search keywords
```

### Components Structure

```yaml
components:
  instructions:
    - name: instruction-name
      description: What it does
      file: instructions/file.md
      tags: [tag1, tag2]

  mcp_servers:
    - name: server-name
      description: What it provides
      file: mcp/config.json
      tags: [tag1]
      requires_credentials:
        - ENV_VAR_NAME

  hooks:
    - name: hook-name
      description: When it runs
      file: hooks/script.sh
      tags: [tag1]

  commands:
    - name: command-name
      description: What it does
      file: commands/script.sh
      tags: [tag1]

  resources:
    - name: resource-name
      description: What it is
      file: resources/filename
      install_path: .filename  # Optional, defaults to project root
      tags: [tag1]
```

### Complete Example

```yaml
name: django-dev-complete
version: 2.1.0
description: Complete Django development environment with best practices
author: Django Team
author_email: team@example.com
namespace: web-frameworks/django
license: MIT
homepage: https://github.com/your-org/django-package
repository: https://github.com/your-org/django-package
keywords: [django, python, web, orm]

components:
  instructions:
    - name: django-models
      description: Django model design patterns
      file: instructions/models.md
      tags: [django, orm, database]

    - name: django-views
      description: Class-based vs function-based views
      file: instructions/views.md
      tags: [django, views, patterns]

  hooks:
    - name: pre-commit
      description: Run linting and migrations check
      file: hooks/pre-commit.sh
      tags: [django, linting]

  commands:
    - name: migrate
      description: Run Django migrations
      file: commands/migrate.sh
      tags: [django, database]

  resources:
    - name: settings
      description: Django settings template
      file: resources/settings.py
      install_path: config/settings_template.py
      tags: [django, config]
```

## Testing Your Package

### 1. Validate Manifest

Test that your manifest is valid:

```bash
# Try installing to a test project
cd ~/test-project
aiconfig package install /path/to/your-package --ide claude
```

If the manifest is invalid, you'll see clear error messages:
```
Error: Manifest validation failed: Missing required field: 'version'
```

### 2. Test on Multiple IDEs

Test IDE compatibility:

```bash
# Test on Claude Code (all components)
aiconfig package install ./my-package --ide claude

# Test on Cursor (instructions + resources only)
aiconfig package install ./my-package --ide cursor

# Verify component counts match expectations
aiconfig package list
```

### 3. Test Component Functionality

**Instructions**: Ask AI assistant questions that should trigger the instruction

**Hooks**: Make a commit and verify hook runs
```bash
git add .
git commit -m "test"
# Should see hook output
```

**Commands**: Run the installed command
```bash
./.claude/commands/test.sh
```

**MCP Servers**: Verify server appears in IDE's MCP configuration

**Resources**: Check file installed to correct location
```bash
ls -la .gitignore  # Or other resource install path
```

### 4. Test Conflict Resolution

Test how package handles existing files:

```bash
# Install once
aiconfig package install ./my-package --ide claude

# Modify installed file
echo "# Custom change" >> .claude/rules/my-instruction.md

# Reinstall with different conflict strategies
aiconfig package install ./my-package --ide claude --conflict skip
# Should keep your changes

aiconfig package install ./my-package --ide claude --conflict overwrite
# Should replace with package version

aiconfig package install ./my-package --ide claude --conflict rename
# Should create my-instruction-1.md
```

### 5. Test Uninstallation

```bash
# Uninstall
aiconfig package uninstall my-package

# Verify files removed
ls .claude/rules/  # Should not show package files

# Verify tracking removed
aiconfig package list  # Should not show package
```

## Best Practices

### 1. Start Simple, Iterate

Begin with 1-2 instructions, test thoroughly, then add more components.

```yaml
# Version 1.0.0 - Start simple
components:
  instructions:
    - name: basic-style
      file: instructions/style.md
```

```yaml
# Version 1.1.0 - Add more after testing
components:
  instructions:
    - name: basic-style
      file: instructions/style.md
    - name: testing-guide
      file: instructions/testing.md
  hooks:
    - name: pre-commit
      file: hooks/pre-commit.sh
```

### 2. Use Semantic Versioning

- **Patch** (1.0.0 → 1.0.1): Bug fixes, typos, minor clarifications
- **Minor** (1.0.1 → 1.1.0): New components, backwards-compatible additions
- **Major** (1.1.0 → 2.0.0): Breaking changes, removed components, renamed files

### 3. Document Dependencies

In your README, clearly state what tools are required:

```markdown
## Requirements

- Python 3.10+
- black (install: `pip install black`)
- ruff (install: `pip install ruff`)
```

### 4. Tag Thoughtfully

Use consistent, descriptive tags:

**Good tags:**
```yaml
tags: [python, testing, pytest]
tags: [django, orm, database]
tags: [security, authentication]
```

**Poor tags:**
```yaml
tags: [misc, stuff, important]  # Too vague
tags: [python-testing-with-pytest-and-coverage]  # Too specific, use multiple tags
```

### 5. Keep Instructions Focused

One instruction should cover one topic:

**Good** (focused):
- `python-naming.md` - Naming conventions only
- `python-testing.md` - Testing practices only
- `python-docstrings.md` - Documentation only

**Poor** (too broad):
- `python-everything.md` - All Python topics in one file

### 6. Make Scripts Portable

Write scripts that work across different environments:

```bash
#!/usr/bin/env bash
# Good: Uses env to find bash

# Check for required commands
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Install with: pip install pytest"
    exit 1
fi

# Use portable flags
pytest -v  # Good: Standard flags
pytest --some-custom-flag  # Be careful: May not exist in all versions
```

### 7. Version Control Your Package

```bash
cd my-package
git init
git add .
git commit -m "Initial package version 1.0.0"
git tag v1.0.0
```

### 8. Test Across Python Versions

If your package includes Python-specific content:

```bash
# Test with different Python versions
python3.10 -m pytest
python3.11 -m pytest
python3.12 -m pytest
```

## Publishing and Sharing

### Option 1: Git Repository (Recommended)

**Advantages**: Version control, easy updates, collaborative

1. **Create repository**:
   ```bash
   cd my-package
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Push to GitHub**:
   ```bash
   gh repo create my-org/my-package --public
   git push origin main
   ```

3. **Share installation command**:
   ```bash
   # Users can install directly from Git URL
   aiconfig package install https://github.com/my-org/my-package --ide claude
   ```

### Option 2: Local Directory

**Advantages**: Simple, no hosting needed

1. **Create directory structure**:
   ```bash
   mkdir -p ~/ai-packages/my-package
   cp -r my-package/* ~/ai-packages/my-package/
   ```

2. **Share with team**:
   - Share directory via network drive
   - Include in project repository
   - Distribute as zip file

3. **Installation**:
   ```bash
   aiconfig package install ~/ai-packages/my-package --ide claude
   ```

### Option 3: Package in Project Repository

**Advantages**: Keeps configuration with code

1. **Add to project**:
   ```bash
   mkdir .ai-packages
   cp -r my-package .ai-packages/
   git add .ai-packages/
   git commit -m "Add AI configuration package"
   ```

2. **Install in CI/CD or for new developers**:
   ```bash
   aiconfig package install .ai-packages/my-package --ide claude
   ```

### Documentation Checklist

Before publishing, ensure your package includes:

- ✅ `README.md` with:
  - What the package does
  - Installation instructions
  - Requirements/dependencies
  - Usage examples
  - Version history
- ✅ `ai-config-kit-package.yaml` with all fields complete
- ✅ Meaningful component descriptions
- ✅ Appropriate tags for discovery
- ✅ License file (if public)

## Advanced Topics

### Multi-Package Dependencies

Currently, DevSync doesn't support package dependencies. If you need multiple packages:

```bash
# Install individually
aiconfig package install python-base --ide claude
aiconfig package install django-extensions --ide claude
```

**Workaround**: Create a "meta package" that combines components:
```yaml
name: django-complete
description: Combines python-base and django-extensions
components:
  instructions:
    - name: python-style
      file: instructions/python-style.md  # Copied from python-base
    - name: django-models
      file: instructions/django-models.md  # Copied from django-extensions
```

### Parameterized Components

For components that need customization, use placeholders:

```yaml
# In manifest
components:
  resources:
    - name: config
      file: resources/config.template.yaml
      install_path: config/app.yaml
```

```yaml
# In resources/config.template.yaml
database:
  host: ${DB_HOST}  # User replaces after installation
  port: ${DB_PORT}
```

In README, document required replacements:
```markdown
## Post-Installation

Edit `config/app.yaml` and replace placeholders:
- `${DB_HOST}` - Your database hostname
- `${DB_PORT}` - Your database port
```

### Package Variants

Create variants for different use cases:

```
django-package/
├── django-minimal/
│   └── ai-config-kit-package.yaml  # Basic instructions only
├── django-standard/
│   └── ai-config-kit-package.yaml  # Instructions + hooks
└── django-complete/
    └── ai-config-kit-package.yaml  # Everything
```

Users choose the variant they need:
```bash
aiconfig package install django-package/django-minimal --ide claude
```

## Next Steps

Now that you know how to create packages:

- **[Manifest Reference](manifest-reference.md)** - Complete YAML schema
- **[CLI Reference](cli-reference.md)** - All package commands
- **[Examples](examples.md)** - Real-world package examples
- **[Installation Guide](installation.md)** - How users install your package

---

**Ready to publish?** Create a repository, push your package, and share the installation command with your team!
