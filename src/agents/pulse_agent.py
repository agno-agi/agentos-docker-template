"""Pulse Dispatcher — autonomous operations heartbeat."""

from agno.agent import Agent

from src.models import OpenRouter
from src.models.openrouter import ModelType
from src.prompts import load_prompt
from src.teams.shared import neo_skills, neo_team_learning_store
from src.tools.mcp_tools import build_mcp_tools


def create_pulse_agent(
    agent_id: str = "neo-pulse",
    name: str = "Pulse Dispatcher",
    model_type: ModelType = "gemini-flash",
    tools: list | None = None,
    instructions: str | None = None,
    role: str = "Autonomous operations heartbeat. Scans Plane for ready work, dispatches to team members, detects stalled tasks, and logs operational intelligence.",
    learning=None,
) -> Agent:
    return Agent(
        id=agent_id,
        name=name,
        role=role,
        model=OpenRouter.create(model_type=model_type),
        instructions=instructions if instructions is not None else load_prompt("pulse_dispatcher.md"),
        tools=tools if tools is not None else build_mcp_tools(),
        skills=neo_skills,
        learning=learning if learning is not None else neo_team_learning_store,
        add_datetime_to_context=True,
        enable_agentic_memory=True,
        add_memories_to_context=True,
        markdown=True,
    )


pulse_agent = create_pulse_agent()

__all__ = ["create_pulse_agent", "pulse_agent"]
