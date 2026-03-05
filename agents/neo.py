from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.learn import (
    LearningMachine,
    LearningMode,
    LearnedKnowledgeConfig,
    UserMemoryConfig,
    UserProfileConfig,
)

root_learning = LearningMachine(
    user_profile=UserProfileConfig(mode=LearningMode.AGENTIC),
    user_memory=UserMemoryConfig(mode=LearningMode.AGENTIC),
    learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC),
)

neo = Agent(
    name="Neo",
    model=OpenRouter(id="openai/gpt-5.2-chat"),
    learning=root_learning,
    add_history_to_context=True,
    num_history_runs=3,
    add_datetime_to_context=True,
)

if __name__ == "__main__":
    neo.print_response("Tell me about yourself", stream=True)