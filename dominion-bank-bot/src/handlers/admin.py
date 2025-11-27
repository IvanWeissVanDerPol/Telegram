"""
The Phantom Bot - Admin Command Handlers
/dar_admin, /quitar, /consultar
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.models import TransactionType
from src.database.repositories import (
    AdminRepository,
    TransactionRepository,
    UserRepository,
)
from src.utils.helpers import (
    extract_amount,
    extract_username,
    get_user_info,
    is_group_chat,
)
from src.utils.messages import (
    ERROR_INVALID_AMOUNT,
    ERROR_NOT_ADMIN,
    ERROR_NOT_REGISTERED,
    ERROR_USER_NOT_FOUND,
    USAGE_CONSULTAR,
    USAGE_DAR_ADMIN,
    USAGE_QUITAR,
    admin_give_message,
    admin_remove_message,
    balance_message,
    format_balance,
)

logger = logging.getLogger(__name__)


async def check_admin(
    update: Update,
    session,
    user_repo: UserRepository,
) -> tuple[bool, any]:
    """Check if the user is an admin. Returns (is_admin, user)."""
    if not update.effective_user:
        return False, None

    telegram_id = update.effective_user.id

    # Super admins always have access
    if settings.is_super_admin(telegram_id):
        user = await user_repo.get_by_telegram_id(telegram_id)
        return True, user

    # Check if user is registered and is admin
    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        return False, None

    # Check group admin status
    if is_group_chat(update) and update.effective_chat:
        admin_repo = AdminRepository(session)
        is_admin = await admin_repo.is_admin(user.id, update.effective_chat.id)
        if is_admin:
            return True, user

    # Check if user has global admin flag
    return user.is_admin, user


async def dar_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /dar_admin command - admin gives coins to user."""
    if not update.effective_user or not update.message:
        return

    # Parse arguments
    args_text = " ".join(context.args) if context.args else ""
    parts = args_text.split()

    if len(parts) < 2:
        await update.message.reply_text(USAGE_DAR_ADMIN)
        return

    target_username = extract_username(parts[0])
    amount = extract_amount(parts[1])

    if not target_username:
        await update.message.reply_text(USAGE_DAR_ADMIN)
        return

    if not amount or amount <= 0:
        await update.message.reply_text(ERROR_INVALID_AMOUNT)
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        tx_repo = TransactionRepository(session)

        # Check admin status
        is_admin, admin_user = await check_admin(update, session, user_repo)
        if not is_admin:
            await update.message.reply_text(ERROR_NOT_ADMIN)
            return

        # Get or create target user
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text(ERROR_USER_NOT_FOUND)
            return

        # Add balance
        await user_repo.update_balance(target.id, amount, allow_negative=True)

        # Record transaction
        await tx_repo.create(
            recipient_id=target.id,
            amount=amount,
            transaction_type=TransactionType.ADMIN_GIVE,
            admin_id=admin_user.id if admin_user else None,
            description=f"Admin dar por {admin_user.display_name if admin_user else 'System'}",
        )

        await session.refresh(target)

        logger.info(
            f"Admin give: {admin_user.display_name if admin_user else 'System'} -> {target.display_name}: {amount}"
        )

        message = admin_give_message(
            amount=amount,
            recipient=target.display_name,
            admin=admin_user.display_name if admin_user else "Admin",
            new_balance=target.balance,
        )

    await update.message.reply_text(message)


async def quitar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /quitar command - admin removes coins from user."""
    if not update.effective_user or not update.message:
        return

    # Parse arguments
    args_text = " ".join(context.args) if context.args else ""
    parts = args_text.split()

    if len(parts) < 2:
        await update.message.reply_text(USAGE_QUITAR)
        return

    target_username = extract_username(parts[0])
    amount = extract_amount(parts[1])

    if not target_username:
        await update.message.reply_text(USAGE_QUITAR)
        return

    if not amount or amount <= 0:
        await update.message.reply_text(ERROR_INVALID_AMOUNT)
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        tx_repo = TransactionRepository(session)

        # Check admin status
        is_admin, admin_user = await check_admin(update, session, user_repo)
        if not is_admin:
            await update.message.reply_text(ERROR_NOT_ADMIN)
            return

        # Get target user
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text(ERROR_USER_NOT_FOUND)
            return

        # Check if we allow debt
        allow_negative = settings.allow_debt

        # Remove balance
        success = await user_repo.update_balance(
            target.id, -amount, allow_negative=allow_negative
        )

        if not success:
            await update.message.reply_text(
                f"❌ No se puede quitar {format_balance(amount)} {settings.currency_name}. "
                f"Saldo actual: {format_balance(target.balance)} {settings.currency_name}"
            )
            return

        # Record transaction
        await tx_repo.create(
            recipient_id=target.id,
            amount=amount,
            transaction_type=TransactionType.ADMIN_REMOVE,
            admin_id=admin_user.id if admin_user else None,
            description=f"Admin quitar por {admin_user.display_name if admin_user else 'System'}",
        )

        await session.refresh(target)

        logger.info(
            f"Admin remove: {admin_user.display_name if admin_user else 'System'} -> {target.display_name}: -{amount}"
        )

        message = admin_remove_message(
            amount=amount,
            target=target.display_name,
            admin=admin_user.display_name if admin_user else "Admin",
            new_balance=target.balance,
        )

    await update.message.reply_text(message)


async def consultar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /consultar command - admin checks another user's balance."""
    if not update.effective_user or not update.message:
        return

    # Parse arguments
    args_text = " ".join(context.args) if context.args else ""
    target_username = extract_username(args_text)

    if not target_username:
        await update.message.reply_text(USAGE_CONSULTAR)
        return

    async with get_session() as session:
        user_repo = UserRepository(session)

        # Check admin status
        is_admin, admin_user = await check_admin(update, session, user_repo)
        if not is_admin:
            await update.message.reply_text(ERROR_NOT_ADMIN)
            return

        # Get target user
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text(ERROR_USER_NOT_FOUND)
            return

        message = f"""👤 {target.display_name}

{settings.currency_emoji} Saldo: {format_balance(target.balance)} {settings.currency_name}
📅 Registrado: {target.created_at.strftime('%d/%m/%Y')}
📊 Estado: {target.status.value}"""

    await update.message.reply_text(message)


async def set_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setadmin command - super admin grants admin to user."""
    if not update.effective_user or not update.message:
        return

    # Only super admins can use this
    if not settings.is_super_admin(update.effective_user.id):
        await update.message.reply_text(ERROR_NOT_ADMIN)
        return

    # Parse arguments
    args_text = " ".join(context.args) if context.args else ""
    target_username = extract_username(args_text)

    if not target_username:
        await update.message.reply_text("📝 Uso: /setadmin @usuario")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)

        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text(ERROR_USER_NOT_FOUND)
            return

        await user_repo.set_admin(target.id, True)

        logger.info(f"Admin granted to: {target.display_name}")

    await update.message.reply_text(f"✅ {target.display_name} ahora es administrador")


async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /removeadmin command - super admin removes admin from user."""
    if not update.effective_user or not update.message:
        return

    # Only super admins can use this
    if not settings.is_super_admin(update.effective_user.id):
        await update.message.reply_text(ERROR_NOT_ADMIN)
        return

    # Parse arguments
    args_text = " ".join(context.args) if context.args else ""
    target_username = extract_username(args_text)

    if not target_username:
        await update.message.reply_text("📝 Uso: /removeadmin @usuario")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)

        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text(ERROR_USER_NOT_FOUND)
            return

        await user_repo.set_admin(target.id, False)

        logger.info(f"Admin removed from: {target.display_name}")

    await update.message.reply_text(f"✅ {target.display_name} ya no es administrador")
