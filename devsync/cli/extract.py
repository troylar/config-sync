"""Extract command — reads project configs and produces a shareable package."""

import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from devsync.core.extractor import PracticeExtractor
from devsync.core.package_manifest_v2 import PackageManifestV2
from devsync.llm.config import load_config
from devsync.llm.provider import resolve_provider

console = Console()


def extract_command(
    output: Optional[str] = None,
    name: Optional[str] = None,
    no_ai: bool = False,
    project_dir: Optional[str] = None,
) -> int:
    """Extract practices from the current project into a shareable package.

    Args:
        output: Output directory for the package. Defaults to './devsync-package/'.
        name: Package name. Defaults to project directory name.
        no_ai: Force file-copy mode (no LLM calls).
        project_dir: Project directory to extract from. Defaults to cwd.

    Returns:
        Exit code (0 = success).
    """
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


def _copy_source_files(project_path: Path, output_path: Path, source_files: list[str]) -> None:
    """Copy source instruction files to the output package directory."""
    instructions_dir = output_path / "instructions"
    instructions_dir.mkdir(parents=True, exist_ok=True)
    for rel_path in source_files:
        src = project_path / rel_path
        if src.exists():
            dest = instructions_dir / Path(rel_path).name
            shutil.copy2(str(src), str(dest))
