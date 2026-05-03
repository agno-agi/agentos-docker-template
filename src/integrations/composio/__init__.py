"""Composio integration — domain-scoped tool builders via composio_agno.

Usage::

    from src.integrations.composio import build_composio_tools
    from src.integrations.composio import build_composio_email_tools

Attach the returned tool list to any agent's ``tools`` kwarg.
"""

from .client import get_composio_toolset, is_composio_disabled
from .email import build_composio_email_tools
from .generic import build_composio_tools

__all__ = [
    "get_composio_toolset",
    "is_composio_disabled",
    "build_composio_tools",
    "build_composio_email_tools",
]
