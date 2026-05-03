"""Composio email-scoped tool builder.

Returns tools limited to email-related Composio actions (send, read,
search, draft, etc.).  Attach to agents that need email capabilities.
"""

from __future__ import annotations

import logging

from .client import get_composio_toolset

log = logging.getLogger(__name__)


def build_composio_email_tools() -> list:
    """Build Composio tools scoped to email actions."""
    toolset = get_composio_toolset()
    if toolset is None:
        return []

    try:
        from composio_agno import Action  # pyright: ignore[reportMissingImports]

        return toolset.get_tools(
            actions=[
                Action.GMAIL_SEND_EMAIL,
                Action.GMAIL_FETCH_EMAILS,
                Action.GMAIL_CREATE_EMAIL_DRAFT,
            ],
        )
    except Exception as e:
        log.warning("Failed to build Composio email tools: %s", e)
        return []


__all__ = ["build_composio_email_tools"]
