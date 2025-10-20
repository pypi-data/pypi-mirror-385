"""SSH key generation and management for datum-dbt.

Handles secure key generation with proper permissions.
"""

import os
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def generate_ssh_keypair(output_path: Path) -> tuple[Path, Path]:
    """Generate RSA SSH key pair with secure permissions.

    Args:
        output_path: Path where private key will be saved (e.g., ~/.datum/keys/project-id.pem)

    Returns:
        Tuple of (private_key_path, public_key_path)

    Raises:
        PermissionError: If unable to set file permissions
        OSError: If unable to write key files
    """
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate 2048-bit RSA key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Serialize private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Write private key with secure permissions (600)
    private_key_path = output_path
    private_key_path.write_bytes(private_pem)
    os.chmod(private_key_path, 0o600)

    # Generate and serialize public key
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )

    # Write public key
    public_key_path = output_path.with_suffix(".pub")
    public_key_path.write_bytes(public_pem)
    os.chmod(public_key_path, 0o644)

    return private_key_path, public_key_path


def validate_key_permissions(key_path: Path) -> tuple[bool, str]:
    """Check if SSH private key has correct permissions (600).

    Args:
        key_path: Path to private key file

    Returns:
        Tuple of (is_valid, error_message). error_message is empty if valid.
    """
    if not key_path.exists():
        return False, f"Key file does not exist: {key_path}"

    # Check permissions (should be 0o600)
    stat_info = os.stat(key_path)
    permissions = stat_info.st_mode & 0o777

    if permissions != 0o600:
        return False, (
            f"Key file has incorrect permissions: {oct(permissions)}. "
            f"Expected 0o600. Fix with: chmod 600 {key_path}"
        )

    return True, ""


def fix_key_permissions(key_path: Path) -> None:
    """Fix SSH key permissions to 600.

    Args:
        key_path: Path to private key file

    Raises:
        FileNotFoundError: If key file doesn't exist
        PermissionError: If unable to change permissions
    """
    if not key_path.exists():
        raise FileNotFoundError(f"Key file not found: {key_path}")

    os.chmod(key_path, 0o600)


def read_public_key(public_key_path: Path) -> str:
    """Read public key content.

    Args:
        public_key_path: Path to public key file

    Returns:
        Public key content as string

    Raises:
        FileNotFoundError: If public key doesn't exist
    """
    if not public_key_path.exists():
        raise FileNotFoundError(f"Public key not found: {public_key_path}")

    return public_key_path.read_text().strip()
