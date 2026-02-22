"""Extract command — reads project configs and produces a shareable package."""

import shutil
import warnings
from collections import Counter
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from devsync.core.component_detector import (
    COMPONENT_TYPE_MAP,
    ComponentDetector,
    DetectionResult,
    filter_detection_result,
)
from devsync.core.extractor import PracticeExtractor
from devsync.core.package_manifest_v2 import PackageManifestV2, detect_manifest_format, parse_manifest
from devsync.llm.config import load_config
from devsync.llm.provider import resolve_provider

console = Console()

# Map DetectionResult field names back to user-facing component names
_FIELD_TO_LABEL: dict[str, str] = {
    "instructions": "Rules",
    "mcp_servers": "MCP",
    "hooks": "Hooks",
    "commands": "Commands",
    "skills": "Skills",
    "workflows": "Workflows",
    "memory_files": "Memory",
    "resources": "Resources",
}


def _get_detection_rows(detection: DetectionResult) -> list[tuple[str, str, int]]:
    """Build (component_label, source_tool, count) rows from detection.

    Groups by component type + source tool for a concise table.

    Returns:
        List of (label, source, count) tuples, sorted by label then source.
    """
    rows: list[tuple[str, str, int]] = []

    for field_name, label in _FIELD_TO_LABEL.items():
        items = getattr(detection, field_name, [])
        if not items:
            continue

        source_counts: Counter[str] = Counter()
        for item in items:
            source = getattr(item, "source_tool", "") or getattr(item, "source_ide", "") or "project"
            source_counts[source] += 1

        for source, count in sorted(source_counts.items()):
            rows.append((label, source, count))

    return rows


def _display_detection_summary(detection: DetectionResult) -> None:
    """Display a Rich table summarizing detected components."""
    rows = _get_detection_rows(detection)

    if not rows:
        return

    table = Table(title="Detected Components", show_header=True, header_style="bold cyan")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Source", style="green")
    table.add_column("Count", justify="right")

    for label, source, count in rows:
        table.add_row(label, source, str(count))

    console.print()
    console.print(table)

    tool_sources = {source for _, source, _ in rows if source not in ("project", "devsync")}
    tool_count = len(tool_sources) if tool_sources else 1
    console.print(f"\n  Total: {detection.total_count} components from {tool_count} tool(s)")


def _display_zero_result_warning(
    tool: Optional[list[str]] = None,
    component: Optional[list[str]] = None,
    include_global: bool = False,
) -> None:
    """Display a helpful warning when filters match no components."""
    console.print("\n[yellow]No components found matching your filters.[/yellow]")

    active_filters = []
    if tool:
        active_filters.append(f"--tool {' --tool '.join(tool)}")
    if component:
        active_filters.append(f"--component {' --component '.join(component)}")
    if active_filters:
        console.print(f"\n  Active: {' '.join(active_filters)}")

    console.print("\n  Suggestions:")
    console.print("  - Run [cyan]devsync extract --dry-run[/cyan] without filters to see all available components")
    if not include_global:
        console.print("  - Try [cyan]--include-global[/cyan] to include home directory configs")


def extract_command(
    output: Optional[str] = None,
    name: Optional[str] = None,
    no_ai: bool = False,
    project_dir: Optional[str] = None,
    upgrade: Optional[str] = None,
    tool: Optional[list[str]] = None,
    component: Optional[list[str]] = None,
    scope: str = "project",
    dry_run: bool = False,
    include_global: bool = False,
) -> int:
    """Extract practices from the current project into a shareable package.

    Args:
        output: Output directory for the package. Defaults to './devsync-package/'.
        name: Package name. Defaults to project directory name.
        no_ai: Force file-copy mode (no LLM calls).
        project_dir: Project directory to extract from. Defaults to cwd.
        upgrade: Path to a v1 package to convert to v2 format.
        tool: Only extract from these AI tool(s).
        component: Only extract these component types.
        scope: Detection scope — project, global, or all. Deprecated; use include_global.
        dry_run: Show what would be extracted without writing files.
        include_global: Include home directory / global configs.

    Returns:
        Exit code (0 = success).
    """
    if upgrade:
        return _upgrade_v1_package(upgrade, output=output, name=name, no_ai=no_ai)

    # Resolve effective scope: --include-global takes precedence
    effective_scope = "project"
    if include_global:
        effective_scope = "all"
    elif scope != "project":
        warnings.warn(
            "--scope is deprecated, use --include-global instead",
            DeprecationWarning,
            stacklevel=2,
        )
        console.print("[yellow]--scope is deprecated. Use --include-global instead.[/yellow]")
        effective_scope = scope

    # Validate scope
    if effective_scope not in ("project", "global", "all"):
        console.print(f"[red]Invalid scope: {effective_scope}. Must be project, global, or all.[/red]")
        return 1

    # Validate tool names
    if tool:
        from devsync.ai_tools.detector import AIToolDetector

        detector = AIToolDetector()
        for t in tool:
            if not detector.validate_tool_name(t):
                console.print(f"[red]Unknown tool: {t}[/red]")
                console.print(f"Supported tools: {', '.join(detector.get_tool_names())}")
                return 1

    # Validate component names
    if component:
        for c in component:
            if c.lower() not in COMPONENT_TYPE_MAP:
                valid = sorted(set(COMPONENT_TYPE_MAP.keys()))
                console.print(f"[red]Unknown component type: {c}[/red]")
                console.print(f"Valid types: {', '.join(valid)}")
                return 1

    project_path = Path(project_dir) if project_dir else Path.cwd()
    if not project_path.is_dir():
        console.print(f"[red]Not a directory: {project_path}[/red]")
        return 1

    # Phase 1: Detection + filtering
    comp_detector = ComponentDetector(project_path, scope=effective_scope, tool_filter=tool)
    detection = comp_detector.detect_all()

    if component:
        detection = filter_detection_result(detection, component_filter=component)

    # Zero-result handling
    if detection.total_count == 0:
        _display_zero_result_warning(tool=tool, component=component, include_global=include_global)
        return 0

    # Display detection summary
    _display_detection_summary(detection)

    # Dry-run: stop here
    if dry_run:
        console.print("\n[dim]Dry run — no files written.[/dim]")
        return 0

    # Phase 2: Extraction
    package_name = name or project_path.name
    output_path = Path(output) if output else project_path / "devsync-package"

    llm = None
    if not no_ai:
        config = load_config()
        llm = resolve_provider(
            preferred_provider=config.provider,
            preferred_model=config.model,
        )
        if not llm:
            console.print("[yellow]No LLM API key found. Using file-copy mode.[/yellow]")
            console.print("Run [cyan]devsync setup[/cyan] to configure AI features.\n")

    extractor = PracticeExtractor(llm_provider=llm)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Extracting practices...", total=None)
        result = extractor.extract(project_path, detection=detection)
        progress.update(task, description="Building package...")

    output_path.mkdir(parents=True, exist_ok=True)

    manifest = PackageManifestV2(
        format_version="2.0",
        name=package_name,
        version="1.0.0",
        description=f"Extracted from {project_path.name}",
        practices=result.practices,
        mcp_servers=result.mcp_servers,
    )

    if not result.ai_powered:
        _copy_source_files(project_path, output_path, result.source_files)
        components: dict = {}
        if result.source_files:
            from devsync.core.package_manifest_v2 import ComponentRef

            components["instructions"] = [
                ComponentRef(
                    name=Path(f).stem,
                    file=f"instructions/{Path(f).name}",
                )
                for f in result.source_files
            ]
        manifest.components = components

    manifest_path = output_path / "devsync-package.yaml"
    manifest_path.write_text(manifest.to_yaml())

    # Enhanced output
    mode = "[green]AI-powered[/green]" if result.ai_powered else "[yellow]file-copy[/yellow]"
    console.print(f"\nExtraction complete ({mode})")
    console.print(f"  Practices generated: {len(result.practices)}")
    console.print(f"  MCP servers: {len(result.mcp_servers)}")
    console.print(f"  Source files: {len(result.source_files)}")
    console.print(f"\n  Package written to: [cyan]{output_path}[/cyan]")
    return 0


def _upgrade_v1_package(
    v1_path: str,
    output: Optional[str] = None,
    name: Optional[str] = None,
    no_ai: bool = False,
) -> int:
    """Convert a v1 package to v2 format.

    Reads the v1 manifest, extracts instruction files, and produces a v2
    package with practice declarations (AI-powered) or literal content (no-AI).

    Args:
        v1_path: Path to the v1 package directory.
        output: Output directory for the v2 package.
        name: Package name override.
        no_ai: Disable AI-powered conversion.

    Returns:
        Exit code (0 = success).
    """
    package_path = Path(v1_path).expanduser()
    if not package_path.is_dir():
        console.print(f"[red]Not a directory: {package_path}[/red]")
        return 1

    fmt = detect_manifest_format(package_path)
    if not fmt:
        console.print(f"[red]No manifest found in {package_path}[/red]")
        console.print("Expected: ai-config-kit-package.yaml or devsync-package.yaml")
        return 1

    if fmt == "v2":
        console.print("[yellow]Package is already v2 format. No upgrade needed.[/yellow]")
        return 0

    v1_manifest = parse_manifest(package_path)
    console.print(f"\n[bold]Upgrading v1 package: {v1_manifest.name} v{v1_manifest.version}[/bold]")

    instruction_files: dict[str, str] = {}
    for comp_type, refs in v1_manifest.components.items():
        if comp_type != "instructions":
            continue
        for ref in refs:
            src_file = (package_path / ref.file).resolve()
            try:
                src_file.relative_to(package_path.resolve())
            except ValueError:
                console.print(f"  [red]Rejected (path traversal): {ref.file}[/red]")
                continue
            if src_file.exists() and src_file.stat().st_size < 100_000:
                try:
                    content = src_file.read_text(encoding="utf-8")
                    instruction_files[ref.file] = content
                except (OSError, UnicodeDecodeError):
                    console.print(f"  [yellow]Could not read: {ref.file}[/yellow]")

    if not instruction_files:
        console.print("[red]No instruction files found in v1 package.[/red]")
        return 1

    llm = None
    if not no_ai:
        config = load_config()
        llm = resolve_provider(preferred_provider=config.provider, preferred_model=config.model)
        if not llm:
            console.print("[yellow]No LLM API key found. Using file-copy mode.[/yellow]")

    extractor = PracticeExtractor(llm_provider=llm)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Converting to v2...", total=None)
        if llm:
            result = extractor._extract_with_ai(instruction_files, [])
        else:
            result = extractor._extract_without_ai(instruction_files, [])
        progress.update(task, description="Building v2 package...")

    output_path = Path(output) if output else package_path.parent / f"{package_path.name}-v2"
    output_path.mkdir(parents=True, exist_ok=True)

    package_name = name or v1_manifest.name

    v2_manifest = PackageManifestV2(
        format_version="2.0",
        name=package_name,
        version=v1_manifest.version,
        description=v1_manifest.description or f"Upgraded from v1: {v1_manifest.name}",
        practices=result.practices,
        mcp_servers=result.mcp_servers,
    )

    if not result.ai_powered:
        _copy_source_files(package_path, output_path, list(instruction_files.keys()))
        from devsync.core.package_manifest_v2 import ComponentRef

        v2_manifest.components = {
            "instructions": [
                ComponentRef(name=Path(f).stem, file=f"instructions/{Path(f).name}") for f in instruction_files
            ]
        }

    manifest_path = output_path / "devsync-package.yaml"
    manifest_path.write_text(v2_manifest.to_yaml())

    mode = "[green]AI-powered[/green]" if result.ai_powered else "[yellow]file-copy[/yellow]"
    console.print(f"\nUpgraded ({mode}):")
    console.print(f"  Practices: {len(result.practices)}")
    console.print(f"  Source files: {len(instruction_files)}")
    console.print(f"\nv2 package written to: [cyan]{output_path}[/cyan]")
    return 0


def _copy_source_files(project_path: Path, output_path: Path, source_files: list[str]) -> None:
    """Copy source instruction files to the output package directory."""
    instructions_dir = output_path / "instructions"
    instructions_dir.mkdir(parents=True, exist_ok=True)
    for rel_path in source_files:
        src = project_path / rel_path
        if src.exists():
            dest = instructions_dir / Path(rel_path).name
            shutil.copy2(str(src), str(dest))
