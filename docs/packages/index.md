# Configuration Packages

## What Are Packages?

A configuration package is a shareable bundle of coding practices, MCP server configurations, and other components that configure AI coding assistants as a unit. DevSync v2 packages use AI to extract abstract practice declarations and adapt them intelligently when installed.

A package can contain:

| Component Type | Description |
|----------------|-------------|
| **Practices** | Abstract declarations of coding standards (AI-native, v2) |
| **Instructions** | Markdown guidelines that shape AI behavior (v1 compat) |
| **MCP Servers** | Model Context Protocol server configurations |
| **Hooks** | Scripts triggered by IDE lifecycle events |
| **Commands** | Reusable slash commands and shell scripts |
| **Resources** | Configuration files, templates, .gitignore, etc. |

## v2 Packages: AI-Native

DevSync v2 introduces **practice declarations** -- abstract representations of coding standards that capture intent rather than raw file content. This enables AI-powered adaptation when installing into new projects.

**Creating a package:**

```bash
# Extract practices from your project
devsync extract --output ./team-standards --name team-standards
```

**Installing a package:**

```bash
# AI adapts practices to the target project's existing setup
devsync install ./team-standards
```

The AI reads the target project's existing rules and merges incoming practices intelligently -- no duplication, no blind overwriting.

## v1 Backward Compatibility

DevSync v2 fully supports v1 packages using `ai-config-kit-package.yaml` manifests. When a v1 package is detected, installation uses file-copy mode automatically. You can upgrade v1 packages to v2 format:

```bash
devsync extract --upgrade ./old-v1-package --output ./v2-package --name my-package
```

## Package Structure

### v2 Package (AI-native)

```
team-standards/
├── devsync-package.yaml    # v2 manifest with practices
├── practices/              # Practice declaration files
│   ├── type-safety.md
│   └── error-handling.md
├── mcp/                    # MCP server configs
│   └── github.json
└── README.md
```

### v1 Package (file-copy)

```
my-package/
├── ai-config-kit-package.yaml    # v1 manifest
├── instructions/                 # Instruction .md files
├── mcp/                          # MCP server .json configs
├── hooks/                        # Hook shell scripts
├── commands/                     # Command scripts
└── resources/                    # Any additional files
```

## IDE Compatibility

Different AI coding tools support different component types. When installing a package, DevSync automatically skips components that the target IDE cannot use.

| Component | Claude Code | Cursor | Windsurf | Copilot | Kiro | Cline | Roo Code | Codex CLI |
|-----------|:-----------:|:------:|:--------:|:-------:|:----:|:-----:|:--------:|:---------:|
| Practices/Instructions | Y | Y | Y | Y | Y | Y | Y | Y |
| MCP Servers | Y | Y | Y | Y | -- | -- | Y | -- |
| Hooks | Y | -- | -- | -- | -- | -- | -- | -- |
| Commands | Y | -- | -- | -- | -- | -- | Y | -- |
| Resources | Y | Y | Y | -- | Y | Y | Y | Y |

### Translation Paths

Components are installed to IDE-specific locations:

=== "Claude Code"

    ```
    Practices     -> .claude/rules/*.md
    MCP Servers   -> .claude/settings.local.json
    Hooks         -> .claude/hooks/*.sh
    Commands      -> .claude/commands/*.sh
    Resources     -> specified install_path
    ```

=== "Cursor"

    ```
    Practices     -> .cursor/rules/*.mdc
    MCP Servers   -> .cursor/mcp.json
    Resources     -> specified install_path
    ```

=== "Windsurf"

    ```
    Practices     -> .windsurf/rules/*.md
    MCP Servers   -> ~/.codeium/windsurf/mcp_config.json
    Resources     -> specified install_path
    ```

=== "GitHub Copilot"

    ```
    Practices     -> .github/instructions/*.instructions.md
    MCP Servers   -> .vscode/mcp.json
    ```

=== "Roo Code"

    ```
    Practices     -> .roo/rules/*.md
    MCP Servers   -> .roo/mcp.json
    Commands      -> .roo/commands/*.md
    Resources     -> specified install_path
    ```

## Next Steps

- [Creating Packages](creating.md) -- extract practices from your project
- [Component Types](components.md) -- detailed reference for each component type
- [Installing Packages](installing.md) -- install, list, and manage packages
- [Examples](examples.md) -- complete real-world package examples
