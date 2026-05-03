
from agno.agent import Agent
from pathlib import Path
from textwrap import dedent

from db import create_knowledge, get_postgres_db
from models import OpenRouter
from tools.local_file_loader import LocalFileLoader

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()
quant_knowledge = create_knowledge("Quant Knowledge Agent", "quant_knowledge_agent_docs")
file_loader = LocalFileLoader(knowledge=quant_knowledge)

# Prefer pre-converted markdown (openDataLoader/output/) — falls back to raw knowledge/
_REPO_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIRS = [
    _REPO_ROOT / "knowledge" / "QuantConnect",  # raw PDFs (fallback)
]

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
quant_instructions = dedent("""\
    You are a Quant Knowledge Assistant. You answer questions by searching your knowledge base.

    ## How You Work

    1. Search the knowledge base for relevant information
    2. Answer based on what you find
    3. Cite your sources
    4. If the information isn't in the knowledge base, say so clearly

    ## Guidelines

    - Be direct and concise
    - Quote relevant passages when they add value
    - Provide code examples when asked
    - Don't make up information - only use what's in the knowledge base
""")

# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------
def load_quant_knowledge() -> None:
    """Load all files from the knowledge directories into the knowledge base."""
    for directory in KNOWLEDGE_DIRS:
        if directory.is_dir():
            file_loader.load_directory(str(directory))


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
quant_knowledge_agent = Agent(
    id="quant-knowledge-agent",
    name="Quant Knowledge Agent",
    model=OpenRouter.create(),
    db=agent_db,
    knowledge=quant_knowledge,
    tools=[file_loader],
    instructions=quant_instructions,
    search_knowledge=True,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)


if __name__ == "__main__":
    load_quant_knowledge()
