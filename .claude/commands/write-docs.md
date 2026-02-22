---
name: write-docs
description: Write or update DevSync documentation pages
allowed-tools: Bash, Read, Edit, Grep, Glob
---

Write or update DevSync documentation pages.

## Arguments

The first argument is the doc page path (e.g., `cli/commands.md`). Any additional text describes what to write or update.

## Instructions

You are updating the DevSync documentation. Follow these steps:

### 1. Read the Target Page

If the page exists at `docs/$ARGUMENTS`, read it. If it doesn't exist, you'll create it from scratch.

### 2. Read Source Code

Read the corresponding source code to ensure documentation accuracy:

- CLI commands -> `devsync/cli/`
- AI tool integrations -> `devsync/ai_tools/`
- Core models -> `devsync/core/models.py`
- Repository/manifest parsing -> `devsync/core/repository.py`
- Library management -> `devsync/storage/library.py`
- Installation tracking -> `devsync/storage/tracker.py`
- Package tracking -> `devsync/storage/package_tracker.py`
- TUI -> `devsync/tui/installer.py`
- Package installation -> `devsync/cli/package_install.py`
- Configuration -> `devsync/core/models.py` (Package, PackageComponents)

### 3. Write the Documentation

Follow these style conventions:

- **Voice**: Direct, second-person ("you"), active voice
- **Tone**: Professional but approachable. No filler, no "In this section you will learn..."
- **Opening**: Every page starts with a one-sentence summary, then dives straight in
- **Code examples**: Every concept gets a working example. Use `$ ` prefix for shell commands
- **Tables**: Use for reference material, feature comparisons, parameter lists
- **Cross-references**: Link between pages liberally. Use relative paths

### 4. Verify

Run any available doc build commands to check for issues:

```bash
# Check that referenced files exist
grep -r "devsync/" docs/ | grep -v ".pyc"
```

### 5. Cross-Reference Check

Ensure links to and from the new page are consistent. Update `README.md` if the new page covers functionality documented there.
