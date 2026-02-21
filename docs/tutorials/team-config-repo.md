# Tutorial: Create a Team Config Repository

**Time:** 15 minutes | **Level:** Beginner

Create a shareable package of your team's coding standards and distribute it via Git.

---

## What You Will Learn

- Extract practices from an existing project
- Share the package as a Git repository
- Install the package on other machines and projects

## Prerequisites

- DevSync installed (`pip install devsync`)
- LLM configured (`devsync setup`)
- A project with existing AI rules (`.claude/rules/`, `.cursor/rules/`, etc.)
- Git installed

---

## Step 1: Extract Practices

Navigate to a project that has established coding standards:

```bash
cd ~/my-team-project
```

Run the extract command:

```bash
devsync extract --output ./team-standards --name team-standards
```

Expected output:

```
Extracting practices from /home/user/my-team-project...

  Found 4 rule files across 2 AI tools
  Found 1 MCP server configuration

Extracted:
  Practices: 3
  MCP servers: 1

Package written to: ./team-standards/devsync-package.yaml
```

## Step 2: Review the Package

Check what was created:

```bash
ls team-standards/
```

```
devsync-package.yaml
practices/
mcp/
```

Review the manifest:

```bash
cat team-standards/devsync-package.yaml
```

Verify the practice declarations capture your team's intent accurately. Edit as needed.

## Step 3: Create a Git Repository

```bash
cd team-standards
git init
git add .
git commit -m "Initial team standards package"
```

Push to your Git hosting service:

```bash
git remote add origin https://github.com/your-company/team-standards
git push -u origin main
```

## Step 4: Team Members Install

Each team member runs:

```bash
cd ~/their-project
devsync install https://github.com/your-company/team-standards
```

DevSync clones the repo, reads the practices, and adapts them to the team member's existing setup and detected AI tools.

## Step 5: Update the Standards

When standards change, update the package:

```bash
cd ~/my-team-project
# Update your rules as needed
devsync extract --output ./team-standards --name team-standards
cd team-standards
git add . && git commit -m "Update coding standards"
git push
```

Team members reinstall to get updates:

```bash
devsync install https://github.com/your-company/team-standards --conflict overwrite
```

---

## Troubleshooting

**No practices extracted?** Make sure your project has AI rule files in standard locations (`.claude/rules/`, `.cursor/rules/`, etc.).

**AI not working?** Run `devsync setup` to configure your LLM provider. Or use `--no-ai` for file-copy mode.

---

## Next Steps

- [Onboard New Developers](onboard-new-developer.md) -- use your package to onboard team members
- [Multi-IDE Workflow](multi-ide-workflow.md) -- install across multiple AI tools
- [Custom Packages](custom-packages.md) -- build packages with more component types
