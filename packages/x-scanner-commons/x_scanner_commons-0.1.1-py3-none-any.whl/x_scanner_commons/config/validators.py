"""Configuration validators."""

import re
from urllib.parse import urlparse


def validate_port(port: int) -> int:
    """Validate port number.

    Args:
        port: Port number

    Returns:
        Validated port number

    Raises:
        ValueError: If port is invalid
    """
    if not isinstance(port, int):
        raise ValueError(f"Port must be an integer, got {type(port)}")

    if port < 1 or port > 65535:
        raise ValueError(f"Port must be between 1 and 65535, got {port}")

    return port


def validate_database_url(url: str) -> str:
    """Validate database URL.

    Args:
        url: Database URL

    Returns:
        Validated URL

    Raises:
        ValueError: If URL is invalid
    """
    if not url:
        raise ValueError("Database URL cannot be empty")

    parsed = urlparse(url)

    # Check scheme
    valid_schemes = {
        "postgresql",
        "postgresql+asyncpg",
        "postgresql+psycopg2",
        "mysql",
        "mysql+aiomysql",
        "mysql+pymysql",
        "sqlite",
        "sqlite+aiosqlite",
    }

    if parsed.scheme not in valid_schemes:
        raise ValueError(f"Invalid database scheme: {parsed.scheme}")

    # Check required components for non-SQLite
    if not parsed.scheme.startswith("sqlite"):
        if not parsed.hostname:
            raise ValueError("Database URL must include hostname")
        if not parsed.username:
            raise ValueError("Database URL must include username")
        if not parsed.path or parsed.path == "/":
            raise ValueError("Database URL must include database name")

    return url


def validate_redis_url(url: str) -> str:
    """Validate Redis URL.

    Args:
        url: Redis URL

    Returns:
        Validated URL

    Raises:
        ValueError: If URL is invalid
    """
    if not url:
        raise ValueError("Redis URL cannot be empty")

    parsed = urlparse(url)

    # Check scheme
    if parsed.scheme not in ("redis", "rediss"):
        raise ValueError(f"Invalid Redis scheme: {parsed.scheme}")

    # Check hostname
    if not parsed.hostname:
        raise ValueError("Redis URL must include hostname")

    # Check port
    if parsed.port:
        validate_port(parsed.port)

    return url


def validate_email(email: str) -> str:
    """Validate email address.

    Args:
        email: Email address

    Returns:
        Validated email

    Raises:
        ValueError: If email is invalid
    """
    if not email:
        raise ValueError("Email cannot be empty")

    # Basic email regex
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        raise ValueError(f"Invalid email address: {email}")

    return email.lower()


def validate_url(url: str, require_https: bool = False) -> str:
    """Validate URL.

    Args:
        url: URL to validate
        require_https: Require HTTPS scheme

    Returns:
        Validated URL

    Raises:
        ValueError: If URL is invalid
    """
    if not url:
        raise ValueError("URL cannot be empty")

    parsed = urlparse(url)

    # Check scheme
    if require_https and parsed.scheme != "https":
        raise ValueError(f"URL must use HTTPS scheme, got {parsed.scheme}")
    elif parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}")

    # Check hostname
    if not parsed.hostname:
        raise ValueError("URL must include hostname")

    return url


def validate_environment(env: str) -> str:
    """Validate environment name.

    Args:
        env: Environment name

    Returns:
        Validated environment

    Raises:
        ValueError: If environment is invalid
    """
    valid_environments = {
        "development",
        "dev",
        "testing",
        "test",
        "staging",
        "stage",
        "production",
        "prod",
    }

    env_lower = env.lower()

    if env_lower not in valid_environments:
        raise ValueError(
            f"Invalid environment: {env}. Must be one of: {', '.join(valid_environments)}"
        )

    return env_lower


def validate_log_level(level: str) -> str:
    """Validate log level.

    Args:
        level: Log level

    Returns:
        Validated log level

    Raises:
        ValueError: If log level is invalid
    """
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    level_upper = level.upper()

    if level_upper not in valid_levels:
        raise ValueError(
            f"Invalid log level: {level}. Must be one of: {', '.join(valid_levels)}"
        )

    return level_upper


def validate_path(path: str, must_exist: bool = False) -> str:
    """Validate file path.

    Args:
        path: File path
        must_exist: Check if path exists

    Returns:
        Validated path

    Raises:
        ValueError: If path is invalid
    """
    if not path:
        raise ValueError("Path cannot be empty")

    from pathlib import Path

    path_obj = Path(path)

    if must_exist and not path_obj.exists():
        raise ValueError(f"Path does not exist: {path}")

    return str(path_obj)
