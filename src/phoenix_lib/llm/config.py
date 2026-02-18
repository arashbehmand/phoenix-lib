"""LLM configuration model shared across Phoenix services."""

from typing import Any, Dict

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM configuration for a specific use case."""

    model: str = Field(
        "openai/gpt-4o-mini",
        description="LiteLLM model string (e.g., 'openai/gpt-4o-mini', 'anthropic/claude-3-5-sonnet')",
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional model parameters (temperature, max_tokens, thinking_level, etc.)",
    )
