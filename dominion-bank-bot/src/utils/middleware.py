"""
Middleware Layer
Provides pre-processing and post-processing for handlers.
"""
import logging
import time
from functools import wraps
from typing import Callable, Optional

from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.repositories import UserRepository
from src.utils.rate_limiter import rate_limiter, flood_protection
from src.utils.validators import ValidationError

logger = logging.getLogger(__name__)


def require_registration(func: Callable):
    """
    Decorator to require user registration before accessing a command.

    Automatically registers new users if they don't exist.
    """
    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs
    ):
        if not update.effective_user:
            return None

        user_id = update.effective_user.id

        async with get_session() as session:
            user_repo = UserRepository(session)
            user, created = await user_repo.get_or_create(
                telegram_id=user_id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name or "Usuario",
                default_balance=settings.default_balance,
            )

            if created:
                logger.info(f"Auto-registered user: {user_id}")

            # Store user in context for handler access
            context.user_data["db_user"] = user
            context.user_data["db_user_id"] = user.id

        return await func(update, context, *args, **kwargs)

    return wrapper


def require_admin(func: Callable):
    """
    Decorator to require admin privileges.

    Checks super admin, global admin, and group admin status.
    """
    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs
    ):
        if not update.effective_user:
            return None

        user_id = update.effective_user.id

        # Check super admin
        if settings.is_super_admin(user_id):
            return await func(update, context, *args, **kwargs)

        # Check database admin status
        async with get_session() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(user_id)

            if user and user.is_admin:
                return await func(update, context, *args, **kwargs)

        # Not an admin
        if update.message:
            await update.message.reply_text(
                "Solo los administradores pueden usar este comando."
            )
        return None

    return wrapper


def require_super_admin(func: Callable):
    """
    Decorator to require super admin privileges.

    Only super admins defined in settings can access.
    """
    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs
    ):
        if not update.effective_user:
            return None

        user_id = update.effective_user.id

        if not settings.is_super_admin(user_id):
            if update.message:
                await update.message.reply_text(
                    "Solo los super administradores pueden usar este comando."
                )
            return None

        return await func(update, context, *args, **kwargs)

    return wrapper


def require_group(func: Callable):
    """
    Decorator to require command to be used in a group.
    """
    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs
    ):
        if not update.effective_chat:
            return None

        if update.effective_chat.type not in ("group", "supergroup"):
            if update.message:
                await update.message.reply_text(
                    "Este comando solo funciona en grupos."
                )
            return None

        return await func(update, context, *args, **kwargs)

    return wrapper


def require_private(func: Callable):
    """
    Decorator to require command to be used in private chat.
    """
    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs
    ):
        if not update.effective_chat:
            return None

        if update.effective_chat.type != "private":
            if update.message:
                await update.message.reply_text(
                    "Este comando solo funciona en chat privado."
                )
            return None

        return await func(update, context, *args, **kwargs)

    return wrapper


def log_command(func: Callable):
    """
    Decorator to log command usage with timing.
    """
    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs
    ):
        start_time = time.time()

        user_id = update.effective_user.id if update.effective_user else "unknown"
        chat_id = update.effective_chat.id if update.effective_chat else "unknown"
        command = func.__name__

        logger.debug(f"Command start: {command} | user={user_id} | chat={chat_id}")

        try:
            result = await func(update, context, *args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(
                f"Command done: {command} | user={user_id} | "
                f"chat={chat_id} | time={elapsed:.3f}s"
            )
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Command error: {command} | user={user_id} | "
                f"chat={chat_id} | time={elapsed:.3f}s | error={e}"
            )
            raise

    return wrapper


def handle_validation_errors(func: Callable):
    """
    Decorator to handle ValidationError exceptions gracefully.
    """
    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs
    ):
        try:
            return await func(update, context, *args, **kwargs)

        except ValidationError as e:
            if update.message:
                await update.message.reply_text(f"{e.message}")
            return None

    return wrapper


def with_typing(func: Callable):
    """
    Decorator to show typing indicator while processing.
    Useful for commands that take time to execute.
    """
    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs
    ):
        if update.effective_chat:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )

        return await func(update, context, *args, **kwargs)

    return wrapper


def feature_flag(flag_name: str, message: Optional[str] = None):
    """
    Decorator to check if a feature is enabled.

    Args:
        flag_name: Name of the settings attribute to check
        message: Custom message when feature is disabled
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
            *args,
            **kwargs
        ):
            # Check if feature is enabled
            enabled = getattr(settings, flag_name, False)

            if not enabled:
                if update.message:
                    msg = message or "Esta funcion no esta disponible."
                    await update.message.reply_text(msg)
                return None

            return await func(update, context, *args, **kwargs)

        return wrapper
    return decorator


def combine_decorators(*decorators):
    """
    Combine multiple decorators into one.

    Usage:
        @combine_decorators(require_registration, log_command, rate_limit(5, 60))
        async def my_command(update, context):
            ...
    """
    def decorator(func):
        for dec in reversed(decorators):
            func = dec(func)
        return func
    return decorator


# Pre-built decorator combinations for common patterns
def standard_command(rate_calls: int = 10, rate_period: int = 60):
    """
    Standard command decorator stack.

    Includes: registration, logging, rate limiting, validation handling.
    """
    from src.utils.rate_limiter import rate_limit

    def decorator(func):
        @require_registration
        @log_command
        @rate_limit(max_calls=rate_calls, period=rate_period)
        @handle_validation_errors
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def admin_command():
    """
    Admin command decorator stack.

    Includes: admin check, logging, validation handling.
    """
    def decorator(func):
        @require_admin
        @log_command
        @handle_validation_errors
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def super_admin_command():
    """
    Super admin command decorator stack.

    Includes: super admin check, logging, validation handling.
    """
    def decorator(func):
        @require_super_admin
        @log_command
        @handle_validation_errors
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator
