"""Communication Agent — user intake, email, and direct conversation."""

from agno.agent import Agent

from src.models import OpenRouter
from src.models.openrouter import ModelType
from src.prompts import load_prompt


def create_communication_agent(
    agent_id: str = "neo-communication-agent",
    name: str = "Communication Agent",
    model_type: ModelType = "claude-sonnet",
    tools: list | None = None,
    instructions: str | None = None,
    role: str = "Global communication hub. Handles user intake, email (if enabled), and direct conversation.",
) -> Agent:
    return Agent(
        id=agent_id,
        name=name,
        role=role,
        model=OpenRouter.create(model_type=model_type),
        instructions=instructions if instructions is not None else load_prompt("communication_agent.md"),
        tools=tools or [],
        add_datetime_to_context=True,
        add_history_to_context=True,
        num_history_runs=5,
        markdown=True,
    )


communication_agent = create_communication_agent()

__all__ = ["create_communication_agent", "communication_agent"]
