# Tutorial: Build Custom Packages

**Time:** 20 minutes | **Level:** Intermediate

Build a package with practices, MCP servers, and other components.

---

## What You Will Learn

- Extract an AI-native v2 package from a project
- Customize the extracted package manifest
- Include MCP server configurations
- Test and distribute the package

## Prerequisites

- DevSync installed (`pip install devsync`)
- LLM configured (`devsync setup`)
- A project with AI rules and/or MCP configurations

---

## Step 1: Extract from Your Project

```bash
cd ~/my-project
devsync extract --output ./my-package --name my-package
```

This creates a v2 package with practice declarations and MCP configs.

## Step 2: Review and Customize

Open the manifest:

```bash
cat my-package/devsync-package.yaml
```

You can edit the manifest to:

- Rename practices for clarity
- Add or remove principles
- Adjust tags for better categorization
- Add MCP servers not detected automatically

### Adding an MCP Server Manually

Add to the `mcp_servers` section of the manifest:

```yaml
mcp_servers:
  - name: postgres-explorer
    description: Read-only database access for AI assistants
    command: npx
    args: ["-y", "@modelcontextprotocol/server-postgres"]
    credentials:
      - name: DATABASE_URL
        description: PostgreSQL connection string
        required: true
```

## Step 3: Build a v1-Style Package (Alternative)

If you need hooks, commands, or resources, create a v1-format package manually:

```
my-package/
├── ai-config-kit-package.yaml
├── instructions/
│   └── code-quality.md
├── mcp/
│   └── github.json
├── hooks/
│   └── pre-commit.sh
├── commands/
│   └── test.sh
└── resources/
    └── .editorconfig
```

```yaml
# ai-config-kit-package.yaml
name: my-package
version: 1.0.0
description: Custom development package
author: Your Name
license: MIT
namespace: company/my-package

components:
  instructions:
    - name: code-quality
      file: instructions/code-quality.md
      description: Code quality guidelines
      tags: [quality]

  mcp_servers:
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
      description: Run checks before commits
      hook_type: pre-commit

  commands:
    - name: test
      file: commands/test.sh
      description: Run test suite
      command_type: shell

  resources:
    - name: editorconfig
      file: resources/.editorconfig
      description: Editor configuration
      install_path: .editorconfig
      checksum: sha256:abc123...
      size: 280
```

## Step 4: Test the Package

```bash
# Create a test project
mkdir /tmp/test-project && cd /tmp/test-project
git init

# Install the package
devsync install ~/my-project/my-package

# Check what was installed
devsync list

# Verify files
ls -la .claude/rules/
ls -la .cursor/rules/

# Clean up
devsync uninstall my-package --force
```

Test across multiple IDEs:

```bash
# Claude Code gets all component types
devsync install ./my-package --tool claude

# Cursor gets practices/instructions, MCP, and resources only
devsync install ./my-package --tool cursor
```

## Step 5: Distribute

### Via Git

```bash
cd my-package
git init && git add . && git commit -m "Initial package"
git remote add origin https://github.com/company/my-package
git push -u origin main
```

### Via Shared Directory

```bash
cp -r ./my-package /shared/packages/
```

### Inside a Project Repo

```bash
# Include as a subdirectory
cp -r ./my-package ~/my-project/.devsync-package/
```

---

## Next Steps

- [Package Examples](../packages/examples.md) -- complete real-world package examples
- [Component Types](../packages/components.md) -- detailed reference for each component
- [Multi-IDE Workflow](multi-ide-workflow.md) -- managing across multiple IDEs
