"""Simple MCP tool builders used across agents and teams."""

import logging
import os
import shutil
from functools import lru_cache
from typing import Iterable, Optional
from urllib.parse import urlparse

from agno.tools.mcp import MCPTools

log = logging.getLogger(__name__)
_DISABLED_VALUES = {"1", "true", "yes"}
_EMPTY_VALUES = {"none", "disabled", "false", "0"}
_NON_MCP_DOC_SUFFIXES = (".txt", ".md", ".rst", ".pdf", ".html", ".yaml", ".yml", ".json")


def _parse_urls(raw_urls: str) -> list[str]:
    """Parse comma/newline separated URLs into a deduplicated list."""
    urls: list[str] = []
    for part in raw_urls.replace("\n", ",").split(","):
        url = part.strip().strip('"').strip("'")
        if not url:
            continue
        if not url.startswith(("http://", "https://")):
            continue

        parsed = urlparse(url)
        # Skip obvious docs/static files that are not MCP endpoints.
        if parsed.path.lower().endswith(_NON_MCP_DOC_SUFFIXES):
            log.warning("Skipping non-MCP URL in MCP_SERVER_URLS-like env: %s", url)
            continue

        if url not in urls:
            urls.append(url)
    return urls


def _get_urls_from_env(env_var: str, default_urls: Iterable[str] | None) -> list[str]:
    raw = os.getenv(env_var, "").strip().lower()
    if raw in _EMPTY_VALUES:
        return []
    urls = _parse_urls(os.getenv(env_var, ""))
    return urls if urls else list(default_urls or [])


def _build_plane_stdio_tool() -> Optional[MCPTools]:
    """Build optional Plane stdio MCP tool for self-hosted Plane."""
    base_url = os.getenv("PLANE_BASE_URL", "").strip()
    workspace_slug = os.getenv("PLANE_WORKSPACE_SLUG", "").strip()
    api_key = os.getenv("PLANE_API_KEY", "").strip() or os.getenv("PLANE_MCP_API_KEY", "").strip()
    if not base_url or not workspace_slug or not api_key:
        return None
    if shutil.which("uvx") is None:
        log.warning("Skipping Plane stdio MCP tool: 'uvx' not found in PATH.")
        return None
    return MCPTools(
        command="uvx plane-mcp-server stdio",
        env={
            "PLANE_BASE_URL": base_url,
            "PLANE_WORKSPACE_SLUG": workspace_slug,
            "PLANE_API_KEY": api_key,
        },
    )


def build_mcp_tools(
    *,
    env_var: str = "MCP_SERVER_URLS",
    default_urls: Iterable[str] | None = None,
    disable_env_var: str = "MCP_DISABLED",
    include_plane_stdio: bool = True,
 ) -> list[MCPTools]:
    """
    Build MCP tools from URLs plus optional Plane stdio tool.

    Instances are cached by call signature so multiple agents can share one
    initialized tool connection set instead of spawning duplicate MCP clients.
    """
    default_urls_tuple = tuple(default_urls or ())
    return list(
        _build_mcp_tools_cached(
            env_var=env_var,
            default_urls=default_urls_tuple,
            disable_env_var=disable_env_var,
            include_plane_stdio=include_plane_stdio,
        )
    )


@lru_cache(maxsize=16)
def _build_mcp_tools_cached(
    *,
    env_var: str,
    default_urls: tuple[str, ...],
    disable_env_var: str,
    include_plane_stdio: bool,
) -> tuple[MCPTools, ...]:
    if os.getenv(disable_env_var, "").strip().lower() in _DISABLED_VALUES:
        return ()

    urls = _get_urls_from_env(env_var=env_var, default_urls=default_urls)
    tools: list[MCPTools] = []
    for url in urls:
        try:
            tools.append(MCPTools(url=url, transport="streamable-http"))
        except Exception as e:
            log.warning("Skipping MCP server %s: %s", url, e)

    if include_plane_stdio:
        try:
            plane_stdio_tool = _build_plane_stdio_tool()
            if plane_stdio_tool is not None:
                tools.append(plane_stdio_tool)
        except Exception as e:
            log.warning("Skipping Plane stdio MCP tool: %s", e)

    return tuple(tools)


__all__ = ["build_mcp_tools"]
