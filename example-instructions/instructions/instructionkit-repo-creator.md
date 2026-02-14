# DevSync Repository Creator

When a user asks you to create an DevSync-compatible repository or instruction collection, follow this guide to help them build a properly structured repository.

## Repository Structure Required

Every DevSync repository must have:

```
repository-name/
├── devsync.yaml          # REQUIRED: Metadata file
├── instructions/                # REQUIRED: Instruction files directory
│   ├── instruction-1.md
│   └── instruction-2.md
└── README.md                    # OPTIONAL: Documentation
```

## Creating devsync.yaml

This is the core metadata file. **Always create this file first.**

### Minimal Template

```yaml
name: Repository Name
description: Brief description of what these instructions do
version: 1.0.0

instructions:
  - name: instruction-name
    description: What this instruction does
    file: instructions/instruction-name.md
    tags:
      - tag1
      - tag2
```

### Full Template with Bundles

```yaml
name: Repository Name
description: Brief description of the collection
version: 1.0.0
author: Author Name or Team
repository: https://github.com/username/repo

instructions:
  - name: instruction-1
    description: What this instruction does
    file: instructions/instruction-1.md
    tags:
      - category
      - topic

  - name: instruction-2
    description: What this instruction does
    file: instructions/instruction-2.md
    tags:
      - category
      - topic

bundles:
  - name: bundle-name
    description: What this bundle provides
    instructions:
      - instruction-1
      - instruction-2
    tags:
      - category
```

## Field Requirements

**Required fields in devsync.yaml:**
- `name`: Repository name
- `description`: Brief description
- `version`: Semantic version (e.g., "1.0.0")
- `instructions`: Array of instruction definitions
  - Each instruction needs: `name`, `description`, `file`

**Optional fields:**
- `author`: Author or team name
- `repository`: Git repository URL
- `tags`: Array of tags for filtering
- `bundles`: Grouped instruction sets

## Writing Instruction Files

Instruction files are markdown documents that guide AI coding assistants. They should be:

1. **Clear and specific**: Give concrete guidance, not vague principles
2. **Actionable**: Tell the AI what to do, not just what to know
3. **Contextual**: Include when and why to apply the instruction
4. **Example-rich**: Show concrete code examples

### Good Instruction Template

```markdown
# [Instruction Title]

## Purpose
[When to use this instruction and what problem it solves]

## Guidelines

### [Principle 1]
[Specific guidance]
- [Detail]
- [Detail]

### [Principle 2]
[Specific guidance]

## Code Examples

\`\`\`[language]
// Good example showing the right approach
[code]
\`\`\`

\`\`\`[language]
// What to avoid
[code]
\`\`\`

## Key Points
- [Important takeaway 1]
- [Important takeaway 2]
```

## Creating Bundles

Bundles group related instructions for installation together. Create bundles for:

- **Onboarding**: Everything new team members need
- **Tech stacks**: Related technologies (e.g., Python + FastAPI)
- **Project types**: Frontend, backend, full-stack
- **Workflows**: Testing, deployment, code review

Example:
```yaml
bundles:
  - name: python-backend
    description: Complete Python backend development setup
    instructions:
      - python-style
      - testing-practices
      - api-design
    tags:
      - python
      - backend
```

## File Naming Conventions

- **Repository**: Use kebab-case (e.g., `my-instructions`)
- **Instruction names**: Use kebab-case (e.g., `python-style-guide`)
- **Instruction files**: Match instruction name + `.md` (e.g., `python-style-guide.md`)
- **Bundles**: Use kebab-case (e.g., `python-backend`)

## User Workflow Support

When helping users create DevSync repositories:

1. **Ask about their goal**: What instructions do they want to create?
2. **Create directory structure**: Make folders first
3. **Write devsync.yaml**: Start with metadata
4. **Create instruction files**: One by one
5. **Add bundles if needed**: Group related instructions
6. **Create README.md**: Document usage and installation
7. **Help them test**: Guide local testing before publishing

### Testing Commands to Suggest

```bash
# List available instructions
devsync list available --repo .

# Install locally to test
devsync install [name] --repo . --scope project

# Verify installation
devsync list installed
```

## Common Use Cases

### Enterprise Team
- Coding standards
- Security guidelines
- Architecture patterns
- Code review checklists

### Open Source Project
- Contributing guidelines
- Code style
- Testing requirements
- Release procedures

### Personal Library
- Favorite patterns
- Language-specific helpers
- Debugging techniques
- Documentation templates

### Education
- Course materials
- Assignment guidelines
- Best practices for students
- Project structures

## Validation Checklist

Before finalizing, ensure:
- [ ] `devsync.yaml` exists at root
- [ ] All instruction files referenced in YAML exist
- [ ] All instruction names are unique
- [ ] Bundle instruction references are valid
- [ ] File paths are correct (relative to repo root)
- [ ] Version follows semantic versioning
- [ ] Tags are meaningful and consistent
- [ ] Markdown files are properly formatted

## Installation Instructions for Users

Include this in the README.md you create:

```markdown
## Installation

### From GitHub
\`\`\`bash
# Install specific instruction
devsync install [name] --repo https://github.com/username/repo

# Install globally (available in all projects)
devsync install [name] --repo https://github.com/username/repo --scope global

# Install to current project only
devsync install [name] --repo https://github.com/username/repo --scope project

# Install a bundle
devsync install [bundle-name] --bundle --repo https://github.com/username/repo
\`\`\`

### From Local Folder
\`\`\`bash
devsync install [name] --repo ./path/to/repo
\`\`\`
```

## Quick Start Example

When a user asks "help me create an DevSync repository", suggest this workflow:

1. Create directory structure:
```bash
mkdir my-instructions
cd my-instructions
mkdir instructions
```

2. Create `devsync.yaml` with their specifications

3. Create instruction markdown files in `instructions/`

4. Test locally:
```bash
devsync list available --repo .
```

5. Add to Git:
```bash
git init
git add .
git commit -m "Initial instruction repository"
```

## Remember

- DevSync repositories can be stored in Git or used locally
- Users can install from GitHub, GitLab, Bitbucket, or local folders
- Instructions are installed into AI tools: Cursor, GitHub Copilot, Windsurf, Claude Code
- Global scope = available in all projects
- Project scope = only in current project
- Always validate YAML syntax before testing
