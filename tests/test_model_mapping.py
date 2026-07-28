"""
Unit tests for src/models/model_mapping.py

Tests cover:
- ModelConfig dataclass with default and custom values
- get_perplexity_model() function
- get_model_config() function
- list_available_models() function
- MODEL_REGISTRY structure and content
"""

import pytest
from src.models.model_mapping import (
    ModelConfig,
    MODEL_REGISTRY,
    DEFAULT_MODEL,
    DEFAULT_MODE,
    DEFAULT_SEARCH_FOCUS,
    get_perplexity_model,
    get_model_config,
    list_available_models,
)


# Representative (alias -> internal perplexity_model) pairs from the current
# registry. Update this list when the model selector changes.
CURRENT_MAPPINGS = [
    ("best", "pplx_pro"),
    ("sonar", "experimental"),
    ("sonar-2", "experimental"),
    ("pplx-alpha", "pplx_alpha"),
    ("claude-sonnet-5", "claude50sonnet"),
    ("claude-sonnet-5-thinking", "claude50sonnetthinking"),
    ("claude-opus-5", "claude50opus"),
    ("claude-opus-5-thinking", "claude50opusthinking"),
    ("gpt-5.6-terra", "gpt56_terra"),
    ("gpt-5.6-terra-thinking", "gpt56_terra_thinking"),
    ("gpt-5.6-sol", "gpt56_sol"),
    ("gpt-5.6-sol-thinking", "gpt56_sol_thinking"),
    ("gemini-3.1-pro", "gemini31pro_low"),
    ("gemini-3.1-pro-thinking", "gemini31pro_high"),
    ("grok-4.5", "grok45low"),
    ("grok-4.5-thinking", "grok45medium"),
    ("kimi-k3", "kimik3thinking"),
    ("glm-5.2", "glm_5_2"),
    ("nemotron-3-ultra", "nv_nemotron_3_ultra"),
    ("nemotron-3-super", "nv_nemotron_3_super"),
    # Legacy OpenAI compatibility aliases
    ("gpt-4", "gpt56_terra"),
    ("gpt-4o", "gpt56_terra"),
    ("gpt-3.5-turbo", "pplx_alpha"),
]


# ============================================================================
# ModelConfig Dataclass Tests
# ============================================================================


class TestModelConfig:
    """Tests for ModelConfig dataclass."""

    def test_model_config_default_values(self):
        config = ModelConfig(perplexity_model="test_model")

        assert config.perplexity_model == "test_model"
        assert config.search_focus == "internet"
        assert config.mode == "copilot"
        assert config.sources == ["web", "scholar"]
        assert config.description == ""

    def test_model_config_custom_values(self):
        config = ModelConfig(
            perplexity_model="custom_model",
            search_focus="academic",
            mode="search",
            sources=["web"],
            description="Custom test model",
        )

        assert config.perplexity_model == "custom_model"
        assert config.search_focus == "academic"
        assert config.mode == "search"
        assert config.sources == ["web"]
        assert config.description == "Custom test model"

    def test_model_config_default_sources_independence(self):
        """Default sources list must not share references between instances."""
        config1 = ModelConfig(perplexity_model="model1")
        config2 = ModelConfig(perplexity_model="model2")

        config1.sources.append("custom")

        assert config2.sources == ["web", "scholar"]

    def test_model_config_with_partial_custom_values(self):
        config = ModelConfig(
            perplexity_model="model",
            search_focus="academic",
        )

        assert config.perplexity_model == "model"
        assert config.search_focus == "academic"
        assert config.mode == "copilot"  # Default
        assert config.sources == ["web", "scholar"]  # Default


# ============================================================================
# get_perplexity_model() Tests
# ============================================================================


class TestGetPerplexityModel:
    """Tests for get_perplexity_model() function."""

    @pytest.mark.parametrize("alias,expected", CURRENT_MAPPINGS)
    def test_valid_model_mappings(self, alias, expected):
        assert get_perplexity_model(alias) == expected

    def test_unknown_model_returns_default(self):
        result = get_perplexity_model("unknown-model-xyz")
        assert result == DEFAULT_MODEL
        assert result == "gpt56_terra_thinking"

    def test_empty_string_returns_default(self):
        assert get_perplexity_model("") == DEFAULT_MODEL

    def test_case_sensitive_model_name(self):
        """Model names are case-sensitive; wrong case falls back to default."""
        assert get_perplexity_model("CLAUDE-SONNET-5") == DEFAULT_MODEL

    def test_internal_perplexity_model_names(self):
        """Internal Perplexity IDs are self-mapping."""
        assert get_perplexity_model("claude50sonnet") == "claude50sonnet"
        assert get_perplexity_model("gpt56_terra") == "gpt56_terra"

    def test_legacy_gpt_4_compatibility(self):
        assert get_perplexity_model("gpt-4") == "gpt56_terra"
        assert get_perplexity_model("gpt-4o") == "gpt56_terra"


# ============================================================================
# get_model_config() Tests
# ============================================================================


class TestGetModelConfig:
    """Tests for get_model_config() function."""

    def test_valid_model_returns_full_config(self):
        config = get_model_config("claude-sonnet-5")

        assert isinstance(config, ModelConfig)
        assert config.perplexity_model == "claude50sonnet"
        assert config.search_focus == "internet"
        assert config.mode == "copilot"
        assert config.sources == ["web", "scholar"]

    def test_valid_model_with_description(self):
        config = get_model_config("claude-sonnet-5")
        assert config.description == "Claude Sonnet 5"

    def test_unknown_model_returns_default_config(self):
        config = get_model_config("unknown-model-xyz")

        assert isinstance(config, ModelConfig)
        assert config.perplexity_model == DEFAULT_MODEL
        assert config.search_focus == "internet"
        assert config.mode == "copilot"

    def test_unknown_model_has_empty_description(self):
        config = get_model_config("unknown-model-xyz")
        assert config.description == ""

    def test_empty_string_returns_default_config(self):
        config = get_model_config("")
        assert config.perplexity_model == DEFAULT_MODEL

    def test_config_immutability_across_calls(self):
        config1 = get_model_config("claude-sonnet-5")
        config2 = get_model_config("gpt-5.6-terra")

        config1.sources.append("custom")

        assert config1.sources != config2.sources


# ============================================================================
# list_available_models() Tests
# ============================================================================


class TestListAvailableModels:
    """Tests for list_available_models() function."""

    def test_returns_non_empty_list(self):
        result = list_available_models()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_contains_all_registry_keys(self):
        result = list_available_models()
        assert set(result) == set(MODEL_REGISTRY.keys())

    @pytest.mark.parametrize("alias,_expected", CURRENT_MAPPINGS)
    def test_contains_current_models(self, alias, _expected):
        assert alias in list_available_models()

    def test_contains_perplexity_native_models(self):
        result = list_available_models()
        assert "sonar" in result
        assert "experimental" in result
        assert "pplx-alpha" in result
        assert "perplexity-alpha" in result

    def test_model_count_matches_registry(self):
        assert len(list_available_models()) == len(MODEL_REGISTRY)


# ============================================================================
# MODEL_REGISTRY Structure Tests
# ============================================================================


class TestModelRegistry:
    """Tests for MODEL_REGISTRY structure and content."""

    def test_registry_is_dict(self):
        assert isinstance(MODEL_REGISTRY, dict)

    def test_registry_keys_are_strings(self):
        for key in MODEL_REGISTRY.keys():
            assert isinstance(key, str)

    def test_registry_values_are_model_configs(self):
        for value in MODEL_REGISTRY.values():
            assert isinstance(value, ModelConfig)

    def test_all_model_configs_have_nonempty_perplexity_model(self):
        for config in MODEL_REGISTRY.values():
            assert isinstance(config.perplexity_model, str)
            assert config.perplexity_model  # Non-empty

    @pytest.mark.parametrize("alias,expected", CURRENT_MAPPINGS)
    def test_registry_entries(self, alias, expected):
        assert MODEL_REGISTRY[alias].perplexity_model == expected

    def test_internal_ids_are_self_mapping(self):
        """Every internal ID present as a key maps to itself."""
        for _alias, internal in CURRENT_MAPPINGS:
            if internal in MODEL_REGISTRY:
                assert MODEL_REGISTRY[internal].perplexity_model == internal

    def test_all_configs_have_sources_list(self):
        for config in MODEL_REGISTRY.values():
            assert isinstance(config.sources, list)


# ============================================================================
# Constants Tests
# ============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_default_model_constant(self):
        assert DEFAULT_MODEL == "gpt56_terra_thinking"
        assert isinstance(DEFAULT_MODEL, str)

    def test_default_mode_constant(self):
        assert DEFAULT_MODE == "copilot"

    def test_default_search_focus_constant(self):
        assert DEFAULT_SEARCH_FOCUS == "internet"

    def test_default_model_is_in_registry(self):
        assert DEFAULT_MODEL in MODEL_REGISTRY

    def test_default_mode_is_valid(self):
        assert DEFAULT_MODE in ["copilot", "search"]

    def test_default_search_focus_is_valid(self):
        assert DEFAULT_SEARCH_FOCUS in ["internet", "academic"]


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_get_model_config_uses_registry(self):
        model_name = "claude-sonnet-5"
        config = get_model_config(model_name)
        registry_config = MODEL_REGISTRY[model_name]

        assert config.perplexity_model == registry_config.perplexity_model
        assert config.search_focus == registry_config.search_focus
        assert config.mode == registry_config.mode

    def test_get_perplexity_model_matches_get_model_config(self):
        model_name = "gpt-5.6-terra"
        assert get_perplexity_model(model_name) == get_model_config(model_name).perplexity_model

    def test_list_available_models_all_resolve(self):
        for model in list_available_models():
            config = get_model_config(model)
            assert isinstance(config, ModelConfig)
            assert config.perplexity_model
            assert get_perplexity_model(model)

    def test_multiple_aliases_for_same_model(self):
        aliases = ["claude-sonnet-5", "claude50sonnet"]
        resolved = {get_perplexity_model(a) for a in aliases}
        assert resolved == {"claude50sonnet"}

    def test_unknown_model_behavior_consistency(self):
        unknown_models = ["invalid-model", "fake-gpt-10", "nonexistent", "xyz-123-abc"]
        results = [get_perplexity_model(m) for m in unknown_models]
        assert all(r == DEFAULT_MODEL for r in results)
