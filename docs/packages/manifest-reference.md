# Manifest Reference

**Complete technical reference for the ai-config-kit-package.yaml manifest schema**

This document provides comprehensive details on every field, property, and option available in package manifests.

## Table of Contents

- [Overview](#overview)
- [Manifest Structure](#manifest-structure)
- [Root Fields](#root-fields)
- [Components Section](#components-section)
- [Component Types](#component-types)
- [Validation Rules](#validation-rules)
- [Examples](#examples)

## Overview

The manifest file (`ai-config-kit-package.yaml`) is a YAML file that describes your package. It defines metadata, components, and how they should be installed.

**Location**: Must be named `ai-config-kit-package.yaml` in the package root directory

**Format**: YAML 1.2

**Encoding**: UTF-8

## Manifest Structure

```yaml
# Package Metadata (Required)
name: string
version: string
description: string
author: string
namespace: string

# Package Metadata (Optional)
author_email: string
license: string
homepage: string
repository: string
keywords: [string, ...]

# Components (At least one component required)
components:
  instructions: [...]
  mcp_servers: [...]
  hooks: [...]
  commands: [...]
  resources: [...]
```

## Root Fields

### name

**Type**: `string`

**Required**: Yes

**Description**: Unique identifier for the package

**Constraints**:
- Lowercase letters, numbers, hyphens only
- No underscores, spaces, or special characters
- Must start with a letter
- Length: 3-50 characters
- Must be unique within your namespace

**Valid examples**:
```yaml
name: python-dev-setup
name: django-best-practices
name: react-2024
```

**Invalid examples**:
```yaml
name: Python_Setup        # Uppercase and underscore
name: my package          # Space
name: 123-package         # Starts with number
name: my@package          # Special character
```

---

### version

**Type**: `string`

**Required**: Yes

**Description**: Package version following semantic versioning

**Format**: `MAJOR.MINOR.PATCH`

**Constraints**:
- Must follow semantic versioning (semver)
- Format: `<major>.<minor>.<patch>`
- All parts must be non-negative integers
- Optional pre-release: `1.0.0-alpha.1`
- Optional build metadata: `1.0.0+20250114`

**Examples**:
```yaml
version: 1.0.0            # Initial release
version: 1.2.3            # Standard version
version: 2.0.0-beta.1     # Pre-release
version: 1.0.0+build.123  # With build metadata
```

**Semantic versioning guide**:
- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backwards compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes

---

### description

**Type**: `string`

**Required**: Yes

**Description**: Brief description of what the package does

**Constraints**:
- Length: 10-500 characters
- Single line (no newlines)
- Should be clear and concise

**Examples**:
```yaml
description: Python development best practices and tooling setup
description: Complete Django configuration with ORM guidelines and testing patterns
description: React component library with TypeScript and testing utilities
```

---

### author

**Type**: `string`

**Required**: Yes

**Description**: Name of the package author or organization

**Constraints**:
- Length: 1-100 characters
- Can include spaces and special characters

**Examples**:
```yaml
author: John Doe
author: Acme Corporation
author: Django Team
```

---

### namespace

**Type**: `string`

**Required**: Yes

**Description**: Hierarchical namespace for organizing packages

**Format**: `organization/category` or `organization/category/subcategory`

**Constraints**:
- Forward slash separated
- Each segment: lowercase, hyphens, numbers
- 2-5 segments recommended
- Total length: 5-100 characters

**Examples**:
```yaml
namespace: acme/python-tools
namespace: my-org/web-frameworks/django
namespace: personal/utilities
namespace: team-frontend/react/components
```

**Best practices**:
- Use organization/team name as first segment
- Use technology or category as second segment
- Keep it hierarchical and logical
- Avoid overly deep nesting (>4 levels)

---

### author_email

**Type**: `string`

**Required**: No

**Description**: Contact email for package maintainer

**Constraints**:
- Must be valid email format
- Length: 5-100 characters

**Examples**:
```yaml
author_email: john.doe@example.com
author_email: team@acmecorp.com
```

---

### license

**Type**: `string`

**Required**: No (but recommended for public packages)

**Description**: Software license identifier

**Format**: SPDX license identifier preferred

**Examples**:
```yaml
license: MIT
license: Apache-2.0
license: GPL-3.0
license: BSD-3-Clause
license: Proprietary
```

**Common licenses**:
- `MIT` - Permissive, simple
- `Apache-2.0` - Permissive, explicit patent grant
- `GPL-3.0` - Copyleft, requires derivatives to be open source
- `BSD-3-Clause` - Permissive, minimal restrictions
- `Proprietary` - Private/internal use

**Resources**: https://spdx.org/licenses/

---

### homepage

**Type**: `string`

**Required**: No

**Description**: URL to package documentation or homepage

**Constraints**:
- Must be valid URL
- Should start with `http://` or `https://`

**Examples**:
```yaml
homepage: https://github.com/your-org/package-name
homepage: https://docs.example.com/packages/my-package
homepage: https://mypackage.dev
```

---

### repository

**Type**: `string`

**Required**: No

**Description**: URL to source code repository

**Constraints**:
- Must be valid URL
- Typically a Git repository

**Examples**:
```yaml
repository: https://github.com/your-org/package-name
repository: https://gitlab.com/your-org/package-name
repository: https://bitbucket.org/your-org/package-name
```

---

### keywords

**Type**: `array of strings`

**Required**: No

**Description**: Search keywords for discovering the package

**Constraints**:
- 0-10 keywords recommended
- Each keyword: 2-30 characters
- Lowercase preferred
- Use hyphens for multi-word keywords

**Examples**:
```yaml
keywords: [python, django, web, orm]
keywords: [react, typescript, components, testing]
keywords: [linting, code-quality, best-practices]
```

**Best practices**:
- Include primary technology (python, javascript, etc.)
- Include framework if applicable (django, react, etc.)
- Include category (testing, linting, documentation)
- Avoid redundant keywords

---

## Components Section

The `components` section defines what's included in the package.

**Structure**:
```yaml
components:
  instructions: []      # Optional
  mcp_servers: []       # Optional
  hooks: []             # Optional
  commands: []          # Optional
  resources: []         # Optional
```

**Requirements**:
- At least one component type must be present
- At least one component must be defined
- Empty component type sections can be omitted

**Valid examples**:
```yaml
# Only instructions
components:
  instructions:
    - name: style-guide
      file: instructions/style.md
      description: Style guidelines

# Multiple types
components:
  instructions: [...]
  hooks: [...]
  commands: [...]

# All types (omit empty sections)
components:
  instructions: [...]
  mcp_servers: [...]
  hooks: [...]
  commands: [...]
  resources: [...]
```

---

## Component Types

### Instructions

**Purpose**: Guidelines and rules for AI assistant behavior

**File format**: Markdown (`.md`)

**IDE compatibility**: All (Claude Code, Cursor, Windsurf, GitHub Copilot)

**Schema**:
```yaml
components:
  instructions:
    - name: string              # Required
      description: string       # Required
      file: string              # Required
      tags: [string, ...]       # Optional
```

**Fields**:

#### name
- **Type**: string
- **Required**: Yes
- **Description**: Component identifier
- **Constraints**: Lowercase, hyphens, 2-50 chars
- **Example**: `python-style-guide`

#### description
- **Type**: string
- **Required**: Yes
- **Description**: What the instruction does
- **Constraints**: 5-200 chars
- **Example**: `PEP 8 style guidelines for Python code`

#### file
- **Type**: string
- **Required**: Yes
- **Description**: Relative path to instruction file
- **Constraints**: Must exist, must be `.md`, relative to package root
- **Example**: `instructions/python-style.md`

#### tags
- **Type**: array of strings
- **Required**: No
- **Description**: Categorization tags
- **Constraints**: 0-10 tags, each 2-30 chars
- **Example**: `[python, style, pep8]`

**Complete example**:
```yaml
components:
  instructions:
    - name: python-style-guide
      description: PEP 8 style guidelines for Python code
      file: instructions/python-style.md
      tags: [python, style, pep8]

    - name: testing-best-practices
      description: Test-driven development and pytest patterns
      file: instructions/testing.md
      tags: [python, testing, pytest, tdd]
```

---

### MCP Servers

**Purpose**: Model Context Protocol server configurations

**File format**: JSON

**IDE compatibility**: Claude Code only

**Schema**:
```yaml
components:
  mcp_servers:
    - name: string                    # Required
      description: string             # Required
      file: string                    # Required
      tags: [string, ...]             # Optional
      requires_credentials: [string, ...]  # Optional
```

**Fields**:

#### name
- **Type**: string
- **Required**: Yes
- **Description**: MCP server identifier
- **Constraints**: Lowercase, hyphens, 2-50 chars
- **Example**: `filesystem`

#### description
- **Type**: string
- **Required**: Yes
- **Description**: What capabilities the server provides
- **Constraints**: 5-200 chars
- **Example**: `Filesystem access for reading and writing files`

#### file
- **Type**: string
- **Required**: Yes
- **Description**: Relative path to MCP config JSON
- **Constraints**: Must exist, must be `.json`, relative to package root
- **Example**: `mcp/filesystem.json`

#### tags
- **Type**: array of strings
- **Required**: No
- **Example**: `[filesystem, io, mcp]`

#### requires_credentials
- **Type**: array of strings
- **Required**: No
- **Description**: Environment variables needed for MCP server
- **Constraints**: Each must be valid env var name (UPPERCASE_SNAKE_CASE)
- **Example**: `[ALLOWED_DIRECTORIES, API_KEY]`

**Complete example**:
```yaml
components:
  mcp_servers:
    - name: filesystem
      description: Filesystem access for reading and writing files
      file: mcp/filesystem.json
      tags: [filesystem, io]
      requires_credentials:
        - ALLOWED_DIRECTORIES

    - name: github
      description: GitHub API integration for repository operations
      file: mcp/github.json
      tags: [github, api, vcs]
      requires_credentials:
        - GITHUB_TOKEN
        - GITHUB_ORG
```

**MCP config file format** (`mcp/filesystem.json`):
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

---

### Hooks

**Purpose**: Scripts that run automatically at specific points

**File format**: Shell scripts (`.sh`, `.bash`)

**IDE compatibility**: Claude Code only

**Schema**:
```yaml
components:
  hooks:
    - name: string              # Required
      description: string       # Required
      file: string              # Required
      tags: [string, ...]       # Optional
```

**Fields**:

#### name
- **Type**: string
- **Required**: Yes
- **Description**: Hook identifier
- **Constraints**: Lowercase, hyphens, 2-50 chars
- **Common names**: `pre-commit`, `pre-push`, `post-checkout`
- **Example**: `pre-commit`

#### description
- **Type**: string
- **Required**: Yes
- **Description**: What the hook does and when it runs
- **Constraints**: 5-200 chars
- **Example**: `Run linting and formatting checks before commits`

#### file
- **Type**: string
- **Required**: Yes
- **Description**: Relative path to hook script
- **Constraints**: Must exist, must be `.sh` or `.bash`, relative to package root
- **Example**: `hooks/pre-commit.sh`

#### tags
- **Type**: array of strings
- **Required**: No
- **Example**: `[git, linting, pre-commit]`

**Complete example**:
```yaml
components:
  hooks:
    - name: pre-commit
      description: Run black and ruff before commits
      file: hooks/pre-commit.sh
      tags: [git, python, linting]

    - name: pre-push
      description: Run full test suite before pushing
      file: hooks/pre-push.sh
      tags: [git, testing]
```

**Hook file requirements**:
- Must include shebang: `#!/usr/bin/env bash`
- Must be executable (chmod +x)
- Exit code 0 = success, non-zero = failure
- Should provide clear output

---

### Commands

**Purpose**: Reusable scripts for common tasks

**File format**: Shell scripts (`.sh`, `.bash`)

**IDE compatibility**: Claude Code only

**Schema**:
```yaml
components:
  commands:
    - name: string              # Required
      description: string       # Required
      file: string              # Required
      tags: [string, ...]       # Optional
```

**Fields**:

#### name
- **Type**: string
- **Required**: Yes
- **Description**: Command identifier
- **Constraints**: Lowercase, hyphens, 2-50 chars
- **Example**: `test`, `lint`, `deploy`, `migrate`

#### description
- **Type**: string
- **Required**: Yes
- **Description**: What the command does
- **Constraints**: 5-200 chars
- **Example**: `Run pytest with coverage reporting`

#### file
- **Type**: string
- **Required**: Yes
- **Description**: Relative path to command script
- **Constraints**: Must exist, must be `.sh` or `.bash`, relative to package root
- **Example**: `commands/test.sh`

#### tags
- **Type**: array of strings
- **Required**: No
- **Example**: `[testing, pytest, automation]`

**Complete example**:
```yaml
components:
  commands:
    - name: test
      description: Run pytest with coverage reporting
      file: commands/test.sh
      tags: [testing, pytest]

    - name: lint
      description: Run ruff linter with auto-fix
      file: commands/lint.sh
      tags: [linting, code-quality]

    - name: deploy
      description: Deploy application to staging environment
      file: commands/deploy.sh
      tags: [deployment, automation]
```

**Command file requirements**:
- Must include shebang: `#!/usr/bin/env bash`
- Should be executable (chmod +x)
- Should accept arguments for flexibility
- Should provide verbose output
- Exit code 0 = success, non-zero = failure

---

### Resources

**Purpose**: Configuration files, templates, or other assets

**File format**: Any

**IDE compatibility**: Claude Code, Cursor, Windsurf

**Schema**:
```yaml
components:
  resources:
    - name: string              # Required
      description: string       # Required
      file: string              # Required
      install_path: string      # Optional
      tags: [string, ...]       # Optional
```

**Fields**:

#### name
- **Type**: string
- **Required**: Yes
- **Description**: Resource identifier
- **Constraints**: Lowercase, hyphens, 2-50 chars
- **Example**: `gitignore`, `editorconfig`, `dockerfile`

#### description
- **Type**: string
- **Required**: Yes
- **Description**: What the resource is
- **Constraints**: 5-200 chars
- **Example**: `Standard Python .gitignore file`

#### file
- **Type**: string
- **Required**: Yes
- **Description**: Relative path to resource file
- **Constraints**: Must exist, relative to package root
- **Example**: `resources/.gitignore`

#### install_path
- **Type**: string
- **Required**: No
- **Description**: Where to install in target project (relative to project root)
- **Default**: Project root directory
- **Constraints**: Relative path only, no absolute paths
- **Example**: `.gitignore`, `config/app.yaml`, `docs/README.md`

#### tags
- **Type**: array of strings
- **Required**: No
- **Example**: `[git, config, python]`

**Complete example**:
```yaml
components:
  resources:
    - name: gitignore
      description: Standard Python .gitignore
      file: resources/.gitignore
      install_path: .gitignore
      tags: [git, python]

    - name: editorconfig
      description: Editor configuration for consistent style
      file: resources/.editorconfig
      install_path: .editorconfig
      tags: [editor, config]

    - name: dockerfile
      description: Production-ready Docker configuration
      file: resources/Dockerfile
      install_path: docker/Dockerfile
      tags: [docker, deployment]
```

---

## Validation Rules

DevSync validates manifests during installation. Here are all validation rules:

### Package-Level Validation

| Rule | Error Message |
|------|--------------|
| Manifest file must exist | `Manifest not found at: <path>` |
| Must be valid YAML | `Invalid YAML syntax: <details>` |
| All required fields must be present | `Missing required field: '<field>'` |
| `name` must match pattern | `Invalid package name: must be lowercase with hyphens` |
| `version` must be valid semver | `Invalid version: must follow semantic versioning (X.Y.Z)` |
| `namespace` must have 2+ segments | `Invalid namespace: must be format 'org/category'` |
| At least one component must exist | `Package must contain at least one component` |

### Component-Level Validation

| Rule | Error Message |
|------|--------------|
| Component `name` must be unique | `Duplicate component name: '<name>'` |
| Component `file` must exist | `Component file not found: <file>` |
| Instruction `file` must be `.md` | `Invalid instruction file: must be .md` |
| MCP `file` must be `.json` | `Invalid MCP config: must be .json` |
| MCP JSON must be valid | `Invalid MCP config JSON: <details>` |
| Hook `file` must be `.sh` or `.bash` | `Invalid hook file: must be .sh or .bash` |
| Command `file` must be `.sh` or `.bash` | `Invalid command file: must be .sh or .bash` |
| Resource `install_path` must be relative | `Invalid install_path: must be relative path` |

### Tag Validation

| Rule | Error Message |
|------|--------------|
| Max 10 tags per component | `Too many tags: maximum 10 allowed` |
| Tag must be 2-30 characters | `Invalid tag '<tag>': must be 2-30 characters` |
| Tags should be lowercase | `Warning: tags should be lowercase` |

### Credential Validation

| Rule | Error Message |
|------|--------------|
| Credential names must be UPPERCASE | `Invalid credential name '<name>': must be UPPERCASE_SNAKE_CASE` |
| Credential must be valid env var name | `Invalid credential name '<name>': not a valid environment variable name` |

---

## Examples

### Minimal Package

Smallest valid package:

```yaml
name: minimal-package
version: 1.0.0
description: A minimal example package
author: John Doe
namespace: examples/minimal

components:
  instructions:
    - name: hello
      description: Simple hello world instruction
      file: instructions/hello.md
```

### Instructions-Only Package

Package with only instructions:

```yaml
name: python-style
version: 2.1.0
description: Python style guidelines and best practices
author: Python Team
author_email: team@example.com
namespace: python/style
license: MIT
keywords: [python, style, pep8, best-practices]

components:
  instructions:
    - name: pep8-style
      description: PEP 8 style guide
      file: instructions/pep8.md
      tags: [style, pep8]

    - name: naming-conventions
      description: Naming conventions for Python
      file: instructions/naming.md
      tags: [style, naming]

    - name: docstrings
      description: Docstring formatting guidelines
      file: instructions/docstrings.md
      tags: [documentation, style]
```

### Complete Package (All Components)

Package with all component types:

```yaml
name: django-complete
version: 3.0.0
description: Complete Django development environment with best practices
author: Django Team
author_email: django@example.com
namespace: web-frameworks/django
license: MIT
homepage: https://github.com/example/django-package
repository: https://github.com/example/django-package
keywords: [django, python, web, orm, testing]

components:
  instructions:
    - name: django-models
      description: Django model design patterns and best practices
      file: instructions/models.md
      tags: [django, orm, models]

    - name: django-views
      description: Class-based vs function-based views
      file: instructions/views.md
      tags: [django, views]

    - name: django-testing
      description: Testing strategies for Django applications
      file: instructions/testing.md
      tags: [django, testing, pytest]

  mcp_servers:
    - name: database
      description: PostgreSQL database access via MCP
      file: mcp/database.json
      tags: [database, postgresql]
      requires_credentials:
        - DATABASE_URL

  hooks:
    - name: pre-commit
      description: Run migrations check and linting before commits
      file: hooks/pre-commit.sh
      tags: [git, linting, django]

    - name: pre-push
      description: Run full test suite before pushing
      file: hooks/pre-push.sh
      tags: [git, testing]

  commands:
    - name: migrate
      description: Run Django database migrations
      file: commands/migrate.sh
      tags: [django, database]

    - name: test
      description: Run Django test suite with coverage
      file: commands/test.sh
      tags: [testing, django]

    - name: collectstatic
      description: Collect static files for deployment
      file: commands/collectstatic.sh
      tags: [django, deployment]

  resources:
    - name: settings
      description: Django settings template with best practices
      file: resources/settings.py
      install_path: config/settings_template.py
      tags: [django, config]

    - name: gitignore
      description: Django-specific .gitignore
      file: resources/.gitignore
      install_path: .gitignore
      tags: [git, django]
```

### Monorepo Package (Multiple Related Packages)

Structure for related packages:

```yaml
name: python-toolkit
version: 1.0.0
description: Comprehensive Python development toolkit
author: DevTools Team
namespace: devtools/python
license: MIT

components:
  instructions:
    # Core Python
    - name: python-basics
      description: Core Python guidelines
      file: instructions/basics.md
      tags: [python, fundamentals]

    # Testing
    - name: pytest-patterns
      description: Pytest testing patterns
      file: instructions/testing/pytest.md
      tags: [testing, pytest]

    - name: coverage-guidelines
      description: Code coverage best practices
      file: instructions/testing/coverage.md
      tags: [testing, coverage]

    # Code Quality
    - name: linting-setup
      description: Linting with ruff
      file: instructions/quality/linting.md
      tags: [quality, linting]

    - name: type-checking
      description: Type checking with mypy
      file: instructions/quality/typing.md
      tags: [quality, typing]

  hooks:
    - name: pre-commit
      description: Comprehensive pre-commit checks
      file: hooks/pre-commit.sh
      tags: [git, quality]

  commands:
    - name: test-all
      description: Run all tests with coverage
      file: commands/test-all.sh
      tags: [testing]

    - name: quality-check
      description: Run all quality checks
      file: commands/quality.sh
      tags: [quality]
```

---

## Related Documentation

- **[Creating Packages](creating-packages.md)** - Step-by-step package creation guide
- **[Installation Guide](installation.md)** - How to install packages
- **[CLI Reference](cli-reference.md)** - All package commands
- **[Examples](examples.md)** - Real-world package examples

---

**Questions?** Check the [Troubleshooting Guide](troubleshooting.md) or [open an issue](https://github.com/troylar/devsync/issues).
