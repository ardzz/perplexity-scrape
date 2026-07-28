"""
Model mapping between OpenAI-style model names and Perplexity internal models.
"""

from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    """Internal model configuration."""

    perplexity_model: str
    search_focus: str = "internet"
    mode: str = "copilot"
    sources: list[str] = field(default_factory=lambda: ["web", "scholar"])
    description: str = ""


# Model registry mapping OpenAI-style names to Perplexity configurations.
# Internal perplexity_model IDs mirror Perplexity's live model selector
# (mode="search" entries). Update these when Perplexity ships new models.
MODEL_REGISTRY: dict[str, ModelConfig] = {
    # =========================================================================
    # Perplexity Native / Auto
    # =========================================================================
    "best": ModelConfig(
        perplexity_model="pplx_pro",
        description="Best - auto-selects the best model per query",
    ),
    "auto": ModelConfig(
        perplexity_model="pplx_pro",
        description="Best - auto-selects the best model per query",
    ),
    "pplx_pro": ModelConfig(
        perplexity_model="pplx_pro",
        description="Best - auto-selects the best model per query",
    ),
    "sonar": ModelConfig(
        perplexity_model="experimental",
        description="Sonar 2 - Perplexity's latest in-house model",
    ),
    "sonar-2": ModelConfig(
        perplexity_model="experimental",
        description="Sonar 2 - Perplexity's latest in-house model",
    ),
    "experimental": ModelConfig(
        perplexity_model="experimental",
        description="Sonar 2 - Perplexity's latest in-house model",
    ),
    "pplx-alpha": ModelConfig(
        perplexity_model="pplx_alpha",
        description="Perplexity Alpha - deep research",
    ),
    "perplexity-alpha": ModelConfig(
        perplexity_model="pplx_alpha",
        description="Perplexity Alpha - deep research",
    ),
    # =========================================================================
    # Claude (Anthropic) - current: Sonnet 5, Opus 5
    # =========================================================================
    "claude-sonnet-5": ModelConfig(
        perplexity_model="claude50sonnet",
        description="Claude Sonnet 5",
    ),
    "claude50sonnet": ModelConfig(
        perplexity_model="claude50sonnet",
        description="Claude Sonnet 5",
    ),
    "claude-sonnet-5-thinking": ModelConfig(
        perplexity_model="claude50sonnetthinking",
        description="Claude Sonnet 5 with Reasoning (default)",
    ),
    "claude50sonnetthinking": ModelConfig(
        perplexity_model="claude50sonnetthinking",
        description="Claude Sonnet 5 with Reasoning",
    ),
    "claude-opus-5": ModelConfig(
        perplexity_model="claude50opus",
        description="Claude Opus 5",
    ),
    "claude50opus": ModelConfig(
        perplexity_model="claude50opus",
        description="Claude Opus 5",
    ),
    "claude-opus-5-thinking": ModelConfig(
        perplexity_model="claude50opusthinking",
        description="Claude Opus 5 with Reasoning",
    ),
    "claude50opusthinking": ModelConfig(
        perplexity_model="claude50opusthinking",
        description="Claude Opus 5 with Reasoning",
    ),
    # =========================================================================
    # GPT (OpenAI) - current: 5.6 Terra, 5.6 Sol
    # =========================================================================
    "gpt-5.6-terra": ModelConfig(
        perplexity_model="gpt56_terra",
        description="GPT-5.6 Terra",
    ),
    "gpt56_terra": ModelConfig(
        perplexity_model="gpt56_terra",
        description="GPT-5.6 Terra",
    ),
    "gpt-5.6-terra-thinking": ModelConfig(
        perplexity_model="gpt56_terra_thinking",
        description="GPT-5.6 Terra with Reasoning",
    ),
    "gpt56_terra_thinking": ModelConfig(
        perplexity_model="gpt56_terra_thinking",
        description="GPT-5.6 Terra with Reasoning",
    ),
    "gpt-5.6-sol": ModelConfig(
        perplexity_model="gpt56_sol",
        description="GPT-5.6 Sol - OpenAI's most powerful model",
    ),
    "gpt56_sol": ModelConfig(
        perplexity_model="gpt56_sol",
        description="GPT-5.6 Sol - OpenAI's most powerful model",
    ),
    "gpt-5.6-sol-thinking": ModelConfig(
        perplexity_model="gpt56_sol_thinking",
        description="GPT-5.6 Sol with Reasoning",
    ),
    "gpt56_sol_thinking": ModelConfig(
        perplexity_model="gpt56_sol_thinking",
        description="GPT-5.6 Sol with Reasoning",
    ),
    # Legacy OpenAI compatibility mappings
    "gpt-4": ModelConfig(
        perplexity_model="gpt56_terra",
        description="GPT-4 compatibility (maps to GPT-5.6 Terra)",
    ),
    "gpt-4o": ModelConfig(
        perplexity_model="gpt56_terra",
        description="GPT-4o compatibility (maps to GPT-5.6 Terra)",
    ),
    "gpt-4-turbo": ModelConfig(
        perplexity_model="gpt56_terra",
        description="GPT-4 Turbo compatibility (maps to GPT-5.6 Terra)",
    ),
    "gpt-3.5-turbo": ModelConfig(
        perplexity_model="pplx_alpha",
        description="GPT-3.5 compatibility (maps to Perplexity Alpha)",
    ),
    # =========================================================================
    # Gemini (Google) - current: 3.1 Pro
    # =========================================================================
    "gemini-3.1-pro": ModelConfig(
        perplexity_model="gemini31pro_low",
        description="Gemini 3.1 Pro",
    ),
    "gemini31pro_low": ModelConfig(
        perplexity_model="gemini31pro_low",
        description="Gemini 3.1 Pro",
    ),
    "gemini-3.1-pro-thinking": ModelConfig(
        perplexity_model="gemini31pro_high",
        description="Gemini 3.1 Pro with Reasoning",
    ),
    "gemini31pro_high": ModelConfig(
        perplexity_model="gemini31pro_high",
        description="Gemini 3.1 Pro with Reasoning",
    ),
    # =========================================================================
    # Grok (xAI) - current: 4.5
    # =========================================================================
    "grok-4.5": ModelConfig(
        perplexity_model="grok45low",
        description="Grok 4.5",
    ),
    "grok45low": ModelConfig(
        perplexity_model="grok45low",
        description="Grok 4.5",
    ),
    "grok-4.5-thinking": ModelConfig(
        perplexity_model="grok45medium",
        description="Grok 4.5 with Reasoning",
    ),
    "grok45medium": ModelConfig(
        perplexity_model="grok45medium",
        description="Grok 4.5 with Reasoning",
    ),
    # =========================================================================
    # Kimi (Moonshot) - current: K3
    # =========================================================================
    "kimi-k3": ModelConfig(
        perplexity_model="kimik3thinking",
        description="Kimi K3 (Thinking)",
    ),
    "kimi-k3-thinking": ModelConfig(
        perplexity_model="kimik3thinking",
        description="Kimi K3 (Thinking)",
    ),
    "kimik3thinking": ModelConfig(
        perplexity_model="kimik3thinking",
        description="Kimi K3 (Thinking)",
    ),
    # =========================================================================
    # GLM (Z.ai) - current: 5.2
    # =========================================================================
    "glm-5.2": ModelConfig(
        perplexity_model="glm_5_2",
        description="GLM 5.2 (Thinking)",
    ),
    "glm_5_2": ModelConfig(
        perplexity_model="glm_5_2",
        description="GLM 5.2 (Thinking)",
    ),
    # =========================================================================
    # Nemotron (NVIDIA) - current: 3 Ultra / 3 Super
    # =========================================================================
    "nemotron-3-ultra": ModelConfig(
        perplexity_model="nv_nemotron_3_ultra",
        description="Nemotron 3 Ultra 550B",
    ),
    "nv_nemotron_3_ultra": ModelConfig(
        perplexity_model="nv_nemotron_3_ultra",
        description="Nemotron 3 Ultra 550B",
    ),
    "nemotron-3-super": ModelConfig(
        perplexity_model="nv_nemotron_3_super",
        description="Nemotron 3 Super 120B",
    ),
    "nv_nemotron_3_super": ModelConfig(
        perplexity_model="nv_nemotron_3_super",
        description="Nemotron 3 Super 120B",
    ),
}

# Default model when unknown model is requested
DEFAULT_MODEL = "gpt56_terra_thinking"
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
