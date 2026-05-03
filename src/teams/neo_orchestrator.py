"""Neo Orchestrator Team — top-level team composition."""

from agno.team import Team
from agno.team.mode import TeamMode

from src.agents.communication_agent import communication_agent
from src.agents.content_agent import content_agent
from src.agents.plane_agent import plane_agent
from src.agents.project_manager import project_manager
from src.agents.pulse_agent import pulse_agent
from src.agents.tools_agent import tools_agent
from src.models import OpenRouter
from src.prompts import load_prompt
from src.teams.dev_team import dev_team
from src.teams.research_team import research_team
from src.teams.shared import neo_team_learning_store

neo_team = Team(
    id="neo-team",
    name="Neo Orchestrator Team",
    mode=TeamMode.coordinate,
    model=OpenRouter.create(model_type="claude-sonnet"),
    members=[
        communication_agent,
        project_manager,
        plane_agent,
        tools_agent,
        dev_team,
        research_team,
        content_agent,
    ],
    instructions=load_prompt("neo_agent.md"),
    learning=neo_team_learning_store,
    show_members_responses=True,
    enable_session_summaries=True,
    enable_agentic_memory=True,
    enable_agentic_state=True,
    add_session_state_to_context=True,
    add_memories_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    add_datetime_to_context=True,
    markdown=True,
)

__all__ = [
    "neo_team",
    "communication_agent",
    "pulse_agent",
    "project_manager",
    "plane_agent",
    "tools_agent",
    "content_agent",
]
