"""Plane Agent — system-of-record operator for Plane."""

from agno.agent import Agent

from src.models import OpenRouter
from src.models.openrouter import ModelType
from src.prompts import load_prompt
from src.teams.shared import neo_skills
from src.tools.mcp_tools import build_mcp_tools


def create_plane_agent(
    agent_id: str = "neo-plane-agent",
    name: str = "Plane Agent",
    model_type: ModelType = "gemini-flash",
    tools: list | None = None,
    instructions: str | None = None,
    role: str = "Plane system-of-record operator. Creates, updates, and queries projects, issues, prompts, and templates in Plane.",
) -> Agent:
    return Agent(
        id=agent_id,
        name=name,
        role=role,
        model=OpenRouter.create(model_type=model_type),
        instructions=instructions if instructions is not None else load_prompt("plane_agent.md"),
        tools=tools if tools is not None else build_mcp_tools(),
        skills=neo_skills,
        add_datetime_to_context=True,
        markdown=True,
    )


plane_agent = create_plane_agent()

__all__ = ["create_plane_agent", "plane_agent"]
