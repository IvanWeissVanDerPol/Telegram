"""
The Phantom Bot - Text Loader
Loads all text content from YAML files
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from src.config import settings


# Directory containing YAML files
TEXTS_DIR = Path(__file__).parent


class TextLoader:
    """Loads and caches text content from YAML files."""

    _instance: Optional["TextLoader"] = None
    _cache: Dict[str, Dict] = {}

    def __new__(cls) -> "TextLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all()
        return cls._instance

    def _load_all(self) -> None:
        """Load all YAML files into cache."""
        yaml_files = [
            "emojis",
            "errors",
            "core",
            "bdsm",
            "help",
            "ai_responses",
        ]

        for name in yaml_files:
            file_path = TEXTS_DIR / f"{name}.yaml"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    self._cache[name] = yaml.safe_load(f) or {}

    def get(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific text by category and key."""
        if category not in self._cache:
            return default
        return self._cache[category].get(key, default)

    def get_nested(self, category: str, *keys: str, default: Any = None) -> Any:
        """Get a nested value from the YAML structure."""
        if category not in self._cache:
            return default

        value = self._cache[category]
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value

    @property
    def emojis(self) -> Dict:
        """Get all emojis."""
        return self._cache.get("emojis", {})

    @property
    def errors(self) -> Dict:
        """Get all error messages."""
        return self._cache.get("errors", {})

    @property
    def core(self) -> Dict:
        """Get core messages."""
        return self._cache.get("core", {})

    @property
    def bdsm(self) -> Dict:
        """Get BDSM messages."""
        return self._cache.get("bdsm", {})

    @property
    def help(self) -> Dict:
        """Get help content."""
        return self._cache.get("help", {})

    @property
    def ai_responses(self) -> Dict:
        """Get AI response templates."""
        return self._cache.get("ai_responses", {})


# Singleton instance
_loader = TextLoader()


def get_emoji(category: str, name: str) -> str:
    """Get an emoji by category and name."""
    emojis = _loader.emojis.get(category, {})
    if isinstance(emojis, dict):
        return emojis.get(name, "")
    elif isinstance(emojis, list):
        # For lists like medals or mystical
        return emojis
    return ""


def get_divider(name: str = "default") -> str:
    """Get a divider string."""
    return _loader.emojis.get("dividers", {}).get(name, "━━━━━━━━━━━━━━━━━━━━")


def get_error(key: str, **kwargs) -> str:
    """Get an error message with optional formatting."""
    msg = _loader.errors.get("errors", {}).get(key, "")
    return _format_text(msg, **kwargs)


def get_bdsm_error(key: str, **kwargs) -> str:
    """Get a BDSM-specific error message."""
    msg = _loader.errors.get("bdsm_errors", {}).get(key, "")
    return _format_text(msg, **kwargs)


def get_warning(key: str, **kwargs) -> str:
    """Get a warning message."""
    msg = _loader.errors.get("warnings", {}).get(key, "")
    return _format_text(msg, **kwargs)


def get_info(key: str, **kwargs) -> str:
    """Get an info message."""
    msg = _loader.errors.get("info", {}).get(key, "")
    return _format_text(msg, **kwargs)


def get_usage(command: str, **kwargs) -> str:
    """Get usage instructions for a command."""
    msg = _loader.errors.get("usage", {}).get(command, "")
    return _format_text(msg, **kwargs)


def get_core_message(section: str, key: str, **kwargs) -> str:
    """Get a core message."""
    msg = _loader.core.get(section, {}).get(key, "")
    return _format_text(msg, **kwargs)


def get_bdsm_message(section: str, key: str, **kwargs) -> str:
    """Get a BDSM message."""
    msg = _loader.bdsm.get(section, {}).get(key, "")
    return _format_text(msg, **kwargs)


def get_help_category(category: str) -> Dict:
    """Get help content for a category."""
    return _loader.help.get("categories", {}).get(category, {})


def get_static_help_section(section: str, **kwargs) -> str:
    """Get a static help section."""
    msg = _loader.help.get("static_help", {}).get(section, "")
    return _format_text(msg, **kwargs)


def get_ai_response(command: str, key: str = "response", **kwargs) -> str:
    """Get an AI command response template."""
    msg = _loader.ai_responses.get(command, {}).get(key, "")
    return _format_text(msg, **kwargs)


def get_ai_data(command: str, key: str) -> Any:
    """Get AI command data (lists, dicts, etc.)."""
    return _loader.ai_responses.get(command, {}).get(key)


def _format_text(text: str, **kwargs) -> str:
    """Format text with emoji placeholders and dynamic values."""
    if not text:
        return ""

    # Build emoji mapping
    emoji_map = {
        # Status emojis
        "success": get_emoji("status", "success"),
        "error": get_emoji("status", "error"),
        "warning": get_emoji("status", "warning"),
        "info": get_emoji("status", "info"),
        "loading": get_emoji("status", "loading"),
        "gift": get_emoji("status", "gift"),
        # Feature emojis
        "balance_emoji": get_emoji("features", "balance"),
        "transfer_emoji": get_emoji("features", "transfer"),
        "ranking": get_emoji("features", "ranking"),
        "history": get_emoji("features", "history"),
        "profile": get_emoji("features", "profile"),
        "admin": get_emoji("features", "admin"),
        "bot": get_emoji("features", "bot"),
        # BDSM emojis
        "collar": get_emoji("bdsm", "collar"),
        "whip": get_emoji("bdsm", "whip"),
        "dungeon": get_emoji("bdsm", "dungeon"),
        "auction": get_emoji("bdsm", "auction"),
        "tribute": get_emoji("bdsm", "tribute"),
        "contract": get_emoji("bdsm", "contract"),
        # Role emojis
        "dom": get_emoji("roles", "dom"),
        "sub": get_emoji("roles", "sub"),
        "switch": get_emoji("roles", "switch"),
        # Privacy emojis
        "public": get_emoji("privacy", "public"),
        "friends": get_emoji("privacy", "friends"),
        "private": get_emoji("privacy", "private"),
        # AI emojis
        "dice": get_emoji("ai", "dice"),
        "roulette": get_emoji("ai", "roulette"),
        "crystal": get_emoji("ai", "crystal"),
        "fantasy": get_emoji("ai", "fantasy"),
        "task": get_emoji("ai", "task"),
        "challenge": get_emoji("ai", "challenge"),
        "reward": get_emoji("ai", "reward"),
        "scene": get_emoji("ai", "scene"),
        "ritual": get_emoji("ai", "ritual"),
        "title_emoji": get_emoji("ai", "title"),
        "compatibility": get_emoji("ai", "compatibility"),
        # Dividers
        "divider": get_divider("default"),
        "divider_light": get_divider("light"),
        "divider_double": get_divider("double"),
        # Settings
        "currency": settings.currency_name,
        "currency_emoji": settings.currency_emoji,
        "currency_symbol": settings.currency_symbol,
        "bot_name": settings.bot_name,
        "min_amount": settings.min_transfer_amount,
        "max_amount": settings.max_transfer_amount,
        "default_balance": settings.default_balance,
    }

    # Merge with provided kwargs
    emoji_map.update(kwargs)

    # Format the text
    try:
        return text.format(**emoji_map)
    except KeyError as e:
        # Return original text if formatting fails
        return text


# Export loader instance for direct access
texts = _loader


# Convenience exports
__all__ = [
    "texts",
    "get_emoji",
    "get_divider",
    "get_error",
    "get_bdsm_error",
    "get_warning",
    "get_info",
    "get_usage",
    "get_core_message",
    "get_bdsm_message",
    "get_help_category",
    "get_static_help_section",
    "get_ai_response",
    "get_ai_data",
]
