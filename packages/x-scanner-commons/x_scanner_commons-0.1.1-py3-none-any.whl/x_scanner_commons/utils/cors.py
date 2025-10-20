"""Shared utilities for CORS configuration across x-scanner services."""

from __future__ import annotations

import os
from typing import Iterable, Sequence

DEFAULT_BASE_ORIGINS: tuple[str, ...] = (
    "http://scanner.evil.pe",
    "https://scanner.evil.pe",
    "https://x-scanner.evil.pe",
    "http://x-scanner.evil.pe",
    "http://x-scanner.evil.pe.cd535ff9428f84dbdadc5d21e17c4aa8a.cn-beijing.alicontainer.com",
    "http://x-scanner.evil.pe.cc645c33006424e22b2806d688cbbee15.cn-beijing.alicontainer.com",
)

DEFAULT_DEV_AND_LOCAL_ORIGINS: tuple[str, ...] = (
    "http://dev.scanner.evil.pe",
    "https://dev.scanner.evil.pe",
    "http://test.scanner.evil.pe",
    "https://test.scanner.evil.pe",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost",
    "http://localhost:8200",
    "http://localhost:8300",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8200",
    "http://127.0.0.1:8300",
)


__all__ = [
    "DEFAULT_BASE_ORIGINS",
    "DEFAULT_DEV_AND_LOCAL_ORIGINS",
    "build_allowed_origins",
]


def build_allowed_origins(
    *,
    env: str | None = None,
    port: str | None = None,
    service_port: int | str | None = None,
    base_origins: Sequence[str] | None = None,
    dev_and_local_origins: Sequence[str] | None = None,
    extra_dev_ports: Iterable[int | str] | None = None,
) -> list[str]:
    """Build the list of allowed CORS origins used by x-scanner services.

    Parameters
    ----------
    env:
        Explicit environment name. Defaults to the ``ENV`` environment variable.
    port:
        Explicit port hint. Defaults to the ``PORT`` environment variable.
    service_port:
        Optional service port used to flag local development scenarios.
    base_origins:
        Custom base origins. Defaults to ``DEFAULT_BASE_ORIGINS`` when omitted.
    dev_and_local_origins:
        Custom development/local origins. Defaults to ``DEFAULT_DEV_AND_LOCAL_ORIGINS``.
    extra_dev_ports:
        Additional port values that should enable development origins.
    """

    env = env if env is not None else os.getenv("ENV")
    port = port if port is not None else os.getenv("PORT")

    origins = list(base_origins or DEFAULT_BASE_ORIGINS)
    dev_origins = list(dev_and_local_origins or DEFAULT_DEV_AND_LOCAL_ORIGINS)

    should_include_dev = env == "dev"

    if not should_include_dev:
        allowed_ports = {"8000"}
        if service_port is not None:
            allowed_ports.add(str(service_port))
        if extra_dev_ports is not None:
            allowed_ports.update(str(candidate) for candidate in extra_dev_ports)

        if port is not None and port in allowed_ports:
            should_include_dev = True

    if should_include_dev:
        origins.extend(dev_origins)

    return list(dict.fromkeys(origins))
