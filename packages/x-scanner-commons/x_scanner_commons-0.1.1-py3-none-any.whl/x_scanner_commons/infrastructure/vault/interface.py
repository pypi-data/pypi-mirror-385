"""Vault interface definition."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from x_scanner_commons.infrastructure.vault.models import VaultCredential, VaultSecret


class VaultInterface(ABC):
    """Abstract base class for vault implementations."""

    @abstractmethod
    async def get_secret(self, path: str, key: Optional[str] = None) -> VaultSecret:
        """Get a secret from vault.

        Args:
            path: Secret path
            key: Optional specific key from secret

        Returns:
            VaultSecret object

        Raises:
            VaultNotFoundError: If secret not found
            VaultError: If operation fails
        """
        pass

    @abstractmethod
    async def set_secret(self, path: str, data: dict[str, Any]) -> bool:
        """Set a secret in vault.

        Args:
            path: Secret path
            data: Secret data

        Returns:
            True if successful

        Raises:
            VaultError: If operation fails
        """
        pass

    @abstractmethod
    async def delete_secret(self, path: str) -> bool:
        """Delete a secret from vault.

        Args:
            path: Secret path

        Returns:
            True if successful

        Raises:
            VaultError: If operation fails
        """
        pass

    @abstractmethod
    async def list_secrets(self, path: str) -> list[str]:
        """List secrets at path.

        Args:
            path: Path to list

        Returns:
            List of secret paths

        Raises:
            VaultError: If operation fails
        """
        pass

    @abstractmethod
    async def get_credential(self, name: str) -> VaultCredential:
        """Get a credential from vault.

        Args:
            name: Credential name

        Returns:
            VaultCredential object

        Raises:
            VaultNotFoundError: If credential not found
            VaultError: If operation fails
        """
        pass

    @abstractmethod
    async def set_credential(self, credential: VaultCredential) -> bool:
        """Set a credential in vault.

        Args:
            credential: VaultCredential object

        Returns:
            True if successful

        Raises:
            VaultError: If operation fails
        """
        pass

    @abstractmethod
    async def rotate_secret(self, path: str) -> VaultSecret:
        """Rotate a secret.

        Args:
            path: Secret path

        Returns:
            New VaultSecret object

        Raises:
            VaultNotFoundError: If secret not found
            VaultError: If operation fails
        """
        pass

    @abstractmethod
    async def is_sealed(self) -> bool:
        """Check if vault is sealed.

        Returns:
            True if sealed
        """
        pass

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        """Get vault health status.

        Returns:
            Health status dictionary
        """
        pass

    async def close(self) -> None:
        """Close vault connection."""
        pass
