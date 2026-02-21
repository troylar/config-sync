# Package Examples

Complete package examples covering common use cases.

---

## 1. Team Standards (v2 AI-Native)

A v2 package extracted from a project with established coding standards. Contains practice declarations that AI adapts to each recipient's setup.

### Creating the Package

```bash
cd ~/team-project
devsync extract --output ./team-standards --name team-standards
```

### Output Structure

```
team-standards/
├── devsync-package.yaml
├── practices/
│   ├── code-style.md
│   ├── testing-strategy.md
│   └── error-handling.md
└── mcp/
    └── github.json
```

### Manifest

```yaml
name: team-standards
version: 1.0.0
description: Team coding standards extracted from the main project

practices:
  - name: code-style
    intent: Consistent code formatting and naming conventions
    principles:
      - Line length 120 characters maximum
      - Use black for formatting, ruff for linting
      - snake_case for functions and variables, PascalCase for classes
      - Modern type hints (list[str] not List[str])
    enforcement_patterns:
      - Pre-commit hooks run black and ruff
      - CI pipeline includes format and lint checks
    examples:
      - "def process_items(items: list[dict[str, str]], limit: int = 10) -> list[str]:"
    tags: [python, style, formatting]

  - name: testing-strategy
    intent: Test-first development with pytest
    principles:
      - Write tests before implementation
      - Use pytest fixtures, not setUp/tearDown
      - Mock external dependencies in unit tests
      - Minimum 80% coverage target
    enforcement_patterns:
      - CI pipeline runs pytest with coverage
      - PRs blocked if coverage drops
    tags: [python, testing, pytest]

  - name: error-handling
    intent: Structured error handling with custom exceptions
    principles:
      - Use custom exception classes for domain errors
      - Handle errors at the appropriate abstraction level
      - Never swallow exceptions silently
      - Log errors with context (user ID, request ID)
    enforcement_patterns:
      - Code review checklist includes error handling review
    tags: [python, errors, logging]

mcp_servers:
  - name: github
    description: GitHub API access for PRs and issues
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    credentials:
      - name: GITHUB_TOKEN
        description: GitHub personal access token with repo scope
        required: true
```

### Installation

```bash
# AI-powered installation (adapts to existing rules)
devsync install ./team-standards

# Or from Git
devsync install https://github.com/company/team-standards
```

---

## 2. Security Compliance (v2 AI-Native)

A security-focused package with practices covering OWASP guidelines.

### Manifest

```yaml
name: security-compliance
version: 1.0.0
description: OWASP-aligned secure coding practices

practices:
  - name: input-validation
    intent: Validate all input on the server side
    principles:
      - Use allowlists over denylists for validation
      - Parameterized queries for all database operations
      - Context-encode all output (HTML, JS, URL)
      - Validate file uploads (MIME type, extension, size)
    enforcement_patterns:
      - SAST scanning in CI (Semgrep, CodeQL)
      - Dependency vulnerability scanning (pip-audit, npm audit)
    tags: [security, validation, owasp]

  - name: authentication
    intent: Secure authentication and session management
    principles:
      - Use established auth frameworks, never roll your own
      - Passwords stored with Argon2id or bcrypt (cost >= 12)
      - Session IDs from CSPRNG with >= 128 bits entropy
      - Rate limiting on login endpoints
    enforcement_patterns:
      - Security review required for auth changes
    tags: [security, auth, sessions]

  - name: secrets-management
    intent: No hardcoded secrets, credentials in env vars or secrets manager
    principles:
      - Never hardcode API keys, passwords, or tokens
      - Use environment variables or secrets manager
      - Never log credential values
      - TLS 1.2+ for all data in transit
    enforcement_patterns:
      - Secret scanning in CI (gitleaks, trufflehog)
      - Pre-commit hooks check for hardcoded patterns
    tags: [security, secrets, credentials]
```

### Installation

```bash
# Works with any IDE
devsync install ./security-compliance
devsync install ./security-compliance --tool claude --tool cursor
```

---

## 3. Full-Stack Team (v1 Format)

A v1-format package that bundles instructions, MCP servers, hooks, commands, and resources.

### Directory Structure

```
fullstack-team/
├── ai-config-kit-package.yaml
├── instructions/
│   ├── api-design.md
│   ├── react-components.md
│   └── database-patterns.md
├── mcp/
│   ├── filesystem.json
│   └── github.json
├── hooks/
│   └── pre-commit.sh
├── commands/
│   └── test-all.sh
└── resources/
    └── .editorconfig
```

### Manifest

```yaml
name: fullstack-team
version: 2.0.0
description: Full-stack development environment
author: Engineering
license: MIT
namespace: acme/fullstack

components:
  instructions:
    - name: api-design
      file: instructions/api-design.md
      description: RESTful API design patterns
      tags: [api, rest, backend]

    - name: react-components
      file: instructions/react-components.md
      description: React component patterns with TypeScript
      tags: [react, typescript, frontend]

    - name: database-patterns
      file: instructions/database-patterns.md
      description: Database schema design and query optimization
      tags: [database, sql, backend]

  mcp_servers:
    - name: filesystem
      file: mcp/filesystem.json
      description: Project filesystem access
      credentials:
        - name: ALLOWED_DIRECTORIES
          description: Directories to expose
          required: false
          default: "."

    - name: github
      file: mcp/github.json
      description: GitHub API access
      credentials:
        - name: GITHUB_TOKEN
          description: GitHub personal access token
          required: true

  hooks:
    - name: pre-commit
      file: hooks/pre-commit.sh
      description: Run ESLint, Prettier, and backend linting
      hook_type: pre-commit

  commands:
    - name: test-all
      file: commands/test-all.sh
      description: Run frontend and backend test suites
      command_type: shell

  resources:
    - name: editorconfig
      file: resources/.editorconfig
      description: Editor configuration
      install_path: .editorconfig
      checksum: sha256:d4e5f6a7b8c9...
      size: 280
```

### Installation

```bash
# v1 packages use file-copy mode automatically
devsync install ./fullstack-team

# Install to specific tools
devsync install ./fullstack-team --tool claude --tool cursor
```

---

## 4. Upgrading v1 to v2

Convert any v1 package to v2 format using `--upgrade`:

```bash
# Upgrade v1 package
devsync extract --upgrade ./fullstack-team --output ./fullstack-v2 --name fullstack-team

# The new package uses practice declarations
cat fullstack-v2/devsync-package.yaml
```

The upgraded package preserves MCP server configurations and converts instructions into practice declarations.

!!! tip "Mixed packages"
    A v2 package can include both practice declarations and v1-style components. DevSync handles both formats during installation.
