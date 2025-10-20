"""Helper utility functions."""

import asyncio
import hashlib
import secrets
import string
from collections.abc import Callable
from datetime import UTC, datetime
from functools import wraps
from typing import Any, Optional, TypeVar, Union
from uuid import uuid4

T = TypeVar("T")


def generate_id(prefix: Optional[str] = None) -> str:
    """Generate unique ID.

    Args:
        prefix: Optional prefix for ID

    Returns:
        Unique ID string
    """
    uid = str(uuid4())
    if prefix:
        return f"{prefix}_{uid}"
    return uid


def generate_token(length: int = 32, include_punctuation: bool = False) -> str:
    """Generate secure random token.

    Args:
        length: Token length
        include_punctuation: Include punctuation characters

    Returns:
        Random token string
    """
    alphabet = string.ascii_letters + string.digits
    if include_punctuation:
        alphabet += string.punctuation

    return "".join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash password using SHA256.

    Args:
        password: Plain text password
        salt: Optional salt (generated if None)

    Returns:
        Hashed password with salt prefix
    """
    if salt is None:
        salt = secrets.token_hex(16)

    # Combine salt and password
    salted = f"{salt}{password}".encode()
    hashed = hashlib.sha256(salted).hexdigest()

    # Return salt:hash format
    return f"{salt}:{hashed}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash.

    Args:
        password: Plain text password
        hashed: Hashed password with salt

    Returns:
        True if password matches
    """
    try:
        salt, expected_hash = hashed.split(":", 1)
        actual_hash = hash_password(password, salt)
        return secrets.compare_digest(actual_hash, hashed)
    except (ValueError, AttributeError):
        return False


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp.

    Returns:
        Current UTC datetime
    """
    return datetime.now(UTC)


def format_bytes(size: int, precision: int = 2) -> str:
    """Format bytes to human readable string.

    Args:
        size: Size in bytes
        precision: Decimal precision

    Returns:
        Formatted string (e.g., "1.23 MB")
    """
    if size < 0:
        raise ValueError("Size cannot be negative")

    if size == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.{precision}f} {units[unit_index]}"


def parse_bool(value: Any) -> bool:
    """Parse boolean from various types.

    Args:
        value: Value to parse

    Returns:
        Boolean value

    Raises:
        ValueError: If value cannot be parsed
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in ("true", "yes", "y", "1", "on"):
            return True
        elif value_lower in ("false", "no", "n", "0", "off"):
            return False
        else:
            raise ValueError(f"Cannot parse '{value}' as boolean")

    if isinstance(value, (int, float)):
        return bool(value)

    raise ValueError(f"Cannot parse {type(value)} as boolean")


def deep_merge(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    """Deep merge dictionaries.

    Args:
        base: Base dictionary
        update: Dictionary to merge

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def chunk_list(items: list[T], chunk_size: int) -> list[list[T]]:
    """Split list into chunks.

    Args:
        items: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks

    Raises:
        ValueError: If chunk_size <= 0
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i:i + chunk_size])

    return chunks


def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """Decorator for async function retry.

    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries
        backoff: Delay multiplier for each retry
        exceptions: Exceptions to catch

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """Sanitize filename for filesystem.

    Args:
        filename: Original filename
        replacement: Character to replace invalid chars

    Returns:
        Sanitized filename
    """
    # Invalid characters for most filesystems
    invalid_chars = '<>:"/\\|?*'

    # Replace invalid characters
    for char in invalid_chars:
        filename = filename.replace(char, replacement)

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Ensure not empty
    if not filename:
        filename = "unnamed"

    return filename


def truncate_string(
    text: str,
    max_length: int,
    suffix: str = "...",
) -> str:
    """Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    if max_length <= len(suffix):
        return text[:max_length]

    return text[:max_length - len(suffix)] + suffix


def flatten_dict(
    data: dict[str, Any],
    parent_key: str = "",
    separator: str = ".",
) -> dict[str, Any]:
    """Flatten nested dictionary.

    Args:
        data: Dictionary to flatten
        parent_key: Parent key prefix
        separator: Key separator

    Returns:
        Flattened dictionary
    """
    items: list[tuple[str, Any]] = []

    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(
                flatten_dict(value, new_key, separator).items()
            )
        else:
            items.append((new_key, value))

    return dict(items)


def calculate_checksum(data: Union[str, bytes], algorithm: str = "sha256") -> str:
    """Calculate checksum of data.

    Args:
        data: Data to checksum
        algorithm: Hash algorithm (sha256, md5, etc.)

    Returns:
        Hex digest checksum
    """
    if isinstance(data, str):
        data = data.encode()

    hasher = hashlib.new(algorithm)
    hasher.update(data)

    return hasher.hexdigest()
