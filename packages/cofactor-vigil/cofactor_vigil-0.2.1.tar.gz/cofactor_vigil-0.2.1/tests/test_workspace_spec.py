"""Comprehensive tests for workspace_spec module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from vigil.tools import workspace_spec


def _write_manifest(
    path: Path,
    image: str | None = None,
    extensions: list[str] | None = None,
) -> None:
    """Write a minimal Vigil manifest."""
    if image is None:
        image = "ghcr.io/acme/capsule@sha256:" + "a" * 64
    if extensions is None:
        extensions = ["snakemake"]

    lines = [
        "version: 1",
        "capsule:",
        f"  image: {image}",
    ]

    if extensions is not None:
        lines.append("  extensions:")
        lines.extend(f"    - {ext}" for ext in extensions)
    else:
        lines.append("  extensions: []")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_workspace_spec(
    path: Path,
    image: str | None = None,
    extensions: list[str] | None = None,
) -> None:
    """Write a workspace spec JSON file."""
    if image is None:
        image = "ghcr.io/acme/capsule@sha256:" + "a" * 64
    if extensions is None:
        extensions = ["snakemake"]

    spec = {
        "capsule": {
            "image": image,
            "extensions": extensions,
        }
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class TestValidateImageDigest:
    """Tests for _validate_image_digest function."""

    def test_valid_sha256_digest(self):
        """Valid sha256 digest should pass."""
        valid_image = "ghcr.io/org/image@sha256:" + "a" * 64
        workspace_spec._validate_image_digest(valid_image)  # Should not raise

    def test_valid_sha256_mixed_case(self):
        """SHA256 digest with mixed case hex should pass."""
        valid_image = "ghcr.io/org/image@sha256:" + "AbCdEf0123456789" * 4
        workspace_spec._validate_image_digest(valid_image)  # Should not raise

    def test_missing_at_symbol(self):
        """Image without @ should fail."""
        invalid_image = "ghcr.io/org/image:latest"
        with pytest.raises(ValueError, match="must be pinned with @digest"):
            workspace_spec._validate_image_digest(invalid_image)

    def test_wrong_digest_algorithm(self):
        """Digest with sha512 should fail."""
        invalid_image = "ghcr.io/org/image@sha512:" + "a" * 128
        with pytest.raises(ValueError, match="must be sha256 with 64 hex characters"):
            workspace_spec._validate_image_digest(invalid_image)

    def test_short_digest(self):
        """Digest with fewer than 64 characters should fail."""
        invalid_image = "ghcr.io/org/image@sha256:" + "a" * 63
        with pytest.raises(ValueError, match="must be sha256 with 64 hex characters"):
            workspace_spec._validate_image_digest(invalid_image)

    def test_long_digest(self):
        """Digest with more than 64 characters should fail."""
        invalid_image = "ghcr.io/org/image@sha256:" + "a" * 65
        with pytest.raises(ValueError, match="must be sha256 with 64 hex characters"):
            workspace_spec._validate_image_digest(invalid_image)

    def test_non_hex_characters(self):
        """Digest with non-hex characters should fail."""
        invalid_image = "ghcr.io/org/image@sha256:" + "g" * 64
        with pytest.raises(ValueError, match="must be sha256 with 64 hex characters"):
            workspace_spec._validate_image_digest(invalid_image)

    def test_latest_tag(self):
        """Image with :latest tag should fail."""
        invalid_image = "ghcr.io/org/image:latest"
        with pytest.raises(ValueError, match="must be pinned with @digest"):
            workspace_spec._validate_image_digest(invalid_image)


class TestValidateExtensions:
    """Tests for _validate_extensions function."""

    def test_valid_string_list(self):
        """List of strings should pass."""
        extensions = ["snakemake", "ms-python.python@2024.6.0"]
        workspace_spec._validate_extensions(extensions)  # Should not raise

    def test_empty_list(self):
        """Empty list should pass."""
        workspace_spec._validate_extensions([])  # Should not raise

    def test_numeric_values(self):
        """Numeric values should pass (they're convertible to strings)."""
        extensions = ["ext1", 123, 45.6]
        workspace_spec._validate_extensions(extensions)  # Should not raise

    def test_boolean_values(self):
        """Boolean values should pass (they're convertible to strings)."""
        extensions = ["ext1", True, False]
        workspace_spec._validate_extensions(extensions)  # Should not raise

    def test_not_a_list(self):
        """Non-list should fail."""
        with pytest.raises(ValueError, match="must be a list"):
            workspace_spec._validate_extensions("not-a-list")  # type: ignore

    def test_dict_in_list(self):
        """Dict in list should fail."""
        extensions = ["valid", {"invalid": "dict"}]
        with pytest.raises(ValueError, match="has invalid type dict"):
            workspace_spec._validate_extensions(extensions)

    def test_list_in_list(self):
        """Nested list should fail."""
        extensions = ["valid", ["nested", "list"]]
        with pytest.raises(ValueError, match="has invalid type list"):
            workspace_spec._validate_extensions(extensions)


class TestSyncWorkspaceSpec:
    """Tests for sync_workspace_spec function."""

    def test_sync_valid_manifest(self, tmp_path):
        """Syncing valid manifest should succeed."""
        manifest = tmp_path / "vigil.yaml"
        valid_image = "ghcr.io/acme/capsule@sha256:" + "a" * 64
        _write_manifest(manifest, image=valid_image, extensions=["snakemake", "python"])

        spec, target = workspace_spec.sync_workspace_spec(tmp_path)

        assert spec["capsule"]["image"] == valid_image
        assert spec["capsule"]["extensions"] == ["snakemake", "python"]
        assert target == tmp_path / ".vigil" / "workspace.spec.json"

    def test_sync_preserves_existing_fields(self, tmp_path):
        """Syncing should preserve existing fields in workspace spec."""
        manifest = tmp_path / "vigil.yaml"
        valid_image = "ghcr.io/acme/capsule@sha256:" + "a" * 64
        _write_manifest(manifest, image=valid_image, extensions=["snakemake"])

        # Create existing workspace spec with additional fields
        workspace_spec_path = tmp_path / ".vigil" / "workspace.spec.json"
        existing_spec = {
            "version": "1.0.0",
            "scopes": ["preview_data", "run_target"],
            "capsule": {
                "image": "old@sha256:" + "b" * 64,
                "extensions": ["old"],
            },
        }
        workspace_spec_path.parent.mkdir(parents=True)
        workspace_spec_path.write_text(json.dumps(existing_spec, indent=2) + "\n", encoding="utf-8")

        spec, _ = workspace_spec.sync_workspace_spec(tmp_path)

        # Should update capsule but preserve other fields
        assert spec["version"] == "1.0.0"
        assert spec["scopes"] == ["preview_data", "run_target"]
        assert spec["capsule"]["image"] == valid_image
        assert spec["capsule"]["extensions"] == ["snakemake"]

    def test_sync_invalid_digest_fails(self, tmp_path):
        """Syncing manifest with invalid digest should fail."""
        manifest = tmp_path / "vigil.yaml"
        _write_manifest(manifest, image="ghcr.io/acme/capsule:latest")

        with pytest.raises(ValueError, match="must be pinned with @digest"):
            workspace_spec.sync_workspace_spec(tmp_path)

    def test_sync_short_digest_fails(self, tmp_path):
        """Syncing manifest with short digest should fail."""
        manifest = tmp_path / "vigil.yaml"
        short_digest = "ghcr.io/acme/capsule@sha256:" + "a" * 63
        _write_manifest(manifest, image=short_digest)

        with pytest.raises(ValueError, match="must be sha256 with 64 hex characters"):
            workspace_spec.sync_workspace_spec(tmp_path)

    def test_sync_invalid_extensions_fails(self, tmp_path):
        """Syncing manifest with invalid extensions should fail."""
        manifest = tmp_path / "vigil.yaml"
        manifest.write_text(
            "version: 1\n"
            "capsule:\n"
            f"  image: ghcr.io/acme/capsule@sha256:{'a' * 64}\n"
            "  extensions: not-a-list\n",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="missing capsule.extensions list"):
            workspace_spec.sync_workspace_spec(tmp_path)

    def test_sync_missing_manifest_fails(self, tmp_path):
        """Syncing without manifest should fail."""
        with pytest.raises(ValueError, match="vigil.yaml not found or empty"):
            workspace_spec.sync_workspace_spec(tmp_path)

    def test_sync_missing_capsule_section_fails(self, tmp_path):
        """Syncing manifest without capsule section should fail."""
        manifest = tmp_path / "vigil.yaml"
        manifest.write_text("version: 1\n", encoding="utf-8")

        with pytest.raises(ValueError, match="capsule section is missing or malformed"):
            workspace_spec.sync_workspace_spec(tmp_path)

    def test_sync_missing_image_fails(self, tmp_path):
        """Syncing manifest without image should fail."""
        manifest = tmp_path / "vigil.yaml"
        manifest.write_text(
            "version: 1\n" "capsule:\n" "  extensions:\n" "    - snakemake\n",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="missing capsule.image"):
            workspace_spec.sync_workspace_spec(tmp_path)


class TestWriteWorkspaceSpec:
    """Tests for write_workspace_spec function."""

    def test_write_creates_directory(self, tmp_path):
        """Writing should create parent directory if needed."""
        target = tmp_path / "nested" / "dir" / "workspace.spec.json"
        spec = {"capsule": {"image": "test", "extensions": []}}

        workspace_spec.write_workspace_spec(spec, target)

        assert target.exists()
        assert target.parent.exists()

    def test_write_canonical_format(self, tmp_path):
        """Writing should produce canonical JSON format."""
        target = tmp_path / "workspace.spec.json"
        spec = {
            "zebra": "last",
            "apple": "first",
            "capsule": {"image": "test", "extensions": ["b", "a"]},
        }

        workspace_spec.write_workspace_spec(spec, target)

        content = target.read_text(encoding="utf-8")

        # Should have sorted keys (apple, capsule, zebra alphabetically)
        [line for line in content.split("\n") if line.strip()]
        assert '"apple"' in content
        assert '"capsule"' in content
        assert '"zebra"' in content
        # Verify apple comes before zebra in content
        assert content.index('"apple"') < content.index('"zebra"')

        # Should have trailing newline
        assert content.endswith("\n")

        # Should be valid JSON
        parsed = json.loads(content)
        assert parsed == spec

    def test_write_trailing_newline(self, tmp_path):
        """Writing should add trailing newline."""
        target = tmp_path / "workspace.spec.json"
        spec = {"capsule": {"image": "test", "extensions": []}}

        workspace_spec.write_workspace_spec(spec, target)

        content = target.read_text(encoding="utf-8")
        assert content.endswith("\n")
        # Verify exactly one trailing newline
        assert not content.endswith("\n\n")

    def test_write_preserves_unicode(self, tmp_path):
        """Writing should preserve unicode characters."""
        target = tmp_path / "workspace.spec.json"
        spec = {"description": "Unicode: 你好 🚀"}

        workspace_spec.write_workspace_spec(spec, target)

        content = target.read_text(encoding="utf-8")
        parsed = json.loads(content)
        assert parsed["description"] == "Unicode: 你好 🚀"


class TestRunCommand:
    """Tests for run_command CLI entrypoint."""

    def test_sync_success(self, tmp_path, monkeypatch):
        """Successful sync should write file."""
        manifest = tmp_path / "vigil.yaml"
        valid_image = "ghcr.io/acme/capsule@sha256:" + "a" * 64
        _write_manifest(manifest, image=valid_image, extensions=["snakemake"])

        # Mock typer.Option to use tmp_path
        import typer

        output = []

        def mock_echo(msg, **kwargs):
            output.append(msg)

        monkeypatch.setattr(typer, "echo", mock_echo)

        # Call run_command
        try:
            workspace_spec.run_command(
                base_path=tmp_path,
                spec_path=None,
                dry_run=False,
            )
        except typer.Exit:
            pass

        # Verify file was written
        spec_path = tmp_path / ".vigil" / "workspace.spec.json"
        assert spec_path.exists()

        # Verify canonical format
        content = spec_path.read_text(encoding="utf-8")
        assert content.endswith("\n")
        parsed = json.loads(content)
        assert parsed["capsule"]["image"] == valid_image

    def test_dry_run_no_write(self, tmp_path, monkeypatch):
        """Dry run should not write file."""
        manifest = tmp_path / "vigil.yaml"
        valid_image = "ghcr.io/acme/capsule@sha256:" + "a" * 64
        _write_manifest(manifest, image=valid_image, extensions=["snakemake"])

        import typer

        output = []

        def mock_echo(msg, **kwargs):
            output.append(msg)

        monkeypatch.setattr(typer, "echo", mock_echo)

        # Call with dry_run
        with pytest.raises(typer.Exit) as exc_info:
            workspace_spec.run_command(
                base_path=tmp_path,
                spec_path=None,
                dry_run=True,
            )

        assert exc_info.value.exit_code == 0

        # Verify file was NOT written
        spec_path = tmp_path / ".vigil" / "workspace.spec.json"
        assert not spec_path.exists()

        # Verify output was printed
        assert len(output) > 0
        # Output should be valid JSON with trailing newline
        json_output = "".join(output)
        assert json_output.endswith("\n")
        parsed = json.loads(json_output)
        assert parsed["capsule"]["image"] == valid_image


class TestLoadFunctions:
    """Tests for load_manifest and load_workspace_spec."""

    def test_load_manifest_missing(self, tmp_path):
        """Loading missing manifest should return empty dict."""
        manifest = workspace_spec.load_manifest(tmp_path)
        assert manifest == {}

    def test_load_workspace_spec_missing(self, tmp_path):
        """Loading missing workspace spec should return empty dict."""
        spec = workspace_spec.load_workspace_spec(tmp_path)
        assert spec == {}

    def test_load_manifest_invalid_yaml(self, tmp_path):
        """Loading invalid YAML should raise ValueError."""
        manifest = tmp_path / "vigil.yaml"
        manifest.write_text("invalid: yaml: content: [", encoding="utf-8")

        with pytest.raises(ValueError, match="Failed to parse"):
            workspace_spec.load_manifest(tmp_path)

    def test_load_workspace_spec_invalid_json(self, tmp_path):
        """Loading invalid JSON should raise ValueError."""
        spec_path = tmp_path / ".vigil" / "workspace.spec.json"
        spec_path.parent.mkdir(parents=True)
        spec_path.write_text("{invalid json", encoding="utf-8")

        with pytest.raises(ValueError, match="Failed to parse"):
            workspace_spec.load_workspace_spec(tmp_path)

    def test_load_manifest_not_dict(self, tmp_path):
        """Loading non-dict YAML should raise ValueError."""
        manifest = tmp_path / "vigil.yaml"
        manifest.write_text("- list\n- of\n- items\n", encoding="utf-8")

        with pytest.raises(ValueError, match="should contain a mapping"):
            workspace_spec.load_manifest(tmp_path)

    def test_load_workspace_spec_not_dict(self, tmp_path):
        """Loading non-dict JSON should raise ValueError."""
        spec_path = tmp_path / ".vigil" / "workspace.spec.json"
        spec_path.parent.mkdir(parents=True)
        spec_path.write_text('["list", "of", "items"]', encoding="utf-8")

        with pytest.raises(ValueError, match="should contain a JSON object"):
            workspace_spec.load_workspace_spec(tmp_path)
