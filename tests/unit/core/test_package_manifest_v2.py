"""Tests for v2 package manifest parser."""

from pathlib import Path

import pytest
import yaml

from devsync.core.package_manifest_v2 import (
    ComponentRef,
    PackageManifestV2,
    detect_manifest_format,
    parse_manifest,
)


class TestComponentRef:
    def test_create(self) -> None:
        ref = ComponentRef(name="test", file="instructions/test.md")
        assert ref.name == "test"
        assert ref.description == ""

    def test_roundtrip(self) -> None:
        ref = ComponentRef(name="hook", file="hooks/pre.sh", hook_type="pre-commit", tags=["git"])
        restored = ComponentRef.from_dict(ref.to_dict())
        assert restored.name == ref.name
        assert restored.hook_type == ref.hook_type


class TestPackageManifestV2:
    def test_empty_manifest(self) -> None:
        m = PackageManifestV2()
        assert m.is_v2 is True
        assert m.has_practices is False
        assert m.has_components is False

    def test_v1_format_version(self) -> None:
        m = PackageManifestV2(format_version="1.0")
        assert m.is_v2 is False

    def test_to_dict(self) -> None:
        from devsync.core.practice import PracticeDeclaration

        m = PackageManifestV2(
            name="test-pkg",
            version="1.0.0",
            description="Test package",
            practices=[PracticeDeclaration(name="style", intent="Code style")],
        )
        d = m.to_dict()
        assert d["name"] == "test-pkg"
        assert len(d["practices"]) == 1

    def test_to_yaml(self) -> None:
        m = PackageManifestV2(name="pkg", version="1.0.0", description="Test")
        yaml_str = m.to_yaml()
        loaded = yaml.safe_load(yaml_str)
        assert loaded["name"] == "pkg"


class TestDetectManifestFormat:
    def test_v2_format(self, tmp_path: Path) -> None:
        (tmp_path / "devsync-package.yaml").write_text("name: test")
        assert detect_manifest_format(tmp_path) == "v2"

    def test_v1_format(self, tmp_path: Path) -> None:
        (tmp_path / "ai-config-kit-package.yaml").write_text("name: test")
        assert detect_manifest_format(tmp_path) == "v1"

    def test_v2_takes_priority(self, tmp_path: Path) -> None:
        (tmp_path / "devsync-package.yaml").write_text("name: test")
        (tmp_path / "ai-config-kit-package.yaml").write_text("name: test")
        assert detect_manifest_format(tmp_path) == "v2"

    def test_no_manifest(self, tmp_path: Path) -> None:
        assert detect_manifest_format(tmp_path) is None


class TestParseManifest:
    def test_parse_v2_manifest(self, tmp_path: Path) -> None:
        manifest = {
            "format_version": "2.0",
            "name": "team-standards",
            "version": "1.0.0",
            "description": "Python standards",
            "author": "Team",
            "practices": [
                {
                    "name": "type-safety",
                    "intent": "Enforce type hints",
                    "principles": ["Use type hints"],
                    "tags": ["python"],
                }
            ],
            "mcp_servers": [
                {
                    "name": "github-mcp",
                    "description": "GitHub API",
                    "command": "npx",
                    "args": ["-y", "server"],
                    "credentials": [{"name": "GITHUB_TOKEN", "description": "PAT"}],
                }
            ],
            "components": {"instructions": [{"name": "style", "file": "instructions/style.md", "tags": ["python"]}]},
        }
        (tmp_path / "devsync-package.yaml").write_text(yaml.dump(manifest))

        result = parse_manifest(tmp_path)
        assert result.is_v2
        assert result.name == "team-standards"
        assert len(result.practices) == 1
        assert result.practices[0].name == "type-safety"
        assert len(result.mcp_servers) == 1
        assert result.mcp_servers[0].name == "github-mcp"
        assert len(result.mcp_servers[0].credentials) == 1
        assert len(result.components.get("instructions", [])) == 1

    def test_parse_v1_manifest(self, tmp_path: Path) -> None:
        manifest = {
            "name": "old-package",
            "version": "0.5.0",
            "description": "Legacy package",
            "author": "Dev",
            "license": "MIT",
            "namespace": "org/repo",
            "components": {
                "instructions": [{"name": "rules", "file": "instructions/rules.md", "description": "Rules"}],
                "mcp_servers": [
                    {
                        "name": "db",
                        "description": "Database",
                        "command": "python",
                        "args": ["server.py"],
                        "credentials": [{"name": "DB_PASS", "description": "DB password"}],
                    }
                ],
            },
        }
        (tmp_path / "ai-config-kit-package.yaml").write_text(yaml.dump(manifest))

        result = parse_manifest(tmp_path)
        assert not result.is_v2
        assert result.name == "old-package"
        assert result.practices == []
        assert len(result.mcp_servers) == 1
        assert result.mcp_servers[0].name == "db"
        assert len(result.components.get("instructions", [])) == 1

    def test_parse_no_manifest_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            parse_manifest(tmp_path)

    def test_parse_invalid_yaml_raises(self, tmp_path: Path) -> None:
        (tmp_path / "devsync-package.yaml").write_text("- not: a: dict: [invalid")
        with pytest.raises(Exception):
            parse_manifest(tmp_path)

    def test_parse_hybrid_v2_package(self, tmp_path: Path) -> None:
        """V2 package with both practices and v1-style components."""
        manifest = {
            "format_version": "2.0",
            "name": "hybrid",
            "version": "1.0.0",
            "description": "Hybrid package",
            "practices": [{"name": "testing", "intent": "Ensure test coverage", "tags": ["testing"]}],
            "components": {
                "instructions": [{"name": "testing-rules", "file": "instructions/testing.md"}],
                "hooks": [{"name": "pre-commit", "file": "hooks/pre-commit.sh", "hook_type": "pre-commit"}],
            },
        }
        (tmp_path / "devsync-package.yaml").write_text(yaml.dump(manifest))

        result = parse_manifest(tmp_path)
        assert result.is_v2
        assert result.has_practices
        assert result.has_components
        assert len(result.practices) == 1
        assert len(result.components["instructions"]) == 1
        assert len(result.components["hooks"]) == 1
