"""Vigil URL resolver that produces signed workspace specifications.

The resolver is intentionally light-weight so it can run from any Python
environment without requiring an additional web framework.  It exposes both a
pure resolver that understands Vigil URLs as well as a tiny WSGI application
that serves ``/.well-known/vigil/resolve``.  This keeps the core logic easy to
unit-test while still satisfying the HTTP contract exercised by clients.
"""

from __future__ import annotations

import base64
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import parse_qs, urlparse

import yaml


# ---------------------------------------------------------------------------
# Exceptions and helpers


class ResolverError(Exception):
    """Raised when a Vigil URL cannot be converted into a workspace spec."""

    def __init__(self, message: str, status: HTTPStatus = HTTPStatus.BAD_REQUEST) -> None:
        super().__init__(message)
        self.status = status


def _canonical_json(payload: Mapping[str, Any]) -> str:
    """Return a canonical JSON encoding suitable for signing."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


# ---------------------------------------------------------------------------
# Signing


@dataclass(frozen=True)
class SignatureBundle:
    """Container describing the signature returned alongside the spec."""

    algorithm: str
    key_id: str
    value: str


class HmacSigner:
    """Simple HMAC-SHA256 signer used for resolver responses."""

    def __init__(self, key_material: str | bytes, key_id: str, *, algorithm: str = "HMAC-SHA256") -> None:
        if isinstance(key_material, str):
            key_bytes = key_material.encode("utf-8")
        else:
            key_bytes = key_material
        if not key_bytes:
            raise ValueError("Signing key material must not be empty")
        self._key = key_bytes
        self._algorithm = algorithm
        self._key_id = key_id

    def sign(self, payload: Mapping[str, Any]) -> SignatureBundle:
        digest = hmac.new(self._key, _canonical_json(payload).encode("utf-8"), "sha256").digest()
        encoded = base64.b64encode(digest).decode("ascii")
        return SignatureBundle(algorithm=self._algorithm, key_id=self._key_id, value=encoded)

    def verify(self, payload: Mapping[str, Any], bundle: SignatureBundle) -> bool:
        if bundle.algorithm != self._algorithm or bundle.key_id != self._key_id:
            return False
        expected = hmac.new(self._key, _canonical_json(payload).encode("utf-8"), "sha256").digest()
        provided = base64.b64decode(bundle.value.encode("ascii"))
        return secrets.compare_digest(expected, provided)


# ---------------------------------------------------------------------------
# Manifest loading and validation


MANIFEST_CANDIDATES = ("vigil.yaml", "bench.yaml", "trail.yaml")
DEFAULT_SCOPES = ("preview_data", "run_target", "promote")
DISALLOWED_SCOPE_MARKERS = ("pat", "token")


@dataclass
class Manifest:
    resolver_host: str
    org: str
    project: str
    capsule_image: str
    inputs: list[str]
    policies: Mapping[str, Any]
    scopes: list[str]


def _load_yaml(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, Mapping):
        raise ResolverError(f"{path.name} must contain a mapping")
    return data


def _normalise_inputs(raw_inputs: Any) -> list[str]:
    if raw_inputs is None:
        return []
    if not isinstance(raw_inputs, list):
        raise ResolverError("inputs must be a list of strings in manifest")
    inputs: list[str] = []
    for item in raw_inputs:
        if not isinstance(item, str):
            raise ResolverError("inputs entries must be strings")
        inputs.append(item)
    return inputs


def _derive_scopes(data: Mapping[str, Any]) -> list[str]:
    raw_scopes = data.get("scopes")
    if raw_scopes is None:
        return list(DEFAULT_SCOPES)
    if not isinstance(raw_scopes, list):
        raise ResolverError("scopes must be provided as a list")
    scopes: list[str] = []
    for scope in raw_scopes:
        if not isinstance(scope, str):
            raise ResolverError("scope entries must be strings")
        lowered = scope.lower()
        if any(marker in lowered for marker in DISALLOWED_SCOPE_MARKERS):
            raise ResolverError("manifest scopes may not request personal access tokens")
        scopes.append(scope)
    if not scopes:
        raise ResolverError("scopes list must not be empty")
    return scopes


def load_manifest(base_path: Path) -> tuple[Manifest, Path]:
    """Load the first manifest recognised by the resolver."""

    for name in MANIFEST_CANDIDATES:
        candidate = base_path / name
        if not candidate.exists():
            continue
        data = _load_yaml(candidate)
        if not data:
            continue
        try:
            capsule = data["capsule"]
        except KeyError as exc:
            raise ResolverError("manifest is missing capsule section") from exc
        if not isinstance(capsule, Mapping):
            raise ResolverError("capsule section must be a mapping")

        image = capsule.get("image")
        if not isinstance(image, str) or "@" not in image:
            raise ResolverError("capsule.image must include a pinned digest")

        resolver_host = data.get("resolverHost")
        org = data.get("org")
        project = data.get("project")
        if not all(isinstance(item, str) and item for item in (resolver_host, org, project)):
            raise ResolverError("manifest must include resolverHost, org, and project")

        inputs = _normalise_inputs(data.get("inputs"))
        policies = data.get("policies") or {}
        if not isinstance(policies, Mapping):
            raise ResolverError("policies must be a mapping if provided")
        scopes = _derive_scopes(data)

        manifest = Manifest(
            resolver_host=resolver_host,
            org=org,
            project=project,
            capsule_image=image,
            inputs=inputs,
            policies=policies,
            scopes=scopes,
        )
        return manifest, candidate

    raise ResolverError(
        "No vigil.yaml, bench.yaml, or trail.yaml manifest found", status=HTTPStatus.NOT_FOUND
    )


# ---------------------------------------------------------------------------
# Resolver core


@dataclass
class WorkspaceSpec:
    ref: str
    capsuleDigest: str
    inputs: list[str]
    scopes: list[str]
    policies: Mapping[str, Any]
    issuedAt: str
    expiresAt: str

    def asdict(self) -> Mapping[str, Any]:
        return {
            "ref": self.ref,
            "capsuleDigest": self.capsuleDigest,
            "inputs": list(self.inputs),
            "scopes": list(self.scopes),
            "policies": dict(self.policies),
            "issuedAt": self.issuedAt,
            "expiresAt": self.expiresAt,
        }


class VigilResolver:
    """Convert Vigil URLs into signed workspace specifications."""

    def __init__(
        self,
        *,
        base_path: Path,
        signer: HmacSigner,
        clock: Callable[[], datetime] = _utc_now,
        ttl: timedelta = timedelta(hours=1),
    ) -> None:
        self._base_path = base_path
        self._signer = signer
        self._clock = clock
        self._ttl = ttl

    def resolve(self, url: str) -> tuple[WorkspaceSpec, SignatureBundle]:
        manifest, _ = load_manifest(self._base_path)
        parsed = urlparse(url)
        if parsed.scheme != "vigil":
            raise ResolverError("url must use the vigil:// scheme")
        if not parsed.netloc:
            raise ResolverError("url is missing resolver host")
        if parsed.netloc != manifest.resolver_host:
            raise ResolverError("resolver host does not match manifest")

        path = parsed.path.lstrip("/")
        path_parts = path.split("/", 1)
        if len(path_parts) != 2:
            raise ResolverError("url path must include org and project")
        org, project_part = path_parts
        if org != manifest.org:
            raise ResolverError("url org does not match manifest")
        if "@" not in project_part:
            raise ResolverError("url must include repository ref")
        project, ref = project_part.split("@", 1)
        if project != manifest.project:
            raise ResolverError("url project does not match manifest")
        if not ref:
            raise ResolverError("url ref segment is empty")

        query = parse_qs(parsed.query)
        digest_param = query.get("img", [""])[0]
        if not digest_param:
            raise ResolverError("url is missing img query parameter")

        capsule_digest = manifest.capsule_image.split("@", 1)[1]
        if digest_param != capsule_digest:
            raise ResolverError("url capsule digest does not match manifest")

        now = _ensure_utc(self._clock())
        issued_at = now.replace(microsecond=0)
        expires_at = (now + self._ttl).replace(microsecond=0)

        spec = WorkspaceSpec(
            ref=ref,
            capsuleDigest=capsule_digest,
            inputs=manifest.inputs,
            scopes=manifest.scopes,
            policies=manifest.policies,
            issuedAt=issued_at.isoformat().replace("+00:00", "Z"),
            expiresAt=expires_at.isoformat().replace("+00:00", "Z"),
        )

        signature = self._signer.sign(spec.asdict())
        return spec, signature


# ---------------------------------------------------------------------------
# HTTP wiring


class ResolverApp:
    """Minimal WSGI application exposing the resolver over HTTP."""

    def __init__(self, resolver: VigilResolver) -> None:
        self._resolver = resolver

    def __call__(self, environ: Mapping[str, Any], start_response: Callable) -> Iterable[bytes]:
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "")
        query_string = environ.get("QUERY_STRING", "")

        if method != "GET":
            return self._respond(start_response, HTTPStatus.METHOD_NOT_ALLOWED, {"error": "method not allowed"})

        if path != "/.well-known/vigil/resolve":
            return self._respond(start_response, HTTPStatus.NOT_FOUND, {"error": "not found"})

        params = parse_qs(query_string)
        url_values = params.get("url", [])
        if not url_values:
            return self._respond(start_response, HTTPStatus.BAD_REQUEST, {"error": "missing url parameter"})

        try:
            spec, signature = self._resolver.resolve(url_values[0])
        except ResolverError as exc:  # pragma: no cover - exercised in tests via resolver
            return self._respond(start_response, exc.status, {"error": str(exc)})
        except Exception as exc:  # pragma: no cover - defensive fallback
            return self._respond(start_response, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})

        body = {
            "spec": spec.asdict(),
            "signature": {
                "algorithm": signature.algorithm,
                "keyId": signature.key_id,
                "value": signature.value,
            },
        }
        return self._respond(start_response, HTTPStatus.OK, body)

    @staticmethod
    def _respond(
        start_response: Callable, status: HTTPStatus, payload: Mapping[str, Any]
    ) -> Iterable[bytes]:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
        ]
        start_response(f"{status.value} {status.phrase}", headers)
        return [body]


__all__ = [
    "HmacSigner",
    "ResolverApp",
    "ResolverError",
    "SignatureBundle",
    "VigilResolver",
    "WorkspaceSpec",
    "load_manifest",
]

