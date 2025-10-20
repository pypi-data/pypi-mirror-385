"""HashiCorp Vault client implementation."""

import asyncio
from typing import Any, Optional

try:
    import hvac
    from hvac import Client
except ImportError:
    raise ImportError(
        "Vault dependencies not installed. Install with: pip install 'x-scanner-commons[vault]'"
    )

from x_scanner_commons.infrastructure.vault.exceptions import (
    VaultConnectionError,
    VaultError,
    VaultNotFoundError,
    VaultPermissionError,
)
from x_scanner_commons.infrastructure.vault.interface import VaultInterface
from x_scanner_commons.infrastructure.vault.models import VaultCredential, VaultSecret


class VaultClient(VaultInterface):
    """HashiCorp Vault client implementation."""

    def __init__(
        self,
        url: str = "http://localhost:8200",
        token: Optional[str] = None,
        mount_point: str = "secret",
        kv_version: int = 2,
        **kwargs: Any,
    ) -> None:
        """Initialize Vault client.

        Args:
            url: Vault server URL
            token: Authentication token
            mount_point: KV mount point
            kv_version: KV version (1 or 2)
            **kwargs: Additional client arguments
        """
        self._client = Client(url=url, token=token, **kwargs)
        self._mount_point = mount_point
        self._kv_version = kv_version
        self._executor = asyncio.get_event_loop()

    def _run_sync(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Run synchronous function in executor."""
        return asyncio.get_event_loop().run_in_executor(
            None, lambda: func(*args, **kwargs)
        )

    async def _check_response(self, response: Any, path: str) -> Any:
        """Check vault response for errors."""
        if response is None:
            raise VaultNotFoundError(f"Secret not found at path: {path}")
        return response

    async def get_secret(self, path: str, key: Optional[str] = None) -> VaultSecret:
        """Get a secret from vault."""
        try:
            if self._kv_version == 2:
                response = await self._run_sync(
                    self._client.secrets.kv.v2.read_secret_version,
                    path=path,
                    mount_point=self._mount_point,
                    raise_on_deleted_version=True,
                )
            else:
                response = await self._run_sync(
                    self._client.secrets.kv.v1.read_secret,
                    path=path,
                    mount_point=self._mount_point,
                )

            response = await self._check_response(response, path)
            secret = VaultSecret.from_secret(path, response)

            if key:
                value = secret.get(key)
                if value is None:
                    raise VaultNotFoundError(f"Key '{key}' not found in secret at path: {path}")
                secret.data = {key: value}

            return secret

        except hvac.exceptions.Forbidden:
            raise VaultPermissionError(f"Permission denied for path: {path}")
        except hvac.exceptions.InvalidPath:
            raise VaultNotFoundError(f"Secret not found at path: {path}")
        except hvac.exceptions.VaultError as e:
            raise VaultError(f"Vault error: {str(e)}")
        except Exception as e:
            if "not found" in str(e).lower():
                raise VaultNotFoundError(f"Secret not found at path: {path}")
            raise VaultConnectionError(f"Failed to connect to vault: {str(e)}")

    async def set_secret(self, path: str, data: dict[str, Any]) -> bool:
        """Set a secret in vault."""
        try:
            if self._kv_version == 2:
                response = await self._run_sync(
                    self._client.secrets.kv.v2.create_or_update_secret,
                    path=path,
                    secret=data,
                    mount_point=self._mount_point,
                )
            else:
                response = await self._run_sync(
                    self._client.secrets.kv.v1.create_or_update_secret,
                    path=path,
                    secret=data,
                    mount_point=self._mount_point,
                )

            return response is not None

        except hvac.exceptions.Forbidden:
            raise VaultPermissionError(f"Permission denied for path: {path}")
        except hvac.exceptions.VaultError as e:
            raise VaultError(f"Vault error: {str(e)}")
        except Exception as e:
            raise VaultConnectionError(f"Failed to connect to vault: {str(e)}")

    async def delete_secret(self, path: str) -> bool:
        """Delete a secret from vault."""
        try:
            if self._kv_version == 2:
                response = await self._run_sync(
                    self._client.secrets.kv.v2.delete_metadata_and_all_versions,
                    path=path,
                    mount_point=self._mount_point,
                )
            else:
                response = await self._run_sync(
                    self._client.secrets.kv.v1.delete_secret,
                    path=path,
                    mount_point=self._mount_point,
                )

            return True

        except hvac.exceptions.Forbidden:
            raise VaultPermissionError(f"Permission denied for path: {path}")
        except hvac.exceptions.InvalidPath:
            return False  # Already deleted
        except hvac.exceptions.VaultError as e:
            raise VaultError(f"Vault error: {str(e)}")
        except Exception as e:
            raise VaultConnectionError(f"Failed to connect to vault: {str(e)}")

    async def list_secrets(self, path: str) -> list[str]:
        """List secrets at path."""
        try:
            if self._kv_version == 2:
                response = await self._run_sync(
                    self._client.secrets.kv.v2.list_secrets,
                    path=path,
                    mount_point=self._mount_point,
                )
            else:
                response = await self._run_sync(
                    self._client.secrets.kv.v1.list_secrets,
                    path=path,
                    mount_point=self._mount_point,
                )

            if response and "data" in response and "keys" in response["data"]:
                return response["data"]["keys"]
            return []

        except hvac.exceptions.Forbidden:
            raise VaultPermissionError(f"Permission denied for path: {path}")
        except hvac.exceptions.InvalidPath:
            return []
        except hvac.exceptions.VaultError as e:
            raise VaultError(f"Vault error: {str(e)}")
        except Exception as e:
            raise VaultConnectionError(f"Failed to connect to vault: {str(e)}")

    async def get_credential(self, name: str) -> VaultCredential:
        """Get a credential from vault."""
        path = f"credentials/{name}"
        secret = await self.get_secret(path)
        return VaultCredential.from_secret(name, secret)

    async def set_credential(self, credential: VaultCredential) -> bool:
        """Set a credential in vault."""
        path = f"credentials/{credential.name}"
        return await self.set_secret(path, credential.to_dict())

    async def rotate_secret(self, path: str) -> VaultSecret:
        """Rotate a secret."""
        # This is a simplified implementation
        # In production, you would implement proper secret rotation
        secret = await self.get_secret(path)

        # Example: rotate a password
        if "password" in secret.data:
            import secrets
            import string

            alphabet = string.ascii_letters + string.digits + string.punctuation
            new_password = "".join(secrets.choice(alphabet) for _ in range(32))
            secret.data["password"] = new_password
            await self.set_secret(path, secret.data)

        return secret

    async def is_sealed(self) -> bool:
        """Check if vault is sealed."""
        try:
            response = await self._run_sync(self._client.sys.read_seal_status)
            return response.get("sealed", True)
        except Exception:
            return True

    async def health(self) -> dict[str, Any]:
        """Get vault health status."""
        try:
            is_authenticated = await self._run_sync(
                lambda: self._client.is_authenticated()
            )
            seal_status = await self._run_sync(self._client.sys.read_seal_status)

            return {
                "healthy": is_authenticated and not seal_status.get("sealed", True),
                "authenticated": is_authenticated,
                "sealed": seal_status.get("sealed", True),
                "version": seal_status.get("version", "unknown"),
                "cluster_name": seal_status.get("cluster_name"),
                "cluster_id": seal_status.get("cluster_id"),
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
            }
