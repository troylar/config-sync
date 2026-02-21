"""Extract command — reads project configs and produces a shareable package."""

import shutil
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from devsync.core.extractor import PracticeExtractor
from devsync.core.package_manifest_v2 import PackageManifestV2, detect_manifest_format, parse_manifest
from devsync.llm.config import load_config
from devsync.llm.provider import resolve_provider

console = Console()


def extract_command(
    output: Optional[str] = None,
    name: Optional[str] = None,
    no_ai: bool = False,
    project_dir: Optional[str] = None,
    upgrade: Optional[str] = None,
) -> int:
    """Extract practices from the current project into a shareable package.

    Args:
        output: Output directory for the package. Defaults to './devsync-package/'.
        name: Package name. Defaults to project directory name.
        no_ai: Force file-copy mode (no LLM calls).
        project_dir: Project directory to extract from. Defaults to cwd.
        upgrade: Path to a v1 package to convert to v2 format.

    Returns:
        Exit code (0 = success).
    """
    if upgrade:
        return _upgrade_v1_package(upgrade, output=output, name=name, no_ai=no_ai)

    project_path = Path(project_dir) if project_dir else Path.cwd()
    if not project_path.is_dir():
        console.print(f"[red]Not a directory: {project_path}[/red]")
        return 1

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
        task = progress.add_task("Scanning project...", total=None)
        result = extractor.extract(project_path)
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

    mode = "[green]AI-powered[/green]" if result.ai_powered else "[yellow]file-copy[/yellow]"
    console.print(f"\nExtracted ({mode}):")
    console.print(f"  Practices: {len(result.practices)}")
    console.print(f"  MCP servers: {len(result.mcp_servers)}")
    console.print(f"  Source files: {len(result.source_files)}")
    console.print(f"\nPackage written to: [cyan]{output_path}[/cyan]")
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
            src_file = package_path / ref.file
            if src_file.exists() and src_file.stat().st_size < 100_000:
                try:
                    content = src_file.read_text(encoding="utf-8")
                    instruction_files[ref.file] = content
                except (OSError, UnicodeDecodeError):
                    console.print(f"  [yellow]Could not read: {ref.file}[/yellow]")

    if not instruction_files:
        console.print("[yellow]No instruction files found in v1 package.[/yellow]")
        return 0

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
