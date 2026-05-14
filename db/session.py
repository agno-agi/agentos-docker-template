"""
Database Session
================

PostgreSQL connection helpers.
``get_postgres_db()`` for agent storage backed by Postgres.
``create_knowledge()`` for agent knowledge backed by PgVector.
"""

from agno.db.postgres import PostgresDb
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.pgvector import PgVector, SearchType

from db.url import db_url

DB_ID = "agentos-db"


def get_postgres_db(contents_table: str | None = None) -> PostgresDb:
    """Create a PostgresDb instance.

    Pass ``contents_table`` only when this database is the ``contents_db``
    of a Knowledge base — it tells agno where to persist document contents.
    For plain agent persistence (sessions, memory) leave it unset.
    """
    if contents_table is not None:
        return PostgresDb(id=DB_ID, db_url=db_url, knowledge_table=contents_table)
    return PostgresDb(id=DB_ID, db_url=db_url)


def create_knowledge(name: str, table_name: str) -> Knowledge:
    """PgVector knowledge base with hybrid search.

    Plug into an Agent's ``knowledge=`` to give it a RAG surface. Vectors
    land in ``table_name``; document contents in ``{table_name}_contents``.
    """
    return Knowledge(
        name=name,
        vector_db=PgVector(
            db_url=db_url,
            table_name=table_name,
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
        contents_db=get_postgres_db(contents_table=f"{table_name}_contents"),
    )
