"""Research and analysis sub-team with evidence synthesis roles."""

from agno.agent import Agent
from agno.team import Team
from agno.team.mode import TeamMode

from src.models import OpenRouter
from src.models.openrouter import ModelType
from src.prompts import load_prompt

#todo: add shared learning machine, and distinct kb 
# todo: create distinct teams for each purpose

# Neo Research Team
    # todo: implement

# Standalone Research Team
    # todo: implement



def create_deep_researcher(
    agent_id: str = "neo-deep-researcher",
    name: str = "Deep Researcher",
    model_type: ModelType = "perplexity-reasoning",
    instructions: str | None = None,
    role: str = "Perform deep web-grounded research with citations using Perplexity.",
 ) -> Agent:
    return Agent(
        id=agent_id,
        name=name,
        role=role,
        model=OpenRouter.create(model_type=model_type),
        instructions=instructions if instructions is not None else load_prompt("deep_researcher.md"),
        add_datetime_to_context=True,
        markdown=True,
    )


def create_research_analyst(
    agent_id: str = "neo-research-analyst",
    name: str = "Research Analyst",
    model_type: ModelType = "claude-sonnet",
    instructions: str | None = None,
    role: str = "Evaluate evidence quality, grade sources, and produce structured analysis.",
 ) -> Agent:
    return Agent(
        id=agent_id,
        name=name,
        role=role,
        model=OpenRouter.create(model_type=model_type),
        instructions=instructions if instructions is not None else load_prompt("research_analyst.md"),
        add_datetime_to_context=True,
        markdown=True,
    )


def create_research_team(
    team_id: str = "neo-research-team",
    name: str = "Research Team",
    model_type: ModelType = "claude-sonnet",
    members: list | None = None,
    instructions: str | None = None,
    role: str = (
        "Evidence-based discovery, deep research, and synthesis. Produces structured "
        "findings reports with source grading and recommendations."
    ),
 ) -> Team:
    return Team(
        id=team_id,
        name=name,
        role=role,
        mode=TeamMode.coordinate,
        model=OpenRouter.create(model_type=model_type),
        members=members if members is not None else [deep_researcher, research_analyst],
        instructions=instructions if instructions is not None else load_prompt("research_lead.md"),
        show_members_responses=True,
        markdown=True,
    )


# Default Neo Team
deep_researcher = create_deep_researcher()
research_analyst = create_research_analyst()
research_team = create_research_team()

# Standalone Research Team



__all__ = [
    "create_deep_researcher",
    "create_research_analyst",
    "create_research_team",
    "deep_researcher",
    "research_analyst",
    "research_team",
]
