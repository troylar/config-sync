"""V2 install command — AI-powered package installation."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from devsync.core.practice import MCPDeclaration

from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from devsync.core.adapter import PracticeAdapter
from devsync.core.mcp_credential_prompter import build_mcp_config, prompt_mcp_credentials
from devsync.core.package_manifest_v2 import PackageManifestV2, detect_manifest_format, parse_manifest
from devsync.llm.config import load_config
from devsync.llm.provider import resolve_provider
from devsync.llm.response_models import AdaptationPlan
from devsync.utils.project import find_project_root

console = Console()


def install_v2_command(
    source: str,
    tool: Optional[list[str]] = None,
    no_ai: bool = False,
    conflict: str = "prompt",
    project_dir: Optional[str] = None,
    skip_pip: bool = False,
) -> int:
    """Install a package into the current project.

    Accepts Git URLs, local paths, or package directories.

    Args:
        source: Package source (Git URL, local path, or directory).
        tool: Target AI tool(s). Auto-detects if not specified.
        no_ai: Disable AI-powered adaptation.
        conflict: Conflict strategy ('prompt', 'skip', 'overwrite', 'rename').
        project_dir: Target project directory. Defaults to cwd.
        skip_pip: Skip pip package installations for MCP servers.

    Returns:
        Exit code (0 = success).
    """
    project_path = Path(project_dir) if project_dir else Path.cwd()
    project_root = find_project_root(project_path)
    if not project_root:
        project_root = project_path

    cloned_tmp: Path | None = None
    package_path = _resolve_source(source)
    if not package_path:
        console.print(f"[red]Could not resolve source: {source}[/red]")
        return 1

    # Track if we cloned a temp directory so we can clean it up
    if source.startswith(("http://", "https://", "git@", "github.com")):
        cloned_tmp = package_path

    try:
        fmt = detect_manifest_format(package_path)
        if not fmt:
            console.print(f"[red]No manifest found in {package_path}[/red]")
            console.print("Expected: devsync-package.yaml or ai-config-kit-package.yaml")
            return 1

        manifest = parse_manifest(package_path)
        target_tools = _resolve_tools(tool)

        console.print(f"\n[bold]Installing: {manifest.name} v{manifest.version}[/bold]")
        console.print(f"  {manifest.description}")
        console.print(f"  Format: {'v2 (AI-native)' if manifest.is_v2 else 'v1 (file-copy)'}")
        console.print(f"  Tools: {', '.join(target_tools)}")

        if manifest.is_v2 and manifest.has_practices and not no_ai:
            return _install_v2_ai(manifest, project_root, target_tools, skip_pip=skip_pip)
        return _install_v2_fallback(manifest, package_path, project_root, target_tools, conflict, skip_pip=skip_pip)
    finally:
        if cloned_tmp and cloned_tmp.exists():
            shutil.rmtree(cloned_tmp, ignore_errors=True)


def _resolve_source(source: str) -> Optional[Path]:
    """Resolve a source string to a local package directory."""
    source_path = Path(source).expanduser()
    if source_path.is_dir():
        return source_path

    if source.startswith(("http://", "https://", "git@", "github.com")):
        return _clone_source(source)

    if source_path.exists():
        return source_path

    return None


def _clone_source(url: str) -> Optional[Path]:
    """Clone a Git repository to a temp directory."""
    try:
        from devsync.core.git_operations import GitOperations

        tmp_dir = Path(tempfile.mkdtemp(prefix="devsync-"))
        GitOperations.clone_repository(url, tmp_dir)
        return tmp_dir
    except Exception as e:
        console.print(f"[red]Failed to clone {url}: {e}[/red]")
        return None


def _resolve_tools(tool_names: Optional[list[str]]) -> list[str]:
    """Resolve target tools (auto-detect if not specified)."""
    if tool_names:
        return tool_names

    from devsync.ai_tools.detector import get_detector

    detected = get_detector().detect_installed_tools()
    if detected:
        return [t.tool_type.value for t in detected]

    return ["claude"]


def _install_v2_ai(
    manifest: PackageManifestV2,
    project_root: Path,
    target_tools: list[str],
    skip_pip: bool = False,
) -> int:
    """Install using AI-powered adaptation."""
    config = load_config()
    llm = resolve_provider(preferred_provider=config.provider, preferred_model=config.model)

    adapter = PracticeAdapter(llm_provider=llm)
    plan = adapter.adapt(manifest.practices, project_root, target_tools)

    _display_plan(plan)

    if not Confirm.ask("\nProceed with installation?", default=True):
        console.print("[yellow]Installation cancelled.[/yellow]")
        return 0

    _execute_plan(plan, project_root, target_tools)

    if manifest.mcp_servers:
        _install_mcp_servers(manifest, project_root, skip_pip=skip_pip)

    console.print(f"\n[green]Installed {manifest.name} successfully.[/green]")
    return 0


def _install_v2_fallback(
    manifest: PackageManifestV2,
    package_path: Path,
    project_root: Path,
    target_tools: list[str],
    conflict: str,
    skip_pip: bool = False,
) -> int:
    """Install using file-copy mode (v1 compat or --no-ai)."""
    installed_count = 0

    for component_type, refs in manifest.components.items():
        if component_type != "instructions":
            continue
        for ref in refs:
            src_file = (package_path / ref.file).resolve()
            try:
                src_file.relative_to(package_path.resolve())
            except ValueError:
                console.print(f"  [red]Rejected (path traversal): {ref.file}[/red]")
                continue
            if not src_file.exists():
                console.print(f"  [yellow]Missing: {ref.file}[/yellow]")
                continue

            content = src_file.read_text(encoding="utf-8")
            for tool_name in target_tools:
                dest = _get_tool_instruction_path(tool_name, project_root, ref.name)
                if not dest:
                    continue
                if dest.exists():
                    if conflict == "skip":
                        console.print(f"  [dim]Skipped (exists): {ref.name} → {dest.relative_to(project_root)}[/dim]")
                        continue
                    elif conflict == "overwrite":
                        dest.write_text(content, encoding="utf-8")
                        installed_count += 1
                        console.print(f"  Overwritten: {ref.name} → {dest.relative_to(project_root)}")
                    elif conflict == "rename":
                        suffix = 1
                        renamed = dest.with_stem(f"{dest.stem}-{suffix}")
                        while renamed.exists():
                            suffix += 1
                            renamed = dest.with_stem(f"{dest.stem}-{suffix}")
                        renamed.parent.mkdir(parents=True, exist_ok=True)
                        renamed.write_text(content, encoding="utf-8")
                        installed_count += 1
                        console.print(f"  Installed (renamed): {ref.name} → {renamed.relative_to(project_root)}")
                    else:
                        rel = dest.relative_to(project_root)
                        console.print(f"  [yellow]Exists: {ref.name} → {rel} (skipped)[/yellow]")
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(content, encoding="utf-8")
                    installed_count += 1
                    console.print(f"  Installed: {ref.name} → {dest.relative_to(project_root)}")

    if manifest.mcp_servers:
        _install_mcp_servers(manifest, project_root, skip_pip=skip_pip)

    console.print(f"\n[green]Installed {installed_count} instructions.[/green]")
    return 0


def _display_plan(plan: AdaptationPlan) -> None:
    """Display the adaptation plan for user review."""
    table = Table(title="Adaptation Plan")
    table.add_column("Practice", style="cyan")
    table.add_column("Action", style="bold")
    table.add_column("Reason")

    for action in plan.actions:
        style = {"install": "green", "merge": "yellow", "skip": "dim"}.get(action.action, "")
        table.add_row(action.practice_name, f"[{style}]{action.action}[/{style}]", action.reason)

    console.print(table)
    console.print(f"\n  Install: {len(plan.installs)} | Merge: {len(plan.merges)} | Skip: {len(plan.skips)}")


def _execute_plan(plan: AdaptationPlan, project_root: Path, target_tools: list[str]) -> None:
    """Execute the adaptation plan — write files to tool-specific directories."""
    for action in plan.actions:
        if action.action == "skip":
            continue
        for tool_name in target_tools:
            dest = _get_tool_instruction_path(tool_name, project_root, action.practice_name)
            if dest:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(action.content, encoding="utf-8")
                console.print(f"  Installed: {action.practice_name} → {dest.relative_to(project_root)}")


def _get_tool_instruction_path(tool_name: str, project_root: Path, instruction_name: str) -> Optional[Path]:
    """Get the file path for an instruction in a specific tool."""
    if ".." in instruction_name or "/" in instruction_name or "\\" in instruction_name:
        return None
    tool_paths: dict[str, tuple[str, str]] = {
        "claude": (".claude/rules", ".md"),
        "cursor": (".cursor/rules", ".mdc"),
        "windsurf": (".windsurf/rules", ".md"),
        "copilot": (".github/instructions", ".md"),
        "kiro": (".kiro/steering", ".md"),
        "cline": (".clinerules", ".md"),
        "roo": (".roo/rules", ".md"),
    }
    if tool_name not in tool_paths:
        return None
    dir_name, ext = tool_paths[tool_name]
    return project_root / dir_name / f"{instruction_name}{ext}"


def _install_mcp_servers(
    manifest: PackageManifestV2,
    project_root: Path,
    skip_pip: bool = False,
) -> None:
    """Install MCP server configurations with pip dependencies and credential prompting."""
    failed_pip_servers = _install_pip_dependencies(manifest.mcp_servers, skip_pip=skip_pip)

    # Skip credential prompting for servers whose pip deps failed
    eligible_servers = [s for s in manifest.mcp_servers if s.name not in failed_pip_servers]
    servers_with_creds = [s for s in eligible_servers if s.credentials]
    if servers_with_creds:
        env_path = project_root / ".devsync" / ".env"
        credentials = prompt_mcp_credentials(servers_with_creds, env_path=env_path)

        for server in eligible_servers:
            server_creds = credentials.get(server.name, {})
            build_mcp_config(server, server_creds)
            console.print(f"  MCP: {server.name} configured")
    else:
        for server in eligible_servers:
            console.print(f"  MCP: {server.name} (no credentials needed)")


def _install_pip_dependencies(
    mcp_servers: list[MCPDeclaration],
    skip_pip: bool = False,
) -> set[str]:
    """Install pip package dependencies for MCP servers.

    Args:
        mcp_servers: List of MCPDeclaration objects.
        skip_pip: If True, skip all pip installations.

    Returns:
        Set of server names whose pip dependency installation failed or was declined.
    """
    from devsync.core.pip_utils import (
        get_installed_version,
        install_pip_package,
        installed_version_satisfies,
        validate_pip_spec,
    )

    failed_servers: set[str] = set()
    servers_with_pip = [s for s in mcp_servers if s.pip_package]
    if not servers_with_pip:
        return failed_servers

    console.print("\n[bold]MCP Server Dependencies[/bold]")

    if skip_pip:
        console.print("  [yellow]Skipping pip installations (--skip-pip)[/yellow]")
        for server in servers_with_pip:
            console.print(f"  [dim]{server.name}: {server.pip_package} (skipped)[/dim]")
        return failed_servers

    for server in servers_with_pip:
        spec = server.pip_package
        assert spec is not None  # guarded by servers_with_pip filter

        if not validate_pip_spec(spec):
            console.print(f"  [red]Invalid package spec for {server.name}: {spec}[/red]")
            failed_servers.add(server.name)
            continue

        if installed_version_satisfies(spec):
            installed_ver = get_installed_version(spec)
            console.print(f"  [dim]{server.name}: {spec} already installed (v{installed_ver})[/dim]")
            continue

        console.print(f"  [cyan]{server.name} requires pip package: {spec}[/cyan]")
        if server.description:
            console.print(f"  [dim]{server.description}[/dim]")

        if not Confirm.ask(f"  Install {spec}?", default=True):
            console.print(f"  [yellow]Skipped pip install for {server.name}[/yellow]")
            failed_servers.add(server.name)
            continue

        with console.status(f"  Installing {spec}..."):
            success, message = install_pip_package(spec)

        if success:
            console.print(f"  [green]{message}[/green]")
        else:
            console.print(f"  [red]{message}[/red]")
            console.print(f"  [yellow]MCP server {server.name} may not work without {spec}[/yellow]")
            failed_servers.add(server.name)

    return failed_servers
