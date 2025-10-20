"""Vault data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse


@dataclass
class VaultSecret:
    """Vault secret data model."""

    path: str
    data: dict[str, Any]
    version: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from secret data.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Value or default
        """
        return self.data.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        result = {
            "path": self.path,
            "data": self.data,
        }

        if self.version is not None:
            result["version"] = self.version
        if self.created_at:
            result["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            result["updated_at"] = self.updated_at.isoformat()
        if self.metadata:
            result["metadata"] = self.metadata

        return result

    @classmethod
    def from_secret(cls, path: str, secret_data: dict[str, Any]) -> "VaultSecret":
        """Create from secret response.

        Args:
            path: Secret path
            secret_data: Secret response data

        Returns:
            VaultSecret instance
        """
        # Handle different vault response formats
        data = secret_data.get("data", {})
        if "data" in data:  # KV v2 format
            actual_data = data["data"]
            metadata = data.get("metadata", {})
        else:
            actual_data = data or secret_data
            metadata = {}

        return cls(
            path=path,
            data=actual_data,
            version=metadata.get("version"),
            created_at=metadata.get("created_time"),
            updated_at=metadata.get("updated_time"),
            metadata=metadata,
        )


@dataclass
class VaultCredential:
    """Vault credential data model."""

    name: str
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    token: Optional[str] = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        result = {"name": self.name}

        if self.username:
            result["username"] = self.username
        if self.password:
            result["password"] = self.password
        if self.host:
            result["host"] = self.host
        if self.port:
            result["port"] = self.port
        if self.database:
            result["database"] = self.database
        if self.url:
            result["url"] = self.url
        if self.api_key:
            result["api_key"] = self.api_key
        if self.secret_key:
            result["secret_key"] = self.secret_key
        if self.token:
            result["token"] = self.token
        if self.extra:
            result.update(self.extra)

        return result

    def to_uri(self, scheme: str = "postgresql") -> str:
        """Convert to URI format.

        Args:
            scheme: URI scheme

        Returns:
            URI string
        """
        if self.url:
            return self.url

        if not self.host:
            raise ValueError("Host is required for URI format")

        auth = ""
        if self.username:
            auth = self.username
            if self.password:
                auth += f":{self.password}"
            auth += "@"

        port = f":{self.port}" if self.port else ""
        database = f"/{self.database}" if self.database else ""

        return f"{scheme}://{auth}{self.host}{port}{database}"

    @classmethod
    def from_uri(cls, name: str, uri: str) -> "VaultCredential":
        """Create from URI.

        Args:
            name: Credential name
            uri: URI string

        Returns:
            VaultCredential instance
        """
        parsed = urlparse(uri)

        return cls(
            name=name,
            username=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path.lstrip("/") if parsed.path else None,
            url=uri,
        )

    @classmethod
    def from_secret(cls, name: str, secret: VaultSecret) -> "VaultCredential":
        """Create from VaultSecret.

        Args:
            name: Credential name
            secret: VaultSecret object

        Returns:
            VaultCredential instance
        """
        data = secret.data

        return cls(
            name=name,
            username=data.get("username"),
            password=data.get("password"),
            host=data.get("host"),
            port=data.get("port"),
            database=data.get("database"),
            url=data.get("url"),
            api_key=data.get("api_key"),
            secret_key=data.get("secret_key"),
            token=data.get("token"),
            extra={k: v for k, v in data.items()
                   if k not in ["username", "password", "host", "port",
                               "database", "url", "api_key", "secret_key", "token"]},
        )
