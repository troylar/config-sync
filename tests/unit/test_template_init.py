"""Tests for template init command."""

from unittest.mock import patch

import pytest
import typer

from aiconfigkit.cli.template_init import init_command


class TestTemplateInit:
    """Tests for template init command."""

    def test_init_basic(self, tmp_path):
        """Test basic template initialization."""
        repo_name = "my-templates"
        repo_path = tmp_path / repo_name

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(directory=repo_name)

        # Verify directory structure (IDE-agnostic)
        assert repo_path.exists()
        assert (repo_path / "templatekit.yaml").exists()
        assert (repo_path / "README.md").exists()
        assert (repo_path / ".gitignore").exists()
        assert (repo_path / "templates" / "instructions").exists()
        assert (repo_path / "templates" / "commands").exists()
        assert (repo_path / "templates" / "hooks").exists()

    def test_init_with_examples(self, tmp_path):
        """Test that example templates are created."""
        repo_name = "my-templates"
        repo_path = tmp_path / repo_name

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(directory=repo_name)

        # Verify example files (IDE-agnostic paths)
        assert (repo_path / "templates" / "instructions" / "example-instruction.md").exists()
        assert (repo_path / "templates" / "commands" / "example-command.md").exists()
        assert (repo_path / "templates" / "hooks" / "example-hook.md").exists()

        # Verify content is not empty
        instruction = (repo_path / "templates" / "instructions" / "example-instruction.md").read_text(encoding="utf-8")
        assert len(instruction) > 100
        assert "Example Coding Standards" in instruction

    def test_init_with_custom_namespace(self, tmp_path):
        """Test initialization with custom namespace."""
        repo_name = "company-standards"
        repo_path = tmp_path / repo_name
        custom_namespace = "acme"

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(directory=repo_name, namespace=custom_namespace)

        # Verify namespace in manifest
        manifest = (repo_path / "templatekit.yaml").read_text(encoding="utf-8")
        assert custom_namespace in manifest

        # Verify namespace in README
        readme = (repo_path / "README.md").read_text(encoding="utf-8")
        assert custom_namespace in readme

    def test_init_with_description(self, tmp_path):
        """Test initialization with custom description."""
        repo_name = "my-templates"
        repo_path = tmp_path / repo_name
        description = "ACME Corp Engineering Standards"

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(directory=repo_name, description=description)

        # Verify description in manifest
        manifest = (repo_path / "templatekit.yaml").read_text(encoding="utf-8")
        assert description in manifest

        # Verify description in README
        readme = (repo_path / "README.md").read_text(encoding="utf-8")
        assert description in readme

    def test_init_with_author(self, tmp_path):
        """Test initialization with custom author."""
        repo_name = "my-templates"
        repo_path = tmp_path / repo_name
        author = "Jane Doe"

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(directory=repo_name, author=author)

        # Verify author in manifest
        manifest = (repo_path / "templatekit.yaml").read_text(encoding="utf-8")
        assert author in manifest

    def test_init_existing_directory_no_force(self, tmp_path):
        """Test that init fails when directory exists without --force."""
        repo_name = "my-templates"
        repo_path = tmp_path / repo_name
        repo_path.mkdir()

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            with pytest.raises(typer.Exit) as exc_info:
                init_command(directory=repo_name, force=False)

            assert exc_info.value.exit_code == 1

    def test_init_existing_directory_with_force(self, tmp_path):
        """Test that init overwrites when --force is used."""
        repo_name = "my-templates"
        repo_path = tmp_path / repo_name
        repo_path.mkdir()
        (repo_path / "existing.txt").write_text("old content")

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(directory=repo_name, force=True)

        # Verify new files were created (IDE-agnostic paths)
        assert (repo_path / "templatekit.yaml").exists()
        assert (repo_path / "templates" / "instructions" / "example-instruction.md").exists()

    def test_init_manifest_structure(self, tmp_path):
        """Test that templatekit.yaml has correct structure."""
        repo_name = "my-templates"
        repo_path = tmp_path / repo_name

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(directory=repo_name)

        manifest_content = (repo_path / "templatekit.yaml").read_text(encoding="utf-8")

        # Verify required fields
        assert "name:" in manifest_content
        assert "description:" in manifest_content
        assert "version: 1.0.0" in manifest_content
        assert "author:" in manifest_content
        assert "templates:" in manifest_content

        # Verify example templates
        assert "example-instruction" in manifest_content
        assert "example-command" in manifest_content
        assert "example-hook" in manifest_content

        # Verify bundles section
        assert "bundles:" in manifest_content
        assert "getting-started" in manifest_content

    def test_init_readme_structure(self, tmp_path):
        """Test that README.md has proper documentation."""
        repo_name = "my-templates"
        repo_path = tmp_path / repo_name

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(directory=repo_name)

        readme_content = (repo_path / "README.md").read_text(encoding="utf-8")

        # Verify essential sections
        assert "Installation" in readme_content or "installation" in readme_content.lower()
        assert "Usage" in readme_content or "usage" in readme_content.lower()
        assert "Customization" in readme_content or "customization" in readme_content.lower()
        assert "DevSync" in readme_content

        # Verify example commands
        assert "devsync template install" in readme_content
        assert "devsync template list" in readme_content

    def test_init_gitignore_content(self, tmp_path):
        """Test that .gitignore has appropriate entries."""
        repo_name = "my-templates"
        repo_path = tmp_path / repo_name

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(directory=repo_name)

        gitignore_content = (repo_path / ".gitignore").read_text(encoding="utf-8")

        # Verify important ignores
        assert ".instructionkit/" in gitignore_content
        assert "__pycache__/" in gitignore_content
        assert ".vscode/" in gitignore_content or ".idea/" in gitignore_content

    def test_init_namespace_sanitization(self, tmp_path):
        """Test that namespace is sanitized from directory name."""
        repo_name = "my-awesome-templates"
        repo_path = tmp_path / repo_name

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(directory=repo_name)

        readme = (repo_path / "README.md").read_text(encoding="utf-8")

        # Namespace should have underscores instead of hyphens
        assert "my_awesome_templates" in readme

    def test_init_all_options(self, tmp_path):
        """Test initialization with all options specified."""
        repo_name = "company-templates"
        repo_path = tmp_path / repo_name

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(
                directory=repo_name,
                namespace="acme",
                description="ACME Engineering Standards",
                author="ACME Engineering Team",
                force=False,
            )

        # Verify all customizations applied
        manifest = (repo_path / "templatekit.yaml").read_text(encoding="utf-8")
        assert "ACME Engineering Standards" in manifest
        assert "ACME Engineering Team" in manifest

        # Verify namespace in README (namespace is used in install examples, not in manifest)
        readme = (repo_path / "README.md").read_text(encoding="utf-8")
        assert "acme" in readme

    def test_init_file_content_quality(self, tmp_path):
        """Test that generated files have helpful content."""
        repo_name = "my-templates"
        repo_path = tmp_path / repo_name

        with patch("aiconfigkit.cli.template_init.Path.resolve", return_value=repo_path):
            init_command(directory=repo_name)

        # Check instruction file has guidance (IDE-agnostic paths)
        instruction = (repo_path / "templates" / "instructions" / "example-instruction.md").read_text(encoding="utf-8")
        assert "Purpose" in instruction
        assert "Customization" in instruction
        assert len(instruction) > 500  # Should be substantial

        # Check command file has guidance
        command = (repo_path / "templates" / "commands" / "example-command.md").read_text(encoding="utf-8")
        assert "Purpose" in command
        assert "Example" in command or "example" in command.lower()
        assert len(command) > 500

        # Check hook file has guidance
        hook = (repo_path / "templates" / "hooks" / "example-hook.md").read_text(encoding="utf-8")
        assert "Purpose" in hook
        assert "Hook Types" in hook or "hook" in hook.lower()
        assert len(hook) > 500

    @patch("aiconfigkit.cli.template_init.Path.mkdir")
    def test_init_exception_handling(self, mock_mkdir, tmp_path):
        """Test exception handling during init."""
        repo_name = "my-templates"
        mock_mkdir.side_effect = RuntimeError("Permission denied")

        with pytest.raises(typer.Exit) as exc_info:
            init_command(directory=repo_name)

        assert exc_info.value.exit_code == 1
