"""Developer execution sub-team and members."""

from agno.agent import Agent
from agno.team import Team
from agno.team.mode import TeamMode

from src.models import OpenRouter
from src.models.openrouter import ModelType
from src.prompts import load_prompt


def create_dev_implementer(
    agent_id: str = "neo-dev-implementer",
    name: str = "Dev Implementer",
    model_type: ModelType = "claude-sonnet",
    instructions: str | None = None,
    role: str = "Build solutions and implement tasks according to the approach set by the Dev Lead.",
 ) -> Agent:
    return Agent(
        id=agent_id,
        name=name,
        role=role,
        model=OpenRouter.create(model_type=model_type),
        instructions=instructions if instructions is not None else load_prompt("dev_implementer.md"),
        add_datetime_to_context=True,
        markdown=True,
    )


def create_dev_reviewer(
    agent_id: str = "neo-dev-reviewer",
    name: str = "Dev Reviewer",
    model_type: ModelType = "grok",
    instructions: str | None = None,
    role: str = "Validate implementation output against acceptance criteria and report pass/fail.",
 ) -> Agent:
    return Agent(
        id=agent_id,
        name=name,
        role=role,
        model=OpenRouter.create(model_type=model_type),
        instructions=instructions if instructions is not None else load_prompt("dev_reviewer.md"),
        add_datetime_to_context=True,
        markdown=True,
    )


def create_dev_team(
    team_id: str = "neo-dev-team",
    name: str = "Dev Team",
    model_type: ModelType = "claude-sonnet",
    members: list | None = None,
    instructions: str | None = None,
    role: str = (
        "Implementation, debugging, and technical problem-solving. Receives defined "
        "tasks with acceptance criteria and delivers verified results."
    ),
 ) -> Team:
    return Team(
        id=team_id,
        name=name,
        role=role,
        mode=TeamMode.coordinate,
        model=OpenRouter.create(model_type=model_type),
        members=members if members is not None else [dev_implementer, dev_reviewer],
        instructions=instructions if instructions is not None else load_prompt("dev_lead.md"),
        show_members_responses=True,
        markdown=True,
    )

# Neo Dev Team
dev_implementer = create_dev_implementer()
dev_reviewer = create_dev_reviewer()
dev_team = create_dev_team()

# Standalone Dev Team
    # todo: implement

__all__ = [
    "create_dev_implementer",
    "create_dev_reviewer",
    "create_dev_team",
    "dev_implementer",
    "dev_reviewer",
    "dev_team",
]
