"""
The Phantom Bot - Helper Utilities
"""
import re
from datetime import datetime, timedelta
from typing import Optional

from telegram import Update, User as TelegramUser


def extract_username(text: str) -> Optional[str]:
    """Extract username from text (with or without @)."""
    if not text:
        return None
    # Match @username pattern
    match = re.search(r"@?([a-zA-Z][a-zA-Z0-9_]{4,31})", text)
    return match.group(1) if match else None


def extract_amount(text: str) -> Optional[int]:
    """Extract amount from text."""
    if not text:
        return None
    # Match number pattern (with optional thousands separator)
    match = re.search(r"(\d[\d.,]*)", text.replace(".", "").replace(",", ""))
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def parse_transfer_args(text: str) -> tuple[Optional[str], Optional[int]]:
    """Parse transfer command arguments. Returns (username, amount)."""
    if not text:
        return None, None

    parts = text.split()
    username = None
    amount = None

    for part in parts:
        if part.startswith("@") or (not username and re.match(r"^[a-zA-Z]", part)):
            username = extract_username(part)
        elif part.isdigit() or re.match(r"^\d[\d.,]*$", part):
            amount = extract_amount(part)

    return username, amount


def get_user_info(user: TelegramUser) -> dict:
    """Extract user info from Telegram user object."""
    return {
        "telegram_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


def format_time_ago(dt: datetime) -> str:
    """Format datetime as relative time string in Spanish."""
    now = datetime.utcnow()
    diff = now - dt

    if diff < timedelta(minutes=1):
        return "ahora"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"hace {minutes}m"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"hace {hours}h"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"hace {days}d"
    else:
        return dt.strftime("%d/%m/%Y")


def get_chat_type(update: Update) -> str:
    """Get the type of chat from update."""
    if update.effective_chat:
        return update.effective_chat.type
    return "unknown"


def is_group_chat(update: Update) -> bool:
    """Check if the update is from a group chat."""
    chat_type = get_chat_type(update)
    return chat_type in ("group", "supergroup")


def is_private_chat(update: Update) -> bool:
    """Check if the update is from a private chat."""
    return get_chat_type(update) == "private"


def sanitize_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def parse_amount(text: str) -> Optional[int]:
    """Parse a string as an integer amount. Alias for extract_amount."""
    if not text:
        return None
    try:
        # Remove whitespace and try direct conversion
        cleaned = text.strip().replace(",", "").replace(".", "")
        return int(cleaned)
    except ValueError:
        return extract_amount(text)
