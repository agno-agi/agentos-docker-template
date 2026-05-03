"""Content Agent — writing, summaries, and documentation."""

from agno.agent import Agent

from src.models import OpenRouter
from src.models.openrouter import ModelType
from src.prompts import load_prompt


def create_content_agent(
    agent_id: str = "neo-exec-content",
    name: str = "Content Agent",
    model_type: ModelType = "claude-sonnet",
    tools: list | None = None,
    instructions: str | None = None,
    role: str = "Writing and communication specialist. Produces status updates, documentation, stakeholder summaries, and task completion narratives.",
) -> Agent:
    return Agent(
        id=agent_id,
        name=name,
        role=role,
        model=OpenRouter.create(model_type=model_type),
        instructions=instructions if instructions is not None else load_prompt("exec_content_agent.md"),
        tools=tools or [],
        add_datetime_to_context=True,
        markdown=True,
    )


content_agent = create_content_agent()

__all__ = ["create_content_agent", "content_agent"]
