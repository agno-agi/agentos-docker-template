"""Minimal Composio + OpenAI Agents email test.

Usage:
    source .venv/bin/activate
    python scripts/composio_email_test.py
"""

import asyncio
import importlib
import os
import sys
from pathlib import Path

# This repository has a local `agents/` package that shadows the OpenAI Agents
# SDK module (`agents`). Remove repo paths before importing SDK symbols.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path = [p for p in sys.path if p not in ("", str(REPO_ROOT))]
# Composio reads this at import-time.
os.environ.setdefault("COMPOSIO_CACHE_DIR", str(REPO_ROOT / ".composio_cache"))

from agents import Agent, HostedMCPTool, Runner  # noqa: E402


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


async def main() -> None:
    dotenv_module = importlib.import_module("dotenv")
    load_dotenv = getattr(dotenv_module, "load_dotenv")
    load_dotenv()

    composio_api_key = require_env("COMPOSIO_API_KEY")
    external_user_id = (
        os.getenv("COMPOSIO_EXTERNAL_USER_ID", "").strip()
        or os.getenv("COMPOSIO_EXT_USER_ID", "").strip()
        or "local-test-user"
    )
    model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    # OpenAI Agents SDK uses OpenAI-compatible env vars. Point those at
    # OpenRouter when OPENROUTER_API_KEY is provided.
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if openrouter_api_key:
        os.environ["OPENAI_API_KEY"] = openrouter_api_key
        os.environ.setdefault("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        os.environ.setdefault("OPENAI_MODEL", model_name)

    composio_module = importlib.import_module("composio")
    Composio = getattr(composio_module, "Composio")
    composio = Composio(api_key=composio_api_key)
    session = composio.create(user_id=external_user_id)

    composio_mcp = HostedMCPTool(
        tool_config={
            "type": "mcp",
            "server_label": "tool_router",
            "server_url": session.mcp.url,
            "require_approval": "never",
            "headers": session.mcp.headers,
        }
    )

    agent = Agent(
        name="Email Manager",
        instructions="You are a helpful assistant that can use the tools provided to you.",
        model=model_name,
        tools=[composio_mcp],
    )

    result = await Runner.run(
        starting_agent=agent,
        input=(
            "Send an email to tyler@theaibuildr.com with the subject "
            "'Hello from Composio' and the body 'This is a test email!'"
        ),
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
