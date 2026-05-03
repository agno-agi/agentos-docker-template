"""RAG-oriented agent for document-backed knowledge retrieval."""

from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.pgvector import PgVector, SearchType

from db import db_url, get_postgres_db
from src.models import OpenRouter
from src.prompts import load_prompt


def create_knowledge_store(
    table_name: str = "knowledge_agent_docs",
    contents_table: str = "knowledge_agent_contents",
    embedder_id: str = "text-embedding-3-small",
    max_results: int = 10,
 ) -> tuple:
    """Return (knowledge, db) for a knowledge agent."""
    agent_db = get_postgres_db(contents_table=contents_table)
    knowledge_store = Knowledge(
        name="Knowledge Agent",
        vector_db=PgVector(
            db_url=db_url,
            table_name=table_name,
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id=embedder_id),
        ),
        max_results=max_results,
        contents_db=agent_db,
    )
    return knowledge_store, agent_db


def create_knowledge_agent(
    agent_id: str = "knowledge-agent",
    name: str = "Knowledge Agent",
    model_id: str = "openai/gpt-5.4",
    knowledge_store: Knowledge | None = None,
    db=None,
    instructions: str | None = None,
 ) -> Agent:
    if knowledge_store is None or db is None:
        knowledge_store, db = create_knowledge_store()
    return Agent(
        id=agent_id,
        name=name,
        model=OpenRouter.create(model_id),
        db=db,
        knowledge=knowledge_store,
        instructions=instructions if instructions is not None else load_prompt("knowledge_agent.md"),
        search_knowledge=True,
        enable_agentic_memory=True,
        add_datetime_to_context=True,
        add_history_to_context=True,
        read_chat_history=True,
        num_history_runs=5,
        markdown=True,
    )


knowledge, _agent_db = create_knowledge_store()
knowledge_agent = create_knowledge_agent(knowledge_store=knowledge, db=_agent_db)


def load_default_documents() -> None:
    """Load default documents into the knowledge base."""
    knowledge.insert(
        name="Agno Introduction",
        url="https://docs.agno.com/introduction.md",
        skip_if_exists=True,
    )
    knowledge.insert(
        name="Agno First Agent",
        url="https://docs.agno.com/first-agent.md",
        skip_if_exists=True,
    )


if __name__ == "__main__":
    load_default_documents()


__all__ = ["create_knowledge_store", "create_knowledge_agent", "knowledge_agent", "knowledge", "load_default_documents"]
