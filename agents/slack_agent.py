
from agno.agent import Agent
from agno.tools.slack import SlackTools

from db import get_postgres_db
from models import OpenRouter

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------

agent_db = get_postgres_db()

slack_agent = Agent(
    id="slack-agent",
    name="Slack Agent",
    model=OpenRouter.create(),
    db=agent_db,
    tools=[
        SlackTools(all=True), 
    ],
    instructions="You are a helpful assistant that can help with Slack tasks and messages.",
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)