"""Refactored install command with library support."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm

from aiconfigkit.ai_tools.base import AITool
from aiconfigkit.ai_tools.detector import AIToolDetector, get_detector
from aiconfigkit.core.conflict_resolution import ConflictResolver, prompt_conflict_resolution
from aiconfigkit.core.models import (
    ConflictResolution,
    InstallationRecord,
    InstallationScope,
    LibraryInstruction,
    RefType,
)
from aiconfigkit.storage.library import LibraryManager
from aiconfigkit.storage.tracker import InstallationTracker
from aiconfigkit.tui.installer import show_installer_tui
from aiconfigkit.utils.project import find_project_root
from aiconfigkit.utils.ui import print_error, print_info, print_success

console = Console()


# ============================================================================
# Helper Functions - Shared Installation Logic
# ============================================================================


def _extract_ref_from_namespace(namespace: str) -> tuple[Optional[str], Optional[RefType]]:
    """Extract Git reference from versioned namespace.

    Args:
        namespace: Repository namespace (e.g., 'github.com_owner_repo@v1.0.0')

    Returns:
        Tuple of (ref, ref_type) or (None, None) if no version info
    """
    if "@" not in namespace:
        return (None, None)

    # Split at @ to get the ref part
    ref = namespace.split("@", 1)[1]

    # Try to determine ref type from the ref format
    # This is a best-effort detection since we don't have the original ref_type stored
    import re

    # Tags typically start with 'v' followed by numbers
    if re.match(r"^v?\d+\.\d+", ref):
        return (ref, RefType.TAG)
    # Commit hashes are hex strings
    elif re.match(r"^[0-9a-f]{7,40}$", ref):
        return (ref, RefType.COMMIT)
    # Everything else is likely a branch
    else:
        # Restore slashes that were converted to underscores
        # This is approximate - feature_new might have been feature/new
        return (ref, RefType.BRANCH)


def _parse_conflict_strategy(conflict_strategy: str) -> Optional[ConflictResolution]:
    """Parse and validate conflict resolution strategy.

    Args:
        conflict_strategy: Strategy string (prompt, skip, rename, overwrite)

    Returns:
        ConflictResolution enum or None if invalid
    """
    try:
        return ConflictResolution(conflict_strategy.lower())
    except ValueError:
        print_error(
            f"Invalid conflict strategy: {conflict_strategy}. " "Must be 'prompt', 'skip', 'rename', or 'overwrite'."
        )
        return None


def _get_project_root_for_installation() -> Optional[Path]:
    """Detect and validate project root for installation.

    Returns:
        Project root path or None if not found
    """
    project_root = find_project_root()
    if not project_root:
        print_error("Could not detect project root. " "Make sure you're running from within a project directory.")
        return None
    console.print(f"Detected project root: [cyan]{project_root}[/cyan]")
    return project_root


def _load_instructions_from_library(instruction_ids: list[str], library: LibraryManager) -> Optional[list]:
    """Load instructions from library by IDs.

    Args:
        instruction_ids: List of instruction IDs to load
        library: Library manager instance

    Returns:
        List of LibraryInstruction objects or None if any not found
    """
    instructions = []
    for inst_id in instruction_ids:
        inst = library.get_instruction(inst_id)
        if not inst:
            print_error(f"Instruction not found in library: {inst_id}")
            return None
        instructions.append(inst)
    return instructions


def _detect_installed_collisions(
    instructions: list[LibraryInstruction],
    ai_tools: list[AITool],
    install_names: dict[str, str],
    project_root: Optional[Path],
) -> dict[str, list[InstallationRecord]]:
    """Detect collisions with already-installed instructions.

    Args:
        instructions: List of instructions to install
        ai_tools: List of AI tools to install to
        install_names: Mapping of instruction IDs to install names
        project_root: Project root path

    Returns:
        Dictionary mapping instruction_id to list of existing installations with same name
    """
    tracker = InstallationTracker()
    collisions = {}

    for inst in instructions:
        install_name = install_names[inst.id]

        # Check if this name is already used in any tool
        existing = tracker.find_instructions_by_name(install_name, project_root)

        # Filter to only collisions from different repositories
        different_repo_collisions = [e for e in existing if e.source_repo != inst.repo_url]

        if different_repo_collisions:
            collisions[inst.id] = different_repo_collisions

    return collisions


def _prompt_for_custom_filename(
    instruction: LibraryInstruction,
    existing_installations: list[InstallationRecord],
    current_name: str,
) -> Optional[str]:
    """Prompt user to provide custom filename for collision resolution.

    Args:
        instruction: Instruction being installed
        existing_installations: List of existing installations with same name
        current_name: Current proposed install name

    Returns:
        Custom filename or None to skip installation
    """
    console.print(f"\n[yellow]⚠️  Name Collision:[/yellow] '{current_name}' is already installed")
    console.print("\n[bold]Existing installations:[/bold]")
    for existing in existing_installations:
        repo_display = existing.source_repo or "unknown"
        ref_display = existing.source_ref or "unknown"
        console.print(f"  • {existing.ai_tool.value}: {repo_display} @ {ref_display}")

    console.print("\n[bold]New installation:[/bold]")
    console.print(f"  • Repository: {instruction.repo_url}")
    console.print(f"  • Namespace: {instruction.repo_namespace}")

    console.print("\n[bold]Options:[/bold]")
    console.print("  [1] Provide custom filename")
    console.print("  [2] Skip this instruction")

    choice = typer.prompt("Select (1-2)", default="2")

    if choice == "1":
        custom_name = typer.prompt(
            "Enter custom filename (without extension)",
            default=f"{instruction.repo_namespace.replace('@', '-').replace('/', '-')}_{instruction.name}",
        )
        return str(custom_name)
    else:
        return None


def _resolve_name_conflicts(instructions: list[LibraryInstruction]) -> Optional[dict[str, str]]:
    """Resolve naming conflicts for instructions with duplicate names.

    Args:
        instructions: List of LibraryInstruction objects

    Returns:
        Dict mapping instruction ID to install name, or None if cancelled
    """
    # Check for name conflicts
    name_conflicts: dict[str, list[LibraryInstruction]] = {}
    for inst in instructions:
        if inst.name not in name_conflicts:
            name_conflicts[inst.name] = []
        name_conflicts[inst.name].append(inst)

    # Handle conflicts
    install_names = {}  # Map instruction ID to final install name
    for name, insts in name_conflicts.items():
        if len(insts) > 1:
            console.print(f"\n[yellow]⚠️  Name Conflict:[/yellow] " f"{len(insts)} instructions named '{name}'")
            console.print("\nHow should they be installed?")
            console.print("  [1] Namespace by repository (recommended)")
            for inst in insts:
                console.print(f"      → {inst.repo_namespace}/{name}")
            console.print("  [2] Skip installation (cancel)")

            choice = typer.prompt("Select (1-2)", default="1")

            if choice == "1":
                # Use namespaced names
                for inst in insts:
                    install_names[inst.id] = f"{inst.repo_namespace}/{name}"
            else:
                print_info("Installation cancelled")
                return None
        else:
            # No conflict, use simple name
            install_names[insts[0].id] = name

    return install_names


def _get_ai_tools_from_names(tool_names: list[str], detector: AIToolDetector) -> Optional[list[AITool]]:
    """Get AI tool instances from tool names.

    Args:
        tool_names: List of tool name strings
        detector: AI tool detector instance

    Returns:
        List of AITool instances or None if any invalid/not installed
    """
    ai_tools = []
    for tool_name in tool_names:
        tool = detector.get_tool_by_name(tool_name)
        if not tool:
            print_error(f"AI tool not found: {tool_name}")
            return None
        if not tool.is_installed():
            print_error(f"{tool.tool_name} is not installed")
            return None
        ai_tools.append(tool)
    return ai_tools


def _show_installation_preview(
    project_root: Path, instructions: list, ai_tools: list, install_names: dict[str, str]
) -> bool:
    """Show installation preview and ask for confirmation.

    Args:
        project_root: Project root path
        instructions: List of instructions to install
        ai_tools: List of AI tools to install to
        install_names: Mapping of instruction IDs to install names

    Returns:
        True if user confirms, False otherwise
    """
    console.print("\n[bold cyan]📦 Installation Preview[/bold cyan]")
    console.print(f"\n[bold]Project:[/bold] {project_root}")
    console.print(f"[bold]Instructions:[/bold] {len(instructions)} selected")
    console.print(f"[bold]Target tools:[/bold] {', '.join([t.tool_name for t in ai_tools])}\n")

    # Show where files will be created
    console.print("[bold yellow]The following files will be created:[/bold yellow]\n")

    for ai_tool in ai_tools:
        tool_dir = ai_tool.get_project_instructions_directory(project_root)
        console.print(f"[cyan]{ai_tool.tool_name}[/cyan] → {tool_dir}")
        for inst in instructions:
            install_name = install_names[inst.id]
            filename = f"{install_name}{ai_tool.get_instruction_file_extension()}"
            console.print(f"  • {filename}")
        console.print()

    # Ask for confirmation
    return Confirm.ask("\n[bold]Proceed with installation?[/bold]", default=True)


def _check_for_upgrades(
    instructions: list,
    ai_tools: list,
    install_names: dict[str, str],
    project_root: Optional[Path],
) -> dict[str, tuple[InstallationRecord, LibraryInstruction]]:
    """Check if any instructions being installed are upgrades of existing installations.

    Args:
        instructions: List of instructions to install
        ai_tools: List of AI tools to install to
        install_names: Mapping of instruction IDs to install names
        project_root: Project root path

    Returns:
        Dictionary mapping instruction_id to (existing_record, new_instruction) for upgrades
    """
    tracker = InstallationTracker()
    upgrades = {}

    for ai_tool in ai_tools:
        for inst in instructions:
            install_name = install_names[inst.id]

            # Check if this instruction is already installed for this tool
            existing = tracker.get_installation(install_name, ai_tool.tool_type, project_root)

            if existing:
                # Extract ref from both old and new
                old_ref = existing.source_ref
                new_ref, new_ref_type = _extract_ref_from_namespace(inst.repo_namespace)

                # Check if versions differ (potential upgrade)
                if old_ref and new_ref and old_ref != new_ref:
                    key = f"{inst.id}_{ai_tool.tool_type.value}"
                    upgrades[key] = (existing, inst)

    return upgrades


def _prompt_for_upgrade(
    existing: InstallationRecord,
    new_instruction: LibraryInstruction,
) -> bool:
    """Prompt user to confirm upgrade from one version to another.

    Args:
        existing: Existing installation record
        new_instruction: New instruction being installed

    Returns:
        True if user confirms upgrade, False otherwise
    """
    old_ref = existing.source_ref or "unknown"
    new_ref, _ = _extract_ref_from_namespace(new_instruction.repo_namespace)
    new_ref = new_ref or "unknown"

    console.print(f"\n[yellow]⚠️  Upgrade Detected:[/yellow] {existing.instruction_name}")
    console.print(f"  Current version: [cyan]{old_ref}[/cyan]")
    console.print(f"  New version:     [green]{new_ref}[/green]")
    console.print(f"  Tool: {existing.ai_tool.value}")

    return Confirm.ask("\n[bold]Upgrade to new version?[/bold]", default=True)


def _perform_installation(
    instructions: list,
    ai_tools: list,
    install_names: dict[str, str],
    install_scope: InstallationScope,
    project_root: Optional[Path],
    strategy: ConflictResolution,
) -> tuple[int, int]:
    """Perform the actual installation of instructions to tools.

    Args:
        instructions: List of instructions to install
        ai_tools: List of AI tools to install to
        install_names: Mapping of instruction IDs to install names
        install_scope: Installation scope (project/global)
        project_root: Project root path
        strategy: Conflict resolution strategy

    Returns:
        Tuple of (installed_count, skipped_count)
    """
    tracker = InstallationTracker()
    resolver = ConflictResolver(default_strategy=strategy)

    installed_count = 0
    skipped_count = 0

    for ai_tool in ai_tools:
        console.print(f"\nInstalling to [cyan]{ai_tool.tool_name}[/cyan]...")

        for inst in instructions:
            install_name = install_names[inst.id]

            # Get target path
            target_path = ai_tool.get_instruction_path(install_name, install_scope, project_root)

            # Handle existing files
            if target_path.exists():
                # Determine the actual strategy to use
                actual_strategy = strategy

                # If strategy is PROMPT, ask user interactively
                if strategy == ConflictResolution.PROMPT:
                    actual_strategy = prompt_conflict_resolution(install_name)

                if actual_strategy == ConflictResolution.SKIP:
                    console.print(f"  [yellow]Skipped:[/yellow] {install_name} (already exists)")
                    skipped_count += 1
                    continue
                elif actual_strategy == ConflictResolution.RENAME:
                    conflict_info = resolver.resolve(install_name, target_path, actual_strategy)
                    if conflict_info.new_path is None:
                        console.print(f"  [red]Error:[/red] Failed to rename {install_name}")
                        continue
                    target_path = Path(conflict_info.new_path)
                    console.print(f"  [yellow]Renamed:[/yellow] {install_name} -> {target_path.name}")
                elif actual_strategy == ConflictResolution.OVERWRITE:
                    console.print(f"  [yellow]Overwriting:[/yellow] {install_name}")

            # Copy file from library
            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Read from library
                source_path = Path(inst.file_path)
                content = source_path.read_text(encoding="utf-8")

                # Write to target
                target_path.write_text(content, encoding="utf-8")

                # Extract ref information from namespace
                source_ref, source_ref_type = _extract_ref_from_namespace(inst.repo_namespace)

                # Track installation
                record = InstallationRecord(
                    instruction_name=install_name,
                    ai_tool=ai_tool.tool_type,
                    source_repo=inst.repo_url,
                    installed_path=str(target_path),
                    installed_at=datetime.now(),
                    checksum=inst.checksum,
                    bundle_name=None,
                    scope=install_scope,
                    source_ref=source_ref,
                    source_ref_type=source_ref_type,
                )
                tracker.add_installation(record, project_root)

                console.print(f"  [green]✓[/green] Installed: {install_name}")
                installed_count += 1

            except Exception as e:
                print_error(f"Failed to install {install_name}: {e}")

    return installed_count, skipped_count


# ============================================================================
# Public Installation Functions
# ============================================================================


def install_from_library_tui(
    tool: Optional[str] = None,
) -> int:
    """
    Show TUI to select and install instructions from library.

    Args:
        tool: AI tool to install to (None = auto-detect)

    Returns:
        Exit code
    """
    library = LibraryManager()

    # Check if library is empty
    if not library.list_instructions():
        print_info("Library is empty. Use 'devsync download --repo <url>' to add instructions.")
        return 1

    # Show TUI (always installs to project level)
    result = show_installer_tui(library=library, tool=tool)

    if not result:
        console.print("[dim]Cancelled[/dim]")
        return 0

    # Install selected instructions
    selected_instructions = result["instructions"]
    selected_tools = result["tools"]  # Now a list of tool names

    return install_from_library_direct_multi_tool(
        instruction_ids=[inst.id for inst in selected_instructions],
        tools=selected_tools,
        conflict_strategy="skip",
    )


def install_from_library_direct_multi_tool(
    instruction_ids: list[str],
    tools: list[str],
    conflict_strategy: str = "skip",
) -> int:
    """
    Install specific instructions from library by ID to multiple tools.

    Args:
        instruction_ids: List of instruction IDs to install
        tools: List of AI tool names to install to
        conflict_strategy: Conflict resolution strategy

    Returns:
        Exit code
    """
    library = LibraryManager()
    install_scope = InstallationScope.PROJECT

    # Parse conflict strategy
    strategy = _parse_conflict_strategy(conflict_strategy)
    if strategy is None:
        return 1

    # Get project root
    project_root = _get_project_root_for_installation()
    if project_root is None:
        return 1

    # Load instructions from library
    instructions = _load_instructions_from_library(instruction_ids, library)
    if instructions is None:
        return 1

    # Resolve name conflicts
    install_names = _resolve_name_conflicts(instructions)
    if install_names is None:
        return 0

    # Get AI tools
    detector = get_detector()
    ai_tools = _get_ai_tools_from_names(tools, detector)
    if ai_tools is None:
        return 1

    # Detect collisions with installed instructions from different repositories
    collisions = _detect_installed_collisions(instructions, ai_tools, install_names, project_root)
    if collisions:
        console.print("\n[bold cyan]Handling Name Collisions[/bold cyan]")
        for inst in instructions:
            if inst.id in collisions:
                current_name = install_names[inst.id]
                custom_name = _prompt_for_custom_filename(inst, collisions[inst.id], current_name)
                if custom_name is None:
                    # User chose to skip
                    console.print(f"[dim]Skipping {current_name}[/dim]")
                    # Remove from installation list
                    instructions = [i for i in instructions if i.id != inst.id]
                else:
                    # Use custom name
                    install_names[inst.id] = custom_name

        if not instructions:
            console.print("[yellow]No instructions remaining to install[/yellow]")
            return 0

    # Show preview and confirm
    if not _show_installation_preview(project_root, instructions, ai_tools, install_names):
        console.print("[dim]Installation cancelled[/dim]")
        return 0

    # Check for upgrades and prompt if needed
    upgrades = _check_for_upgrades(instructions, ai_tools, install_names, project_root)
    if upgrades:
        console.print("\n[bold cyan]Upgrade Confirmation[/bold cyan]")
        for key, (existing, new_inst) in upgrades.items():
            if not _prompt_for_upgrade(existing, new_inst):
                console.print("[dim]Installation cancelled[/dim]")
                return 0

    # Perform installation
    installed_count, skipped_count = _perform_installation(
        instructions, ai_tools, install_names, install_scope, project_root, strategy
    )

    # Summary
    console.print()
    if installed_count > 0:
        print_success(f"✓ Successfully installed {installed_count} instruction(s)")
    if skipped_count > 0:
        print_info(f"Skipped {skipped_count} existing instruction(s)")

    return 0


def install_from_library_direct(
    instruction_ids: list[str],
    tool: Optional[str] = None,
    conflict_strategy: str = "skip",
) -> int:
    """
    Install specific instructions from library by ID.

    Args:
        instruction_ids: List of instruction IDs to install
        tool: AI tool to install to
        conflict_strategy: Conflict resolution strategy

    Returns:
        Exit code
    """
    library = LibraryManager()
    install_scope = InstallationScope.PROJECT

    # Parse conflict strategy
    strategy = _parse_conflict_strategy(conflict_strategy)
    if strategy is None:
        return 1

    # Get project root
    project_root = _get_project_root_for_installation()
    if project_root is None:
        return 1

    # Load instructions from library
    instructions = _load_instructions_from_library(instruction_ids, library)
    if instructions is None:
        return 1

    # Resolve name conflicts
    install_names = _resolve_name_conflicts(instructions)
    if install_names is None:
        return 0

    # Determine AI tool(s)
    detector = get_detector()
    if tool:
        ai_tools = _get_ai_tools_from_names([tool], detector)
        if ai_tools is None:
            return 1
    else:
        ai_tools = detector.detect_installed_tools()
        if not ai_tools:
            print_error("No AI coding tools detected")
            return 1

    # Detect collisions with installed instructions from different repositories
    collisions = _detect_installed_collisions(instructions, ai_tools, install_names, project_root)
    if collisions:
        console.print("\n[bold cyan]Handling Name Collisions[/bold cyan]")
        for inst in instructions:
            if inst.id in collisions:
                current_name = install_names[inst.id]
                custom_name = _prompt_for_custom_filename(inst, collisions[inst.id], current_name)
                if custom_name is None:
                    # User chose to skip
                    console.print(f"[dim]Skipping {current_name}[/dim]")
                    # Remove from installation list
                    instructions = [i for i in instructions if i.id != inst.id]
                else:
                    # Use custom name
                    install_names[inst.id] = custom_name

        if not instructions:
            console.print("[yellow]No instructions remaining to install[/yellow]")
            return 0

    # Show preview and confirm
    if not _show_installation_preview(project_root, instructions, ai_tools, install_names):
        console.print("[dim]Installation cancelled[/dim]")
        return 0

    # Check for upgrades and prompt if needed
    upgrades = _check_for_upgrades(instructions, ai_tools, install_names, project_root)
    if upgrades:
        console.print("\n[bold cyan]Upgrade Confirmation[/bold cyan]")
        for key, (existing, new_inst) in upgrades.items():
            if not _prompt_for_upgrade(existing, new_inst):
                console.print("[dim]Installation cancelled[/dim]")
                return 0

    # Perform installation
    installed_count, skipped_count = _perform_installation(
        instructions, ai_tools, install_names, install_scope, project_root, strategy
    )

    # Summary
    console.print()
    if installed_count > 0:
        print_success(f"✓ Successfully installed {installed_count} instruction(s)")
    if skipped_count > 0:
        print_info(f"Skipped {skipped_count} existing instruction(s)")

    return 0


def install_from_library_by_name(
    name: str,
    tool: Optional[str] = None,
    conflict_strategy: str = "skip",
) -> int:
    """
    Install instruction(s) from library by name.

    Supports source/name format for disambiguation (e.g., 'company/python-best-practices').

    Args:
        name: Instruction name (or source/name format)
        tool: AI tool to install to
        conflict_strategy: Conflict resolution strategy

    Returns:
        Exit code
    """
    library = LibraryManager()

    # Parse source/name format
    source_alias = None
    instruction_name = name
    if "/" in name:
        parts = name.split("/", 1)
        source_alias = parts[0]
        instruction_name = parts[1]

    # Find instructions with this name
    if source_alias:
        # Filter by source alias
        instructions = library.get_instructions_by_source_and_name(source_alias, instruction_name)
    else:
        instructions = library.get_instructions_by_name(instruction_name)

    if not instructions:
        print_error(f"No instruction named '{name}' found in library.")
        print_info("Use 'devsync list library --instructions' to see available instructions.")
        return 1

    if len(instructions) == 1:
        # Single match, install it
        return install_from_library_direct(
            instruction_ids=[instructions[0].id],
            tool=tool,
            conflict_strategy=conflict_strategy,
        )

    # Multiple matches - show options
    console.print(f"\n[yellow]Multiple instructions named '{name}' found:[/yellow]\n")
    for i, inst in enumerate(instructions, 1):
        # Extract ref from namespace for display
        ref, ref_type = _extract_ref_from_namespace(inst.repo_namespace)
        ref_display = f"@{ref}" if ref else f"v{inst.version}"
        console.print(f"  [{i}] {inst.repo_name} ({ref_display}) - {inst.author}")
        console.print(f"      {inst.description}")
        console.print()

    console.print("  [A] Install all")
    console.print("  [C] Cancel")
    console.print()

    choice = typer.prompt("Select", default="C")

    if choice.upper() == "C":
        print_info("Installation cancelled")
        return 0
    elif choice.upper() == "A":
        # Install all
        return install_from_library_direct(
            instruction_ids=[inst.id for inst in instructions],
            tool=tool,
            conflict_strategy=conflict_strategy,
        )
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(instructions):
            return install_from_library_direct(
                instruction_ids=[instructions[idx].id],
                tool=tool,
                conflict_strategy=conflict_strategy,
            )

    print_error("Invalid selection")
    return 1


# Keep the original direct install function for backward compatibility
def install_from_repo_direct(
    name: str,
    repo: str,
    tool: Optional[str] = None,
    conflict_strategy: str = "skip",
    bundle: bool = False,
) -> int:
    """
    Install directly from a repository (backward compatibility).

    This is the original install function, preserved for --repo usage.
    """
    # Import the original function
    from aiconfigkit.cli.install import install_instruction as original_install

    return original_install(
        name=name,
        repo=repo,
        tool=tool,
        conflict_strategy=conflict_strategy,
        bundle=bundle,
    )


def install_multiple_from_library(
    names: list[str],
    tools: Optional[list[str]],
    conflict_strategy: str,
) -> int:
    """
    Install multiple instructions from library.

    Args:
        names: List of instruction names
        tools: List of AI tool names (None = all detected tools)
        conflict_strategy: Conflict resolution strategy

    Returns:
        Exit code
    """
    library = LibraryManager()

    # Get all instructions by name
    all_instructions = []
    for name in names:
        insts = library.get_instructions_by_name(name)
        if not insts:
            print_error(f"No instruction named '{name}' found in library.")
            return 1

        if len(insts) > 1:
            # Multiple matches - show options
            console.print(f"\n[yellow]Multiple instructions named '{name}' found:[/yellow]\n")
            for i, inst in enumerate(insts, 1):
                console.print(f"  [{i}] {inst.repo_name} (v{inst.version}) - {inst.author}")
            console.print()

            choice = typer.prompt(f"Select which '{name}' to install (1-{len(insts)})", default="1")

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(insts):
                    all_instructions.append(insts[idx])
                else:
                    print_error("Invalid selection")
                    return 1
            else:
                print_error("Invalid selection")
                return 1
        else:
            all_instructions.append(insts[0])

    # Get instruction IDs
    instruction_ids = [inst.id for inst in all_instructions]

    # Install using the multi-tool function
    if tools:
        return install_from_library_direct_multi_tool(
            instruction_ids=instruction_ids,
            tools=tools,
            conflict_strategy=conflict_strategy,
        )
    else:
        # Use existing single-tool logic (all tools)
        return install_from_library_direct(
            instruction_ids=instruction_ids,
            tool=None,  # Will install to all detected tools
            conflict_strategy=conflict_strategy,
        )


def install_instruction_unified(
    names: Optional[list[str]] = None,
    repo: Optional[str] = None,
    tools: Optional[list[str]] = None,
    conflict_strategy: str = "prompt",
    bundle: bool = False,
) -> int:
    """
    Unified install function that routes to appropriate implementation.

    All installations are at project level.

    Args:
        names: Instruction name(s) (optional, can be multiple)
        repo: Repository URL (optional)
        tools: AI tool(s) to install to (optional, can be multiple)
        conflict_strategy: Conflict resolution strategy
        bundle: Whether installing a bundle

    Returns:
        Exit code
    """
    # Convert single tool format (backward compat)
    tool = tools[0] if tools and len(tools) == 1 else None

    # Case 1: Direct install from repo (backward compat)
    if repo:
        if not names or len(names) == 0:
            print_error("When using --repo, you must specify an instruction name")
            return 1

        # Only support single name with --repo for now
        if len(names) > 1:
            print_error("Cannot install multiple instructions with --repo. Install one at a time or use the library.")
            return 1

        return install_from_repo_direct(
            name=names[0],
            repo=repo,
            tool=tool,
            conflict_strategy=conflict_strategy,
            bundle=bundle,
        )

    # Case 2: Install from library with TUI
    if not names or len(names) == 0:
        return install_from_library_tui(tool=tool)

    # Case 3: Install multiple instructions from library
    if len(names) > 1 or (tools and len(tools) > 1):
        return install_multiple_from_library(
            names=names,
            tools=tools,
            conflict_strategy=conflict_strategy,
        )

    # Case 4: Install single instruction from library by name
    return install_from_library_by_name(
        name=names[0],
        tool=tool,
        conflict_strategy=conflict_strategy,
    )
