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
from dataclasses import dataclass, field
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


# ============================================================================
# ModelConfig Dataclass Tests
# ============================================================================


class TestModelConfig:
    """Tests for ModelConfig dataclass."""

    def test_model_config_default_values(self):
        """Test ModelConfig has correct default values."""
        config = ModelConfig(perplexity_model="test_model")

        assert config.perplexity_model == "test_model"
        assert config.search_focus == "internet"
        assert config.mode == "copilot"
        assert config.sources == ["web", "scholar"]
        assert config.description == ""

    def test_model_config_custom_values(self):
        """Test ModelConfig with custom values."""
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
        """Test that default sources list doesn't share references."""
        config1 = ModelConfig(perplexity_model="model1")
        config2 = ModelConfig(perplexity_model="model2")

        # Modify one list
        config1.sources.append("custom")

        # Other config should not be affected
        assert config2.sources == ["web", "scholar"]

    def test_model_config_with_partial_custom_values(self):
        """Test ModelConfig with only some custom values."""
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

    def test_valid_model_claude_sonnet(self):
        """Test mapping Claude 4.5 Sonnet."""
        result = get_perplexity_model("claude-4.5-sonnet")
        assert result == "claude45sonnet"

    def test_valid_model_gpt_5_2(self):
        """Test mapping GPT 5.2."""
        result = get_perplexity_model("gpt-5.2")
        assert result == "gpt52"

    def test_valid_model_claude_sonnet_thinking(self):
        """Test mapping Claude Sonnet with Reasoning."""
        result = get_perplexity_model("claude-4.5-sonnet-thinking")
        assert result == "claude45sonnetthinking"

    def test_valid_model_gpt_5_2_thinking(self):
        """Test mapping GPT 5.2 with Reasoning."""
        result = get_perplexity_model("gpt-5.2-thinking")
        assert result == "gpt52_thinking"

    def test_valid_model_gemini_flash(self):
        """Test mapping Gemini Flash."""
        result = get_perplexity_model("gemini-3-flash")
        assert result == "gemini30flash"

    def test_valid_model_grok(self):
        """Test mapping Grok model."""
        result = get_perplexity_model("grok-4.1")
        assert result == "grok41nonreasoning"

    def test_valid_model_kimi(self):
        """Test mapping Kimi model."""
        result = get_perplexity_model("kimi-k2.5-thinking")
        assert result == "kimik25thinking"

    def test_unknown_model_returns_default(self):
        """Test unknown model returns DEFAULT_MODEL."""
        result = get_perplexity_model("unknown-model-xyz")
        assert result == DEFAULT_MODEL
        assert result == "claude45sonnetthinking"

    def test_empty_string_returns_default(self):
        """Test empty string returns DEFAULT_MODEL."""
        result = get_perplexity_model("")
        assert result == DEFAULT_MODEL

    def test_case_sensitive_model_name(self):
        """Test model names are case-sensitive."""
        # Lowercase should not match uppercase keys
        result = get_perplexity_model("CLAUDE-4.5-SONNET")
        assert result == DEFAULT_MODEL

    def test_internal_perplexity_model_names(self):
        """Test using internal Perplexity model names directly."""
        result = get_perplexity_model("claude45sonnet")
        assert result == "claude45sonnet"

    def test_legacy_gpt_4_compatibility(self):
        """Test legacy GPT-4 mapping for compatibility."""
        result = get_perplexity_model("gpt-4")
        assert result == "gpt52"

    def test_legacy_gpt_4o_compatibility(self):
        """Test legacy GPT-4o mapping for compatibility."""
        result = get_perplexity_model("gpt-4o")
        assert result == "gpt52"

    def test_perplexity_alpha_model(self):
        """Test Perplexity Alpha models."""
        result = get_perplexity_model("pplx-alpha")
        assert result == "pplx_alpha"


# ============================================================================
# get_model_config() Tests
# ============================================================================


class TestGetModelConfig:
    """Tests for get_model_config() function."""

    def test_valid_model_returns_full_config(self):
        """Test valid model returns full ModelConfig."""
        config = get_model_config("claude-4.5-sonnet")

        assert isinstance(config, ModelConfig)
        assert config.perplexity_model == "claude45sonnet"
        assert config.search_focus == "internet"
        assert config.mode == "copilot"
        assert config.sources == ["web", "scholar"]

    def test_valid_model_with_description(self):
        """Test valid model config includes description."""
        config = get_model_config("claude-4.5-sonnet")
        assert config.description == "Claude 4.5 Sonnet"

    def test_unknown_model_returns_default_config(self):
        """Test unknown model returns config with DEFAULT_MODEL."""
        config = get_model_config("unknown-model-xyz")

        assert isinstance(config, ModelConfig)
        assert config.perplexity_model == DEFAULT_MODEL
        assert config.search_focus == "internet"
        assert config.mode == "copilot"

    def test_unknown_model_has_empty_description(self):
        """Test unknown model returns config with empty description."""
        config = get_model_config("unknown-model-xyz")
        assert config.description == ""

    def test_config_for_gpt_5_2(self):
        """Test full config for GPT 5.2."""
        config = get_model_config("gpt-5.2")
        assert config.perplexity_model == "gpt52"
        assert config.description == "GPT 5.2"

    def test_config_for_gemini(self):
        """Test full config for Gemini."""
        config = get_model_config("gemini-3-flash")
        assert config.perplexity_model == "gemini30flash"
        assert config.description == "Gemini 3 Flash"

    def test_empty_string_returns_default_config(self):
        """Test empty string returns default config."""
        config = get_model_config("")
        assert config.perplexity_model == DEFAULT_MODEL

    def test_config_immutability_across_calls(self):
        """Test configs are independent across calls."""
        config1 = get_model_config("claude-4.5-sonnet")
        config2 = get_model_config("gpt-5.2")

        # Modify one config's sources
        config1.sources.append("custom")

        # Other config should not be affected (testing independence)
        # Note: We're testing the returned configs are separate instances
        assert config1.sources != config2.sources


# ============================================================================
# list_available_models() Tests
# ============================================================================


class TestListAvailableModels:
    """Tests for list_available_models() function."""

    def test_returns_list(self):
        """Test function returns a list."""
        result = list_available_models()
        assert isinstance(result, list)

    def test_returns_non_empty_list(self):
        """Test function returns non-empty list."""
        result = list_available_models()
        assert len(result) > 0

    def test_contains_all_registry_keys(self):
        """Test returned list contains all MODEL_REGISTRY keys."""
        result = list_available_models()
        registry_keys = set(MODEL_REGISTRY.keys())
        result_set = set(result)

        assert registry_keys == result_set

    def test_contains_claude_models(self):
        """Test list includes Claude models."""
        result = list_available_models()

        assert "claude-4.5-sonnet" in result
        assert "claude45sonnet" in result
        assert "claude-4.5-sonnet-thinking" in result
        assert "claude45sonnetthinking" in result

    def test_contains_gpt_models(self):
        """Test list includes GPT models."""
        result = list_available_models()

        assert "gpt-5.2" in result
        assert "gpt52" in result
        assert "gpt-5.2-thinking" in result
        assert "gpt52_thinking" in result

    def test_contains_gemini_models(self):
        """Test list includes Gemini models."""
        result = list_available_models()

        assert "gemini-3-flash" in result
        assert "gemini30flash" in result
        assert "gemini-3-flash-thinking" in result

    def test_contains_grok_models(self):
        """Test list includes Grok models."""
        result = list_available_models()

        assert "grok-4.1" in result
        assert "grok41" in result
        assert "grok-4.1-thinking" in result

    def test_contains_kimi_models(self):
        """Test list includes Kimi models."""
        result = list_available_models()

        assert "kimi-k2.5" in result
        assert "kimi-k2.5-thinking" in result
        assert "kimik25thinking" in result

    def test_contains_legacy_gpt_models(self):
        """Test list includes legacy GPT compatibility mappings."""
        result = list_available_models()

        assert "gpt-4" in result
        assert "gpt-4o" in result
        assert "gpt-4-turbo" in result
        assert "gpt-3.5-turbo" in result

    def test_contains_perplexity_models(self):
        """Test list includes native Perplexity models."""
        result = list_available_models()

        assert "sonar" in result
        assert "experimental" in result
        assert "pplx-alpha" in result
        assert "perplexity-alpha" in result

    def test_model_count_matches_registry(self):
        """Test number of models matches MODEL_REGISTRY size."""
        result = list_available_models()
        assert len(result) == len(MODEL_REGISTRY)


# ============================================================================
# MODEL_REGISTRY Structure Tests
# ============================================================================


class TestModelRegistry:
    """Tests for MODEL_REGISTRY structure and content."""

    def test_registry_is_dict(self):
        """Test MODEL_REGISTRY is a dictionary."""
        assert isinstance(MODEL_REGISTRY, dict)

    def test_registry_keys_are_strings(self):
        """Test all registry keys are strings."""
        for key in MODEL_REGISTRY.keys():
            assert isinstance(key, str)

    def test_registry_values_are_model_configs(self):
        """Test all registry values are ModelConfig instances."""
        for value in MODEL_REGISTRY.values():
            assert isinstance(value, ModelConfig)

    def test_all_model_configs_have_perplexity_model(self):
        """Test all ModelConfig entries have perplexity_model."""
        for key, config in MODEL_REGISTRY.items():
            assert hasattr(config, "perplexity_model")
            assert isinstance(config.perplexity_model, str)
            assert config.perplexity_model  # Non-empty string

    def test_claude_sonnet_entries(self):
        """Test Claude 4.5 Sonnet entries."""
        # All should map to same perplexity_model
        assert MODEL_REGISTRY["claude-4.5-sonnet"].perplexity_model == "claude45sonnet"
        assert MODEL_REGISTRY["claude45sonnet"].perplexity_model == "claude45sonnet"

    def test_claude_sonnet_thinking_entries(self):
        """Test Claude 4.5 Sonnet Thinking entries."""
        assert (
            MODEL_REGISTRY["claude-4.5-sonnet-thinking"].perplexity_model
            == "claude45sonnetthinking"
        )
        assert (
            MODEL_REGISTRY["claude45sonnetthinking"].perplexity_model
            == "claude45sonnetthinking"
        )

    def test_claude_opus_entries(self):
        """Test Claude 4.5 Opus entries."""
        assert MODEL_REGISTRY["claude-4.5-opus"].perplexity_model == "claude45opus"
        assert MODEL_REGISTRY["claude45opus"].perplexity_model == "claude45opus"

    def test_claude_opus_thinking_entries(self):
        """Test Claude 4.5 Opus Thinking entries."""
        assert (
            MODEL_REGISTRY["claude-4.5-opus-thinking"].perplexity_model
            == "claude45opusthinking"
        )
        assert (
            MODEL_REGISTRY["claude45opusthinking"].perplexity_model
            == "claude45opusthinking"
        )

    def test_gpt_5_2_entries(self):
        """Test GPT 5.2 entries."""
        assert MODEL_REGISTRY["gpt-5.2"].perplexity_model == "gpt52"
        assert MODEL_REGISTRY["gpt52"].perplexity_model == "gpt52"

    def test_gpt_5_2_thinking_entries(self):
        """Test GPT 5.2 Thinking entries."""
        assert MODEL_REGISTRY["gpt-5.2-thinking"].perplexity_model == "gpt52_thinking"
        assert MODEL_REGISTRY["gpt52_thinking"].perplexity_model == "gpt52_thinking"

    def test_gemini_flash_entries(self):
        """Test Gemini Flash entries."""
        assert MODEL_REGISTRY["gemini-3-flash"].perplexity_model == "gemini30flash"
        assert MODEL_REGISTRY["gemini30flash"].perplexity_model == "gemini30flash"

    def test_gemini_flash_thinking_entries(self):
        """Test Gemini Flash Thinking entries."""
        assert (
            MODEL_REGISTRY["gemini-3-flash-thinking"].perplexity_model
            == "gemini30flash_high"
        )
        assert (
            MODEL_REGISTRY["gemini30flash_high"].perplexity_model
            == "gemini30flash_high"
        )

    def test_gemini_pro_entries(self):
        """Test Gemini Pro entries."""
        assert MODEL_REGISTRY["gemini-3-pro"].perplexity_model == "gemini30pro"
        assert MODEL_REGISTRY["gemini30pro"].perplexity_model == "gemini30pro"

    def test_grok_entries(self):
        """Test Grok entries."""
        assert MODEL_REGISTRY["grok-4.1"].perplexity_model == "grok41nonreasoning"
        assert MODEL_REGISTRY["grok41"].perplexity_model == "grok41nonreasoning"
        assert (
            MODEL_REGISTRY["grok41nonreasoning"].perplexity_model
            == "grok41nonreasoning"
        )

    def test_grok_thinking_entries(self):
        """Test Grok with Reasoning entries."""
        assert MODEL_REGISTRY["grok-4.1-thinking"].perplexity_model == "grok41reasoning"
        assert MODEL_REGISTRY["grok41reasoning"].perplexity_model == "grok41reasoning"

    def test_kimi_entries(self):
        """Test Kimi entries."""
        assert MODEL_REGISTRY["kimi-k2.5"].perplexity_model == "kimik25thinking"
        assert (
            MODEL_REGISTRY["kimi-k2.5-thinking"].perplexity_model == "kimik25thinking"
        )
        assert MODEL_REGISTRY["kimik25thinking"].perplexity_model == "kimik25thinking"

    def test_legacy_gpt_4_mapping(self):
        """Test legacy GPT-4 maps to GPT 5.2."""
        assert MODEL_REGISTRY["gpt-4"].perplexity_model == "gpt52"

    def test_legacy_gpt_4o_mapping(self):
        """Test legacy GPT-4o maps to GPT 5.2."""
        assert MODEL_REGISTRY["gpt-4o"].perplexity_model == "gpt52"

    def test_legacy_gpt_4_turbo_mapping(self):
        """Test legacy GPT-4 Turbo maps to GPT 5.2."""
        assert MODEL_REGISTRY["gpt-4-turbo"].perplexity_model == "gpt52"

    def test_legacy_gpt_3_5_turbo_mapping(self):
        """Test legacy GPT-3.5 Turbo maps to Perplexity Alpha."""
        assert MODEL_REGISTRY["gpt-3.5-turbo"].perplexity_model == "pplx_alpha"

    def test_perplexity_sonar_entry(self):
        """Test Perplexity Sonar entry."""
        assert MODEL_REGISTRY["sonar"].perplexity_model == "experimental"

    def test_perplexity_alpha_entry(self):
        """Test Perplexity Alpha entry."""
        assert MODEL_REGISTRY["pplx-alpha"].perplexity_model == "pplx_alpha"
        assert MODEL_REGISTRY["perplexity-alpha"].perplexity_model == "pplx_alpha"

    def test_all_configs_have_default_search_focus(self):
        """Test all configs have search_focus (default or custom)."""
        for key, config in MODEL_REGISTRY.items():
            assert hasattr(config, "search_focus")

    def test_all_configs_have_default_mode(self):
        """Test all configs have mode (default or custom)."""
        for key, config in MODEL_REGISTRY.items():
            assert hasattr(config, "mode")

    def test_all_configs_have_sources(self):
        """Test all configs have sources list."""
        for key, config in MODEL_REGISTRY.items():
            assert hasattr(config, "sources")
            assert isinstance(config.sources, list)


# ============================================================================
# Constants Tests
# ============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_default_model_constant(self):
        """Test DEFAULT_MODEL constant is set."""
        assert DEFAULT_MODEL == "claude45sonnetthinking"
        assert isinstance(DEFAULT_MODEL, str)

    def test_default_mode_constant(self):
        """Test DEFAULT_MODE constant is set."""
        assert DEFAULT_MODE == "copilot"
        assert isinstance(DEFAULT_MODE, str)

    def test_default_search_focus_constant(self):
        """Test DEFAULT_SEARCH_FOCUS constant is set."""
        assert DEFAULT_SEARCH_FOCUS == "internet"
        assert isinstance(DEFAULT_SEARCH_FOCUS, str)

    def test_default_model_is_in_registry(self):
        """Test DEFAULT_MODEL exists in MODEL_REGISTRY."""
        assert DEFAULT_MODEL in MODEL_REGISTRY

    def test_default_mode_is_valid(self):
        """Test DEFAULT_MODE is a known mode."""
        # Modes observed in registry: "copilot", "search"
        assert DEFAULT_MODE in ["copilot", "search"]

    def test_default_search_focus_is_valid(self):
        """Test DEFAULT_SEARCH_FOCUS is a known focus."""
        # Focus values observed: "internet", "academic"
        assert DEFAULT_SEARCH_FOCUS in ["internet", "academic"]


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_get_model_config_uses_registry(self):
        """Test get_model_config returns actual registry entries."""
        model_name = "claude-4.5-sonnet"
        config = get_model_config(model_name)
        registry_config = MODEL_REGISTRY[model_name]

        assert config.perplexity_model == registry_config.perplexity_model
        assert config.search_focus == registry_config.search_focus
        assert config.mode == registry_config.mode

    def test_get_perplexity_model_matches_get_model_config(self):
        """Test get_perplexity_model result matches get_model_config."""
        model_name = "gpt-5.2"

        perplexity_model = get_perplexity_model(model_name)
        config = get_model_config(model_name)

        assert perplexity_model == config.perplexity_model

    def test_list_available_models_all_work_with_get_model_config(self):
        """Test all listed models work with get_model_config."""
        models = list_available_models()

        for model in models:
            config = get_model_config(model)
            assert isinstance(config, ModelConfig)
            assert config.perplexity_model

    def test_list_available_models_all_work_with_get_perplexity_model(self):
        """Test all listed models work with get_perplexity_model."""
        models = list_available_models()

        for model in models:
            perplexity_model = get_perplexity_model(model)
            assert isinstance(perplexity_model, str)
            assert perplexity_model  # Non-empty

    def test_multiple_aliases_for_same_model(self):
        """Test multiple aliases map to same perplexity model."""
        aliases = ["claude-4.5-sonnet", "claude45sonnet"]
        perplexity_models = [get_perplexity_model(alias) for alias in aliases]

        # All should map to same perplexity model
        assert len(set(perplexity_models)) == 1
        assert perplexity_models[0] == "claude45sonnet"

    def test_unknown_model_behavior_consistency(self):
        """Test unknown models consistently return DEFAULT_MODEL."""
        unknown_models = [
            "invalid-model",
            "fake-gpt-10",
            "nonexistent",
            "xyz-123-abc",
        ]

        results = [get_perplexity_model(model) for model in unknown_models]

        # All should return DEFAULT_MODEL
        assert all(result == DEFAULT_MODEL for result in results)
        assert all(result == "claude45sonnetthinking" for result in results)
