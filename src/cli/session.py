"""
Chat Session Manager

Manages conversation history, model selection, and session persistence.
Models are loaded dynamically from opencode-provider.json.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


# ─── Dynamic model loading from opencode-provider.json ───────────────────────

def _load_models_from_provider(provider_path: Optional[str] = None) -> list[dict]:
    """
    Load model list from opencode-provider.json.
    Returns list of {id, name, thinking, context} dicts.
    """
    search_paths = [
        provider_path,
        Path(__file__).parent.parent.parent / "opencode-provider.json",
        Path.cwd() / "opencode-provider.json",
    ]

    for path in search_paths:
        if path is None:
            continue
        p = Path(path)
        if p.exists():
            try:
                with open(p) as f:
                    data = json.load(f)
                # Structure: {"perplexity-scrape": {"models": {id: {name, ...}}}}
                for provider_data in data.values():
                    models_dict = provider_data.get("models", {})
                    result = []
                    for model_id, model_info in models_dict.items():
                        result.append({
                            "id": model_id,
                            "name": model_info.get("name", model_id),
                            "thinking": model_info.get("thinking", False),
                            "context": model_info.get("limit", {}).get("context", 0),
                        })
                    if result:
                        return result
            except Exception:
                pass

    # Fallback hardcoded list (mirrors opencode-provider.json)
    return [
        {"id": "claude45sonnetthinking", "name": "Claude 4.5 Sonnet + Reasoning", "thinking": True,  "context": 200000},
        {"id": "claude45sonnet",         "name": "Claude 4.5 Sonnet",             "thinking": False, "context": 200000},
        {"id": "claude45opusthinking",   "name": "Claude 4.5 Opus + Reasoning",   "thinking": True,  "context": 200000},
        {"id": "claude45opus",           "name": "Claude 4.5 Opus",               "thinking": False, "context": 200000},
        {"id": "gemini30flash",          "name": "Gemini 3 Flash",                "thinking": False, "context": 1048576},
        {"id": "gemini30flash_high",     "name": "Gemini 3 Flash + Reasoning",    "thinking": True,  "context": 1048576},
        {"id": "gemini30pro",            "name": "Gemini 3 Pro + Reasoning",      "thinking": True,  "context": 1048576},
        {"id": "gpt52",                  "name": "GPT-5.2",                       "thinking": False, "context": 128000},
        {"id": "gpt52_thinking",         "name": "GPT-5.2 + Reasoning",           "thinking": True,  "context": 128000},
        {"id": "grok41nonreasoning",     "name": "Grok 4.1",                      "thinking": False, "context": 128000},
        {"id": "grok41reasoning",        "name": "Grok 4.1 + Reasoning",          "thinking": True,  "context": 128000},
        {"id": "kimik25thinking",        "name": "Kimi K2.5 Thinking",            "thinking": True,  "context": 128000},
        {"id": "sonar",                  "name": "Sonar (Experimental)",           "thinking": False, "context": 128000},
    ]


# Load at import time
_ALL_MODELS: list[dict] = _load_models_from_provider()
AVAILABLE_MODELS: list[str] = [m["id"] for m in _ALL_MODELS]
DEFAULT_MODEL: str = AVAILABLE_MODELS[0] if AVAILABLE_MODELS else "claude45sonnetthinking"


def get_model_info(model_id: str) -> dict:
    """Get full info dict for a model ID."""
    for m in _ALL_MODELS:
        if m["id"] == model_id:
            return m
    return {"id": model_id, "name": model_id, "thinking": False, "context": 0}


def get_model_name(model_id: str) -> str:
    """Get display name for a model ID."""
    return get_model_info(model_id).get("name", model_id)


def reload_models(provider_path: Optional[str] = None) -> list[str]:
    """Reload model list from opencode-provider.json."""
    global _ALL_MODELS, AVAILABLE_MODELS, DEFAULT_MODEL
    _ALL_MODELS = _load_models_from_provider(provider_path)
    AVAILABLE_MODELS = [m["id"] for m in _ALL_MODELS]
    DEFAULT_MODEL = AVAILABLE_MODELS[0] if AVAILABLE_MODELS else "claude45sonnetthinking"
    return AVAILABLE_MODELS


MAX_HISTORY_MESSAGES = 50  # keep last N messages to avoid token overflow


class ChatSession:
    """Manages a single chat session with history and model config."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        mode: str = "copilot",
        search_focus: str = "internet",
        system_prompt: Optional[str] = None,
        is_incognito: bool = False,
    ):
        self.model = model
        self.mode = mode
        self.search_focus = search_focus
        self.system_prompt = system_prompt
        self.is_incognito = is_incognito
        self.messages: list[dict] = []
        self.created_at = datetime.now()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def add_user_message(self, content: str) -> None:
        """Add a user message to history."""
        self.messages.append({
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })

    def add_assistant_message(self, content: str, citations: list[dict] | None = None) -> None:
        """Add an assistant message to history."""
        msg: dict = {
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if citations:
            msg["citations"] = citations
        self.messages.append(msg)

    def add_tool_result(self, tool_name: str, result: str) -> None:
        """Add a tool execution result to history."""
        self.messages.append({
            "role": "tool",
            "tool_name": tool_name,
            "content": result,
            "timestamp": datetime.now().isoformat(),
        })

    def get_history_for_display(self) -> list[dict]:
        """Return messages formatted for display."""
        return self.messages

    def build_query_with_context(self, new_query: str) -> str:
        """
        Build the full query string including conversation history context.
        Perplexity doesn't have native multi-turn, so we inject history as context.
        """
        if not self.messages:
            return new_query

        recent = self.messages[-MAX_HISTORY_MESSAGES:]
        context_parts = []

        if self.system_prompt:
            context_parts.append(f"[System Instructions]\n{self.system_prompt}\n")

        context_parts.append("[Conversation History]")
        for msg in recent:
            role = msg["role"].upper()
            content = msg["content"]
            if role == "TOOL":
                context_parts.append(f"[Tool: {msg.get('tool_name', '?')}]\n{content}")
            else:
                context_parts.append(f"{role}: {content}")

        context_parts.append(f"\n[Current Question]\n{new_query}")
        context_parts.append(
            "\nPlease answer the current question, taking the conversation history into account."
        )

        return "\n\n".join(context_parts)

    def clear(self) -> None:
        """Clear conversation history."""
        self.messages = []

    def set_model(self, model: str) -> bool:
        """Change the active model. Returns True if valid."""
        self.model = model
        return True

    def set_system_prompt(self, prompt: str) -> None:
        """Set or update the system prompt."""
        self.system_prompt = prompt

    def save(self, path: Optional[str] = None) -> str:
        """Save session to JSON file. Returns the file path."""
        if path is None:
            save_dir = Path.home() / ".perplexity_cli" / "sessions"
            save_dir.mkdir(parents=True, exist_ok=True)
            path = str(save_dir / f"session_{self.session_id}.json")

        data = {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "model": self.model,
            "mode": self.mode,
            "search_focus": self.search_focus,
            "system_prompt": self.system_prompt,
            "is_incognito": self.is_incognito,
            "messages": self.messages,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return path

    @classmethod
    def load(cls, path: str) -> "ChatSession":
        """Load a session from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        session = cls(
            model=data.get("model", DEFAULT_MODEL),
            mode=data.get("mode", "copilot"),
            search_focus=data.get("search_focus", "internet"),
            system_prompt=data.get("system_prompt"),
            is_incognito=data.get("is_incognito", False),
        )
        session.session_id = data.get("session_id", session.session_id)
        session.messages = data.get("messages", [])

        return session

    @staticmethod
    def list_saved_sessions() -> list[dict]:
        """List all saved sessions."""
        save_dir = Path.home() / ".perplexity_cli" / "sessions"
        if not save_dir.exists():
            return []

        sessions = []
        for f in sorted(save_dir.glob("session_*.json"), reverse=True):
            try:
                with open(f) as fp:
                    data = json.load(fp)
                sessions.append({
                    "path": str(f),
                    "session_id": data.get("session_id", "?"),
                    "created_at": data.get("created_at", "?"),
                    "model": data.get("model", "?"),
                    "message_count": len(data.get("messages", [])),
                })
            except Exception:
                pass

        return sessions

    @property
    def message_count(self) -> int:
        return len(self.messages)

    @property
    def user_messages(self) -> int:
        return sum(1 for m in self.messages if m["role"] == "user")
