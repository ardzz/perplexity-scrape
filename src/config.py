"""
Configuration management for the OpenAI-compatible REST API.

Loads environment variables and provides centralized configuration.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Application configuration."""

    # REST API settings
    rest_api_host: str = "127.0.0.1"
    rest_api_port: int = 8045

    # Perplexity defaults
    default_model: str = "claude45sonnetthinking"
    default_mode: str = "copilot"
    default_search_focus: str = "internet"

    # API settings
    api_title: str = "Perplexity OpenAI-Compatible API"
    api_version: str = "1.0.0"

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            rest_api_host=os.getenv("REST_API_HOST", "127.0.0.1"),
            rest_api_port=int(os.getenv("REST_API_PORT", "8045")),
            default_model=os.getenv("DEFAULT_MODEL", "claude45sonnetthinking"),
            default_mode=os.getenv("DEFAULT_MODE", "copilot"),
            default_search_focus=os.getenv("DEFAULT_SEARCH_FOCUS", "internet"),
        )


# Global config instance
config = Config.from_env()
