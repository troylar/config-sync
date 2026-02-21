"""V2 package manifest parser with backwards compatibility."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from devsync.core.practice import CredentialSpec, MCPDeclaration, PracticeDeclaration

logger = logging.getLogger(__name__)

V2_MANIFEST_FILE = "devsync-package.yaml"
V1_MANIFEST_FILE = "ai-config-kit-package.yaml"


@dataclass
class ComponentRef:
    """Reference to a file-based component (v1 compatibility).

    Attributes:
        name: Component identifier.
        file: Relative file path within the package.
        description: Human-readable description.
        tags: Categorization tags.
        hook_type: For hooks, the type (pre-commit, etc.).
        command_type: For commands, the type (shell, etc.).
    """

    name: str
    file: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    hook_type: Optional[str] = None
    command_type: Optional[str] = None

    def to_dict(self) -> dict:
        result: dict = {"name": self.name, "file": self.file}
        if self.description:
            result["description"] = self.description
        if self.tags:
            result["tags"] = self.tags
        if self.hook_type:
            result["hook_type"] = self.hook_type
        if self.command_type:
            result["command_type"] = self.command_type
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ComponentRef":
        return cls(
            name=data["name"],
            file=data["file"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
            hook_type=data.get("hook_type"),
            command_type=data.get("command_type"),
        )


@dataclass
class PackageManifestV2:
    """Unified package manifest supporting both v1 and v2 formats.

    Attributes:
        format_version: '1.0' for v1, '2.0' for v2.
        name: Package name.
        version: Package version.
        description: Package description.
        author: Package author.
        license: License identifier.
        namespace: Source namespace (e.g., 'org/repo').
        practices: AI-extracted practice declarations (v2 only).
        mcp_servers: MCP server declarations.
        components: File-based component references (v1 compatibility).
    """

    format_version: str = "2.0"
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    license: str = ""
    namespace: str = ""
    practices: list[PracticeDeclaration] = field(default_factory=list)
    mcp_servers: list[MCPDeclaration] = field(default_factory=list)
    components: dict[str, list[ComponentRef]] = field(default_factory=dict)

    @property
    def is_v2(self) -> bool:
        return self.format_version.startswith("2")

    @property
    def has_practices(self) -> bool:
        return len(self.practices) > 0

    @property
    def has_components(self) -> bool:
        return any(len(refs) > 0 for refs in self.components.values())

    def to_dict(self) -> dict:
        result: dict = {
            "format_version": self.format_version,
            "name": self.name,
            "version": self.version,
            "description": self.description,
        }
        if self.author:
            result["author"] = self.author
        if self.license:
            result["license"] = self.license
        if self.namespace:
            result["namespace"] = self.namespace
        if self.practices:
            result["practices"] = [p.to_dict() for p in self.practices]
        if self.mcp_servers:
            result["mcp_servers"] = [m.to_dict() for m in self.mcp_servers]
        if self.has_components:
            result["components"] = {key: [c.to_dict() for c in refs] for key, refs in self.components.items() if refs}
        return result

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)


def detect_manifest_format(package_path: Path) -> Optional[str]:
    """Detect whether a package uses v1 or v2 manifest format.

    Args:
        package_path: Root directory of the package.

    Returns:
        'v2' if devsync-package.yaml exists, 'v1' if ai-config-kit-package.yaml exists,
        None if neither found.
    """
    if (package_path / V2_MANIFEST_FILE).exists():
        return "v2"
    if (package_path / V1_MANIFEST_FILE).exists():
        return "v1"
    return None


def parse_manifest(package_path: Path) -> PackageManifestV2:
    """Parse a package manifest (auto-detects v1 vs v2).

    Args:
        package_path: Root directory of the package.

    Returns:
        PackageManifestV2 with parsed content.

    Raises:
        FileNotFoundError: If no manifest file found.
        ValueError: If manifest is malformed.
    """
    fmt = detect_manifest_format(package_path)
    if fmt == "v2":
        return _parse_v2(package_path / V2_MANIFEST_FILE)
    if fmt == "v1":
        return _parse_v1(package_path / V1_MANIFEST_FILE)
    raise FileNotFoundError(f"No manifest found in {package_path} (expected {V2_MANIFEST_FILE} or {V1_MANIFEST_FILE})")


def _parse_v2(manifest_path: Path) -> PackageManifestV2:
    """Parse a v2 devsync-package.yaml manifest."""
    with open(manifest_path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid manifest: expected dict, got {type(data).__name__}")

    practices = [PracticeDeclaration.from_dict(p) for p in data.get("practices", [])]

    mcp_servers = []
    for m in data.get("mcp_servers", []):
        mcp_servers.append(MCPDeclaration.from_dict(m))

    components = _parse_components(data.get("components", {}))

    return PackageManifestV2(
        format_version=str(data.get("format_version", "2.0")),
        name=data.get("name", ""),
        version=str(data.get("version", "1.0.0")),
        description=data.get("description", ""),
        author=data.get("author", ""),
        license=data.get("license", ""),
        namespace=data.get("namespace", ""),
        practices=practices,
        mcp_servers=mcp_servers,
        components=components,
    )


def _parse_v1(manifest_path: Path) -> PackageManifestV2:
    """Parse a v1 ai-config-kit-package.yaml manifest into the v2 structure."""
    with open(manifest_path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid manifest: expected dict, got {type(data).__name__}")

    components = _parse_components(data.get("components", {}))

    mcp_servers = []
    for m in data.get("components", {}).get("mcp_servers", []):
        creds = [CredentialSpec.from_dict(c) for c in m.get("credentials", [])]
        mcp_servers.append(
            MCPDeclaration(
                name=m["name"],
                description=m.get("description", ""),
                command=m.get("command", ""),
                args=m.get("args", []),
                credentials=creds,
            )
        )

    return PackageManifestV2(
        format_version="1.0",
        name=data.get("name", ""),
        version=str(data.get("version", "1.0.0")),
        description=data.get("description", ""),
        author=data.get("author", ""),
        license=data.get("license", ""),
        namespace=data.get("namespace", ""),
        practices=[],
        mcp_servers=mcp_servers,
        components=components,
    )


def _parse_components(components_data: dict) -> dict[str, list[ComponentRef]]:
    """Parse the components section into ComponentRef lists."""
    result: dict[str, list[ComponentRef]] = {}
    for component_type, items in components_data.items():
        if component_type == "mcp_servers":
            continue
        if isinstance(items, list):
            result[component_type] = [ComponentRef.from_dict(item) for item in items]
    return result
