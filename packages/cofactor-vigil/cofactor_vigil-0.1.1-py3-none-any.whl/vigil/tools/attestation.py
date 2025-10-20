"""SLSA provenance and in-toto attestation generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, TypedDict


class DigestSet(TypedDict):
    """A set of cryptographic digests for an artifact."""

    sha256: str


class Subject(TypedDict):
    """Subject of an in-toto attestation."""

    name: str
    digest: DigestSet


class ExternalParameters(TypedDict, total=False):
    """External parameters for SLSA build definition."""

    vigilUrl: str
    gitRef: str
    inputs: list[dict[str, Any]]


class InternalParameters(TypedDict, total=False):
    """Internal parameters for SLSA build definition."""

    capsuleDigest: str
    profile: str | None
    cores: int | None


class ResolvedDependency(TypedDict):
    """A resolved dependency in SLSA format."""

    uri: str
    digest: DigestSet


class BuildDefinition(TypedDict):
    """SLSA build definition."""

    buildType: str
    externalParameters: ExternalParameters
    internalParameters: InternalParameters
    resolvedDependencies: list[ResolvedDependency]


class BuilderMetadata(TypedDict):
    """Metadata about the build execution."""

    invocationId: str
    startedOn: str
    finishedOn: str


class Builder(TypedDict):
    """Information about the builder."""

    id: str


class Byproduct(TypedDict):
    """A byproduct of the build process."""

    name: str
    digest: DigestSet


class RunDetails(TypedDict):
    """Details about the build run."""

    builder: Builder
    metadata: BuilderMetadata
    byproducts: list[Byproduct]


class SLSAProvenance(TypedDict):
    """SLSA provenance v1.0 predicate."""

    buildDefinition: BuildDefinition
    runDetails: RunDetails


class InTotoStatement(TypedDict):
    """in-toto attestation statement v1."""

    _type: str
    subject: list[Subject]
    predicateType: str
    predicate: SLSAProvenance


def compute_sha256(path: Path) -> str:
    """Compute SHA256 hash of a file (hex digest only, no prefix)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_content_sha256(content: str | bytes) -> str:
    """Compute SHA256 hash of content (hex digest only, no prefix)."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def generate_attestation(
    receipt_path: Path,
    vigil_url: str,
    git_ref: str,
    capsule_digest: str,
    runlet_id: str,
    started_at: str,
    finished_at: str,
    profile: str | None = None,
    cores: int | None = None,
    inputs: list[dict[str, Any]] | None = None,
    outputs: list[dict[str, Any]] | None = None,
    byproducts: list[dict[str, Any]] | None = None,
) -> InTotoStatement:
    """
    Generate an in-toto attestation with SLSA provenance v1.0.

    Args:
        receipt_path: Path to the receipt file
        vigil_url: Vigil URL for the run
        git_ref: Git reference (commit hash or ref)
        capsule_digest: Docker image digest
        runlet_id: Unique run identifier
        started_at: ISO 8601 timestamp when run started
        finished_at: ISO 8601 timestamp when run finished
        profile: Execution profile (cpu, gpu, tee, etc.)
        cores: Number of cores used
        inputs: List of input artifacts
        outputs: List of output artifacts
        byproducts: List of byproduct artifacts (metrics, logs, etc.)

    Returns:
        in-toto attestation statement with SLSA provenance
    """
    if inputs is None:
        inputs = []
    if outputs is None:
        outputs = []
    if byproducts is None:
        byproducts = []

    # Compute receipt digest as the subject
    receipt_digest = compute_sha256(receipt_path)
    receipt_name = receipt_path.name

    subject: Subject = {
        "name": receipt_name,
        "digest": {"sha256": receipt_digest},
    }

    # Build external parameters
    external_params: ExternalParameters = {
        "vigilUrl": vigil_url,
        "gitRef": git_ref,
        "inputs": inputs,
    }

    # Build internal parameters
    internal_params: InternalParameters = {
        "capsuleDigest": capsule_digest,
    }
    if profile:
        internal_params["profile"] = profile
    if cores is not None:
        internal_params["cores"] = cores

    # Resolve dependencies from outputs
    resolved_deps: list[ResolvedDependency] = []
    for output in outputs:
        # Parse checksum (format: "sha256:hex")
        checksum = output.get("checksum", "")
        if checksum.startswith("sha256:"):
            sha256_hex = checksum.split(":", 1)[1]
        else:
            sha256_hex = checksum

        dep: ResolvedDependency = {
            "uri": output.get("uri", ""),
            "digest": {"sha256": sha256_hex},
        }
        resolved_deps.append(dep)

    # Build definition
    build_def: BuildDefinition = {
        "buildType": "https://vigil.science/build/v1",
        "externalParameters": external_params,
        "internalParameters": internal_params,
        "resolvedDependencies": resolved_deps,
    }

    # Build run details
    builder: Builder = {
        "id": "https://vigil.science/builder/v1",
    }

    metadata: BuilderMetadata = {
        "invocationId": runlet_id,
        "startedOn": started_at,
        "finishedOn": finished_at,
    }

    byproduct_list: list[Byproduct] = []
    for byproduct in byproducts:
        checksum = byproduct.get("checksum", "")
        if checksum.startswith("sha256:"):
            sha256_hex = checksum.split(":", 1)[1]
        else:
            sha256_hex = checksum

        bp: Byproduct = {
            "name": byproduct.get("uri", ""),
            "digest": {"sha256": sha256_hex},
        }
        byproduct_list.append(bp)

    run_details: RunDetails = {
        "builder": builder,
        "metadata": metadata,
        "byproducts": byproduct_list,
    }

    # SLSA provenance
    provenance: SLSAProvenance = {
        "buildDefinition": build_def,
        "runDetails": run_details,
    }

    # in-toto statement
    statement: InTotoStatement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [subject],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": provenance,
    }

    return statement


def save_attestation(attestation: InTotoStatement, output_path: Path) -> None:
    """Save attestation to a JSON file."""
    output_path.write_text(json.dumps(attestation, indent=2), encoding="utf-8")
