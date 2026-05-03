"""Shared team dependencies: memory store, skills, and local data paths."""

from functools import lru_cache
from os import getenv
from pathlib import Path
from typing import cast

from agno.learn import (
    LearnedKnowledgeConfig,
    LearningMachine,
    LearningMode,
    UserMemoryConfig,
    UserProfileConfig,
)
from agno.skills import LocalSkills, Skills

from db import get_postgres_db
from src.models import OpenRouter
from src.models.openrouter import ModelType


@lru_cache(maxsize=1)
def get_db():
    return get_postgres_db()


@lru_cache(maxsize=1)
def get_data_dir() -> Path:
    data_dir = Path(getenv("DATA_DIR", "/data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@lru_cache(maxsize=1)
def get_duckdb_path() -> str:
    return str(get_data_dir() / "neo_team.db")


@lru_cache(maxsize=1)
def get_skills() -> Skills:
    skills_dir = Path(__file__).resolve().parent.parent / "skills"
    return Skills(loaders=[LocalSkills(str(skills_dir))])


@lru_cache(maxsize=1)
def get_learning_model():
    model_type = cast(ModelType, getenv("LEARNING_MODEL", "claude-sonnet"))
    return OpenRouter.create(model_type=model_type)


@lru_cache(maxsize=1)
def get_learned_knowledge_config() -> LearnedKnowledgeConfig:
    return LearnedKnowledgeConfig(
        agent_can_save=True,
        agent_can_search=True,
        enable_agent_tools=True,
        mode=LearningMode.AGENTIC,
        instructions="You are a learning machine that can save and search learned knowledge.",
    )


@lru_cache(maxsize=1)
def get_user_profile_config() -> UserProfileConfig:
    return UserProfileConfig(
        agent_can_update_profile=True,
        enable_update_profile=True,
        enable_agent_tools=True,
        mode=LearningMode.AGENTIC,
        instructions="You are a user profile that can save and search learned knowledge.",
    )


@lru_cache(maxsize=1)
def get_user_memory_config() -> UserMemoryConfig:
    return UserMemoryConfig(
        enable_update_memory=True,
        enable_add_memory=True,
        enable_agent_tools=True,
        mode=LearningMode.AGENTIC,
        instructions="You are a user memory that can save and search learned knowledge.",
    )


@lru_cache(maxsize=1)
def get_neo_team_learning_store() -> LearningMachine:
    return LearningMachine(
        namespace="global",
        model=get_learning_model(),
        db=get_db(),
        session_context=True,
        user_profile=get_user_profile_config(),
        user_memory=get_user_memory_config(),
        learned_knowledge=get_learned_knowledge_config(),
    )


# Backward-compatible exports for modules that import concrete values.
db = get_db()
duckdb_path = get_duckdb_path()
neo_skills = get_skills()
neo_team_learning_store = get_neo_team_learning_store()


__all__ = [
    "db",
    "duckdb_path",
    "neo_skills",
    "neo_team_learning_store",
    "get_db",
    "get_data_dir",
    "get_duckdb_path",
    "get_skills",
    "get_learning_model",
    "get_learned_knowledge_config",
    "get_user_profile_config",
    "get_user_memory_config",
    "get_neo_team_learning_store",
]
