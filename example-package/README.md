# Example Configuration Package

This is an example configuration package for DevSync, demonstrating all supported component types.

## Package Contents

### Instructions (2)
- **code-quality.md**: Code quality guidelines and best practices
- **testing-strategy.md**: Testing strategy and TDD guidelines

### MCP Servers (1)
- **filesystem**: Local filesystem access MCP server

### Hooks (1)
- **pre-commit.sh**: Pre-commit hook for linting and formatting

### Commands (1)
- **test.sh**: Run test suite with coverage

### Resources (1)
- **.gitignore**: Standard gitignore for AI projects

## Installation

Install this package to your project:

```bash
# For Claude Code
aiconfig package install example-package --ide claude

# For Cursor
aiconfig package install example-package --ide cursor

# For Windsurf
aiconfig package install example-package --ide windsurf

# For GitHub Copilot
aiconfig package install example-package --ide copilot
```

## Usage

After installation:

### Instructions
Instructions are automatically loaded by your IDE:
- Claude Code: `.claude/rules/code-quality.md`
- Cursor: `.cursor/rules/code-quality.mdc`

### MCP Server
Configure the filesystem MCP server with environment variables:
```bash
export ALLOWED_DIRECTORIES="/path/to/project,/other/path"
```

### Hooks
The pre-commit hook will run automatically before commits:
```bash
git commit -m "Your message"
# Hook runs automatically
```

### Commands
Run the test command:
```bash
./.claude/commands/test.sh
# or
bash ./.claude/commands/test.sh
```

### Resources
The `.gitignore` file is copied to your project root.

## Package Management

```bash
# List installed packages
aiconfig package list

# Uninstall this package
aiconfig package uninstall example-package

# Reinstall with force
aiconfig package install example-package --force
```

## Creating Your Own Package

Use this as a template to create your own packages:

1. Create a directory with your package name
2. Create `ai-config-kit-package.yaml` manifest
3. Add your components in subdirectories:
   - `instructions/` - Instruction files
   - `mcp/` - MCP server configurations
   - `hooks/` - Hook scripts
   - `commands/` - Command scripts
   - `resources/` - Resource files
4. Test installation locally
5. Share your package!

## Package Manifest Format

```yaml
name: your-package-name
version: 1.0.0
description: Package description
author: Your Name
license: MIT
namespace: your-org/repo

components:
  instructions:
    - name: instruction-name
      file: instructions/file.md
      description: Description
      tags: [tag1, tag2]

  mcp_servers:
    - name: server-name
      file: mcp/config.json
      description: Description
      credentials:
        - name: VAR_NAME
          description: Description
          required: true

  hooks:
    - name: hook-name
      file: hooks/script.sh
      description: Description
      hook_type: pre-commit

  commands:
    - name: command-name
      file: commands/script.sh
      description: Description
      command_type: shell

  resources:
    - name: resource-name
      file: resources/file.txt
      description: Description
      checksum: sha256:...
      size: 1234
```

## License

MIT License - See LICENSE file for details
