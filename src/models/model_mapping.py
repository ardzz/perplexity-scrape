"""
Model mapping between OpenAI-style model names and Perplexity internal models.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelConfig:
    """Internal model configuration."""

    perplexity_model: str
    search_focus: str = "internet"
    mode: str = "copilot"
    sources: list[str] = field(default_factory=lambda: ["web", "scholar"])
    description: str = ""


# Model registry mapping OpenAI-style names to Perplexity configurations
MODEL_REGISTRY: dict[str, ModelConfig] = {
    # =========================================================================
    # Perplexity Native Models
    # =========================================================================
    "sonar": ModelConfig(
        perplexity_model="experimental",
        description="Perplexity Sonar (experimental)",
    ),
    "experimental": ModelConfig(
        perplexity_model="experimental",
        description="Perplexity Sonar (experimental)",
    ),
    "pplx-alpha": ModelConfig(
        perplexity_model="pplx_alpha",
        description="Perplexity Alpha - faster responses",
    ),
    "perplexity-alpha": ModelConfig(
        perplexity_model="pplx_alpha",
        description="Perplexity Alpha - faster responses",
    ),
    # =========================================================================
    # Claude Models
    # =========================================================================
    # Claude 4.5 Sonnet
    "claude-4.5-sonnet": ModelConfig(
        perplexity_model="claude45sonnet",
        description="Claude 4.5 Sonnet",
    ),
    "claude45sonnet": ModelConfig(
        perplexity_model="claude45sonnet",
        description="Claude 4.5 Sonnet",
    ),
    "claude-sonnet-4-5-thinking": ModelConfig(
        perplexity_model="claude45sonnetthinking",
        description="Claude 4.5 Sonnet with Reasoning (recommended)",
    ),
    "claude-4.5-sonnet-thinking": ModelConfig(
        perplexity_model="claude45sonnetthinking",
        description="Claude 4.5 Sonnet with Reasoning",
    ),
    "claude45sonnetthinking": ModelConfig(
        perplexity_model="claude45sonnetthinking",
        description="Claude 4.5 Sonnet with Reasoning",
    ),
    # Claude 4.5 Opus
    "claude-4.5-opus": ModelConfig(
        perplexity_model="claude45opus",
        description="Claude 4.5 Opus",
    ),
    "claude45opus": ModelConfig(
        perplexity_model="claude45opus",
        description="Claude 4.5 Opus",
    ),
    "claude-opus-4-5-thinking": ModelConfig(
        perplexity_model="claude45opusthinking",
        description="Claude 4.5 Opus with Reasoning",
    ),
    "claude-4.5-opus-thinking": ModelConfig(
        perplexity_model="claude45opusthinking",
        description="Claude 4.5 Opus with Reasoning",
    ),
    "claude45opusthinking": ModelConfig(
        perplexity_model="claude45opusthinking",
        description="Claude 4.5 Opus with Reasoning",
    ),
    # =========================================================================
    # Gemini Models
    # =========================================================================
    "gemini-3-flash": ModelConfig(
        perplexity_model="gemini30flash",
        description="Gemini 3 Flash",
    ),
    "gemini30flash": ModelConfig(
        perplexity_model="gemini30flash",
        description="Gemini 3 Flash",
    ),
    "gemini-3-flash-thinking": ModelConfig(
        perplexity_model="gemini30flash_high",
        description="Gemini 3 Flash with Reasoning",
    ),
    "gemini30flash_high": ModelConfig(
        perplexity_model="gemini30flash_high",
        description="Gemini 3 Flash with Reasoning",
    ),
    "gemini-3-pro": ModelConfig(
        perplexity_model="gemini30pro",
        description="Gemini Pro with Reasoning",
    ),
    "gemini30pro": ModelConfig(
        perplexity_model="gemini30pro",
        description="Gemini Pro with Reasoning",
    ),
    # =========================================================================
    # GPT Models
    # =========================================================================
    "gpt-5.2": ModelConfig(
        perplexity_model="gpt52",
        description="GPT 5.2",
    ),
    "gpt52": ModelConfig(
        perplexity_model="gpt52",
        description="GPT 5.2",
    ),
    "gpt-5.2-thinking": ModelConfig(
        perplexity_model="gpt52_thinking",
        description="GPT 5.2 with Reasoning",
    ),
    "gpt52_thinking": ModelConfig(
        perplexity_model="gpt52_thinking",
        description="GPT 5.2 with Reasoning",
    ),
    # Legacy OpenAI compatibility mappings
    "gpt-4": ModelConfig(
        perplexity_model="gpt52",
        description="GPT-4 compatibility (maps to GPT 5.2)",
    ),
    "gpt-4o": ModelConfig(
        perplexity_model="gpt52",
        description="GPT-4o compatibility (maps to GPT 5.2)",
    ),
    "gpt-4-turbo": ModelConfig(
        perplexity_model="gpt52",
        description="GPT-4 Turbo compatibility (maps to GPT 5.2)",
    ),
    "gpt-3.5-turbo": ModelConfig(
        perplexity_model="pplx_alpha",
        description="GPT-3.5 compatibility (maps to Perplexity Alpha)",
    ),
    # =========================================================================
    # Grok Models
    # =========================================================================
    "grok-4.1": ModelConfig(
        perplexity_model="grok41nonreasoning",
        description="Grok 4.1",
    ),
    "grok41": ModelConfig(
        perplexity_model="grok41nonreasoning",
        description="Grok 4.1",
    ),
    "grok41nonreasoning": ModelConfig(
        perplexity_model="grok41nonreasoning",
        description="Grok 4.1",
    ),
    "grok-4.1-thinking": ModelConfig(
        perplexity_model="grok41reasoning",
        description="Grok 4.1 with Reasoning",
    ),
    "grok41reasoning": ModelConfig(
        perplexity_model="grok41reasoning",
        description="Grok 4.1 with Reasoning",
    ),
    # =========================================================================
    # Kimi Models
    # =========================================================================
    "kimi-k2": ModelConfig(
        perplexity_model="kimik2thinking",
        description="Kimi K2 Thinking",
    ),
    "kimi-k2-thinking": ModelConfig(
        perplexity_model="kimik2thinking",
        description="Kimi K2 Thinking",
    ),
    "kimik2thinking": ModelConfig(
        perplexity_model="kimik2thinking",
        description="Kimi K2 Thinking",
    ),
}

# Default model when unknown model is requested
DEFAULT_MODEL = "claude45sonnetthinking"
DEFAULT_MODE = "copilot"
DEFAULT_SEARCH_FOCUS = "internet"


def get_perplexity_model(openai_model: str) -> str:
    """
    Map an OpenAI-style model name to Perplexity model preference.

    Args:
        openai_model: The model name from the OpenAI API request

    Returns:
        The Perplexity model_preference value
    """
    config = MODEL_REGISTRY.get(openai_model)
    if config:
        return config.perplexity_model
    return DEFAULT_MODEL


def get_model_config(openai_model: str) -> ModelConfig:
    """
    Get full model configuration for an OpenAI-style model name.

    Args:
        openai_model: The model name from the OpenAI API request

    Returns:
        ModelConfig with all Perplexity settings
    """
    config = MODEL_REGISTRY.get(openai_model)
    if config:
        return config
    return ModelConfig(perplexity_model=DEFAULT_MODEL)


def list_available_models() -> list[str]:
    """Get list of available model IDs."""
    return list(MODEL_REGISTRY.keys())
