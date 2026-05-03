"""Primary personal-assistant agent with memory and tool access."""

from os import getenv
from pathlib import Path

from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.learn import (
    LearnedKnowledgeConfig,
    LearningMachine,
    LearningMode,
    UserMemoryConfig,
    UserProfileConfig,
)
from agno.tools.duckdb import DuckDbTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.pgvector import PgVector, SearchType

from db import db_url, get_postgres_db
from src.models import OpenRouter
from src.prompts import load_prompt
from src.tools.mcp_tools import build_mcp_tools


def create_agno_assist_knowledge(
    table_name: str = "agno_assist_knowledge",
    contents_table: str = "agno_assist_contents",
    embedder_id: str = "text-embedding-3-small",
) -> tuple:
    """Return (knowledge, db) for Agno Assist."""
    agent_db = get_postgres_db(contents_table=contents_table)
    knowledge_store = Knowledge(
        name="Agno Assist Knowledge",
        vector_db=PgVector(
            db_url=db_url,
            table_name=table_name,
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id=embedder_id),
        ),
        contents_db=agent_db,
    )
    return knowledge_store, agent_db


def create_agno_assist(
    agent_id: str = "agno-assist",
    name: str = "Agno Assist",
    model_id: str = "openai/gpt-5.4",
    knowledge_store: Knowledge | None = None,
    db=None,
    tools: list | None = None,
    instructions: str | None = None,
) -> Agent:
    if knowledge_store is None or db is None:
        knowledge_store, db = create_agno_assist_knowledge()

    data_dir = Path(getenv("DATA_DIR", "/data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    duckdb_path = str(data_dir / "agno_assist.db")

    return Agent(
        id=agent_id,
        name=name,
        model=OpenRouter.create(model_id),
        db=db,
        instructions=instructions if instructions is not None else load_prompt("agno_assist.md"),
        learning=LearningMachine(
            knowledge=knowledge_store,
            db=db,
            user_profile=UserProfileConfig(mode=LearningMode.AGENTIC),
            user_memory=UserMemoryConfig(mode=LearningMode.AGENTIC),
            learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC),
        ),
        tools=tools if tools is not None else [
            DuckDuckGoTools(),
            *build_mcp_tools(
                env_var="AGNO_ASSIST_MCP_SERVER_URLS",
                default_urls=[],
                include_plane_stdio=False,
            ),
            DuckDbTools(db_path=duckdb_path),
        ],
        add_datetime_to_context=True,
        add_history_to_context=True,
        read_chat_history=True,
        num_history_runs=5,
        markdown=True,
    )


agno_assist_knowledge, _agent_db = create_agno_assist_knowledge()
agno_assist = create_agno_assist(knowledge_store=agno_assist_knowledge, db=_agent_db)

if __name__ == "__main__":
    agno_assist.print_response("Tell me about yourself", stream=True)


__all__ = ["create_agno_assist_knowledge", "create_agno_assist", "agno_assist", "agno_assist_knowledge"]
