"""Vault configuration settings."""

import os
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class VaultSettings(BaseSettings):
    """HashiCorp Vault configuration settings.
    
    Use environment variables for token-based authentication.
    
    Required:
    - VAULT_ADDR: Vault server address
    - VAULT_TOKEN: Vault authentication token
    
    Optional environment variables:
    - VAULT_NAMESPACE: Explicit namespace (fallback to SERVICE_ENV)
    - SERVICE_ENV: Used to generate namespace as x-scanner/{env}
    - VAULT_MOUNT_PATH: KV mount path (default: 'secret')
    
    Example:
        export VAULT_ADDR='http://172.16.95.75:8200'
        export VAULT_TOKEN='s.xxxxx'
        export SERVICE_ENV='prod'  # generates namespace: x-scanner/prod
    """
    
    # Core settings only - removed all unnecessary fields
    address: str = Field(
        ...,
        description="Vault server address",
    )
    
    token: Optional[str] = Field(
        default=None,
        description="Vault authentication token",
    )
    
    namespace: Optional[str] = Field(
        default=None,
        description="Vault namespace (auto-generated from SERVICE_ENV)",
    )
    
    mount_path: str = Field(
        default="secret",
        description="KV v2 mount path",
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )
    
    def __init__(self, **kwargs):
        """Initialize VaultSettings with environment variable fallbacks."""
        # Check for VAULT_ADDR
        if not kwargs.get("address"):
            if addr := os.environ.get("VAULT_ADDR"):
                kwargs["address"] = addr
                
        # Check for VAULT_TOKEN
        if not kwargs.get("token"):
            if token := os.environ.get("VAULT_TOKEN"):
                kwargs["token"] = token
                
        # Namespace: explicit env first, then derive from SERVICE_ENV
        if not kwargs.get("namespace"):
            if ns := os.environ.get("VAULT_NAMESPACE"):
                kwargs["namespace"] = ns
            else:
                service_env = os.environ.get("SERVICE_ENV")
                if service_env:
                    kwargs["namespace"] = f"x-scanner/{service_env}"
                
        # Check for VAULT_MOUNT_PATH
        if not kwargs.get("mount_path"):
            if mp := os.environ.get("VAULT_MOUNT_PATH"):
                kwargs["mount_path"] = mp
                
        super().__init__(**kwargs)
    
    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Normalize Vault address."""
        # Ensure proper URL format
        if not v.startswith(("http://", "https://")):
            v = f"http://{v}"
        # Remove trailing slash
        return v.rstrip("/")
    
    @property
    def is_configured(self) -> bool:
        """Check if Vault is properly configured."""
        return bool(self.address and self.token)
    
    def get_client_kwargs(self) -> dict:
        """Get kwargs for VaultClient initialization."""
        kwargs = {
            "url": self.address,
            "token": self.token,
            "mount_point": self.mount_path,
        }
        
        if self.namespace:
            kwargs["namespace"] = self.namespace
            
        return kwargs