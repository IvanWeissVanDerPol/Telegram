"""
The Phantom Bot - Core Command Handlers
/start, /ver, /dar
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.models import TransactionType
from src.database.repositories import (
    CooldownRepository,
    TransactionRepository,
    UserRepository,
)
from src.utils.helpers import (
    format_time_ago,
    get_user_info,
    parse_transfer_args,
)
from src.utils.messages import (
    ERROR_COOLDOWN,
    ERROR_INSUFFICIENT_BALANCE,
    ERROR_INVALID_AMOUNT,
    ERROR_MAX_AMOUNT,
    ERROR_MIN_AMOUNT,
    ERROR_NOT_REGISTERED,
    ERROR_SELF_TRANSFER,
    ERROR_USER_NOT_FOUND,
    USAGE_DAR,
    balance_message,
    transfer_success_recipient,
    transfer_success_sender,
    welcome_message,
)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - register user and show welcome."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)

    async with get_session() as session:
        user_repo = UserRepository(session)
        user, created = await user_repo.get_or_create(
            telegram_id=user_info["telegram_id"],
            username=user_info["username"],
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            default_balance=settings.default_balance,
        )

        message = welcome_message(
            balance=user.balance,
            username=user.display_name,
        )

        if created:
            logger.info(f"New user registered: {user}")

    await update.message.reply_text(message)


async def ver_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ver command - show user balance."""
    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(update.effective_user.id)

        if not user:
            await update.message.reply_text(ERROR_NOT_REGISTERED)
            return

        message = balance_message(user.balance)

    await update.message.reply_text(message)


async def dar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /dar command - transfer coins to another user."""
    if not update.effective_user or not update.message:
        return

    # Parse arguments
    args_text = " ".join(context.args) if context.args else ""
    recipient_username, amount = parse_transfer_args(args_text)

    if not recipient_username or not amount:
        await update.message.reply_text(USAGE_DAR)
        return

    # Validate amount
    if amount < settings.min_transfer_amount:
        await update.message.reply_text(ERROR_MIN_AMOUNT)
        return

    if amount > settings.max_transfer_amount:
        await update.message.reply_text(ERROR_MAX_AMOUNT)
        return

    sender_telegram_id = update.effective_user.id

    async with get_session() as session:
        user_repo = UserRepository(session)
        tx_repo = TransactionRepository(session)
        cooldown_repo = CooldownRepository(session)

        # Get sender
        sender = await user_repo.get_by_telegram_id(sender_telegram_id)
        if not sender:
            await update.message.reply_text(ERROR_NOT_REGISTERED)
            return

        # Check cooldown
        cooldown_expires = await cooldown_repo.is_on_cooldown(sender.id, "transfer")
        if cooldown_expires:
            remaining = (cooldown_expires - __import__("datetime").datetime.utcnow()).seconds
            await update.message.reply_text(
                ERROR_COOLDOWN.format(seconds=remaining)
            )
            return

        # Get recipient
        recipient = await user_repo.get_by_username(recipient_username)
        if not recipient:
            await update.message.reply_text(ERROR_USER_NOT_FOUND)
            return

        # Check self-transfer
        if sender.telegram_id == recipient.telegram_id:
            await update.message.reply_text(ERROR_SELF_TRANSFER)
            return

        # Check balance
        if sender.balance < amount:
            await update.message.reply_text(ERROR_INSUFFICIENT_BALANCE)
            return

        # Perform transfer atomically
        await user_repo.update_balance(sender.id, -amount)
        await user_repo.update_balance(recipient.id, amount)

        # Record transaction
        await tx_repo.create(
            sender_id=sender.id,
            recipient_id=recipient.id,
            amount=amount,
            transaction_type=TransactionType.TRANSFER,
        )

        # Set cooldown
        await cooldown_repo.set_cooldown(
            sender.id, "transfer", settings.transfer_cooldown
        )

        # Refresh balances
        await session.refresh(sender)
        await session.refresh(recipient)

        sender_balance = sender.balance
        recipient_balance = recipient.balance
        recipient_display = recipient.display_name

        logger.info(
            f"Transfer: {sender.display_name} -> {recipient.display_name}: {amount}"
        )

    # Send confirmation to sender
    await update.message.reply_text(
        transfer_success_sender(amount, recipient_display, sender_balance)
    )

    # Try to notify recipient (may fail if bot can't message them)
    try:
        await context.bot.send_message(
            chat_id=recipient.telegram_id,
            text=transfer_success_recipient(
                amount,
                sender.display_name if sender else "Unknown",
                recipient_balance,
            ),
        )
    except Exception as e:
        logger.warning(f"Could not notify recipient: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - show available commands."""
    if not update.message:
        return

    help_text = f"""🎭 {settings.bot_name} - Comandos

💰 **Básicos:**
/start - Registrarse
/ver - Ver tu saldo
/dar @user cantidad - Enviar {settings.currency_name}

📊 **Información:**
/ranking - Top 10 usuarios
/historial - Tus últimas transacciones

👑 **Admin:**
/dar_admin @user cantidad - Dar {settings.currency_name}
/quitar @user cantidad - Quitar {settings.currency_name}
/consultar @user - Ver saldo de otro usuario

ℹ️ **Ayuda:**
/help - Este mensaje"""

    await update.message.reply_text(help_text)
