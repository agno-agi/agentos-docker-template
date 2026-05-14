"""
CodeSearch Agent
================
"""

from pathlib import Path

from agno.agent import Agent
from agno.context.workspace import WorkspaceContextProvider

from app.settings import default_model
from db import get_postgres_db

REPO_ROOT = Path(__file__).resolve().parents[1]

# Wraps a read-only Workspace toolkit behind a sub-agent. The parent agent
# sees a single `query_my_codebase(question)` tool; the sub-agent handles
# listing, searching, and reading files.
codebase_context = WorkspaceContextProvider(
    id="my-codebase",
    name="My Codebase",
    root=REPO_ROOT,
    model=default_model(),
)


CODE_SEARCH_INSTRUCTIONS = """\
You answer questions about your own codebase. Be specific and concrete:
quote real file paths and line numbers from the codebase, never guess.
If a question is off-topic or not answered by the project's files, say
so plainly and offer to take a codebase question instead.
"""


code_search = Agent(
    id="code-search",
    name="CodeSearch",
    model=default_model(),
    db=get_postgres_db(),
    tools=codebase_context.get_tools(),
    instructions=CODE_SEARCH_INSTRUCTIONS + "\n\n" + codebase_context.instructions(),
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
