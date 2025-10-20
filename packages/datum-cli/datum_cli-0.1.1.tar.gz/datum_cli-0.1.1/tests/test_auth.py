"""Tests for SSH key generation and management."""

import os
from pathlib import Path

import pytest

from datum.core.auth import (
    fix_key_permissions,
    generate_ssh_keypair,
    read_public_key,
    validate_key_permissions,
)


class TestSSHKeyGeneration:
    """Tests for SSH key pair generation."""

    def test_generate_keypair(self, tmp_path: Path):
        """Test generating SSH key pair."""
        key_path = tmp_path / "test_key.pem"
        
        private_key, public_key = generate_ssh_keypair(key_path)
        
        # Verify both files exist
        assert private_key.exists()
        assert public_key.exists()
        assert private_key == key_path
        assert public_key == key_path.with_suffix(".pub")

    def test_private_key_permissions(self, tmp_path: Path):
        """Test private key has correct permissions (600)."""
        key_path = tmp_path / "test_key.pem"
        
        private_key, _ = generate_ssh_keypair(key_path)
        
        # Check permissions are 600
        stat_info = os.stat(private_key)
        permissions = stat_info.st_mode & 0o777
        assert permissions == 0o600

    def test_public_key_permissions(self, tmp_path: Path):
        """Test public key has correct permissions (644)."""
        key_path = tmp_path / "test_key.pem"
        
        _, public_key = generate_ssh_keypair(key_path)
        
        # Check permissions are 644
        stat_info = os.stat(public_key)
        permissions = stat_info.st_mode & 0o777
        assert permissions == 0o644

    def test_key_content_format(self, tmp_path: Path):
        """Test generated keys have correct format."""
        key_path = tmp_path / "test_key.pem"
        
        private_key, public_key = generate_ssh_keypair(key_path)
        
        # Private key should be PEM format
        private_content = private_key.read_text()
        assert "-----BEGIN RSA PRIVATE KEY-----" in private_content
        assert "-----END RSA PRIVATE KEY-----" in private_content
        
        # Public key should be OpenSSH format
        public_content = public_key.read_text()
        assert public_content.startswith("ssh-rsa ")

    def test_creates_parent_directory(self, tmp_path: Path):
        """Test that parent directories are created if missing."""
        key_path = tmp_path / "nested" / "dir" / "key.pem"
        
        # Parent directory doesn't exist yet
        assert not key_path.parent.exists()
        
        private_key, _ = generate_ssh_keypair(key_path)
        
        # Should create parent and key
        assert key_path.parent.exists()
        assert private_key.exists()

    def test_overwrites_existing_key(self, tmp_path: Path):
        """Test generating key overwrites existing file."""
        key_path = tmp_path / "test_key.pem"
        
        # Create initial key
        generate_ssh_keypair(key_path)
        first_content = key_path.read_text()
        
        # Generate again
        generate_ssh_keypair(key_path)
        second_content = key_path.read_text()
        
        # Content should be different (new key generated)
        assert first_content != second_content


class TestKeyValidation:
    """Tests for SSH key permission validation."""

    def test_validate_correct_permissions(self, tmp_path: Path):
        """Test validation passes for correct permissions."""
        key_path = tmp_path / "test_key.pem"
        generate_ssh_keypair(key_path)
        
        is_valid, error = validate_key_permissions(key_path)
        
        assert is_valid is True
        assert error == ""

    def test_validate_wrong_permissions(self, tmp_path: Path):
        """Test validation fails for wrong permissions."""
        key_path = tmp_path / "test_key.pem"
        generate_ssh_keypair(key_path)
        
        # Change permissions to 644
        os.chmod(key_path, 0o644)
        
        is_valid, error = validate_key_permissions(key_path)
        
        assert is_valid is False
        assert "incorrect permissions" in error
        assert "chmod 600" in error

    def test_validate_nonexistent_key(self, tmp_path: Path):
        """Test validation fails for non-existent key."""
        key_path = tmp_path / "nonexistent.pem"
        
        is_valid, error = validate_key_permissions(key_path)
        
        assert is_valid is False
        assert "does not exist" in error

    def test_validate_too_permissive(self, tmp_path: Path):
        """Test validation fails for too permissive permissions."""
        key_path = tmp_path / "test_key.pem"
        generate_ssh_keypair(key_path)
        
        # Make world-readable (644)
        os.chmod(key_path, 0o644)
        
        is_valid, error = validate_key_permissions(key_path)
        
        assert is_valid is False
        assert "0o644" in error or "644" in error

    def test_validate_too_restrictive(self, tmp_path: Path):
        """Test validation fails even for more restrictive permissions."""
        key_path = tmp_path / "test_key.pem"
        generate_ssh_keypair(key_path)
        
        # Make 400 (read-only for owner)
        os.chmod(key_path, 0o400)
        
        is_valid, error = validate_key_permissions(key_path)
        
        # Should fail because we want exactly 600
        assert is_valid is False


class TestKeyPermissionFix:
    """Tests for fixing SSH key permissions."""

    def test_fix_permissions(self, tmp_path: Path):
        """Test fixing incorrect permissions."""
        key_path = tmp_path / "test_key.pem"
        generate_ssh_keypair(key_path)
        
        # Break permissions
        os.chmod(key_path, 0o644)
        
        # Fix them
        fix_key_permissions(key_path)
        
        # Verify fixed
        stat_info = os.stat(key_path)
        permissions = stat_info.st_mode & 0o777
        assert permissions == 0o600

    def test_fix_nonexistent_key(self, tmp_path: Path):
        """Test fixing permissions on non-existent key raises error."""
        key_path = tmp_path / "nonexistent.pem"
        
        with pytest.raises(FileNotFoundError, match="Key file not found"):
            fix_key_permissions(key_path)

    def test_fix_already_correct(self, tmp_path: Path):
        """Test fixing already-correct permissions is idempotent."""
        key_path = tmp_path / "test_key.pem"
        generate_ssh_keypair(key_path)
        
        # Already 600, fix again
        fix_key_permissions(key_path)
        
        # Should still be 600
        stat_info = os.stat(key_path)
        permissions = stat_info.st_mode & 0o777
        assert permissions == 0o600


class TestPublicKeyReading:
    """Tests for reading public key content."""

    def test_read_public_key(self, tmp_path: Path):
        """Test reading public key content."""
        key_path = tmp_path / "test_key.pem"
        _, public_key_path = generate_ssh_keypair(key_path)
        
        content = read_public_key(public_key_path)
        
        assert content.startswith("ssh-rsa ")
        assert len(content) > 100  # Should be substantial content
        assert "\n" not in content  # Should be stripped

    def test_read_nonexistent_public_key(self, tmp_path: Path):
        """Test reading non-existent public key raises error."""
        public_key_path = tmp_path / "nonexistent.pub"
        
        with pytest.raises(FileNotFoundError, match="Public key not found"):
            read_public_key(public_key_path)

    def test_public_key_strips_whitespace(self, tmp_path: Path):
        """Test that public key content is stripped."""
        key_path = tmp_path / "test_key.pem"
        _, public_key_path = generate_ssh_keypair(key_path)
        
        # Add whitespace to file
        original = public_key_path.read_text()
        public_key_path.write_text(f"\n{original}\n\n")
        
        content = read_public_key(public_key_path)
        
        # Should be stripped
        assert not content.startswith("\n")
        assert not content.endswith("\n")


class TestKeyPairIntegration:
    """Integration tests for key pair generation and usage."""

    def test_full_keypair_workflow(self, tmp_path: Path):
        """Test complete workflow of generating, validating, and reading keys."""
        key_path = tmp_path / "project_key.pem"
        
        # 1. Generate key pair
        private_key, public_key = generate_ssh_keypair(key_path)
        assert private_key.exists()
        assert public_key.exists()
        
        # 2. Validate permissions
        is_valid, _ = validate_key_permissions(private_key)
        assert is_valid is True
        
        # 3. Read public key
        public_content = read_public_key(public_key)
        assert public_content.startswith("ssh-rsa ")
        
        # 4. Break permissions
        os.chmod(private_key, 0o644)
        is_valid, error = validate_key_permissions(private_key)
        assert is_valid is False
        
        # 5. Fix permissions
        fix_key_permissions(private_key)
        is_valid, _ = validate_key_permissions(private_key)
        assert is_valid is True

    def test_multiple_keys_in_directory(self, tmp_path: Path):
        """Test generating multiple key pairs in same directory."""
        key1 = tmp_path / "key1.pem"
        key2 = tmp_path / "key2.pem"
        
        private1, public1 = generate_ssh_keypair(key1)
        private2, public2 = generate_ssh_keypair(key2)
        
        # All should exist
        assert private1.exists() and public1.exists()
        assert private2.exists() and public2.exists()
        
        # Content should be different
        assert private1.read_text() != private2.read_text()
        assert public1.read_text() != public2.read_text()