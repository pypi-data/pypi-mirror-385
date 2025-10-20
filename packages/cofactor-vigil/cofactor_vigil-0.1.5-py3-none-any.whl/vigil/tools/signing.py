"""Cryptographic signing support for attestations."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

try:
    from cryptography.hazmat.primitives import serialization  # type: ignore[import-not-found]
    from cryptography.hazmat.primitives.asymmetric import ed25519  # type: ignore[import-not-found]

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


def generate_keypair(private_key_path: Path, public_key_path: Path) -> None:
    """
    Generate an Ed25519 keypair and save to files.

    Args:
        private_key_path: Path to save private key (PEM format)
        public_key_path: Path to save public key (PEM format)

    Raises:
        ImportError: If cryptography library is not available
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        raise ImportError(
            "cryptography library required for signing. Install with: pip install cryptography"
        )

    # Generate private key
    private_key = ed25519.Ed25519PrivateKey.generate()

    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Save private key
    private_key_path.write_bytes(private_pem)
    private_key_path.chmod(0o600)  # Read/write for owner only

    # Get public key
    public_key = private_key.public_key()

    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Save public key
    public_key_path.write_bytes(public_pem)


def sign_attestation(
    attestation_path: Path,
    private_key_path: Path | None = None,
    signature_path: Path | None = None,
) -> dict[str, Any]:
    """
    Sign an attestation file with Ed25519.

    Args:
        attestation_path: Path to attestation JSON file
        private_key_path: Path to private key (PEM). If None, uses VIGIL_SIGNING_KEY env var
        signature_path: Path to save signature. If None, saves as attestation_path.sig

    Returns:
        Signature envelope with algorithm, public key, and signature value

    Raises:
        ImportError: If cryptography library is not available
        FileNotFoundError: If private key not found
        ValueError: If no private key specified
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        raise ImportError(
            "cryptography library required for signing. Install with: pip install cryptography"
        )

    # Determine private key path
    if private_key_path is None:
        key_path_str = os.environ.get("VIGIL_SIGNING_KEY")
        if not key_path_str:
            raise ValueError(
                "No signing key specified. Provide --signing-key or set VIGIL_SIGNING_KEY"
            )
        private_key_path = Path(key_path_str)

    if not private_key_path.exists():
        raise FileNotFoundError(f"Private key not found: {private_key_path}")

    # Load private key
    private_key_pem = private_key_path.read_bytes()
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)

    if not isinstance(private_key, ed25519.Ed25519PrivateKey):
        raise ValueError("Key is not an Ed25519 private key")

    # Read attestation content
    attestation_content = attestation_path.read_bytes()

    # Sign the attestation
    signature = private_key.sign(attestation_content)

    # Get public key
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Create signature envelope
    signature_envelope = {
        "algorithm": "Ed25519",
        "publicKey": public_pem.decode("utf-8"),
        "signature": base64.b64encode(signature).decode("ascii"),
    }

    # Save signature to file
    if signature_path is None:
        signature_path = attestation_path.with_suffix(attestation_path.suffix + ".sig")

    signature_path.write_text(json.dumps(signature_envelope, indent=2), encoding="utf-8")

    return signature_envelope


def verify_signature(
    attestation_path: Path,
    signature_path: Path | None = None,
    public_key_path: Path | None = None,
) -> bool:
    """
    Verify an attestation signature.

    Args:
        attestation_path: Path to attestation JSON file
        signature_path: Path to signature file. If None, uses attestation_path.sig
        public_key_path: Path to public key (PEM). If None, uses key from signature envelope

    Returns:
        True if signature is valid, False otherwise

    Raises:
        ImportError: If cryptography library is not available
        FileNotFoundError: If signature file not found
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        raise ImportError(
            "cryptography library required for verification. Install with: pip install cryptography"
        )

    # Determine signature path
    if signature_path is None:
        signature_path = attestation_path.with_suffix(attestation_path.suffix + ".sig")

    if not signature_path.exists():
        raise FileNotFoundError(f"Signature file not found: {signature_path}")

    # Load signature envelope
    signature_envelope = json.loads(signature_path.read_text(encoding="utf-8"))

    # Get public key
    if public_key_path is not None:
        public_pem = public_key_path.read_bytes()
    else:
        public_pem = signature_envelope["publicKey"].encode("utf-8")

    public_key = serialization.load_pem_public_key(public_pem)

    if not isinstance(public_key, ed25519.Ed25519PublicKey):
        raise ValueError("Key is not an Ed25519 public key")

    # Get signature
    signature_b64 = signature_envelope["signature"]
    signature = base64.b64decode(signature_b64)

    # Read attestation content
    attestation_content = attestation_path.read_bytes()

    # Verify signature
    try:
        public_key.verify(signature, attestation_content)
        return True
    except Exception:
        return False
