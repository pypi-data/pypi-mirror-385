"""Vault exceptions."""

from typing import Optional


class VaultError(Exception):
    """Base vault exception."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class VaultNotFoundError(VaultError):
    """Secret not found exception."""
    pass


class VaultAuthenticationError(VaultError):
    """Authentication failed exception."""
    pass


class VaultPermissionError(VaultError):
    """Permission denied exception."""
    pass


class VaultSealedError(VaultError):
    """Vault is sealed exception."""
    pass


class VaultConnectionError(VaultError):
    """Connection failed exception."""
    pass


class VaultConfigurationError(VaultError):
    """Vault configuration error."""
    pass


class VaultClientError(VaultError):
    """Generic Vault client error."""
    pass
