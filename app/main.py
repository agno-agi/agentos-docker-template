"""
AgentOS
-------

The main entry point for AgentOS.

Run:
    python -m app.main
"""

from os import getenv
from pathlib import Path
from agno.os import AgentOS
import logging
from agents.knowledge_agent import knowledge_agent
from agents.quant_knowledge_agent import load_quant_knowledge, quant_knowledge_agent
from agents.mcp_agent import mcp_agent
from db import get_postgres_db

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional agents (require env vars to be configured)
# ---------------------------------------------------------------------------
_agents = [knowledge_agent, mcp_agent, quant_knowledge_agent]


# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------
runtime_env = getenv("RUNTIME_ENV", "prd")
scheduler_base_url = "http://127.0.0.1:8000" if runtime_env == "dev" else getenv("AGENTOS_URL")

agent_os = AgentOS(
    name="AgentOS",
    tracing=True,
    scheduler=True,
    scheduler_base_url=scheduler_base_url,
    db=get_postgres_db(),
    agents=_agents,
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()


@app.on_event("startup")
async def seed_knowledge() -> None:
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, load_quant_knowledge)


if __name__ == "__main__":
    agent_os.serve(
        app="main:app",
        reload=(runtime_env == "dev"),
    )
