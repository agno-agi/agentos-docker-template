"""Project Manager — task decomposition and planning."""

from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from src.models import OpenRouter
from src.models.openrouter import ModelType
from src.prompts import load_prompt
from src.teams.shared import neo_skills


def create_project_manager(
    agent_id: str = "neo-project-manager",
    name: str = "Project Manager",
    model_type: ModelType = "claude-sonnet",
    tools: list | None = None,
    instructions: str | None = None,
    role: str = "Task decomposition and planning specialist. Breaks objectives into structured task plans with acceptance criteria and dependencies.",
) -> Agent:
    return Agent(
        id=agent_id,
        name=name,
        role=role,
        model=OpenRouter.create(model_type=model_type),
        instructions=instructions if instructions is not None else load_prompt("project_manager.md"),
        tools=tools if tools is not None else [ReasoningTools(add_instructions=True)],
        skills=neo_skills,
        add_datetime_to_context=True,
        markdown=True,
    )


project_manager = create_project_manager()

__all__ = ["create_project_manager", "project_manager"]
