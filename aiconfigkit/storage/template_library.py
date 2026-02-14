"""Template library management for downloaded template repositories."""

from pathlib import Path
from typing import Optional

from aiconfigkit.core.models import TemplateManifest
from aiconfigkit.core.template_manifest import load_manifest
from aiconfigkit.utils.git_helpers import clone_template_repo, get_repo_version
from aiconfigkit.utils.namespace import derive_namespace


class TemplateLibraryManager:
    """Manages template repositories in local library (~/.instructionkit/templates/)."""

    def __init__(self, library_path: Optional[Path] = None):
        """
        Initialize template library manager.

        Args:
            library_path: Custom library path (default: ~/.instructionkit/templates/)
        """
        if library_path is None:
            library_path = Path.home() / ".instructionkit" / "templates"

        self.library_path = library_path
        self.library_path.mkdir(parents=True, exist_ok=True)

    def clone_repository(
        self, repo_url: str, namespace_override: Optional[str] = None
    ) -> tuple[Path, TemplateManifest]:
        """
        Clone template repository to library.

        Args:
            repo_url: Git repository URL
            namespace_override: Optional namespace override

        Returns:
            Tuple of (repository path, parsed manifest)

        Raises:
            TemplateAuthError: If authentication fails
            TemplateNetworkError: If network/repository unavailable
            TemplateManifestError: If manifest is invalid

        Example:
            >>> manager = TemplateLibraryManager()
            >>> repo_path, manifest = manager.clone_repository(
            ...     "https://github.com/acme/templates"
            ... )
            >>> manifest.name
            'ACME Templates'
        """
        # Derive namespace
        namespace = derive_namespace(repo_url, namespace_override)

        # Clone to library
        destination = self.library_path / namespace

        # Remove existing directory if it exists
        if destination.exists():
            import shutil

            shutil.rmtree(destination)

        clone_template_repo(repo_url, destination)

        # Load and validate manifest
        manifest_path = destination / "templatekit.yaml"
        manifest = load_manifest(manifest_path)

        return destination, manifest

    def get_template_repository(self, namespace: str) -> tuple[Path, TemplateManifest]:
        """
        Get template repository from library by namespace.

        Args:
            namespace: Repository namespace

        Returns:
            Tuple of (repository path, parsed manifest)

        Raises:
            FileNotFoundError: If repository not found in library
            TemplateManifestError: If manifest is invalid

        Example:
            >>> manager = TemplateLibraryManager()
            >>> repo_path, manifest = manager.get_template_repository("acme-templates")
        """
        repo_path = self.library_path / namespace

        if not repo_path.exists():
            raise FileNotFoundError(
                f"Template repository '{namespace}' not found in library.\n"
                f"Install it with: devsync template install <repo-url>"
            )

        manifest_path = repo_path / "templatekit.yaml"
        manifest = load_manifest(manifest_path)

        return repo_path, manifest

    def list_available_templates(self, namespace: str) -> list[str]:
        """
        List all available templates in a repository.

        Args:
            namespace: Repository namespace

        Returns:
            List of template names

        Raises:
            FileNotFoundError: If repository not found
            TemplateManifestError: If manifest is invalid

        Example:
            >>> manager = TemplateLibraryManager()
            >>> templates = manager.list_available_templates("acme-templates")
            >>> "test-command" in templates
            True
        """
        _, manifest = self.get_template_repository(namespace)
        return [template.name for template in manifest.templates]

    def get_repository_version(self, namespace: str) -> Optional[str]:
        """
        Get version of repository in library.

        Args:
            namespace: Repository namespace

        Returns:
            Version string (tag or commit hash) or None if not found

        Example:
            >>> manager = TemplateLibraryManager()
            >>> version = manager.get_repository_version("acme-templates")
            >>> version
            'v1.2.0'
        """
        repo_path = self.library_path / namespace

        if not repo_path.exists():
            return None

        try:
            return get_repo_version(repo_path)
        except Exception:
            return None

    def list_installed_repositories(self) -> list[str]:
        """
        List all template repositories in library.

        Returns:
            List of repository namespaces

        Example:
            >>> manager = TemplateLibraryManager()
            >>> repos = manager.list_installed_repositories()
            >>> "acme-templates" in repos
            True
        """
        if not self.library_path.exists():
            return []

        repositories = []
        for item in self.library_path.iterdir():
            if item.is_dir() and (item / "templatekit.yaml").exists():
                repositories.append(item.name)

        return sorted(repositories)

    def remove_repository(self, namespace: str) -> None:
        """
        Remove template repository from library.

        Args:
            namespace: Repository namespace

        Raises:
            FileNotFoundError: If repository not found

        Example:
            >>> manager = TemplateLibraryManager()
            >>> manager.remove_repository("acme-templates")
        """
        repo_path = self.library_path / namespace

        if not repo_path.exists():
            raise FileNotFoundError(f"Repository '{namespace}' not found in library")

        import shutil

        shutil.rmtree(repo_path)

    def get_template_file_path(self, namespace: str, template_name: str, file_path: str) -> Path:
        """
        Get absolute path to a template file in repository.

        Args:
            namespace: Repository namespace
            template_name: Template name
            file_path: Relative file path from manifest

        Returns:
            Absolute path to template file

        Raises:
            FileNotFoundError: If repository or file not found

        Example:
            >>> manager = TemplateLibraryManager()
            >>> path = manager.get_template_file_path(
            ...     "acme-templates",
            ...     "test-command",
            ...     "templates/test.md"
            ... )
        """
        repo_path, _ = self.get_template_repository(namespace)
        template_file = repo_path / file_path

        if not template_file.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")

        return template_file
