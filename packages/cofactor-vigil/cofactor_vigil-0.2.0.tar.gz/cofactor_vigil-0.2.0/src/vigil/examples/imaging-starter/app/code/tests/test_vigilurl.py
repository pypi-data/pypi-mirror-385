from __future__ import annotations

import textwrap
from typing import Any

import pytest
from vigil.tools import vigilurl


@pytest.fixture
def base_manifest() -> dict[str, Any]:
    return {
        "resolverHost": "resolver.example",
        "org": "acme",
        "project": "demo",
    }


def test_build_vigil_url_requires_capsule_mapping(base_manifest: dict[str, Any]) -> None:
    cfg = base_manifest.copy()
    cfg["capsule"] = "not-a-mapping"

    with pytest.raises(ValueError, match="capsule section must be a mapping"):
        vigilurl.build_vigil_url(cfg)


def test_build_vigil_url_requires_digest(base_manifest: dict[str, Any]) -> None:
    cfg = base_manifest.copy()
    cfg["capsule"] = {"image": "repo:latest"}

    with pytest.raises(ValueError, match="must include an OCI digest"):
        vigilurl.build_vigil_url(cfg)


def test_main_reports_unpinned_manifest(
    tmp_path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest = textwrap.dedent(
        """
        resolverHost: resolver.example
        org: acme
        project: demo
        capsule:
          image: repo:latest
        """
    )
    manifest_path = tmp_path / "vigil.yaml"
    manifest_path.write_text(manifest, encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    exit_code = vigilurl.main()

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert "must include an OCI digest" in captured.err
