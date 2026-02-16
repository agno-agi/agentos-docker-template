from agno.os.interfaces.slack import Slack
from agno.agent import Agent
from agno.models.openrouter import OpenRouter

basic_agent = Agent(
    name="Slack Agent",
    model=OpenRouter(id="openai/gpt-5.2-chat"),
    add_history_to_context=True,
    num_history_runs=3,
    add_datetime_to_context=True,
)