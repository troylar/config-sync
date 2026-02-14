# Tutorial: Sync AI Configuration Across Multiple Computers

**⏱️ Time**: 10 minutes
**🎯 Goal**: Use the same AI assistant configuration on all your devices
**💻 Devices**: Desktop, laptop, or any device where you code

---

## 🎬 The Problem

You have a desktop at home and a laptop for travel. Every time you switch devices, your AI assistant "forgets" your coding preferences. You waste time re-explaining the same conventions on each device.

## ✅ The Solution

Use Git to version control your AI configuration. Set it up once, sync everywhere automatically.

---

## 📋 Prerequisites

- [ ] DevSync installed on all devices (`pip install ai-config-kit`)
- [ ] Git repository for one of your projects
- [ ] Same AI tool (Claude Code, Cursor, etc.) on all devices

---

## 🚀 Quick Start (5 Steps)

### Step 1: Create Package on Device #1
**What**: Create instruction package with your preferences
**Why**: Centralize your coding standards in one place
**How**:

```bash
# On your desktop (Device #1)
# Navigate to where you keep your projects/templates (not inside a project!)
cd ~/projects  # Or your preferred location for packages

# Create a simple package directory here
mkdir my-coding-standards
cd my-coding-standards

# Create package manifest
cat > ai-config-kit-package.yaml << 'EOF'
name: my-standards
version: 1.0.0
description: My personal coding standards
author: Your Name
namespace: yourname/my-standards
license: MIT

components:
  instructions:
    - name: code-style
      description: My preferred code style
      file: instructions/code-style.md
      tags: [style, conventions]
EOF

# Create the instruction file
mkdir instructions
cat > instructions/code-style.md << 'EOF'
# My Code Style Preferences

## Functions
- Always use descriptive names (no single letters except loop counters)
- Add docstrings to all functions
- Maximum function length: 50 lines

## Error Handling
- Use specific exceptions, not generic `Exception`
- Always log errors before re-raising
- Include context in error messages

## Comments
- Explain WHY, not WHAT
- Use TODO comments for future improvements
- Keep comments up-to-date when code changes
EOF
```

**✅ What you just did**: Created a package that defines YOUR coding preferences.

---

### Step 2: Install Package Locally
**What**: Install your package to the current project
**Why**: Test that it works before syncing
**How**:

```bash
# Navigate to your actual project (replace with your project path)
cd ~/projects/my-project  # Or your actual project directory
aiconfig package install ~/projects/my-coding-standards --ide claude
```

**📤 Expected Output**:
```
✓ Package 'my-standards' installed successfully

Installed components:
  ✓ code-style (instruction)

1/1 components installed to .claude/
```

**✅ What happened**: DevSync copied your instructions to `.claude/rules/` and created a tracking file at `.ai-config-kit/packages.json`.

---

### Step 3: Commit to Git
**What**: Add AI configuration to your project's Git repository
**Why**: Git will sync it to all your devices
**How**:

```bash
# Check what was created
ls -la .claude/rules/          # Your instructions
ls -la .ai-config-kit/         # Package tracking

# Add to Git
git add .claude/ .ai-config-kit/
git commit -m "Add AI assistant configuration"
git push
```

**📤 Expected Output**:
```
[main abc1234] Add AI assistant configuration
 2 files changed, 45 insertions(+)
 create mode 100644 .claude/rules/code-style.md
 create mode 100644 .ai-config-kit/packages.json
```

**✅ What happened**: Your AI configuration is now in Git, ready to sync to other devices.

---

### Step 4: Pull on Device #2
**What**: Get the configuration on your laptop
**Why**: AI assistant will automatically use it
**How**:

```bash
# On your laptop (Device #2)
# Navigate to your project (should be same path or cloned repo)
cd ~/projects/my-project  # Or your actual project path
git pull
```

**📤 Expected Output**:
```
remote: Counting objects: 5, done.
remote: Compressing objects: 100% (3/3), done.
Unpacking objects: 100% (5/5), done.
From github.com:yourname/my-project
   def5678..abc1234  main -> origin/main
 .claude/rules/code-style.md         | 20 ++++++++++++++++++++
 .ai-config-kit/packages.json        | 25 +++++++++++++++++++++++++
 2 files changed, 45 insertions(+)
```

**✅ What happened**: Git pulled your AI configuration. It's ready to use—no installation needed!

---

### Step 5: Verify & Test
**What**: Confirm AI assistant sees your preferences
**Why**: Make sure it works before relying on it
**How**:

```bash
# Check files exist
ls .claude/rules/code-style.md     # Should exist
cat .ai-config-kit/packages.json   # Should show your package

# Test with Claude Code
claude "Write a function to validate email addresses"
```

**✅ What to expect**: Claude should follow YOUR preferences:
- Descriptive function name (not `f()` or `validate()`)
- Docstring explaining purpose
- Specific exception types
- Comments explaining WHY

---

## 🔄 Daily Workflow

### When You Update Standards on Device #1:

```bash
# 1. Edit your instruction file
vim .claude/rules/code-style.md

# 2. Commit and push
git add .claude/
git commit -m "Update code style: add error handling guidelines"
git push
```

### On Device #2 (Automatic):

```bash
# Next time you pull, you get updates
git pull
# AI assistant now has latest standards
```

---

## 📦 Advanced: Multiple Projects

**Scenario**: You want the same standards across ALL your projects.

**Solution**: Create a personal "dotfiles" repo for your AI configurations.

```bash
# Create a central config repo (explicit location)
mkdir -p ~/ai-configs
cd ~/ai-configs
git init

# Create your standard packages
mkdir my-python-standards
mkdir my-javascript-standards

# ... create packages ...

# Push to GitHub
git remote add origin git@github.com:yourname/ai-configs.git
git push -u origin main
```

**On any device, any project**:

```bash
cd ~/projects/any-python-project
aiconfig package install ~/ai-configs/my-python-standards --ide claude
git add .claude/ .ai-config-kit/
git commit -m "Add AI config"
```

Now every Python project has the same standards, synced across all devices.

---

## 🐛 Troubleshooting

### ❌ Problem: Git pull doesn't update AI behavior

**Why**: AI tool might cache instructions
**Fix**: Restart your AI tool (Claude Code, Cursor, etc.)

```bash
# Force reload
# For Claude Code: Restart the app
# For Cursor: Cmd/Ctrl + Shift + P → "Reload Window"
```

---

### ❌ Problem: Merge conflicts in `.ai-config-kit/packages.json`

**Why**: You installed different packages on different devices
**Fix**: Keep both, or choose one:

```bash
# Option 1: Keep both (accept both changes in merge conflict)
git add .ai-config-kit/packages.json
git commit

# Option 2: Prefer Device #1's config
git checkout --theirs .ai-config-kit/packages.json

# Option 3: Prefer Device #2's config
git checkout --ours .ai-config-kit/packages.json
```

---

### ❌ Problem: `.claude/` folder is huge (slowing down Git)

**Why**: You installed packages with large resources
**Fix**: Use `.gitignore` for large files:

```bash
echo ".claude/mcp/*.json" >> .gitignore  # Example: ignore large MCP configs
git add .gitignore
git commit -m "Ignore large MCP files"
```

---

## 💡 Pro Tips

### Tip 1: Use Git Branches for Experiments

```bash
# Try new coding standards without affecting team
git checkout -b experiment/new-standards
aiconfig package install new-standards --ide claude
# Test it out...

# If you like it:
git checkout main
git merge experiment/new-standards

# If you don't:
git checkout main
git branch -D experiment/new-standards
```

### Tip 2: .gitignore Template

Not all AI config should be versioned. Here's a recommended `.gitignore`:

```bash
cat >> .gitignore << 'EOF'
# DevSync - Keep instructions, ignore temp files
.ai-config-kit/*.lock
.ai-config-kit/cache/

# Keep MCP server configs, but ignore credentials
.claude/mcp/**/*.json
!.claude/mcp/**/config-template.json

# IDE-specific (if multiple IDEs in one project)
.cursor/cache/
.windsurf/temp/
EOF
```

### Tip 3: Separate Personal vs Team Config

```
.claude/
  rules/
    team-python-style.md        # Shared with team (in Git)
    team-testing-guide.md       # Shared with team (in Git)
    personal-shortcuts.md       # Only for you (in .gitignore)
```

Add to `.gitignore`:
```
.claude/rules/personal-*.md
```

---

## ✅ Summary

What you accomplished:

- ✅ **Device #1**: Created and installed your coding standards
- ✅ **Git**: Committed configuration to version control
- ✅ **Device #2**: Pulled configuration automatically
- ✅ **Updates**: Changes sync across devices via Git

**Time saved**:
- Setup: 10 minutes (one-time)
- Per device sync: 30 seconds (`git pull`)
- Manual reconfiguration per device: 30 minutes ❌
- **Total saved**: 29.5 minutes per new device or update

---

## 🚀 Next Steps

- **Share with teammates**: [Team Standards Tutorial](small-team-shared-standards.md)
- **Create project-specific configs**: [Project Templates Tutorial](project-templates.md)
- **Automate with Git hooks**: [Advanced Git Integration](advanced-git-integration.md)

---

## 🎓 What You Learned

1. AI configurations are just files (can be versioned in Git)
2. `.ai-config-kit/packages.json` tracks what's installed
3. `.claude/rules/*.md` (or `.cursor/rules/`, etc.) contains actual instructions
4. Git pull automatically syncs configuration across devices
5. No special tools needed—just Git!
