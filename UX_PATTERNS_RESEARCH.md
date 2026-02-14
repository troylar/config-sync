# CLI and TUI UX Patterns for Version Selection and Collision Resolution

**Research Date**: 2025-10-26
**Context**: DevSync version management and collision handling
**Technologies**: Typer (CLI), Textual (TUI), Rich (formatting)

---

## Executive Summary

This document provides UX pattern recommendations for implementing version display in TUI tables, collision resolution prompts, and update disambiguation in DevSync. Based on research of popular CLI tools (git, npm, cargo, poetry) and Python CLI best practices, we recommend:

1. **Version Display**: Use compact semver format in tables with tooltips for full version info
2. **Collision Resolution**: Interactive numbered lists with rich previews using questionary
3. **Update Disambiguation**: Table-based selection UI with multi-select capability
4. **Progress Indication**: Rich progress bars with task-specific descriptions

---

## 1. Version Display in TUI Tables

### Current State

DevSync's TUI (`tui/installer.py`) currently has a "Ver" column (line 241) displaying version strings. The table uses Textual's `DataTable` widget with fixed-width columns.

### Research Findings

#### Version Format Patterns

From git and semantic versioning tools:

- **Full version**: `v3.5.2-dev.22+8eaec5d3` (tag + commits + hash)
- **Compact version**: `v3.5.2` (semver only)
- **Commit-based**: `main@abc1234` (branch + short hash)
- **Date-based**: `2024-10-26` (snapshot date)

#### Table Layout Considerations

**Textual DataTable Features**:
- Supports Rich text formatting (bold, colors, styles)
- Fixed and flexible column widths
- Cell-level styling with `update_cell_at()`
- No native tooltip support (would need custom overlay)

### Recommended Patterns

#### Pattern A: Compact Display with Hover (Preferred)

**Display Format**: Use compact semver in table, show full details on selection

```
┌──────┬──────────────────────┬────────┐
│ Name │ Description          │ Ver    │
├──────┼──────────────────────┼────────┤
│ py-t │ Python testing guide │ 1.2.0  │
│ py-t │ Python tests (alt)   │ 1.0.3  │
└──────┴──────────────────────┴────────┘

Selected: py-t v1.2.0
  Repo: acme/examples@v1.2.0 (2024-10-20)
  Commit: abc1234
```

**Advantages**:
- Clean, uncluttered table
- Version sorting works naturally
- Full details available on demand

**Implementation** (Textual):

```python
# In InstructionInstallerScreen.refresh_table()
table.add_column("Ver", key="version", width=8)

# Add rows with compact version
for inst in self.filtered_instructions:
    # Display compact semver
    version_display = inst.version  # e.g., "1.2.0"

    table.add_row(
        checkbox,
        name,
        desc,
        repo,
        author,
        version_display,  # Compact
        tags,
        key=inst.id,
    )

# On row selection, show full version details
@on(DataTable.RowSelected)
def on_row_selected(self, event):
    if event.row_key:
        inst = self._get_instruction(event.row_key.value)
        # Update status bar with full version info
        self.query_one("#status-text").update(
            f"Selected: {inst.name} v{inst.version} | "
            f"Repo: {inst.repo_namespace}@{inst.version_ref} | "
            f"Updated: {inst.last_updated}"
        )
```

#### Pattern B: Two-Column Version (Alternative)

Show both version and ref type separately:

```
┌──────┬────────┬──────────┐
│ Name │ Ver    │ Ref      │
├──────┼────────┼──────────┤
│ py-t │ 1.2.0  │ v1.2.0   │
│ py-t │ 1.0.3  │ main@abc │
└──────┴────────┴──────────┘
```

**Advantages**:
- Distinguishes version from git ref
- Useful when tracking branches vs tags

**Disadvantages**:
- Takes more horizontal space
- May confuse users with dual version info

#### Pattern C: Color-Coded Version Age

Use Rich markup to color-code versions:

```python
from datetime import datetime, timedelta

def format_version_with_age(version: str, last_updated: datetime) -> str:
    """Color-code version by age."""
    age = datetime.now() - last_updated

    if age < timedelta(days=30):
        return f"[green]{version}[/green]"  # Recent
    elif age < timedelta(days=90):
        return f"[yellow]{version}[/yellow]"  # Moderate
    else:
        return f"[dim]{version}[/dim]"  # Old
```

**Advantages**:
- Visual indication of freshness
- No additional columns needed

**Disadvantages**:
- Color may be misleading (old stable vs new beta)
- Accessibility concerns for color-blind users

### Version Display Recommendations

**For DevSync TUI**:

1. **Use Pattern A** (compact + details on selection) - balances clarity with information density
2. **Column width**: Keep at 8 characters for semver (e.g., "v12.34.5")
3. **Truncation**: For longer refs, truncate with ellipsis: "v1.2.0…"
4. **Status bar**: Show full version details when instruction is selected
5. **Sorting**: Enable version column sorting (implement semver comparison)

**Implementation Priority**: Medium (enhances UX but not blocking)

---

## 2. Collision Resolution Prompts

### Current State

DevSync handles name conflicts in `install_new.py` (lines 83-123) with `_resolve_name_conflicts()`:

```python
# Current implementation (simplified)
console.print(f"[yellow]⚠️  Name Conflict:[/yellow] {len(insts)} instructions named '{name}'")
console.print("How should they be installed?")
console.print("  [1] Namespace by repository (recommended)")
console.print("  [2] Skip installation (cancel)")

choice = typer.prompt("Select (1-2)", default="1")
```

### Research Findings

#### Industry Patterns

**npm/yarn**: Automatic resolution with package.json overrides
```bash
$ npm install lodash@4.17.21
# Resolves to specific version automatically
```

**cargo**: Interactive selection with `cargo-interactive-update`
```
? Select dependencies to update:
❯ [x] serde (1.0.193)
  [ ] tokio (1.35.0)
  [x] clap (4.4.8)
```

**git**: Conflict markers with manual resolution
```
<<<<<<< HEAD
version 1
=======
version 2
>>>>>>> branch
```

**poetry**: Automatic lock file resolution with version constraints

### Recommended Patterns

#### Pattern A: Questionary Interactive Selection (Preferred)

Use `questionary.select()` for rich, navigable prompts:

**Installation**:
```bash
pip install questionary
```

**Code Example**:

```python
import questionary
from rich.console import Console
from rich.table import Table

console = Console()

def resolve_collision_interactive(instructions: list[LibraryInstruction]) -> Optional[dict[str, str]]:
    """
    Resolve name collisions using interactive selection.

    Args:
        instructions: List of instructions with duplicate names

    Returns:
        Dict mapping instruction ID to install name, or None if cancelled
    """
    # Group by name
    name_conflicts: dict[str, list[LibraryInstruction]] = {}
    for inst in instructions:
        if inst.name not in name_conflicts:
            name_conflicts[inst.name] = []
        name_conflicts[inst.name].append(inst)

    install_names = {}

    for name, insts in name_conflicts.items():
        if len(insts) == 1:
            # No conflict
            install_names[insts[0].id] = name
            continue

        # Show conflict details
        console.print(f"\n[bold yellow]⚠️  Collision Detected[/bold yellow]")
        console.print(f"Multiple instructions named [cyan]'{name}'[/cyan] selected:\n")

        # Create rich table for comparison
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Source", style="cyan")
        table.add_column("Version", justify="center")
        table.add_column("Description")
        table.add_column("Author", style="dim")

        for i, inst in enumerate(insts, 1):
            table.add_row(
                str(i),
                inst.repo_namespace,
                inst.version,
                inst.description[:40] + "..." if len(inst.description) > 40 else inst.description,
                inst.author,
            )

        console.print(table)
        console.print()

        # Create choices
        choices = []

        # Option 1: Namespace all
        choices.append(questionary.Choice(
            title=f"📁 Namespace all by source (e.g., {insts[0].repo_namespace}/{name})",
            value="namespace_all",
        ))

        # Option 2: Select specific one to keep as-is
        choices.append(questionary.Separator("─── or select one to keep as-is: ───"))

        for i, inst in enumerate(insts):
            choices.append(questionary.Choice(
                title=f"  [{i+1}] {inst.repo_namespace} v{inst.version} → keep as '{name}'",
                value=f"select_{i}",
            ))

        # Option 3: Cancel
        choices.append(questionary.Separator())
        choices.append(questionary.Choice(
            title="❌ Cancel installation",
            value="cancel",
        ))

        # Prompt user
        answer = questionary.select(
            "How would you like to resolve this collision?",
            choices=choices,
            style=questionary.Style([
                ("highlighted", "bold cyan"),
                ("selected", "bold green"),
            ]),
        ).ask()

        if answer == "cancel" or answer is None:
            console.print("[dim]Installation cancelled[/dim]")
            return None

        elif answer == "namespace_all":
            # Namespace all conflicting instructions
            for inst in insts:
                install_names[inst.id] = f"{inst.repo_namespace}/{name}"

        elif answer.startswith("select_"):
            # Install one as-is, namespace the rest
            selected_idx = int(answer.split("_")[1])
            for i, inst in enumerate(insts):
                if i == selected_idx:
                    install_names[inst.id] = name  # Keep original name
                else:
                    install_names[inst.id] = f"{inst.repo_namespace}/{name}"  # Namespace others

    return install_names
```

**User Experience**:

```
⚠️  Collision Detected
Multiple instructions named 'python-testing' selected:

┌───┬─────────────────┬─────────┬──────────────────────────┬────────────┐
│ # │ Source          │ Version │ Description              │ Author     │
├───┼─────────────────┼─────────┼──────────────────────────┼────────────┤
│ 1 │ acme/examples   │ 1.2.0   │ Python testing best pr…  │ John Smith │
│ 2 │ company/guides  │ 2.0.1   │ Comprehensive Python t…  │ Jane Doe   │
└───┴─────────────────┴─────────┴──────────────────────────┴────────────┘

? How would you like to resolve this collision?
❯ 📁 Namespace all by source (e.g., acme/python-testing)
  ─── or select one to keep as-is: ───
    [1] acme/examples v1.2.0 → keep as 'python-testing'
    [2] company/guides v2.0.1 → keep as 'python-testing'

  ❌ Cancel installation
```

**Navigation**: Arrow keys to select, Enter to confirm

#### Pattern B: Typer Confirm Cascade (Current Approach)

Keep current numbered prompt approach but enhance with preview:

```python
def resolve_collision_simple(instructions: list[LibraryInstruction]) -> Optional[dict[str, str]]:
    """Simple numbered prompt with preview."""
    # Group conflicts...

    for name, insts in name_conflicts.items():
        if len(insts) == 1:
            install_names[insts[0].id] = name
            continue

        console.print(f"\n[yellow]⚠️  Collision:[/yellow] {len(insts)} instructions named '{name}'")
        console.print("\nPreview:")

        for i, inst in enumerate(insts, 1):
            console.print(f"  [{i}] [cyan]{inst.repo_namespace}[/cyan] v{inst.version}")
            console.print(f"      {inst.description}")
            console.print()

        console.print("[bold]Resolution options:[/bold]")
        console.print("  [N] Namespace all by source (recommended)")
        console.print("  [1-N] Install only one (others skipped)")
        console.print("  [C] Cancel")

        choice = typer.prompt("Select", default="N")

        if choice.upper() == "C":
            return None
        elif choice.upper() == "N":
            for inst in insts:
                install_names[inst.id] = f"{inst.repo_namespace}/{name}"
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(insts):
                install_names[insts[idx].id] = name
                # Skip others
                for i, inst in enumerate(insts):
                    if i != idx:
                        # Mark as skipped (handled by caller)
                        pass
            else:
                console.print("[red]Invalid selection[/red]")
                return None

    return install_names
```

#### Pattern C: Preview and Compare

For advanced users, show diff-style comparison:

```python
def preview_collision_diff(inst1: LibraryInstruction, inst2: LibraryInstruction):
    """Show side-by-side comparison of colliding instructions."""
    from rich.columns import Columns
    from rich.panel import Panel

    panel1 = Panel(
        f"[bold]{inst1.repo_namespace}[/bold]\n"
        f"Version: {inst1.version}\n"
        f"Author: {inst1.author}\n\n"
        f"{inst1.description}",
        title=f"Option 1",
        border_style="cyan",
    )

    panel2 = Panel(
        f"[bold]{inst2.repo_namespace}[/bold]\n"
        f"Version: {inst2.version}\n"
        f"Author: {inst2.author}\n\n"
        f"{inst2.description}",
        title=f"Option 2",
        border_style="magenta",
    )

    console.print(Columns([panel1, panel2]))
```

### Collision Resolution Recommendations

**For DevSync**:

1. **Implement Pattern A** (questionary) for best UX - rich, navigable, accessible
2. **Add dependency**: `questionary>=2.0` to `pyproject.toml`
3. **Fallback**: Keep Pattern B for non-interactive environments (CI/CD)
4. **Preview**: Always show comparison table before resolution
5. **Default behavior**: Namespace all (safest, preserves both)

**Implementation Priority**: High (critical for multi-source feature)

---

## 3. Update Command Disambiguation

### Current State

No update command disambiguation exists yet. This is new functionality for the update feature.

### Research Findings

#### Industry Patterns

**npm update**:
```bash
$ npm update lodash
# Updates all packages matching name
$ npm update @scope/lodash
# Updates specific scoped package
```

**cargo upgrade** (via cargo-edit):
```bash
$ cargo upgrade serde --workspace
# Upgrades all serde deps in workspace
```

**cargo-interactive-update**:
```
? Select dependencies to update:
❯ [x] serde (1.0.193 → 1.0.194)
  [ ] tokio (1.35.0 → 1.35.1)
  [x] clap (4.4.8 → 4.5.0)
```

### Recommended Patterns

#### Pattern A: Interactive Multi-Select Table (Preferred)

When `aiconfig update python-testing` matches multiple sources, show table and allow selection:

**Code Example**:

```python
import questionary
from rich.console import Console
from rich.table import Table

def update_with_disambiguation(name: str, library: LibraryManager) -> int:
    """
    Update instruction(s) by name, with disambiguation if needed.

    Args:
        name: Instruction name to update
        library: Library manager instance

    Returns:
        Exit code
    """
    console = Console()

    # Find all instructions with this name in library
    matching_instructions = library.get_instructions_by_name(name)

    if not matching_instructions:
        console.print(f"[red]No instruction named '{name}' found in library[/red]")
        return 1

    if len(matching_instructions) == 1:
        # Single match - update directly
        return update_single_instruction(matching_instructions[0], library)

    # Multiple matches - need disambiguation
    console.print(f"\n[bold cyan]Multiple instructions named '{name}' found:[/bold cyan]\n")

    # Create comparison table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Source", style="cyan")
    table.add_column("Current Ver", justify="center")
    table.add_column("Available", justify="center", style="green")
    table.add_column("Description")

    for i, inst in enumerate(matching_instructions, 1):
        # Check for available updates
        available_version = library.check_remote_version(inst.repo_url)
        version_display = available_version if available_version != inst.version else "[dim]up to date[/dim]"

        table.add_row(
            str(i),
            inst.repo_namespace,
            inst.version,
            version_display,
            inst.description[:50] + "..." if len(inst.description) > 50 else inst.description,
        )

    console.print(table)
    console.print()

    # Create choices for questionary
    choices = []

    # Option 1: Update all
    choices.append(questionary.Choice(
        title=f"🔄 Update all {len(matching_instructions)} instructions",
        value="all",
    ))

    # Option 2: Select specific ones
    choices.append(questionary.Separator("─── or select specific ones: ───"))

    for i, inst in enumerate(matching_instructions):
        available = library.check_remote_version(inst.repo_url)
        status = "✓ up to date" if available == inst.version else f"→ {available}"

        choices.append(questionary.Choice(
            title=f"  [{i+1}] {inst.repo_namespace} v{inst.version} {status}",
            value=i,
        ))

    # Option 3: Cancel
    choices.append(questionary.Separator())
    choices.append(questionary.Choice(
        title="❌ Cancel",
        value="cancel",
    ))

    # Prompt
    answer = questionary.select(
        f"Which '{name}' instruction(s) would you like to update?",
        choices=choices,
    ).ask()

    if answer == "cancel" or answer is None:
        console.print("[dim]Update cancelled[/dim]")
        return 0

    if answer == "all":
        # Update all matching instructions
        for inst in matching_instructions:
            update_single_instruction(inst, library)
        console.print(f"\n[green]✓ Updated all {len(matching_instructions)} instructions[/green]")
        return 0

    # Update single selected instruction
    selected = matching_instructions[answer]
    return update_single_instruction(selected, library)


def update_single_instruction(inst: LibraryInstruction, library: LibraryManager) -> int:
    """Update a single instruction."""
    console = Console()
    console.print(f"Updating [cyan]{inst.name}[/cyan] from [cyan]{inst.repo_namespace}[/cyan]...")

    # Perform git pull/fetch
    try:
        library.update_repository(inst.repo_url)
        console.print(f"[green]✓ Updated successfully[/green]")
        return 0
    except Exception as e:
        console.print(f"[red]✗ Update failed: {e}[/red]")
        return 1
```

**User Experience**:

```bash
$ aiconfig update python-testing

Multiple instructions named 'python-testing' found:

┌───┬─────────────────┬─────────────┬───────────┬──────────────────────────┐
│ # │ Source          │ Current Ver │ Available │ Description              │
├───┼─────────────────┼─────────────┼───────────┼──────────────────────────┤
│ 1 │ acme/examples   │ 1.2.0       │ 1.3.0     │ Python testing best pr…  │
│ 2 │ company/guides  │ 2.0.1       │ 2.0.1     │ up to date               │
└───┴─────────────────┴─────────────┴───────────┴──────────────────────────┘

? Which 'python-testing' instruction(s) would you like to update?
❯ 🔄 Update all 2 instructions
  ─── or select specific ones: ───
    [1] acme/examples v1.2.0 → 1.3.0
    [2] company/guides v2.0.1 ✓ up to date

  ❌ Cancel
```

#### Pattern B: Checkbox Multi-Select

Allow users to select multiple instructions at once:

```python
def update_with_multiselect(name: str, library: LibraryManager) -> int:
    """Update with checkbox multi-select."""
    matching = library.get_instructions_by_name(name)

    if len(matching) > 1:
        # Show table (same as Pattern A)
        console.print(table)
        console.print()

        # Create checkbox choices
        choices = []
        for inst in matching:
            available = library.check_remote_version(inst.repo_url)
            status = "✓ up to date" if available == inst.version else f"→ {available}"

            choices.append(questionary.Choice(
                title=f"{inst.repo_namespace} v{inst.version} {status}",
                value=inst.id,
                checked=False,  # Nothing pre-selected
            ))

        # Multi-select prompt
        selected_ids = questionary.checkbox(
            "Select instructions to update (Space to toggle, Enter to confirm):",
            choices=choices,
        ).ask()

        if not selected_ids:
            console.print("[dim]No instructions selected[/dim]")
            return 0

        # Update selected
        selected = [inst for inst in matching if inst.id in selected_ids]
        for inst in selected:
            update_single_instruction(inst, library)

        console.print(f"\n[green]✓ Updated {len(selected)} instruction(s)[/green]")
        return 0
```

**User Experience**:

```
? Select instructions to update (Space to toggle, Enter to confirm):
  [x] acme/examples v1.2.0 → 1.3.0
❯ [ ] company/guides v2.0.1 ✓ up to date
```

#### Pattern C: Flag-Based Disambiguation

Use CLI flags for non-interactive environments:

```python
@app.command()
def update(
    name: str,
    from_source: Optional[str] = typer.Option(None, "--from", help="Source namespace to update from"),
    all_sources: bool = typer.Option(False, "--all", help="Update all matching instructions"),
):
    """
    Update instruction(s) from library.

    Examples:
        aiconfig update python-testing --from acme
        aiconfig update python-testing --all
    """
    library = LibraryManager()
    matching = library.get_instructions_by_name(name)

    if not matching:
        print_error(f"No instruction named '{name}' found")
        return 1

    # Apply filters
    if from_source:
        matching = [inst for inst in matching if inst.repo_namespace == from_source]
        if not matching:
            print_error(f"No instruction from source '{from_source}'")
            return 1

    if len(matching) == 1 or all_sources:
        # Update without prompting
        for inst in matching:
            update_single_instruction(inst, library)
        return 0

    # Multiple matches, no flags - interactive prompt
    return update_with_disambiguation(name, library)
```

**CLI Usage**:

```bash
# Interactive selection
$ aiconfig update python-testing

# Direct update with flag
$ aiconfig update python-testing --from acme

# Update all matches
$ aiconfig update python-testing --all
```

### Update Disambiguation Recommendations

**For DevSync**:

1. **Primary**: Implement Pattern A (interactive single-select) - clear, guided experience
2. **Enhancement**: Add Pattern C flags (`--from`, `--all`) for automation
3. **Table display**: Always show version comparison before selection
4. **Smart defaults**: If only one has updates available, default to that one
5. **Batch mode**: Consider Pattern B (checkbox) for power users

**Implementation Priority**: High (essential for update command)

---

## 4. Progress Indication for Updates

### Research Findings

#### Rich Progress Bar Patterns

Rich provides sophisticated progress tracking with multiple task support:

```python
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

# Custom progress bar for git operations
progress = Progress(
    SpinnerColumn(),
    TextColumn("[bold blue]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TimeElapsedColumn(),
    TimeRemainingColumn(),
)
```

### Recommended Patterns

#### Pattern A: Multi-Task Progress with Spinners

For operations with indeterminate duration (like git clone/pull):

```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console
import time

console = Console()

def update_multiple_repositories(repos: list[Repository]) -> None:
    """Update multiple repositories with progress tracking."""

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:

        # Overall progress
        overall = progress.add_task(
            f"[cyan]Updating {len(repos)} repositories...",
            total=len(repos)
        )

        for repo in repos:
            # Individual repo progress
            repo_task = progress.add_task(
                f"  ↳ {repo.namespace}",
                total=100
            )

            try:
                # Simulate git operations
                progress.update(repo_task, advance=20, description=f"  ↳ {repo.namespace} (fetching...)")
                time.sleep(0.5)

                progress.update(repo_task, advance=40, description=f"  ↳ {repo.namespace} (pulling...)")
                time.sleep(0.5)

                progress.update(repo_task, advance=40, description=f"  ↳ {repo.namespace} (done)")

                # Mark complete
                progress.update(repo_task, completed=100)
                progress.update(overall, advance=1)

            except Exception as e:
                progress.update(repo_task, description=f"  ↳ {repo.namespace} [red]✗ failed[/red]")
                progress.update(overall, advance=1)

        progress.update(overall, description=f"[green]✓ Updated {len(repos)} repositories[/green]")
```

**User Experience**:

```
⠋ Updating 3 repositories... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 33%
  ↳ acme/examples (pulling...)
```

#### Pattern B: Simple Status Updates

For lightweight progress without bars:

```python
def update_with_status(repos: list[Repository]) -> None:
    """Update with simple status messages."""
    console = Console()

    console.print(f"\n[bold]Updating {len(repos)} repositories:[/bold]\n")

    for i, repo in enumerate(repos, 1):
        status = console.status(f"[{i}/{len(repos)}] {repo.namespace}...")
        status.start()

        try:
            # Perform update
            library.update_repository(repo.url)
            status.stop()
            console.print(f"  [green]✓[/green] [{i}/{len(repos)}] {repo.namespace}")
        except Exception as e:
            status.stop()
            console.print(f"  [red]✗[/red] [{i}/{len(repos)}] {repo.namespace}: {e}")

    console.print(f"\n[green]Done![/green]")
```

**User Experience**:

```
Updating 3 repositories:

  ✓ [1/3] acme/examples
  ✓ [2/3] company/guides
  ⠋ [3/3] org/templates...
```

#### Pattern C: Real-Time Git Output

For verbose mode, stream git output:

```python
import subprocess
from rich.live import Live
from rich.text import Text

def update_with_git_output(repo: Repository, verbose: bool = False) -> None:
    """Update repository with optional git output streaming."""
    console = Console()

    if not verbose:
        # Simple progress
        with console.status(f"Updating {repo.namespace}..."):
            subprocess.run(["git", "-C", repo.path, "pull"], check=True, capture_output=True)
        console.print(f"[green]✓[/green] {repo.namespace}")
        return

    # Verbose mode - stream git output
    console.print(f"\n[bold]Updating {repo.namespace}:[/bold]")

    process = subprocess.Popen(
        ["git", "-C", repo.path, "pull"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    output = Text()
    with Live(output, console=console, refresh_per_second=4) as live:
        for line in process.stdout:
            output.append(line)
            live.update(output)

    if process.wait() == 0:
        console.print(f"[green]✓ Update complete[/green]")
    else:
        console.print(f"[red]✗ Update failed[/red]")
```

### Progress Indication Recommendations

**For DevSync**:

1. **Default**: Use Pattern B (simple status) for single repo updates
2. **Batch updates**: Use Pattern A (multi-task progress) for updating multiple repos
3. **Verbose mode**: Add `--verbose` flag to enable Pattern C (git output streaming)
4. **Error handling**: Show clear error messages without stopping entire batch
5. **Summary**: Always print summary after completion (success/failure counts)

**Implementation Example**:

```python
@app.command()
def update(
    name: Optional[str] = None,
    all_repos: bool = typer.Option(False, "--all", help="Update all repositories"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed git output"),
):
    """Update instruction repository/repositories."""
    library = LibraryManager()

    if all_repos:
        repos = library.list_repositories()
        update_multiple_with_progress(repos, verbose=verbose)
    elif name:
        # Disambiguation logic from Pattern A above
        update_with_disambiguation(name, library, verbose=verbose)
    else:
        # Show TUI to select repos to update
        repos = show_update_selector_tui(library)
        if repos:
            update_multiple_with_progress(repos, verbose=verbose)
```

**Implementation Priority**: Medium (enhances UX but not critical path)

---

## 5. Accessibility and Automation Considerations

### Interactive vs Non-Interactive Environments

#### Detection

Check if running in interactive terminal:

```python
import sys

def is_interactive() -> bool:
    """Check if running in an interactive terminal."""
    return sys.stdin.isatty() and sys.stdout.isatty()


def prompt_or_default(prompt_fn, default_value):
    """Use interactive prompt if available, otherwise use default."""
    if is_interactive():
        return prompt_fn()
    else:
        return default_value
```

#### Usage in DevSync

```python
def resolve_collision_smart(instructions: list[LibraryInstruction]) -> Optional[dict[str, str]]:
    """Resolve collisions with automatic fallback for CI/CD."""

    if is_interactive():
        # Use questionary for interactive selection
        return resolve_collision_interactive(instructions)
    else:
        # Non-interactive: use safe default (namespace all)
        console.print("[dim]Non-interactive mode: namespacing all collisions[/dim]")
        install_names = {}
        for inst in instructions:
            install_names[inst.id] = f"{inst.repo_namespace}/{inst.name}"
        return install_names
```

### Environment Variables for Automation

Support environment-based configuration:

```python
import os

# In CLI commands
def get_conflict_strategy() -> ConflictResolution:
    """Get conflict strategy from env or prompt."""
    env_strategy = os.getenv("INSTRUCTIONKIT_CONFLICT_STRATEGY")

    if env_strategy:
        try:
            return ConflictResolution(env_strategy.lower())
        except ValueError:
            pass

    if is_interactive():
        # Prompt user
        return prompt_conflict_strategy()
    else:
        # Default for CI/CD
        return ConflictResolution.SKIP


# Usage in CI/CD
# export INSTRUCTIONKIT_CONFLICT_STRATEGY=overwrite
# aiconfig install python-testing --tool cursor
```

### CI/CD Best Practices

**GitHub Actions Example**:

```yaml
name: Install Instructions
on: [push]

jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install DevSync
        run: pip install devsync

      - name: Download instruction library
        run: aiconfig download --repo https://github.com/acme/instructions

      - name: Install instructions
        env:
          INSTRUCTIONKIT_CONFLICT_STRATEGY: overwrite
        run: |
          aiconfig install python-testing --tool cursor --from acme
          aiconfig install code-review --tool cursor --from acme

      - name: Commit installed instructions
        run: |
          git add .cursor/
          git commit -m "chore: update cursor instructions"
          git push
```

### Accessibility Features

#### Screen Reader Support

- Use clear, descriptive text (avoid unicode symbols as primary info)
- Provide `--no-color` flag for screen readers
- Support keyboard-only navigation (no mouse required)

**Implementation**:

```python
@app.command()
def install(
    no_color: bool = typer.Option(False, "--no-color", help="Disable colors for screen readers"),
):
    """Install instructions."""
    if no_color:
        console = Console(no_color=True, highlight=False)
    else:
        console = Console()
```

#### High Contrast Mode

```python
def get_style() -> questionary.Style:
    """Get questionary style based on preferences."""
    high_contrast = os.getenv("INSTRUCTIONKIT_HIGH_CONTRAST", "false").lower() == "true"

    if high_contrast:
        return questionary.Style([
            ("highlighted", "bold"),
            ("selected", "bold"),
        ])
    else:
        return questionary.Style([
            ("highlighted", "bold cyan"),
            ("selected", "bold green"),
        ])
```

---

## 6. Implementation Roadmap

### Phase 1: Critical Path (Week 1)

**Priority: HIGH**

1. **Collision Resolution with Questionary**
   - Add `questionary>=2.0` dependency
   - Implement `resolve_collision_interactive()` in `install_new.py`
   - Add fallback for non-interactive environments
   - Update `_resolve_name_conflicts()` to use new function

2. **Update Command Disambiguation**
   - Create `cli/update.py` with `update_with_disambiguation()`
   - Implement table-based selection UI
   - Add `--from` and `--all` flags for automation

3. **Testing**
   - Unit tests for collision resolution logic
   - Integration tests for interactive prompts (with mocked input)
   - CI/CD tests for non-interactive mode

### Phase 2: Enhanced UX (Week 2)

**Priority: MEDIUM**

1. **Version Display in TUI**
   - Update `tui/installer.py` to show version in status bar on selection
   - Add version sorting to DataTable
   - Implement truncation for long refs

2. **Progress Indication**
   - Add `update_multiple_with_progress()` for batch updates
   - Implement Rich progress bars
   - Add `--verbose` flag for git output streaming

3. **Accessibility**
   - Add `--no-color` flag support
   - Implement `is_interactive()` detection
   - Document CI/CD usage patterns

### Phase 3: Polish (Week 3)

**Priority: LOW**

1. **Advanced Features**
   - Multi-select checkbox for update command
   - Side-by-side comparison for collisions
   - Color-coded version age indicators

2. **Documentation**
   - Update README with new features
   - Add examples for CI/CD automation
   - Create troubleshooting guide

3. **Performance**
   - Cache remote version checks
   - Parallel git operations for batch updates
   - Optimize TUI rendering for large libraries

---

## 7. Code Examples Summary

### Questionary Integration

**Installation**:
```bash
# Add to pyproject.toml
[project]
dependencies = [
    "typer[all]>=0.9.0",
    "rich>=13.7.0",
    "pyyaml>=6.0",
    "textual>=0.63.0",
    "questionary>=2.0.0",  # New
]
```

**Basic Usage**:
```python
import questionary

# Simple selection
answer = questionary.select(
    "Choose option:",
    choices=["Option 1", "Option 2", "Option 3"]
).ask()

# Multi-select
answers = questionary.checkbox(
    "Select multiple:",
    choices=["A", "B", "C"]
).ask()

# Confirmation
confirmed = questionary.confirm("Proceed?", default=True).ask()
```

### Textual TUI Updates

**Version Column**:
```python
# In tui/installer.py - InstructionInstallerScreen.on_mount()
table.add_column("Ver", key="version", width=8)

# In refresh_table()
version_display = inst.version  # Compact semver

# On row selection, show full details
@on(DataTable.RowSelected)
def on_row_selected(self, event):
    inst = self._get_instruction(event.row_key.value)
    self.query_one("#status-text").update(
        f"Selected: {inst.name} v{inst.version} | "
        f"From: {inst.repo_namespace}@{inst.version_ref}"
    )
```

### Rich Progress Bars

**Multi-Task Progress**:
```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

def update_repositories(repos: list) -> None:
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
    ) as progress:
        overall = progress.add_task(f"Updating {len(repos)} repos...", total=len(repos))

        for repo in repos:
            task = progress.add_task(f"  ↳ {repo.name}", total=100)
            # Do work...
            progress.update(task, advance=50)
            progress.update(overall, advance=1)
```

---

## 8. Accessibility Quick Reference

### Color Independence

✅ **Good**: `[✓] Installed successfully`
❌ **Bad**: `[green]█[/green]` (relies on color alone)

### Keyboard Navigation

✅ **Good**: Arrow keys, Enter, Space, Tab
❌ **Bad**: Mouse-only interactions

### Screen Reader Support

✅ **Good**: `--no-color` flag, descriptive text
❌ **Bad**: Unicode art as primary content

### Non-Interactive Fallbacks

✅ **Good**: Environment variables, CLI flags
❌ **Bad**: Required interactive prompts in CI/CD

---

## 9. References and Resources

### Documentation

- **Typer**: https://typer.tiangolo.com/
- **Rich**: https://rich.readthedocs.io/
- **Textual**: https://textual.textualize.io/
- **Questionary**: https://questionary.readthedocs.io/

### Examples in the Wild

- **cargo-interactive-update**: https://github.com/BenJeau/cargo-interactive-update
- **poetry**: https://python-poetry.org/docs/cli/
- **npm**: https://docs.npmjs.com/cli/
- **git**: https://git-scm.com/docs

### Design Patterns

- CLI Guidelines: https://clig.dev/
- Unix Philosophy: https://en.wikipedia.org/wiki/Unix_philosophy
- Semantic Versioning: https://semver.org/

---

## 10. Mockups and Visual Examples

### Collision Resolution Flow

```
Step 1: Detection
┌────────────────────────────────────────────────────────┐
│ ⚠️  Collision Detected                                 │
│ Multiple instructions named 'python-testing' selected  │
└────────────────────────────────────────────────────────┘

Step 2: Comparison Table
┌───┬─────────────────┬─────────┬──────────────────┬──────────┐
│ # │ Source          │ Version │ Description      │ Author   │
├───┼─────────────────┼─────────┼──────────────────┼──────────┤
│ 1 │ acme/examples   │ 1.2.0   │ Python testing…  │ John S.  │
│ 2 │ company/guides  │ 2.0.1   │ Comprehensive…   │ Jane D.  │
└───┴─────────────────┴─────────┴──────────────────┴──────────┘

Step 3: Interactive Selection
? How would you like to resolve this collision?
❯ 📁 Namespace all by source (recommended)
  ─── or select one to keep as-is: ───
    [1] acme/examples v1.2.0 → keep as 'python-testing'
    [2] company/guides v2.0.1 → keep as 'python-testing'

  ❌ Cancel installation

Step 4: Confirmation
✓ Installing as:
  • acme/python-testing
  • company/python-testing
```

### Update Disambiguation Flow

```
Step 1: Ambiguity Detection
$ aiconfig update python-testing

Multiple instructions named 'python-testing' found:

Step 2: Version Comparison
┌───┬─────────────────┬─────────────┬───────────┬────────────┐
│ # │ Source          │ Current Ver │ Available │ Status     │
├───┼─────────────────┼─────────────┼───────────┼────────────┤
│ 1 │ acme/examples   │ 1.2.0       │ 1.3.0     │ Update ↑   │
│ 2 │ company/guides  │ 2.0.1       │ 2.0.1     │ Up to date │
└───┴─────────────────┴─────────────┴───────────┴────────────┘

Step 3: Selection
? Which 'python-testing' instruction(s) would you like to update?
❯ 🔄 Update all 2 instructions
  ─── or select specific ones: ───
    [1] acme/examples v1.2.0 → 1.3.0
    [2] company/guides v2.0.1 ✓ up to date

  ❌ Cancel

Step 4: Progress
⠋ Updating 1 repository... ━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
  ↳ acme/examples

✓ Update complete
```

### TUI Version Display

```
Before (Current):
┌────────────────┬──────────────────────────────┬─────┬────────┐
│ Name           │ Description                  │ Ver │ Tags   │
├────────────────┼──────────────────────────────┼─────┼────────┤
│ python-testing │ Python testing best practice │ 1.0 │ python │
└────────────────┴──────────────────────────────┴─────┴────────┘

After (Enhanced):
┌────────────────┬──────────────────────────────┬──────────┬────────┐
│ Name           │ Description                  │ Version  │ Tags   │
├────────────────┼──────────────────────────────┼──────────┼────────┤
│ python-testing │ Python testing best practice │ 1.2.0    │ python │
└────────────────┴──────────────────────────────┴──────────┴────────┘

Status bar (on selection):
Selected: python-testing v1.2.0 | From: acme/examples@v1.2.0 | Updated: 2024-10-20
```

---

## Conclusion

This research provides comprehensive patterns for implementing version selection and collision resolution in DevSync. Key recommendations:

1. **Adopt questionary** for rich interactive prompts (collision resolution, update disambiguation)
2. **Enhance TUI** with compact version display and selection-based details
3. **Add CLI flags** (`--from`, `--all`, `--no-color`) for automation and accessibility
4. **Implement progress bars** for batch operations using Rich
5. **Support CI/CD** with environment variables and non-interactive fallbacks

The patterns are battle-tested by popular tools (cargo, npm, poetry, git) and aligned with modern CLI best practices. Implementation can be phased over 2-3 weeks, prioritizing collision resolution and update disambiguation first.
