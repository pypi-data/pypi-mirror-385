"""Vault module for secret management."""

from x_scanner_commons.infrastructure.vault.config import VaultSettings
from x_scanner_commons.infrastructure.vault.exceptions import (
    VaultError,
    VaultNotFoundError,
    VaultAuthenticationError,
    VaultPermissionError,
    VaultSealedError,
    VaultConnectionError,
    VaultConfigurationError,
    VaultClientError,
)
from x_scanner_commons.infrastructure.vault.interface import VaultInterface
from x_scanner_commons.infrastructure.vault.models import VaultCredential, VaultSecret

__all__ = [
    "VaultInterface",
    "VaultSecret",
    "VaultCredential",
    "VaultSettings",
    "VaultError",
    "VaultNotFoundError",
    "VaultAuthenticationError",
    "VaultPermissionError",
    "VaultSealedError",
    "VaultConnectionError",
    "VaultConfigurationError",
    "VaultClientError",
]

# Conditional import for optional dependencies
try:
    from x_scanner_commons.infrastructure.vault.client import VaultClient

    __all__.append("VaultClient")
except ImportError:
    # hvac dependency not installed
    pass
