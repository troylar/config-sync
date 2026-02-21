# YAML Schema Reference

DevSync uses several YAML manifest formats. The primary v2 format is `devsync-package.yaml`. The v1 formats (`ai-config-kit-package.yaml` and `ai-config-kit.yaml`) are still supported for backward compatibility.

## devsync-package.yaml

The v2 package manifest. Placed at the root of a package directory. Supports the `practices` section for AI-native content distribution alongside the v1 `components` section.

### Schema

```yaml
# Required fields
name: string              # Package identifier (lowercase, alphanumeric, hyphens)
version: string           # Semantic version
description: string       # Package description

# Optional metadata
author: string            # Package author
license: string           # License identifier (e.g., "MIT", "Apache-2.0")
namespace: string         # Repository namespace (e.g., "org/repo")

# Practices (AI-native content -- primary v2 approach)
practices:
  - name: string          # Practice identifier (lowercase, hyphenated)
    intent: string        # One-sentence description of what this practice achieves
    principles:           # Core rules or values (list of strings)
      - string
    enforcement_patterns: # Concrete implementation examples (list of strings)
      - string
    examples:             # Optional illustrative examples (list of strings)
      - string
    tags:                 # Optional categorization tags
      - string

# MCP server configurations (in practices-based packages)
mcp_servers:
  - name: string          # Server identifier
    description: string   # What the server provides
    command: string       # Executable command (e.g., "npx")
    args:                 # Command-line arguments
      - string
    credentials:          # Required environment variables
      - name: string      # Env var name (UPPER_SNAKE_CASE)
        description: string
        required: boolean # Default: true
        default: string   # Default value (only if not required)
        example: string   # Example value for guidance

# Components (v1-compatible file-copy approach, optional)
components:
  instructions:
    - name: string
      file: string
      description: string
      tags:
        - string
  # ... (same structure as ai-config-kit-package.yaml components)
```

### practices[] Field Details

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier within the package |
| `intent` | Yes | One-sentence statement of what behavior or standard this practice enforces |
| `principles` | Yes | List of core rules that define the practice |
| `enforcement_patterns` | No | Concrete patterns the AI should look for or enforce |
| `examples` | No | Illustrative code or workflow examples |
| `tags` | No | List of string tags for filtering |

### Example

```yaml
name: python-team-standards
version: 1.0.0
description: Python development standards for AI coding assistants
author: Platform Team
license: MIT

practices:
  - name: type-safety
    intent: Ensure all Python code uses explicit type annotations
    principles:
      - All function signatures must include parameter and return type hints
      - Use built-in generic types (list[str], dict[str, int]) not typing module equivalents
      - Avoid Any except where genuinely unavoidable
    enforcement_patterns:
      - Flag functions missing return type annotations
      - Suggest specific types when Any is used
    tags: [python, types, mypy]

  - name: testing-standards
    intent: Maintain high test coverage with clear, isolated unit tests
    principles:
      - Write tests before implementation (TDD preferred)
      - Each test function covers exactly one behavior
      - Use pytest fixtures for shared state, not setUp/tearDown
    enforcement_patterns:
      - New public functions must have at least one unit test
      - Tests must not depend on external services without mocking
    tags: [python, testing, pytest]

mcp_servers:
  - name: postgres-explorer
    description: Read-only PostgreSQL access for schema exploration
    command: npx
    args: ["-y", "@modelcontextprotocol/server-postgres"]
    credentials:
      - name: DATABASE_URL
        description: PostgreSQL connection string
        required: true
        example: postgresql://user:pass@localhost:5432/mydb
```

---

## ai-config-kit.yaml (v1 instruction repository format)

The v1 instruction repository manifest. Placed at the root of an instruction repository to define available instructions and bundles.

### Schema

```yaml
# Required fields
name: string              # Repository display name
description: string       # Repository description
version: string           # Semantic version (e.g., "1.0.0")

# Optional fields
author: string            # Author or team name

# Instruction definitions (at least one required)
instructions:
  - name: string          # Unique identifier (lowercase, hyphenated)
    description: string   # What this instruction does
    file: string          # Relative path to instruction file
    tags:                 # Optional categorization tags
      - string

# Bundle definitions (optional)
bundles:
  - name: string          # Bundle identifier
    description: string   # What this bundle provides
    instructions:         # List of instruction names (must reference defined instructions)
      - string
    tags:                 # Optional tags
      - string
```

### Field Details

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Human-readable repository name |
| `description` | Yes | What this repository provides |
| `version` | Yes | Semantic version string |
| `author` | No | Author or team name |
| `instructions` | Yes | At least one instruction must be defined |
| `instructions[].name` | Yes | Unique identifier within the repository |
| `instructions[].description` | Yes | Non-empty description |
| `instructions[].file` | Yes | Relative path from repository root to the instruction file |
| `instructions[].tags` | No | List of string tags for filtering |
| `bundles` | No | Predefined groups of instructions |
| `bundles[].name` | Yes | Unique bundle identifier |
| `bundles[].description` | Yes | Non-empty description |
| `bundles[].instructions` | Yes | Must reference at least one defined instruction by name |
| `bundles[].tags` | No | List of string tags |

### Example

```yaml
name: Python Best Practices
description: Curated Python development instructions for AI coding assistants
version: 2.0.0
author: DevOps Team

instructions:
  - name: python-style
    description: PEP 8 style guide enforcement
    file: instructions/python-style.md
    tags: [python, style, formatting]

  - name: testing-guide
    description: pytest testing conventions and patterns
    file: instructions/testing-guide.md
    tags: [python, testing, pytest]

  - name: api-design
    description: REST API design principles
    file: instructions/api-design.md
    tags: [python, api, rest]

  - name: security-rules
    description: OWASP-based security guidelines
    file: instructions/security-rules.md
    tags: [python, security, owasp]

bundles:
  - name: python-backend
    description: Complete Python backend development setup
    instructions:
      - python-style
      - testing-guide
      - api-design
      - security-rules
    tags: [python, backend, full-stack]

  - name: python-minimal
    description: Minimal Python style and testing
    instructions:
      - python-style
      - testing-guide
    tags: [python, minimal]
```

---

## ai-config-kit-package.yaml (v1 package format)

The v1 package manifest. Placed at the root of a package directory to define multi-component configuration bundles. Still supported for backward compatibility -- v1 packages install via file-copy mode.

### Schema

```yaml
# Required fields
name: string              # Package identifier (lowercase, alphanumeric, hyphens)
version: string           # Semantic version
description: string       # Package description

# Optional metadata
author: string            # Package author
license: string           # License identifier (e.g., "MIT", "Apache-2.0")
namespace: string         # Repository namespace (e.g., "org/repo")

# Components (at least one section must be non-empty)
components:
  # Instruction files
  instructions:
    - name: string        # Instruction identifier
      file: string        # Relative path to file
      description: string # What the instruction does
      tags:               # Optional tags
        - string
      ide_support:        # Optional: restrict to specific IDEs
        - string          # e.g., "claude", "cursor"

  # MCP server configurations
  mcp_servers:
    - name: string        # Server identifier
      file: string        # Relative path to JSON config template
      description: string # What the server provides
      ide_support:        # IDEs that support MCP
        - string
      credentials:        # Required environment variables
        - name: string    # Env var name (UPPER_SNAKE_CASE)
          description: string
          required: boolean    # Default: true
          default: string      # Default value (only if not required)
          example: string      # Example value for guidance

  # Lifecycle hooks
  hooks:
    - name: string        # Hook identifier
      file: string        # Relative path to hook script
      description: string # What the hook does
      hook_type: string   # Trigger type: "PreToolUse", "PostToolUse", etc.
      ide_support:        # Default: ["claude"]
        - string

  # Slash commands and scripts
  commands:
    - name: string        # Command identifier
      file: string        # Relative path to command file
      description: string # What the command does
      command_type: string # "slash" or "shell"
      ide_support:
        - string

  # Claude skills (directories with SKILL.md)
  skills:
    - name: string        # Skill identifier (directory name)
      file: string        # Relative path to skill directory
      description: string # What the skill does
      ide_support:        # Default: ["claude"]
        - string

  # Windsurf workflows
  workflows:
    - name: string        # Workflow identifier
      file: string        # Relative path to workflow file
      description: string # What the workflow does
      ide_support:        # Default: ["windsurf"]
        - string

  # CLAUDE.md memory files
  memory_files:
    - name: string        # File identifier
      file: string        # Relative path to CLAUDE.md
      description: string # What context it provides
      ide_support:        # Default: ["claude"]
        - string

  # Arbitrary resource files
  resources:
    - name: string        # Resource identifier
      file: string        # Relative path to file
      description: string # What the resource is
      install_path: string # Where to install (defaults to file path)
      checksum: string    # SHA-256 checksum (sha256:...)
      size: integer       # File size in bytes
```

### Component Type Support by IDE

Not all IDEs support all component types. Unsupported components are automatically skipped during installation.

| Component | Claude | Cursor | Windsurf | Copilot | Kiro | Cline | Roo | Codex | Gemini |
|-----------|--------|--------|----------|---------|------|-------|-----|-------|--------|
| Instructions | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| MCP Servers | Yes | Yes | Yes | Yes | -- | -- | Yes | -- | -- |
| Hooks | Yes | -- | -- | -- | -- | -- | -- | -- | -- |
| Commands | Yes | -- | -- | -- | -- | -- | Yes | -- | -- |
| Skills | Yes | -- | -- | -- | -- | -- | -- | -- | -- |
| Workflows | -- | -- | Yes | -- | -- | -- | -- | -- | -- |
| Memory Files | Yes | -- | -- | -- | -- | -- | -- | -- | -- |
| Resources | Yes | Yes | Yes | -- | Yes | Yes | Yes | Yes | Yes |

### Example

```yaml
name: python-dev-setup
version: 1.0.0
description: Complete Python development configuration for AI assistants
author: Platform Team
license: MIT
namespace: myorg/python-dev-setup

components:
  instructions:
    - name: python-style
      file: instructions/python-style.md
      description: PEP 8 and project-specific style rules
      tags: [python, style]

    - name: testing-guide
      file: instructions/testing-guide.md
      description: pytest conventions and patterns
      tags: [python, testing]

  mcp_servers:
    - name: postgres-explorer
      file: mcp/postgres-explorer.json
      description: Read-only database exploration for AI assistants
      ide_support: [claude, cursor]
      credentials:
        - name: DATABASE_URL
          description: PostgreSQL connection string
          required: true
          example: postgresql://user:pass@localhost:5432/mydb

  hooks:
    - name: lint-check
      file: hooks/lint-check.sh
      description: Run ruff check before AI tool modifications
      hook_type: PreToolUse
      ide_support: [claude]

  commands:
    - name: run-tests
      file: commands/run-tests.md
      description: Execute test suite with coverage
      command_type: slash
      ide_support: [claude]

  skills:
    - name: deploy
      file: skills/deploy/
      description: Production deployment skill
      ide_support: [claude]

  workflows:
    - name: code-review
      file: workflows/code-review.md
      description: Automated code review workflow
      ide_support: [windsurf]

  memory_files:
    - name: project-context
      file: memory/CLAUDE.md
      description: Project architecture and conventions
      ide_support: [claude]

  resources:
    - name: schema-diagram
      file: resources/schema.png
      description: Database schema diagram
      install_path: .devsync/resources/schema.png
      checksum: sha256:abc123...
      size: 45678
```

