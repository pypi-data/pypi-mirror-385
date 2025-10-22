"""
Secure token storage with encryption
"""

import json
import os
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64


class SecureTokenStorage:
    """
    Secure storage for OAuth tokens with encryption.

    Example:
        >>> storage = SecureTokenStorage(
        ...     encryption_key="your-encryption-key"
        ... )
        >>> # Store tokens securely
        >>> storage.store_tokens("user_id", tokens)
        >>> # Retrieve tokens
        >>> tokens = storage.get_tokens("user_id")
    """

    def __init__(
        self,
        encryption_key: Optional[str] = None,
        storage_path: str = ".authkit_tokens",
        salt: Optional[bytes] = None,
    ):
        """
        Initialize secure token storage.

        Args:
            encryption_key: Encryption key for securing tokens. If not provided,
                          one will be generated (and should be persisted separately)
            storage_path: Path to store encrypted tokens (default: .authkit_tokens)
            salt: Optional salt for key derivation. If not provided and encryption_key
                 is set, a random salt will be generated and stored with the data.
        """
        self.storage_path = storage_path
        self.salt_path = storage_path + ".salt"

        if encryption_key:
            # Use provided salt or load/generate one
            if salt is None:
                # Try to load existing salt or generate new one
                salt = self._load_or_generate_salt()

            # Derive a key from the provided encryption key with unique salt
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
            self.salt = salt
        else:
            # Generate a new key without KDF
            key = Fernet.generate_key()
            self.salt = None

        self.fernet = Fernet(key)
        self._ensure_storage_exists()

    def _load_or_generate_salt(self) -> bytes:
        """
        Load existing salt from file or generate a new random salt.

        Returns:
            Salt bytes (16 bytes)
        """
        try:
            if os.path.exists(self.salt_path):
                with open(self.salt_path, "rb") as f:
                    salt = f.read()
                    if len(salt) == 16:  # Validate salt size
                        return salt
        except (IOError, OSError):
            pass

        # Generate new random salt
        salt = os.urandom(16)
        self._save_salt(salt)
        return salt

    def _save_salt(self, salt: bytes) -> None:
        """
        Save salt to file with secure permissions.

        Args:
            salt: Salt bytes to save
        """
        # Create file with restrictive permissions (owner read/write only)
        fd = os.open(
            self.salt_path,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            0o600
        )
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(salt)
        except Exception:
            os.close(fd)
            raise

    def _ensure_storage_exists(self) -> None:
        """Ensure the storage directory exists."""
        os.makedirs(os.path.dirname(self.storage_path) or ".", exist_ok=True)
        if not os.path.exists(self.storage_path):
            self._write_storage({})

    def _read_storage(self) -> Dict[str, Any]:
        """Read and decrypt the storage file."""
        try:
            with open(self.storage_path, "rb") as f:
                encrypted_data = f.read()

            if not encrypted_data:
                return {}

            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_storage(self, data: Dict[str, Any]) -> None:
        """Encrypt and write the storage file with secure permissions."""
        json_data = json.dumps(data).encode()
        encrypted_data = self.fernet.encrypt(json_data)

        # Write with restrictive permissions (owner read/write only)
        fd = os.open(
            self.storage_path,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            0o600
        )
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(encrypted_data)
        except Exception:
            os.close(fd)
            raise

    def store_tokens(self, user_id: str, tokens: Dict[str, Any]) -> None:
        """
        Store tokens securely for a user.

        Args:
            user_id: Unique identifier for the user
            tokens: Token dictionary containing access_token, refresh_token, etc.
        """
        storage = self._read_storage()
        storage[user_id] = tokens
        self._write_storage(storage)

    def get_tokens(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve tokens for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Token dictionary or None if not found
        """
        storage = self._read_storage()
        return storage.get(user_id)

    def delete_tokens(self, user_id: str) -> bool:
        """
        Delete tokens for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            True if tokens were deleted, False if user not found
        """
        storage = self._read_storage()

        if user_id in storage:
            del storage[user_id]
            self._write_storage(storage)
            return True

        return False

    def list_users(self) -> list:
        """
        List all users with stored tokens.

        Returns:
            List of user IDs
        """
        storage = self._read_storage()
        return list(storage.keys())

    def clear_all(self) -> None:
        """Clear all stored tokens."""
        self._write_storage({})

    def update_access_token(self, user_id: str, access_token: str) -> bool:
        """
        Update only the access token for a user.

        Args:
            user_id: Unique identifier for the user
            access_token: New access token

        Returns:
            True if updated, False if user not found
        """
        storage = self._read_storage()

        if user_id in storage:
            storage[user_id]["access_token"] = access_token
            self._write_storage(storage)
            return True

        return False
