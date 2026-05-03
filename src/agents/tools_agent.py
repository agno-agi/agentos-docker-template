"""Tools Agent — MCP tools, web search, and data queries."""

from agno.agent import Agent
from agno.tools.duckdb import DuckDbTools
from agno.tools.duckduckgo import DuckDuckGoTools

from src.models import OpenRouter
from src.models.openrouter import ModelType
from src.prompts import load_prompt
from src.teams.shared import duckdb_path
from src.tools.mcp_tools import build_mcp_tools


def create_tools_agent(
    agent_id: str = "neo-tools-agent",
    name: str = "Tools Agent",
    model_type: ModelType = "gemini-flash",
    tools: list | None = None,
    instructions: str | None = None,
    role: str = "System tool executor. Has access to all MCP tools, web search, and data tools for executing actions on behalf of the team.",
) -> Agent:
    return Agent(
        id=agent_id,
        name=name,
        role=role,
        model=OpenRouter.create(model_type=model_type),
        instructions=instructions if instructions is not None else load_prompt("tools_agent.md"),
        tools=tools if tools is not None else [
            DuckDuckGoTools(),
            DuckDbTools(db_path=duckdb_path),
            *build_mcp_tools(),
        ],
        add_datetime_to_context=True,
        markdown=True,
    )


tools_agent = create_tools_agent()

__all__ = ["create_tools_agent", "tools_agent"]
