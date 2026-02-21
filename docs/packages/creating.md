# Creating Packages

## Using `devsync extract` (Recommended)

The easiest way to create a package is to extract practices from an existing project:

```bash
cd ~/my-project
devsync extract --output ./team-standards --name team-standards
```

DevSync reads the project's AI rules (`.claude/rules/`, `.cursor/rules/`, etc.), MCP configurations, and other tool-specific files. It produces a v2 package with abstract practice declarations.

### What Gets Extracted

| Source | Locations Scanned |
|--------|------------------|
| Rules/Instructions | `.claude/rules/`, `.cursor/rules/`, `.windsurf/rules/`, `.github/instructions/`, `.kiro/steering/`, `.clinerules/`, `.roo/rules/` |
| MCP Configurations | `.claude/settings.local.json`, `.cursor/mcp.json`, `.vscode/mcp.json` |
| Single-file Configs | `AGENTS.md`, `CONVENTIONS.md`, `GEMINI.md` |

### Output Structure

```
team-standards/
├── devsync-package.yaml    # Package manifest
├── practices/              # Practice declaration files
│   ├── type-safety.md
│   ├── error-handling.md
│   └── code-style.md
└── mcp/                    # MCP server configs (if found)
    └── github.json
```

### File-Copy Mode

Extract without AI processing:

```bash
devsync extract --output ./pkg --name my-pkg --no-ai
```

Source files are copied verbatim instead of being converted to practice declarations.

### Upgrading v1 Packages

Convert an existing v1 package to v2 format:

```bash
devsync extract --upgrade ./old-v1-package --output ./v2-package --name my-package
```

## v2 Package Manifest

The `devsync-package.yaml` manifest declares package metadata and practice declarations:

```yaml
name: team-standards
version: 1.0.0
description: Team coding standards and MCP configurations

practices:
  - name: type-safety
    intent: Enforce strict type annotations in all code
    principles:
      - All functions must have type hints for parameters and return values
      - Use modern Python syntax (list[str] not List[str])
      - Prefer strict mypy configuration
    enforcement_patterns:
      - Run mypy in strict mode in CI
      - Use ruff rules for type annotation enforcement
    examples:
      - "def process(items: list[str]) -> dict[str, int]: ..."
    tags: [python, types, quality]

  - name: error-handling
    intent: Structured error handling with custom exceptions
    principles:
      - Use custom exception classes for domain errors
      - Handle errors at the appropriate level
      - Never swallow exceptions silently
    enforcement_patterns:
      - Code review checklist includes error handling
    tags: [python, errors]

mcp_servers:
  - name: github
    description: GitHub API access for PRs and issues
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    credentials:
      - name: GITHUB_TOKEN
        description: GitHub personal access token
        required: true
```

## v1 Package Manifest (Backward Compatible)

DevSync v2 still supports v1 `ai-config-kit-package.yaml` manifests. These use a `components` section with file references:

```yaml
name: python-dev-setup
version: 1.0.0
description: Python development configuration
author: Platform Team
license: MIT
namespace: platform/python

components:
  instructions:
    - name: python-style
      file: instructions/python-style.md
      description: PEP 8 guidelines
      tags: [python, style]

  mcp_servers:
    - name: filesystem
      file: mcp/filesystem.json
      description: Filesystem access server
      credentials:
        - name: ALLOWED_DIRECTORIES
          description: Directories the server can access
          required: false
          default: "."

  hooks:
    - name: pre-commit
      file: hooks/pre-commit.sh
      description: Run checks before commits
      hook_type: pre-commit

  commands:
    - name: test
      file: commands/test.sh
      description: Run test suite
      command_type: shell

  resources:
    - name: gitignore
      file: resources/.gitignore
      description: Standard gitignore
      install_path: .gitignore
```

## Testing a Package

After creating a package, verify it works:

```bash
# Create a temporary test project
mkdir /tmp/test-project && cd /tmp/test-project
git init

# Install the package
devsync install /path/to/my-package

# Check what was installed
devsync list

# Verify files exist
ls -la .claude/rules/
ls -la .cursor/rules/

# Clean up
devsync uninstall my-package --force
```

## Distributing Packages

### Via Git

Push your package directory to a Git repository:

```bash
cd team-standards
git init && git add . && git commit -m "Initial package"
git remote add origin https://github.com/company/team-standards
git push -u origin main
```

Others install with:

```bash
devsync install https://github.com/company/team-standards
```

### Via Shared Directory

Copy the package directory to a shared location (NFS, Dropbox, etc.):

```bash
cp -r ./team-standards /shared/packages/
```

Others install with:

```bash
devsync install /shared/packages/team-standards
```

### Inside a Project Repo

Include the package as a subdirectory in an existing repository:

```bash
my-project/
├── src/
├── tests/
└── .devsync-package/     # Package for new contributors
    └── devsync-package.yaml
```

New contributors install with:

```bash
devsync install ./.devsync-package
```

## Best Practices

**Keep packages focused.** A package for "Python development" is better than a package for "everything." Users can install multiple packages.

**Use semantic versioning.** Bump the patch version for typo fixes, minor for new practices, major for breaking changes.

**Write a README.** Include what the package does, what tools it requires, and how to customize after installation.

**Version control your packages.** A package directory works well as a Git repository. Tag releases to match the manifest version.
