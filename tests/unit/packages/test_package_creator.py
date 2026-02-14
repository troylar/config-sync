"""Unit tests for package creator."""

import json
from pathlib import Path

import pytest
import yaml

from aiconfigkit.core.package_creator import (
    PackageCreationResult,
    PackageCreator,
    PackageMetadata,
    get_git_author,
)


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    project = tmp_path / "project"
    project.mkdir()
    return project


@pytest.fixture
def temp_output(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture
def sample_metadata() -> PackageMetadata:
    """Create sample package metadata."""
    return PackageMetadata(
        name="test-package",
        version="1.0.0",
        description="A test package",
        author="Test Author",
        license="MIT",
        namespace="test/repo",
    )


class TestPackageMetadata:
    """Test PackageMetadata class."""

    def test_default_values(self) -> None:
        """Test default metadata values."""
        metadata = PackageMetadata(name="test")
        assert metadata.version == "1.0.0"
        assert metadata.license == "MIT"
        assert metadata.namespace == "local/local"

    def test_custom_values(self) -> None:
        """Test custom metadata values."""
        metadata = PackageMetadata(
            name="my-package",
            version="2.0.0",
            description="My package",
            author="Me",
            license="Apache-2.0",
            namespace="org/repo",
        )
        assert metadata.name == "my-package"
        assert metadata.version == "2.0.0"
        assert metadata.license == "Apache-2.0"


class TestPackageCreator:
    """Test PackageCreator class."""

    def test_init(self, temp_project: Path, temp_output: Path, sample_metadata: PackageMetadata) -> None:
        """Test creator initialization."""
        creator = PackageCreator(temp_project, temp_output, sample_metadata)
        assert creator.project_root == temp_project.resolve()
        assert creator.output_dir == temp_output.resolve()
        assert creator.scrub_secrets is True

    def test_create_empty_project(
        self, temp_project: Path, temp_output: Path, sample_metadata: PackageMetadata
    ) -> None:
        """Test creation fails for empty project."""
        creator = PackageCreator(temp_project, temp_output, sample_metadata)
        result = creator.create()

        assert result.success is False
        assert "No components" in result.error_message

    def test_create_with_instruction(
        self, temp_project: Path, temp_output: Path, sample_metadata: PackageMetadata
    ) -> None:
        """Test creation with a single instruction."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "coding-style.md").write_text("# Coding Style\nBe consistent.")

        creator = PackageCreator(temp_project, temp_output, sample_metadata)
        result = creator.create()

        assert result.success is True
        assert result.package_path is not None
        assert result.components_included == 1

        manifest_path = result.package_path / "ai-config-kit-package.yaml"
        assert manifest_path.exists()

        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)

        assert manifest["name"] == "test-package"
        assert manifest["version"] == "1.0.0"
        assert len(manifest["components"]["instructions"]) == 1
        assert manifest["components"]["instructions"][0]["name"] == "coding-style"

        inst_file = result.package_path / "instructions" / "coding-style.md"
        assert inst_file.exists()
        assert "# Coding Style" in inst_file.read_text()

    def test_create_package_directory_structure(
        self, temp_project: Path, temp_output: Path, sample_metadata: PackageMetadata
    ) -> None:
        """Test that package directory structure is created."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "test.md").write_text("# Test")

        creator = PackageCreator(temp_project, temp_output, sample_metadata)
        result = creator.create()

        assert result.success is True

        for subdir in ["instructions", "mcp", "hooks", "commands", "resources"]:
            assert (result.package_path / subdir).is_dir()

    def test_create_fails_if_directory_exists(
        self, temp_project: Path, temp_output: Path, sample_metadata: PackageMetadata
    ) -> None:
        """Test creation fails if package directory already exists."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "test.md").write_text("# Test")

        existing_dir = temp_output / "package-test-package"
        existing_dir.mkdir()

        creator = PackageCreator(temp_project, temp_output, sample_metadata)
        result = creator.create()

        assert result.success is False
        assert "already exists" in result.error_message

    def test_create_with_mcp_server(
        self, temp_project: Path, temp_output: Path, sample_metadata: PackageMetadata
    ) -> None:
        """Test creation with MCP server configuration."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "test.md").write_text("# Test")

        claude_dir = temp_project / ".claude"
        settings = {
            "mcpServers": {
                "github": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "env": {"GITHUB_TOKEN": "ghp_secret_token_value"},
                }
            }
        }
        (claude_dir / "settings.local.json").write_text(json.dumps(settings))

        creator = PackageCreator(temp_project, temp_output, sample_metadata, scrub_secrets=True)
        result = creator.create()

        assert result.success is True
        assert result.secrets_templated > 0

        mcp_file = result.package_path / "mcp" / "github.json"
        assert mcp_file.exists()

        with open(mcp_file) as f:
            mcp_config = json.load(f)
        assert "${GITHUB_TOKEN}" in mcp_config["env"]["GITHUB_TOKEN"]

    def test_create_preserves_secrets_when_disabled(
        self, temp_project: Path, temp_output: Path, sample_metadata: PackageMetadata
    ) -> None:
        """Test that secrets are preserved when scrub_secrets=False."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "test.md").write_text("# Test")

        claude_dir = temp_project / ".claude"
        settings = {"mcpServers": {"test": {"command": "cmd", "env": {"API_KEY": "secret-value-12345678"}}}}
        (claude_dir / "settings.local.json").write_text(json.dumps(settings))

        creator = PackageCreator(temp_project, temp_output, sample_metadata, scrub_secrets=False)
        result = creator.create()

        assert result.success is True
        assert result.secrets_templated == 0

    def test_create_with_hooks(self, temp_project: Path, temp_output: Path, sample_metadata: PackageMetadata) -> None:
        """Test creation with hook files."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "test.md").write_text("# Test")

        hooks_dir = temp_project / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "preToolUse.sh").write_text("#!/bin/bash\necho 'pre'")

        creator = PackageCreator(temp_project, temp_output, sample_metadata)
        result = creator.create()

        assert result.success is True

        hook_file = result.package_path / "hooks" / "preToolUse.sh"
        assert hook_file.exists()

        with open(result.package_path / "ai-config-kit-package.yaml") as f:
            manifest = yaml.safe_load(f)
        assert len(manifest["components"]["hooks"]) == 1

    def test_create_with_commands(
        self, temp_project: Path, temp_output: Path, sample_metadata: PackageMetadata
    ) -> None:
        """Test creation with command files."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "test.md").write_text("# Test")

        cmd_dir = temp_project / ".claude" / "commands"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "build.sh").write_text("#!/bin/bash\necho 'build'")

        creator = PackageCreator(temp_project, temp_output, sample_metadata)
        result = creator.create()

        assert result.success is True

        cmd_file = result.package_path / "commands" / "build.sh"
        assert cmd_file.exists()

    def test_create_with_resources(
        self, temp_project: Path, temp_output: Path, sample_metadata: PackageMetadata
    ) -> None:
        """Test creation with resource files."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "test.md").write_text("# Test")

        res_dir = temp_project / ".ai-config-kit" / "resources"
        res_dir.mkdir(parents=True)
        (res_dir / "config.json").write_text('{"setting": "value"}')

        creator = PackageCreator(temp_project, temp_output, sample_metadata)
        result = creator.create()

        assert result.success is True

        res_file = result.package_path / "resources" / "config.json"
        assert res_file.exists()

    def test_generate_readme(self, temp_project: Path, temp_output: Path, sample_metadata: PackageMetadata) -> None:
        """Test README generation."""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "style.md").write_text("# Style Guide")

        creator = PackageCreator(temp_project, temp_output, sample_metadata)
        result = creator.create()

        assert result.success is True

        readme = result.package_path / "README.md"
        assert readme.exists()

        content = readme.read_text()
        assert "# test-package" in content
        assert "A test package" in content
        assert "Installation" in content
        assert "devsync package install" in content


class TestPackageCreationResult:
    """Test PackageCreationResult class."""

    def test_success_result(self) -> None:
        """Test successful result."""
        result = PackageCreationResult(
            success=True,
            package_path=Path("/output/package-test"),
            manifest_path=Path("/output/package-test/ai-config-kit-package.yaml"),
            components_included=5,
            secrets_templated=2,
        )
        assert result.success is True
        assert result.components_included == 5
        assert result.error_message is None

    def test_failure_result(self) -> None:
        """Test failure result."""
        result = PackageCreationResult(
            success=False,
            error_message="Something went wrong",
        )
        assert result.success is False
        assert result.error_message == "Something went wrong"
        assert result.package_path is None


class TestGetGitAuthor:
    """Test get_git_author function."""

    def test_get_git_author(self) -> None:
        """Test getting git author (may return None in some environments)."""
        author = get_git_author()
        assert author is None or isinstance(author, str)
