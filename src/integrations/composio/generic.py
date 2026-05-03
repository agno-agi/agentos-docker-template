"""Catch-all Composio tool builder.

Returns tools with access to *all* connected Composio apps/actions.
Use this when an agent needs broad Composio access rather than a
domain-scoped subset.
"""

from __future__ import annotations

import logging

from .client import get_composio_toolset

log = logging.getLogger(__name__)


def build_composio_tools(
    *,
    apps: list[str] | None = None,
    tags: list[str] | None = None,
) -> list:
    """Build Composio tools, optionally filtered by app names or tags.

    When called with no arguments, returns tools for all connected apps.
    """
    toolset = get_composio_toolset()
    if toolset is None:
        return []

    try:
        kwargs: dict = {}
        if apps:
            kwargs["apps"] = apps
        if tags:
            kwargs["tags"] = tags
        return toolset.get_tools(**kwargs) if kwargs else toolset.get_tools()
    except Exception as e:
        log.warning("Failed to build generic Composio tools: %s", e)
        return []


__all__ = ["build_composio_tools"]
