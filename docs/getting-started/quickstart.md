# Quickstart

Get DevSync working in 5 minutes.

## 1. Install DevSync

```bash
$ pip install devsync
```

## 2. Configure Your LLM Provider

```bash
$ devsync setup
```

DevSync uses an LLM to intelligently extract and adapt coding practices. The setup wizard configures your provider:

```
? Select LLM provider:
  1. Anthropic (Claude)
  2. OpenAI
  3. OpenRouter
> 1

? API key found in ANTHROPIC_API_KEY. Use it? [Y/n]: y

Configuration saved to ~/.devsync/config.yaml
```

!!! info
    No API key? DevSync still works. Use `--no-ai` on any command to fall back to file-copy mode, which copies files verbatim instead of using AI extraction/adaptation.

## 3. Check Your IDEs

```bash
$ devsync tools
```

DevSync auto-detects which AI coding tools are installed. You'll see something like:

```
Detected AI Tools:
  Claude Code    .claude/rules/          (.md)
  Cursor         .cursor/rules/          (.mdc)
  Windsurf       .windsurf/rules/        (.md)
```

## 4. Extract Practices from a Project

Navigate to a project that has existing AI rules or configs, then extract:

```bash
$ cd ~/my-team-project
$ devsync extract --output ./team-standards --name team-standards
```

DevSync reads the project's rules (`.claude/rules/`, `.cursor/rules/`, MCP configs, etc.) and produces a shareable package with abstract practice declarations:

```
Extracting practices from /home/user/my-team-project...

  Found 5 rule files across 2 AI tools
  Found 1 MCP server configuration

Extracted:
  Practices: 4
  MCP servers: 1

Package written to: ./team-standards/devsync-package.yaml
```

!!! tip
    Use `--no-ai` to skip AI extraction and copy files verbatim instead:

    ```bash
    $ devsync extract --output ./team-standards --name team-standards --no-ai
    ```

## 5. Install Practices into Another Project

Navigate to the target project and install:

```bash
$ cd ~/new-project
$ devsync install ~/my-team-project/team-standards
```

DevSync detects your installed AI tools and adapts the practices:

```
Installing team-standards to /home/user/new-project...

  Detected tools: Claude Code, Cursor
  Adapting 4 practices + 1 MCP server...

  Claude Code:
    Created: .claude/rules/type-safety.md
    Created: .claude/rules/error-handling.md
    Merged:  .claude/rules/code-style.md (adapted to existing)
    Created: .claude/rules/testing.md

  Cursor:
    Created: .cursor/rules/type-safety.mdc
    Created: .cursor/rules/error-handling.mdc
    Merged:  .cursor/rules/code-style.mdc (adapted to existing)
    Created: .cursor/rules/testing.mdc

  MCP: Configured 1 server (1 credential prompted)

Installation complete.
```

## 6. Verify

Check what's installed:

```bash
$ devsync list
```

Your AI tools now have the practices. Open your IDE and the coding assistant will follow them automatically.

---

## Install from Git

You can install directly from a Git repository:

```bash
$ devsync install https://github.com/company/team-standards
```

Or install from a local directory:

```bash
$ devsync install ./path/to/package
```

---

## File-Copy Mode (No AI)

Every command works without an API key using the `--no-ai` flag:

```bash
# Extract by copying files verbatim
$ devsync extract --output ./pkg --name my-pkg --no-ai

# Install by copying files without AI adaptation
$ devsync install ./pkg --no-ai
```

---

## What's Next?

- [Core Concepts](concepts.md) -- understand practices, packages, and adaptation
- [CLI Reference](../cli/index.md) -- all 6 commands with examples
- [IDE Integrations](../ide-integrations/index.md) -- setup guide for each AI tool
- [Tutorials](../tutorials/team-config-repo.md) -- step-by-step walkthroughs
