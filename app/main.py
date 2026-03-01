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

from agents.knowledge_agent import knowledge_agent
from agents.mcp_agent import mcp_agent
from db import get_postgres_db

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
    agents=[knowledge_agent, mcp_agent],
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(
        app="main:app",
        reload=(runtime_env == "dev"),
    )
