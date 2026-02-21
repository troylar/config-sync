# Component Types

This page documents each component type that a package can contain: the manifest format, file format, and how the component is installed.

## Practices (v2)

Practices are abstract declarations of coding standards. They are the primary component type in v2 packages and are processed by AI during extraction and installation.

### v2 Manifest Entry

```yaml
practices:
  - name: type-safety
    intent: Enforce strict type annotations
    principles:
      - All functions must have type hints
      - Use modern syntax (list[str] not List[str])
    enforcement_patterns:
      - Run mypy in strict mode
    examples:
      - "def process(items: list[str]) -> int: ..."
    tags: [python, types]
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Short identifier (e.g., `type-safety`) |
| `intent` | Yes | One-line description of what it enforces |
| `principles` | Yes | List of rules and guidelines |
| `enforcement_patterns` | No | How to enforce (CI, linting, etc.) |
| `examples` | No | Code examples demonstrating the practice |
| `tags` | No | Categorization tags |

### How Practices Are Installed

With AI enabled, practices are adapted to the target project's existing rules:

- If no existing rule covers the same topic, a new file is created
- If an existing rule overlaps, the AI merges the practice into it
- Each IDE gets its own adapted version in the correct format

Without AI (`--no-ai`), the raw practice content is written as a markdown file to each tool's directory.

---

## Instructions (v1)

Instructions are Markdown files that guide AI coding assistant behavior. They are the v1 equivalent of practices -- raw file content rather than abstract declarations.

### Manifest Entry

```yaml
components:
  instructions:
    - name: code-quality
      file: instructions/code-quality.md
      description: Code quality and review guidelines
      tags: [quality, review]
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier within the package |
| `file` | Yes | Relative path to the .md file |
| `description` | Yes | What this instruction covers |
| `tags` | No | Searchable categorization tags |

### Installation Paths

| IDE | Installed To | Extension |
|-----|-------------|-----------|
| Claude Code | `.claude/rules/<name>.md` | `.md` |
| Cursor | `.cursor/rules/<name>.mdc` | `.mdc` |
| Windsurf | `.windsurf/rules/<name>.md` | `.md` |
| GitHub Copilot | `.github/instructions/<name>.instructions.md` | `.instructions.md` |
| Kiro | `.kiro/steering/<name>.md` | `.md` |
| Cline | `.clinerules/<name>.md` | `.md` |
| Roo Code | `.roo/rules/<name>.md` | `.md` |
| Codex CLI | Section in `AGENTS.md` | `.md` |

---

## MCP Servers

MCP (Model Context Protocol) server configurations define external tool integrations. Each MCP component is a JSON file that tells the IDE how to launch and connect to an MCP server.

### v2 Manifest Entry

```yaml
mcp_servers:
  - name: github
    description: GitHub API access
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    credentials:
      - name: GITHUB_TOKEN
        description: GitHub personal access token
        required: true
```

### v1 Manifest Entry

```yaml
components:
  mcp_servers:
    - name: filesystem
      file: mcp/filesystem.json
      description: Local filesystem access via MCP
      credentials:
        - name: ALLOWED_DIRECTORIES
          description: Directories to expose
          required: false
          default: "."
```

### Credential Descriptors

Each credential entry describes an environment variable:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Env var name (UPPER_SNAKE_CASE) |
| `description` | Yes | What this credential is for |
| `required` | No | Whether user must provide it (default: true) |
| `default` | No | Default value (only valid when required=false) |

!!! note "Validation"
    A credential cannot be both `required: true` and have a `default` value.

### Supported IDEs

Claude Code, Cursor, Windsurf, Roo Code, GitHub Copilot, and others. See [IDE Compatibility](index.md#ide-compatibility).

---

## Hooks

Hooks are shell scripts triggered by IDE lifecycle events. Currently, only Claude Code supports hooks.

### Manifest Entry

```yaml
components:
  hooks:
    - name: pre-commit
      file: hooks/pre-commit.sh
      description: Run linting before commits
      hook_type: pre-commit
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Hook identifier |
| `file` | Yes | Relative path to shell script |
| `description` | Yes | What the hook does |
| `hook_type` | Yes | Trigger type (e.g., `PreToolUse`, `PostToolUse`) |

### Installation Path

| IDE | Installed To |
|-----|-------------|
| Claude Code | `.claude/hooks/<name>.sh` |

---

## Commands

Commands are shell scripts or slash commands that users invoke on demand.

### Manifest Entry

```yaml
components:
  commands:
    - name: test
      file: commands/test.sh
      description: Run test suite with coverage
      command_type: shell
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Command identifier |
| `file` | Yes | Relative path to script |
| `description` | Yes | What the command does |
| `command_type` | Yes | Type: `shell` or `slash` |

### Installation Paths

| IDE | Installed To |
|-----|-------------|
| Claude Code | `.claude/commands/<name>.sh` |
| Roo Code | `.roo/commands/<name>.md` |

---

## Resources

Resources are arbitrary files -- configuration templates, .gitignore files, editor configs, or any other file that should be part of the project setup.

### Manifest Entry

```yaml
components:
  resources:
    - name: gitignore
      file: resources/.gitignore
      description: Python-specific gitignore
      install_path: .gitignore
      checksum: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      size: 450
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Resource identifier |
| `file` | Yes | Relative path in package |
| `description` | Yes | What the resource is |
| `install_path` | Yes | Where to install relative to project root |
| `checksum` | Yes | SHA-256 checksum for integrity |
| `size` | Yes | File size in bytes |

Resources are copied verbatim (both text and binary files are supported).

| IDE | Supported |
|-----|-----------|
| Claude Code | Yes |
| Cursor | Yes |
| Windsurf | Yes |
| Kiro | Yes |
| Cline | Yes |
| Roo Code | Yes |
| Codex CLI | Yes |
| GitHub Copilot | No |
