"""OpenRouter model abstraction used across agents."""

from __future__ import annotations

from os import getenv
from typing import Any, Literal

from agno.models.openrouter import OpenRouter as AgnoOpenRouter

DEFAULT_MODEL_ID = "anthropic/claude-sonnet-4.6"
ModelType = Literal[
    "default",
    "grok",
    "claude-opus",
    "claude-sonnet",
    "openai",
    "kimi",
    "perplexity",
]
MODEL_PRESETS: dict[ModelType, str] = {
    "default": DEFAULT_MODEL_ID,
    "grok": "x-ai/grok-4.3",
    "claude-opus": "anthropic/claude-opus-4.7",
    "claude-sonnet": "anthropic/claude-sonnet-4.6",
    "openai": "openai/gpt-5.5-pro",
    "kimi": "moonshotai/kimi-k2.6",
    "perplexity": "perplexity/sonar-reasoning-pro",
}


class OpenRouter(AgnoOpenRouter):
    """Project-level OpenRouter wrapper with a shared constructor."""

    @classmethod
    def create(
        cls,
        model_id: str | None = None,
        model_type: ModelType = "default",
        **kwargs: Any,
     ) -> "OpenRouter":
        """
            Create an OpenRouter model instance with project defaults.

            Environment variables:
            - OPENROUTER_MODEL: default model id
            - OPENROUTER_MODEL_<PRESET_NAME>: per-preset model id override
              Example: OPENROUTER_MODEL_CLAUDE, OPENROUTER_MODEL_GEMINI_PRO
            - OPENROUTER_APP_URL: optional HTTP-Referer header
            - OPENROUTER_APP_NAME: optional X-Title header
            """
        if model_id:
            resolved_model_id = model_id
        else:
            preset_id = MODEL_PRESETS.get(model_type)
            if not preset_id:
                supported = ", ".join(MODEL_PRESETS.keys())
                raise ValueError(f"Unsupported model_type '{model_type}'. Use one of: {supported}")
            env_key = f"OPENROUTER_MODEL_{model_type.upper().replace('-', '_')}"
            if model_type == "default":
                resolved_model_id = getenv("OPENROUTER_MODEL", preset_id)
            else:
                resolved_model_id = getenv(env_key, preset_id)

        extra_headers = dict(kwargs.pop("extra_headers", {}) or {})
        app_url = getenv("OPENROUTER_APP_URL", "")
        app_name = getenv("OPENROUTER_APP_NAME", "")

        if app_url and "HTTP-Referer" not in extra_headers:
            extra_headers["HTTP-Referer"] = app_url
        if app_name and "X-Title" not in extra_headers:
            extra_headers["X-Title"] = app_name

        if extra_headers:
            kwargs["extra_headers"] = extra_headers

        return cls(id=resolved_model_id, **kwargs)

    # Preset model creators
    @classmethod
    def create_claude_opus(cls, **kwargs: Any) -> "OpenRouter":
        """Create a Claude Opus preset model instance."""
        return cls.create(model_type="claude-opus", **kwargs)

    @classmethod
    def create_claude_sonnet(cls, **kwargs: Any) -> "OpenRouter":
        """Create a Claude Sonnet preset model instance."""
        return cls.create(model_type="claude-sonnet", **kwargs)

    @classmethod
    def create_grok(cls, **kwargs: Any) -> "OpenRouter":
        """Create a Grok preset model instance."""
        return cls.create(model_type="grok", **kwargs)

    @classmethod
    def create_kimi(cls, **kwargs: Any) -> "OpenRouter":
        """Create a Kimi K2.5 preset model instance."""
        return cls.create(model_type="kimi", **kwargs)

    @classmethod
    def create_perplexity(cls, **kwargs: Any) -> "OpenRouter":
        """Create a Perplexity preset model instance."""
        return cls.create(model_type="perplexity", **kwargs)

    @classmethod
    def create_openai(cls, **kwargs: Any) -> "OpenRouter":
        """Create a OpenAI preset model instance."""
        return cls.create(model_type="openai", **kwargs)
