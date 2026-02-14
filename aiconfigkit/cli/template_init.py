"""Template repository scaffolding command."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()


def init_command(
    directory: str = typer.Argument(..., help="Directory name for new template repository"),
    namespace: Optional[str] = typer.Option(
        None,
        "--namespace",
        "-n",
        help="Default namespace for templates (default: directory name)",
    ),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        "-d",
        help="Repository description",
    ),
    author: Optional[str] = typer.Option(
        None,
        "--author",
        "-a",
        help="Author name",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing directory",
    ),
) -> None:
    """
    Create a new template repository with scaffolded structure.

    This command creates a ready-to-use template repository with:
    - Properly formatted templatekit.yaml
    - Example templates with documentation
    - Directory structure for instructions, commands, and hooks
    - README with usage instructions
    - .gitignore for Python projects

    Example:
        # Create basic template repo
        devsync template init my-templates

        # Create with custom namespace and description
        devsync template init company-standards \\
            --namespace acme \\
            --description "ACME Corp engineering standards" \\
            --author "ACME Engineering Team"

        # Overwrite existing directory
        devsync template init my-templates --force
    """
    try:
        # Handle typer.Option objects when called directly (in tests)
        # When called via CLI, Typer processes these; when called directly, they remain as Option objects
        import typer.models

        if isinstance(namespace, typer.models.OptionInfo):
            namespace = None
        if isinstance(description, typer.models.OptionInfo):
            description = None
        if isinstance(author, typer.models.OptionInfo):
            author = None

        # Convert to Path
        repo_path = Path(directory).resolve()

        # Check if directory exists
        if repo_path.exists() and not force:
            console.print(f"[red]Error: Directory '{directory}' already exists[/red]")
            console.print("Use --force to overwrite")
            raise typer.Exit(1)

        # Use directory name as default namespace
        if namespace is None:
            namespace = directory.replace("-", "_").replace(" ", "_")

        # Set defaults
        if description is None:
            description = f"Template repository for {namespace}"
        if author is None:
            author = "Your Name"

        # Create directory structure
        console.print(f"\n[cyan]Creating template repository: {directory}[/cyan]\n")

        repo_path.mkdir(parents=True, exist_ok=True)

        # Create IDE-agnostic template directories
        (repo_path / "templates" / "instructions").mkdir(parents=True, exist_ok=True)
        (repo_path / "templates" / "commands").mkdir(parents=True, exist_ok=True)
        (repo_path / "templates" / "hooks").mkdir(parents=True, exist_ok=True)

        # Create templatekit.yaml
        manifest_content = f"""# Template Repository Manifest
# See: https://github.com/troylar/devsync

name: {description}
description: {description}
version: 1.0.0
author: {author}

templates:
  # Example instruction/rule template
  - name: example-instruction
    description: Example coding standards and best practices
    files:
      - path: templates/instructions/example-instruction.md
        ide: all  # IDE-agnostic: works with Claude, Cursor, Windsurf, Copilot
    tags: [example, standards]

  # Example slash command template
  - name: example-command
    description: Example slash command for common task
    files:
      - path: templates/commands/example-command.md
        ide: all  # IDE-agnostic: works with any supported IDE
    tags: [example, productivity]

  # Example hook template
  - name: example-hook
    description: Example pre-prompt hook for context injection
    files:
      - path: templates/hooks/example-hook.md
        ide: all  # IDE-agnostic: works with any supported IDE
    tags: [example, automation]

# Optional: Group related templates into bundles
bundles:
  - name: getting-started
    description: Example bundle with all starter templates
    templates:
      - example-instruction
      - example-command
    tags: [example]
"""
        (repo_path / "templatekit.yaml").write_text(manifest_content, encoding="utf-8")
        console.print("✓ Created templatekit.yaml")

        # Create example instruction
        instruction_content = """# Example Coding Standards

This is an example instruction/rule template. It will appear in your IDE's rules/instructions.

## Purpose

Replace this content with your team's coding standards, best practices, or guidelines.

## What to Include

- **Coding Standards**: Formatting, naming conventions, style guides
- **Best Practices**: Design patterns, error handling, testing approaches
- **Team Conventions**: PR guidelines, commit message formats, branch naming
- **Security**: OWASP guidelines, authentication patterns, data handling

## Example: Python Coding Standards

### Naming Conventions
- Use `snake_case` for functions and variables
- Use `PascalCase` for classes
- Use `UPPER_CASE` for constants

### Type Hints
Always use type hints for function signatures:

```python
def process_data(input: str, count: int = 10) -> list[str]:
    \"\"\"Process input data and return results.\"\"\"
    return input.split()[:count]
```

### Documentation
All public functions must have docstrings following Google style.

## Customization

1. Replace this content with your standards
2. Add multiple instruction files for different topics
3. Update templatekit.yaml to reference new files
4. Commit to Git and share with your team!

---
*Generated by DevSync - https://github.com/troylar/devsync*
"""
        (repo_path / "templates" / "instructions" / "example-instruction.md").write_text(
            instruction_content, encoding="utf-8"
        )
        console.print("✓ Created templates/instructions/example-instruction.md")

        # Create example command
        command_content = """# Example Command

This is an example slash command template. Users can invoke it with `/example-command`.

## Purpose

Replace this with your custom command logic. Slash commands are powerful automation tools.

## Command Instructions

When this command is invoked:

1. **Analyze** the current project context
2. **Perform** the specific task (testing, refactoring, code review, etc.)
3. **Report** results back to the user

## Example: Run Tests Command

```markdown
# Run Tests

I will run the project's test suite and provide a comprehensive report.

## Steps:
1. Detect test framework (pytest, unittest, jest, etc.)
2. Run all tests with coverage
3. Parse and summarize results
4. Highlight failing tests with details
5. Show coverage metrics

## Execution:
- Run: `pytest --cov --cov-report=term`
- Parse output
- Create summary table
```

## Customization Ideas

**Common Commands:**
- `/test-api` - Run API integration tests
- `/review-pr` - Perform code review checklist
- `/generate-docs` - Auto-generate documentation
- `/refactor` - Suggest refactoring improvements
- `/security-scan` - Check for security issues

**Best Practices:**
1. Clear purpose and expected output
2. Step-by-step execution plan
3. Error handling instructions
4. Output formatting guidelines

---
*Generated by DevSync - https://github.com/troylar/devsync*
"""
        (repo_path / "templates" / "commands" / "example-command.md").write_text(command_content, encoding="utf-8")
        console.print("✓ Created templates/commands/example-command.md")

        # Create example hook
        hook_content = """# Example Pre-Prompt Hook

This is an example hook that runs before each AI prompt.

## Purpose

Hooks automatically inject context or modify AI behavior without manual intervention.

## Hook Types

### Pre-Prompt Hook
Runs before user's prompt is sent. Use for:
- Adding project context
- Injecting recent changes
- Setting behavioral guidelines

### Post-Response Hook
Runs after AI response. Use for:
- Logging interactions
- Validating output
- Triggering follow-up actions

## Example: Context Injection

```markdown
Before responding, please consider:

## Project Context
- Framework: Django 4.2
- Python: 3.11
- Database: PostgreSQL
- Deployment: AWS ECS

## Current Sprint
Focus: API performance optimization
Priority: Reduce response times by 30%

## Recent Changes
[Automatically inject git log summary]
```

## Customization

1. Replace with your project-specific context
2. Add dynamic content (git logs, recent files, etc.)
3. Set team-wide guidelines
4. Configure IDE-specific behavior

## Best Practices

- Keep hooks concise (< 200 words)
- Focus on actionable context
- Update regularly as project evolves
- Test hook behavior before deploying

---
*Generated by DevSync - https://github.com/troylar/devsync*
"""
        (repo_path / "templates" / "hooks" / "example-hook.md").write_text(hook_content, encoding="utf-8")
        console.print("✓ Created templates/hooks/example-hook.md")

        # Create README.md
        readme_content = f"""# {description}

Template repository for DevSync - distributes IDE-specific artifacts
(instructions, commands, hooks) to your team.

## 📦 What's Included

This repository contains templates for AI coding tools (Claude Code, Cursor, Windsurf, GitHub Copilot):

- **Instructions/Rules** - Coding standards and best practices
- **Commands** - Slash commands for common workflows
- **Hooks** - Automation hooks for context injection

## 🚀 Installation

Team members can install these templates using DevSync:

```bash
# Install from this repository
devsync template install <YOUR_REPO_URL> --as {namespace}

# List installed templates
devsync template list

# Validate installation
devsync template validate
```

## 📝 Usage

After installation, templates are installed to your IDE-specific directories:
- **Claude Code**: `.claude/rules/`, `.claude/commands/`, `.claude/hooks/`
- **Cursor**: `.cursor/rules/`
- **Windsurf**: `.windsurf/rules/`
- **GitHub Copilot**: `.github/copilot/instructions/`

The template system automatically translates to the correct format for each IDE.

## 🛠️ Customization

### Adding New Templates

1. Create template file in the `templates/` directory (IDE-agnostic):
   - Instructions: `templates/instructions/my-template.md`
   - Commands: `templates/commands/my-command.md`
   - Hooks: `templates/hooks/my-hook.md`

2. Register in `templatekit.yaml`:

```yaml
templates:
  - name: my-template
    description: Description of what this template does
    files:
      - path: templates/instructions/my-template.md
        ide: all  # Works with any IDE
    tags: [your, tags]
```

3. Commit and push:

```bash
git add .
git commit -m "feat: add my-template"
git push
```

4. Team members update:

```bash
devsync template update {namespace}
```

### Template Types

- `instruction` - Coding standards, guidelines, best practices
- `command` - Slash commands for automation
- `hook` - Pre/post-prompt hooks for context

### Bundles

Group related templates:

```yaml
bundles:
  - name: python-stack
    description: Complete Python development setup
    templates:
      - python-standards
      - test-command
      - pre-prompt-hook
    tags: [python]
```

## 📚 Documentation

- [DevSync Documentation](https://github.com/troylar/devsync)
- [Template System Guide](https://github.com/troylar/devsync#templates)
- [Manifest Reference](https://github.com/troylar/devsync#template-repository-structure)

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/new-template`
2. Add/modify templates
3. Update `templatekit.yaml`
4. Test locally: `devsync template install . --as {namespace}`
5. Commit and push
6. Create pull request

## 📄 License

Add your license here (MIT, Apache 2.0, etc.)

---
*Generated by [DevSync](https://github.com/troylar/devsync)*
"""
        (repo_path / "README.md").write_text(readme_content, encoding="utf-8")
        console.print("✓ Created README.md")

        # Create .gitignore
        gitignore_content = """# DevSync
.instructionkit/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Distribution
dist/
build/
*.egg-info/
"""
        (repo_path / ".gitignore").write_text(gitignore_content, encoding="utf-8")
        console.print("✓ Created .gitignore")

        # Success message
        console.print("\n[green]✓ Template repository created successfully![/green]\n")

        console.print("[cyan]Next steps:[/cyan]")
        console.print(f"  1. cd {directory}")
        console.print("  2. Customize templates in templates/ directory")
        console.print("  3. Update templatekit.yaml with your templates")
        console.print("  4. Initialize git: git init && git add . && git commit -m 'Initial commit'")
        console.print("  5. Push to GitHub/GitLab/Bitbucket")
        console.print(f"  6. Install to any IDE: devsync template install <repo-url> --as {namespace} --ide <ide>")

        console.print("\n[cyan]Repository structure (IDE-agnostic):[/cyan]")
        console.print(f"{directory}/")
        console.print("├── templatekit.yaml          # Template manifest")
        console.print("├── README.md                 # Usage documentation")
        console.print("├── .gitignore               # Git ignore rules")
        console.print("└── templates/                # IDE-agnostic templates")
        console.print("    ├── instructions/")
        console.print("    │   └── example-instruction.md")
        console.print("    ├── commands/")
        console.print("    │   └── example-command.md")
        console.print("    └── hooks/")
        console.print("        └── example-hook.md")

        console.print("\n[dim]Test locally:[/dim]")
        console.print(f"  devsync template install {repo_path} --as {namespace}")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)
