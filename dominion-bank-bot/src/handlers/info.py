"""
The Phantom Bot - Info Command Handlers
/ranking, /historial
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.models import TransactionType
from src.database.repositories import TransactionRepository, UserRepository
from src.utils.helpers import format_time_ago
from src.utils.messages import (
    ERROR_NOT_REGISTERED,
    history_message,
    ranking_message,
)

logger = logging.getLogger(__name__)


async def ranking_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ranking command - show top users by balance."""
    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)

        # Get requesting user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)

        # Get top 10 users
        top_users = await user_repo.get_ranking(limit=10)

        # Format user data
        users_data = [
            (u.telegram_id, u.display_name, u.balance)
            for u in top_users
        ]

        # Get user's position if registered
        user_position = None
        user_balance = 0
        if user:
            user_position = await user_repo.get_user_rank(user.telegram_id)
            user_balance = user.balance

        message = ranking_message(users_data, user_position, user_balance)

    await update.message.reply_text(message)


async def historial_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /historial command - show user's transaction history."""
    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        tx_repo = TransactionRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text(ERROR_NOT_REGISTERED)
            return

        # Get recent transactions
        transactions = await tx_repo.get_user_history(user.id, limit=10)

        # Format transactions
        tx_data = []
        for tx in transactions:
            tx_info = {
                "amount": tx.amount,
                "time": format_time_ago(tx.created_at),
            }

            if tx.transaction_type == TransactionType.TRANSFER:
                if tx.sender_id == user.id:
                    tx_info["type"] = "sent"
                    tx_info["other"] = tx.recipient.display_name if tx.recipient else "Unknown"
                else:
                    tx_info["type"] = "received"
                    tx_info["other"] = tx.sender.display_name if tx.sender else "Unknown"
            elif tx.transaction_type == TransactionType.ADMIN_GIVE:
                tx_info["type"] = "admin_give"
                tx_info["other"] = "Admin"
            elif tx.transaction_type == TransactionType.ADMIN_REMOVE:
                tx_info["type"] = "admin_remove"
                tx_info["other"] = "Admin"
            else:
                tx_info["type"] = "other"
                tx_info["other"] = tx.transaction_type.value

            tx_data.append(tx_info)

        message = history_message(tx_data, user.balance)

    await update.message.reply_text(message)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command - show bot statistics."""
    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)

        total_users = await user_repo.count_active_users()

        # Get total balance in circulation
        top_users = await user_repo.get_ranking(limit=1000)
        total_balance = sum(u.balance for u in top_users)

        message = f"""📊 Estadísticas de {settings.bot_name}

👥 Usuarios registrados: {total_users}
💰 {settings.currency_name} en circulación: {total_balance:,}
{settings.currency_emoji} Moneda: {settings.currency_name}"""

    await update.message.reply_text(message)
