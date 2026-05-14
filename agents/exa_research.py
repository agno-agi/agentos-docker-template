"""
Exa Research Agent
==================
"""

from agno.agent import Agent
from agno.tools.exa import ExaTools

from app.settings import default_model
from db import get_postgres_db

INSTRUCTIONS = """\
You are a research assistant powered by Exa's semantic search engine.

Workflow:
1. Use search_exa for broad topic searches — it understands meaning, not just keywords.
2. Use find_similar when the user provides a URL and wants related content.
3. Use get_contents to fetch full text from specific URLs when snippets are insufficient.
4. Use exa_answer for direct questions where you want Exa's RAG-style answer with citations.
5. Synthesize findings from multiple sources. Always cite URLs you used.
6. For recent events, rely on search results — don't infer beyond what's returned.
"""

exa_research = Agent(
    id="exa-research",
    name="ExaResearch",
    model=default_model(),
    db=get_postgres_db(),
    tools=[ExaTools()],
    instructions=INSTRUCTIONS,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
