from pathlib import Path

from agno.os import AgentOS

from db import get_postgres_db
from settings import Settings, get_settings


def build_agent_os(settings: Settings | None = None) -> AgentOS:
    """Build and configure the AgentOS runtime."""
    cfg = settings or get_settings()
    db = get_postgres_db()
    repo_root = Path(__file__).resolve().parents[2]
    config_path = repo_root / "app" / "config.yaml"

    from src.agents.agno_assist import agno_assist
    from src.agents.knowledge_agent import knowledge_agent
    from src.teams.neo_orchestrator import neo_team

    # Standalone teams
    from src.teams.research_team import create_research_team
    from src.teams.dev_team import create_dev_team
    from src.agents.communication_agent import create_communication_agent

    comms_gen_agent = create_communication_agent(
        agent_id="comms-gen-agent",
        name="General Comms Agent",
        instructions="You are a Slack-focused communication agent. Route all messages through Slack channels...",
        role="Slack General communications specialist.",
    )

    standalone_research_team = create_research_team(
        team_id="research-team",
        name="Research Team",
    )

    standalone_dev_team = create_dev_team(
        team_id="dev-team",
        name="Dev Team",
    )


    return AgentOS(
        name=cfg.agentos_name,
        tracing=cfg.tracing,
        db=db,
        agents=[agno_assist, knowledge_agent, comms_gen_agent],
        teams=[neo_team, standalone_research_team, standalone_dev_team],
        interfaces=[],
        config=str(config_path),
        scheduler=False,
        scheduler_poll_interval=cfg.scheduler_poll_interval,
    )
