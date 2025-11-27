"""
Rate Limiter Utility
Provides decorators and functions for rate limiting bot commands.
"""
import asyncio
import logging
import time
from collections import defaultdict
from functools import wraps
from typing import Callable, Optional

from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """In-memory rate limiter with sliding window."""

    def __init__(self):
        # Structure: {key: [(timestamp, count), ...]}
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_allowed(
        self,
        key: str,
        max_calls: int,
        period_seconds: int,
    ) -> tuple[bool, int]:
        """
        Check if request is allowed under rate limit.

        Returns:
            tuple: (is_allowed, seconds_until_reset)
        """
        async with self._lock:
            now = time.time()
            window_start = now - period_seconds

            # Clean old entries
            self._requests[key] = [
                ts for ts in self._requests[key] if ts > window_start
            ]

            current_count = len(self._requests[key])

            if current_count >= max_calls:
                # Calculate time until oldest request expires
                if self._requests[key]:
                    oldest = min(self._requests[key])
                    wait_time = int(oldest + period_seconds - now) + 1
                    return False, max(1, wait_time)
                return False, period_seconds

            # Record this request
            self._requests[key].append(now)
            return True, 0

    async def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        async with self._lock:
            self._requests.pop(key, None)

    def get_key(
        self,
        user_id: int,
        chat_id: Optional[int] = None,
        command: Optional[str] = None,
    ) -> str:
        """Generate a rate limit key."""
        parts = [str(user_id)]
        if chat_id:
            parts.append(str(chat_id))
        if command:
            parts.append(command)
        return ":".join(parts)


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(
    max_calls: int = 5,
    period: int = 60,
    per_chat: bool = False,
    admin_bypass: bool = True,
    message: Optional[str] = None,
):
    """
    Decorator to rate limit command handlers.

    Args:
        max_calls: Maximum number of calls allowed in the period
        period: Time period in seconds
        per_chat: If True, rate limit per user per chat
        admin_bypass: If True, admins bypass rate limit
        message: Custom message when rate limited

    Usage:
        @rate_limit(max_calls=3, period=60)
        async def my_command(update, context):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
            *args,
            **kwargs
        ):
            if not update.effective_user:
                return await func(update, context, *args, **kwargs)

            user_id = update.effective_user.id

            # Admin bypass
            if admin_bypass and settings.is_super_admin(user_id):
                return await func(update, context, *args, **kwargs)

            # Generate key
            chat_id = update.effective_chat.id if per_chat and update.effective_chat else None
            key = rate_limiter.get_key(user_id, chat_id, func.__name__)

            # Check rate limit
            allowed, wait_time = await rate_limiter.is_allowed(
                key, max_calls, period
            )

            if not allowed:
                if update.message:
                    msg = message or (
                        f"Demasiadas solicitudes. "
                        f"Espera {wait_time} segundos."
                    )
                    await update.message.reply_text(msg)
                logger.warning(
                    f"Rate limited: user={user_id}, command={func.__name__}, "
                    f"wait={wait_time}s"
                )
                return None

            return await func(update, context, *args, **kwargs)

        return wrapper
    return decorator


def cooldown(seconds: int, message: Optional[str] = None):
    """
    Simple cooldown decorator - one call per cooldown period.

    Args:
        seconds: Cooldown period in seconds
        message: Custom message when on cooldown

    Usage:
        @cooldown(30)
        async def expensive_command(update, context):
            ...
    """
    return rate_limit(
        max_calls=1,
        period=seconds,
        admin_bypass=True,
        message=message,
    )


class FloodProtection:
    """
    Flood protection for detecting spam behavior.
    Tracks rapid message sending patterns.
    """

    def __init__(
        self,
        max_messages: int = 10,
        window_seconds: int = 10,
        ban_duration: int = 300,
    ):
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.ban_duration = ban_duration
        self._messages: dict[int, list[float]] = defaultdict(list)
        self._banned: dict[int, float] = {}
        self._lock = asyncio.Lock()

    async def check(self, user_id: int) -> tuple[bool, Optional[int]]:
        """
        Check if user is flooding.

        Returns:
            tuple: (is_flooding, ban_time_remaining)
        """
        async with self._lock:
            now = time.time()

            # Check if banned
            if user_id in self._banned:
                ban_end = self._banned[user_id]
                if now < ban_end:
                    return True, int(ban_end - now)
                else:
                    del self._banned[user_id]

            # Clean old messages
            window_start = now - self.window_seconds
            self._messages[user_id] = [
                ts for ts in self._messages[user_id] if ts > window_start
            ]

            # Record message
            self._messages[user_id].append(now)

            # Check flood
            if len(self._messages[user_id]) > self.max_messages:
                self._banned[user_id] = now + self.ban_duration
                logger.warning(
                    f"Flood detected: user={user_id}, "
                    f"banned for {self.ban_duration}s"
                )
                return True, self.ban_duration

            return False, None

    async def unban(self, user_id: int) -> None:
        """Manually unban a user."""
        async with self._lock:
            self._banned.pop(user_id, None)
            self._messages.pop(user_id, None)


# Global flood protection instance
flood_protection = FloodProtection()


def anti_flood(func: Callable):
    """
    Decorator to protect against message flooding.

    Usage:
        @anti_flood
        async def my_handler(update, context):
            ...
    """
    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs
    ):
        if not update.effective_user:
            return await func(update, context, *args, **kwargs)

        user_id = update.effective_user.id

        # Admins bypass flood protection
        if settings.is_super_admin(user_id):
            return await func(update, context, *args, **kwargs)

        is_flooding, ban_time = await flood_protection.check(user_id)

        if is_flooding:
            if update.message:
                await update.message.reply_text(
                    f"Has enviado demasiados mensajes. "
                    f"Espera {ban_time} segundos."
                )
            return None

        return await func(update, context, *args, **kwargs)

    return wrapper
