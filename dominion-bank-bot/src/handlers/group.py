"""
The Phantom Bot - Group Handler
Automatically sync Telegram group admins
"""
import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.repositories import AdminRepository, UserRepository

logger = logging.getLogger(__name__)


async def sync_group_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sync Telegram group admins to bot admin list."""
    if not update.effective_chat or update.effective_chat.type not in ("group", "supergroup"):
        return

    chat_id = update.effective_chat.id

    try:
        # Get all admins from Telegram
        tg_admins = await context.bot.get_chat_administrators(chat_id)

        async with get_session() as session:
            user_repo = UserRepository(session)
            admin_repo = AdminRepository(session)

            synced = 0
            for admin in tg_admins:
                # Skip bots
                if admin.user.is_bot:
                    continue

                # Get or create user
                user, created = await user_repo.get_or_create(
                    telegram_id=admin.user.id,
                    username=admin.user.username,
                    first_name=admin.user.first_name,
                    last_name=admin.user.last_name,
                    default_balance=settings.default_balance,
                )

                # Check if already admin in this group
                is_admin = await admin_repo.is_admin(user.id, chat_id)
                if not is_admin:
                    await admin_repo.add_admin(user.id, chat_id)
                    synced += 1
                    logger.info(f"Synced admin: {user.display_name} in group {chat_id}")

            if synced > 0:
                logger.info(f"Synced {synced} admins for group {chat_id}")

    except Exception as e:
        logger.error(f"Error syncing admins for group {chat_id}: {e}")


async def on_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle chat member updates (admin promotions/demotions)."""
    if not update.chat_member:
        return

    chat_id = update.effective_chat.id
    user = update.chat_member.new_chat_member.user

    # Skip bots
    if user.is_bot:
        return

    old_status = update.chat_member.old_chat_member.status
    new_status = update.chat_member.new_chat_member.status

    admin_statuses = (ChatMember.ADMINISTRATOR, ChatMember.OWNER)

    async with get_session() as session:
        user_repo = UserRepository(session)
        admin_repo = AdminRepository(session)

        # Get or create user
        db_user, _ = await user_repo.get_or_create(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            default_balance=settings.default_balance,
        )

        # User promoted to admin
        if new_status in admin_statuses and old_status not in admin_statuses:
            is_admin = await admin_repo.is_admin(db_user.id, chat_id)
            if not is_admin:
                await admin_repo.add_admin(db_user.id, chat_id)
                logger.info(f"Admin promoted: {db_user.display_name} in group {chat_id}")

        # User demoted from admin
        elif old_status in admin_statuses and new_status not in admin_statuses:
            await admin_repo.remove_admin(db_user.id, chat_id)
            logger.info(f"Admin demoted: {db_user.display_name} in group {chat_id}")


async def on_bot_added_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle when bot is added to a group - sync admins and send welcome."""
    if not update.my_chat_member:
        return

    chat = update.effective_chat
    new_status = update.my_chat_member.new_chat_member.status

    # Bot was added to group
    if new_status in (ChatMember.MEMBER, ChatMember.ADMINISTRATOR):
        logger.info(f"Bot added to group: {chat.title} ({chat.id})")

        # Sync admins
        await sync_group_admins(update, context)

        # Send welcome message
        welcome = f"""🎭 ¡{settings.bot_name} ha llegado!

Tu sistema de {settings.currency_name} {settings.currency_emoji}

📜 Comandos disponibles:
/start - Registrarse
/ver - Ver saldo
/dar @user cantidad - Enviar {settings.currency_name}
/ranking - Top usuarios

Los administradores del grupo pueden usar:
/dar_admin @user cantidad
/quitar @user cantidad

¡Que comience el juego! 🎭"""

        try:
            await context.bot.send_message(chat_id=chat.id, text=welcome)
        except Exception as e:
            logger.error(f"Could not send welcome to group {chat.id}: {e}")


async def syncadmins_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /syncadmins command - manually sync group admins."""
    if not update.effective_chat or not update.message:
        return

    if update.effective_chat.type not in ("group", "supergroup"):
        await update.message.reply_text("❌ Este comando solo funciona en grupos.")
        return

    # Check if user is admin in Telegram
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status not in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
            # Also check if super admin
            if not settings.is_super_admin(user_id):
                await update.message.reply_text("❌ Solo los administradores pueden sincronizar.")
                return
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return

    await update.message.reply_text("🔄 Sincronizando administradores...")

    # Get all admins from Telegram
    try:
        tg_admins = await context.bot.get_chat_administrators(chat_id)

        async with get_session() as session:
            user_repo = UserRepository(session)
            admin_repo = AdminRepository(session)

            synced = 0
            admin_names = []

            for admin in tg_admins:
                if admin.user.is_bot:
                    continue

                user, _ = await user_repo.get_or_create(
                    telegram_id=admin.user.id,
                    username=admin.user.username,
                    first_name=admin.user.first_name,
                    last_name=admin.user.last_name,
                    default_balance=settings.default_balance,
                )

                is_admin = await admin_repo.is_admin(user.id, chat_id)
                if not is_admin:
                    await admin_repo.add_admin(user.id, chat_id)
                    synced += 1

                admin_names.append(user.display_name)

        admin_list = "\n".join(f"• {name}" for name in admin_names)
        await update.message.reply_text(
            f"""✅ Administradores sincronizados

👑 Admins del grupo:
{admin_list}

{synced} nuevos admins agregados."""
        )

    except Exception as e:
        logger.error(f"Error syncing admins: {e}")
        await update.message.reply_text(f"❌ Error al sincronizar: {e}")
