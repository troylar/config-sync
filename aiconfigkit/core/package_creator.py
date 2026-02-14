"""Package creator for generating shareable configuration packages."""

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from aiconfigkit.core.component_detector import ComponentDetector, DetectedMCPServer, DetectionResult
from aiconfigkit.core.models import (
    CommandComponent,
    CredentialDescriptor,
    HookComponent,
    InstructionComponent,
    MCPServerComponent,
    MemoryFileComponent,
    PackageComponents,
    ResourceComponent,
    SkillComponent,
    WorkflowComponent,
)
from aiconfigkit.core.secret_detector import SecretDetector, template_secrets_in_config

logger = logging.getLogger(__name__)


@dataclass
class PackageMetadata:
    """Metadata for the package being created.

    Attributes:
        name: Package identifier (lowercase, hyphenated)
        version: Semantic version string
        description: Human-readable description
        author: Package author name
        license: License identifier (e.g., MIT, Apache-2.0)
        namespace: Repository namespace (e.g., owner/repo)
    """

    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    license: str = "MIT"
    namespace: str = "local/local"


@dataclass
class PackageCreationResult:
    """Result of package creation operation.

    Attributes:
        success: Whether package was created successfully
        package_path: Path to created package directory
        manifest_path: Path to generated manifest file
        components_included: Number of components in package
        secrets_templated: Number of secrets that were templated
        warnings: Non-fatal issues encountered
        error_message: Error description if failed
    """

    success: bool
    package_path: Optional[Path] = None
    manifest_path: Optional[Path] = None
    components_included: int = 0
    secrets_templated: int = 0
    warnings: list[str] = field(default_factory=list)
    error_message: Optional[str] = None


class PackageCreator:
    """Creates shareable configuration packages from project components.

    The creator scans a project for configuration components (instructions,
    MCP servers, hooks, commands, resources), templates secrets, and generates
    a package directory with manifest.
    """

    def __init__(
        self,
        project_root: Path,
        output_dir: Path,
        metadata: PackageMetadata,
        scrub_secrets: bool = True,
    ):
        """Initialize package creator.

        Args:
            project_root: Path to source project
            output_dir: Directory where package will be created
            metadata: Package metadata
            scrub_secrets: Whether to template secrets in MCP configs
        """
        self.project_root = project_root.resolve()
        self.output_dir = output_dir.resolve()
        self.metadata = metadata
        self.scrub_secrets = scrub_secrets
        self.secret_detector = SecretDetector()
        self.component_detector = ComponentDetector(self.project_root)

    def create(
        self,
        selected_components: Optional[PackageComponents] = None,
        detection_result: Optional[DetectionResult] = None,
    ) -> PackageCreationResult:
        """Create package from project components.

        Args:
            selected_components: Specific components to include (None = detect all)
            detection_result: Pre-scanned detection result (None = scan now)

        Returns:
            PackageCreationResult with operation outcome
        """
        warnings: list[str] = []
        secrets_templated = 0

        try:
            if detection_result is None:
                detection_result = self.component_detector.detect_all()

            if selected_components is None:
                selected_components = self.component_detector.to_package_components(detection_result)

            if selected_components.total_count == 0:
                return PackageCreationResult(
                    success=False,
                    error_message="No components to package",
                    warnings=warnings,
                )

            package_dir = self.output_dir / f"package-{self.metadata.name}"

            if package_dir.exists():
                return PackageCreationResult(
                    success=False,
                    error_message=f"Package directory already exists: {package_dir}",
                    warnings=warnings,
                )

            package_dir.mkdir(parents=True)

            sub_dirs = ["instructions", "mcp", "hooks", "commands", "skills", "workflows", "memory_files", "resources"]
            for sub_dir in sub_dirs:
                (package_dir / sub_dir).mkdir(exist_ok=True)

            copy_warnings = self._copy_component_files(detection_result, selected_components, package_dir)
            warnings.extend(copy_warnings)

            mcp_warnings, mcp_secrets = self._process_mcp_servers(detection_result.mcp_servers, package_dir)
            warnings.extend(mcp_warnings)
            secrets_templated = mcp_secrets

            final_components = self._update_component_paths(selected_components, detection_result)

            manifest = self._generate_manifest(final_components)
            manifest_path = package_dir / "ai-config-kit-package.yaml"
            with open(manifest_path, "w", encoding="utf-8") as f:
                yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

            readme_content = self._generate_readme(final_components)
            readme_path = package_dir / "README.md"
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)

            return PackageCreationResult(
                success=True,
                package_path=package_dir,
                manifest_path=manifest_path,
                components_included=final_components.total_count,
                secrets_templated=secrets_templated,
                warnings=warnings,
            )

        except Exception as e:
            logger.exception(f"Package creation failed: {e}")
            return PackageCreationResult(
                success=False,
                error_message=str(e),
                warnings=warnings,
            )

    def _copy_component_files(
        self,
        detection_result: DetectionResult,
        components: PackageComponents,
        package_dir: Path,
    ) -> list[str]:
        """Copy component files to package directory.

        Args:
            detection_result: Scan results with file paths
            components: Selected components
            package_dir: Destination package directory

        Returns:
            List of warning messages
        """
        warnings: list[str] = []

        instruction_names = {inst.name for inst in components.instructions}
        for inst in detection_result.instructions:
            if inst.name not in instruction_names:
                continue

            src_path = inst.file_path
            dest_path = package_dir / "instructions" / f"{inst.name}.md"

            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                warnings.append(f"Failed to copy instruction {inst.name}: {e}")

        hook_names = {h.name for h in components.hooks}
        for hook in detection_result.hooks:
            if hook.name not in hook_names:
                continue

            src_path = hook.file_path
            dest_path = package_dir / "hooks" / src_path.name

            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                warnings.append(f"Failed to copy hook {hook.name}: {e}")

        cmd_names = {c.name for c in components.commands}
        for cmd in detection_result.commands:
            if cmd.name not in cmd_names:
                continue

            src_path = cmd.file_path
            dest_path = package_dir / "commands" / src_path.name

            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                warnings.append(f"Failed to copy command {cmd.name}: {e}")

        resource_names = {r.name for r in components.resources}
        for res in detection_result.resources:
            if res.name not in resource_names:
                continue

            src_path = res.file_path
            dest_path = package_dir / "resources" / src_path.name

            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                warnings.append(f"Failed to copy resource {res.name}: {e}")

        # Copy skills (directories)
        skill_names = {s.name for s in components.skills}
        for skill in detection_result.skills:
            if skill.name not in skill_names:
                continue

            src_path = skill.dir_path
            dest_path = package_dir / "skills" / skill.name

            try:
                shutil.copytree(src_path, dest_path)
            except Exception as e:
                warnings.append(f"Failed to copy skill {skill.name}: {e}")

        # Copy workflows
        workflow_names = {w.name for w in components.workflows}
        for wf in detection_result.workflows:
            if wf.name not in workflow_names:
                continue

            src_path = wf.file_path
            dest_path = package_dir / "workflows" / src_path.name

            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                warnings.append(f"Failed to copy workflow {wf.name}: {e}")

        # Copy memory files
        memory_file_names = {m.name for m in components.memory_files}
        for mem in detection_result.memory_files:
            if mem.name not in memory_file_names:
                continue

            src_path = mem.file_path
            # Use relative path for subdirectory memory files
            if mem.is_root:
                dest_path = package_dir / "memory_files" / "CLAUDE.md"
            else:
                # Preserve directory structure for subdirectory memory files
                dest_path = package_dir / "memory_files" / mem.relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                warnings.append(f"Failed to copy memory file {mem.name}: {e}")

        return warnings

    def _process_mcp_servers(
        self,
        detected_servers: list[DetectedMCPServer],
        package_dir: Path,
    ) -> tuple[list[str], int]:
        """Process MCP server configurations and template secrets.

        Args:
            detected_servers: Detected MCP server configs
            package_dir: Destination package directory

        Returns:
            Tuple of (warnings, count of templated secrets)
        """
        warnings: list[str] = []
        total_secrets = 0

        for server in detected_servers:
            try:
                if self.scrub_secrets:
                    templated_config, templated_keys = template_secrets_in_config(server.config, self.secret_detector)
                    total_secrets += len(templated_keys)
                else:
                    templated_config = server.config

                dest_path = package_dir / "mcp" / f"{server.name}.json"
                with open(dest_path, "w", encoding="utf-8") as f:
                    json.dump(templated_config, f, indent=2)

            except Exception as e:
                warnings.append(f"Failed to process MCP server {server.name}: {e}")

        return warnings, total_secrets

    def _update_component_paths(
        self,
        components: PackageComponents,
        detection_result: DetectionResult,
    ) -> PackageComponents:
        """Update component file paths to package-relative paths.

        Args:
            components: Original components with project paths
            detection_result: Detection results for reference

        Returns:
            Updated PackageComponents with package-relative paths
        """
        updated_instructions = []
        for inst in components.instructions:
            updated_instructions.append(
                InstructionComponent(
                    name=inst.name,
                    file=f"instructions/{inst.name}.md",
                    description=inst.description,
                    tags=inst.tags,
                    ide_support=inst.ide_support,
                )
            )

        updated_mcp = []
        mcp_map = {m.name: m for m in detection_result.mcp_servers}
        for mcp in components.mcp_servers:
            detected = mcp_map.get(mcp.name)
            credentials: list[CredentialDescriptor] = []
            if detected and self.scrub_secrets:
                for env_var in detected.env_vars:
                    detection = self.secret_detector.detect("placeholder", env_var)
                    if detection.confidence.value in ("high", "medium"):
                        credentials.append(
                            CredentialDescriptor(
                                name=env_var,
                                description=f"Environment variable for {mcp.name}",
                                required=True,
                            )
                        )

            updated_mcp.append(
                MCPServerComponent(
                    name=mcp.name,
                    file=f"mcp/{mcp.name}.json",
                    description=mcp.description,
                    credentials=credentials,
                    ide_support=mcp.ide_support,
                )
            )

        updated_hooks = []
        hook_map = {h.name: h for h in detection_result.hooks}
        for hook in components.hooks:
            detected_hook = hook_map.get(hook.name)
            hook_file_name = detected_hook.file_path.name if detected_hook else f"{hook.name}.sh"
            updated_hooks.append(
                HookComponent(
                    name=hook.name,
                    file=f"hooks/{hook_file_name}",
                    description=hook.description,
                    hook_type=hook.hook_type,
                    ide_support=hook.ide_support,
                )
            )

        updated_commands = []
        cmd_map = {c.name: c for c in detection_result.commands}
        for cmd in components.commands:
            detected_cmd = cmd_map.get(cmd.name)
            cmd_file_name = detected_cmd.file_path.name if detected_cmd else f"{cmd.name}.sh"
            updated_commands.append(
                CommandComponent(
                    name=cmd.name,
                    file=f"commands/{cmd_file_name}",
                    description=cmd.description,
                    command_type=cmd.command_type,
                    ide_support=cmd.ide_support,
                )
            )

        updated_resources = []
        res_map = {r.name: r for r in detection_result.resources}
        for res in components.resources:
            detected_res = res_map.get(res.name)
            res_file_name = detected_res.file_path.name if detected_res else res.name
            res_checksum = detected_res.checksum if detected_res else res.checksum
            res_size = detected_res.size if detected_res else res.size
            updated_resources.append(
                ResourceComponent(
                    name=res.name,
                    file=f"resources/{res_file_name}",
                    description=res.description,
                    install_path=f"resources/{res_file_name}",
                    checksum=f"sha256:{res_checksum}" if not res_checksum.startswith("sha256:") else res_checksum,
                    size=res_size,
                )
            )

        updated_skills = []
        skill_map = {s.name: s for s in detection_result.skills}
        for skill in components.skills:
            detected_skill = skill_map.get(skill.name)
            updated_skills.append(
                SkillComponent(
                    name=skill.name,
                    file=f"skills/{skill.name}",
                    description=detected_skill.description if detected_skill else skill.description,
                    ide_support=skill.ide_support,
                )
            )

        updated_workflows = []
        workflow_map = {w.name: w for w in detection_result.workflows}
        for wf in components.workflows:
            detected_wf = workflow_map.get(wf.name)
            wf_file_name = detected_wf.file_path.name if detected_wf else f"{wf.name}.md"
            updated_workflows.append(
                WorkflowComponent(
                    name=wf.name,
                    file=f"workflows/{wf_file_name}",
                    description=detected_wf.description if detected_wf else wf.description,
                    ide_support=wf.ide_support,
                )
            )

        updated_memory_files = []
        memory_map = {m.name: m for m in detection_result.memory_files}
        for mem in components.memory_files:
            detected_mem = memory_map.get(mem.name)
            if detected_mem:
                if detected_mem.is_root:
                    mem_file = "memory_files/CLAUDE.md"
                else:
                    mem_file = f"memory_files/{detected_mem.relative_path}"
            else:
                mem_file = f"memory_files/{mem.name}.md"
            updated_memory_files.append(
                MemoryFileComponent(
                    name=mem.name,
                    file=mem_file,
                    description=mem.description,
                    ide_support=mem.ide_support,
                )
            )

        return PackageComponents(
            instructions=updated_instructions,
            mcp_servers=updated_mcp,
            hooks=updated_hooks,
            commands=updated_commands,
            skills=updated_skills,
            workflows=updated_workflows,
            memory_files=updated_memory_files,
            resources=updated_resources,
        )

    def _generate_manifest(self, components: PackageComponents) -> dict:
        """Generate YAML manifest dictionary.

        Args:
            components: Package components

        Returns:
            Manifest dictionary for YAML serialization
        """
        manifest: dict = {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "author": self.metadata.author,
            "license": self.metadata.license,
            "namespace": self.metadata.namespace,
            "created_at": datetime.now().isoformat(),
            "components": {},
        }

        if components.instructions:
            manifest["components"]["instructions"] = [
                {
                    "name": inst.name,
                    "file": inst.file,
                    "description": inst.description,
                    "tags": inst.tags,
                }
                for inst in components.instructions
            ]

        if components.mcp_servers:
            manifest["components"]["mcp_servers"] = [
                {
                    "name": mcp.name,
                    "file": mcp.file,
                    "description": mcp.description,
                    "credentials": [
                        {
                            "name": cred.name,
                            "description": cred.description,
                            "required": cred.required,
                        }
                        for cred in mcp.credentials
                    ],
                    "ide_support": mcp.ide_support,
                }
                for mcp in components.mcp_servers
            ]

        if components.hooks:
            manifest["components"]["hooks"] = [
                {
                    "name": hook.name,
                    "file": hook.file,
                    "description": hook.description,
                    "hook_type": hook.hook_type,
                    "ide_support": hook.ide_support,
                }
                for hook in components.hooks
            ]

        if components.commands:
            manifest["components"]["commands"] = [
                {
                    "name": cmd.name,
                    "file": cmd.file,
                    "description": cmd.description,
                    "command_type": cmd.command_type,
                    "ide_support": cmd.ide_support,
                }
                for cmd in components.commands
            ]

        if components.resources:
            manifest["components"]["resources"] = [
                {
                    "name": res.name,
                    "file": res.file,
                    "description": res.description,
                    "install_path": res.install_path,
                    "checksum": res.checksum,
                    "size": res.size,
                }
                for res in components.resources
            ]

        if components.skills:
            manifest["components"]["skills"] = [
                {
                    "name": skill.name,
                    "file": skill.file,
                    "description": skill.description,
                    "ide_support": skill.ide_support,
                }
                for skill in components.skills
            ]

        if components.workflows:
            manifest["components"]["workflows"] = [
                {
                    "name": wf.name,
                    "file": wf.file,
                    "description": wf.description,
                    "ide_support": wf.ide_support,
                }
                for wf in components.workflows
            ]

        if components.memory_files:
            manifest["components"]["memory_files"] = [
                {
                    "name": mem.name,
                    "file": mem.file,
                    "description": mem.description,
                    "ide_support": mem.ide_support,
                }
                for mem in components.memory_files
            ]

        return manifest

    def _generate_readme(self, components: PackageComponents) -> str:
        """Generate README.md content for the package.

        Args:
            components: Package components

        Returns:
            README content string
        """
        lines = [
            f"# {self.metadata.name}",
            "",
            self.metadata.description or "Configuration package created with Config Sync.",
            "",
            "## Installation",
            "",
            "```bash",
            f"aiconfig package install ./package-{self.metadata.name} --ide claude",
            "```",
            "",
            "## Components",
            "",
        ]

        if components.instructions:
            lines.append("### Instructions")
            lines.append("")
            for inst in components.instructions:
                lines.append(f"- **{inst.name}**: {inst.description}")
            lines.append("")

        if components.mcp_servers:
            lines.append("### MCP Servers")
            lines.append("")
            for mcp in components.mcp_servers:
                lines.append(f"- **{mcp.name}**: {mcp.description}")
                if mcp.credentials:
                    lines.append("  - Required credentials:")
                    for cred in mcp.credentials:
                        lines.append(f"    - `{cred.name}`: {cred.description}")
            lines.append("")

        if components.hooks:
            lines.append("### Hooks")
            lines.append("")
            for hook in components.hooks:
                lines.append(f"- **{hook.name}** ({hook.hook_type}): {hook.description}")
            lines.append("")

        if components.commands:
            lines.append("### Commands")
            lines.append("")
            for cmd in components.commands:
                lines.append(f"- **{cmd.name}** ({cmd.command_type}): {cmd.description}")
            lines.append("")

        if components.resources:
            lines.append("### Resources")
            lines.append("")
            for res in components.resources:
                lines.append(f"- **{res.name}**: {res.description}")
            lines.append("")

        if components.skills:
            lines.append("### Skills")
            lines.append("")
            for skill in components.skills:
                lines.append(f"- **{skill.name}**: {skill.description}")
            lines.append("")

        if components.workflows:
            lines.append("### Workflows")
            lines.append("")
            for wf in components.workflows:
                lines.append(f"- **{wf.name}**: {wf.description}")
            lines.append("")

        if components.memory_files:
            lines.append("### Memory Files")
            lines.append("")
            for mem in components.memory_files:
                lines.append(f"- **{mem.name}**: {mem.description}")
            lines.append("")

        lines.extend(
            [
                "## Author",
                "",
                self.metadata.author or "Unknown",
                "",
                "## License",
                "",
                self.metadata.license,
                "",
                "---",
                "",
                f"*Generated with Config Sync on {datetime.now().strftime('%Y-%m-%d')}*",
            ]
        )

        return "\n".join(lines)


def get_git_author() -> Optional[str]:
    """Get the current git user name.

    Returns:
        Git user name or None if not configured
    """
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None
