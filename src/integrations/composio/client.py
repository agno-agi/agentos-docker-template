"""Composio client management via composio_agno.

Single source of truth for Composio authentication and toolset creation.
All domain-specific tool builders import from here.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache

log = logging.getLogger(__name__)

_DISABLED_VALUES = {"1", "true", "yes"}


def is_composio_disabled(
    env_var: str = "COMPOSIO_DISABLED",
) -> bool:
    return os.getenv(env_var, "").strip().lower() in _DISABLED_VALUES


@lru_cache(maxsize=1)
def get_composio_toolset():
    """Return a shared ``ComposioToolSet`` instance, or ``None`` if unavailable.

    Reads ``COMPOSIO_API_KEY`` automatically (the SDK picks it up from env).
    Returns ``None`` when Composio is disabled, the API key is missing, or
    the ``composio_agno`` package is not installed.
    """
    if is_composio_disabled():
        return None

    api_key = os.getenv("COMPOSIO_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from composio_agno import ComposioToolSet  # pyright: ignore[reportMissingImports]

        return ComposioToolSet(api_key=api_key)
    except ModuleNotFoundError:
        log.warning("composio_agno is not installed; skipping Composio tools.")
        return None
    except Exception as e:
        log.warning("Failed to initialize ComposioToolSet: %s", e)
        return None


__all__ = ["get_composio_toolset", "is_composio_disabled"]
