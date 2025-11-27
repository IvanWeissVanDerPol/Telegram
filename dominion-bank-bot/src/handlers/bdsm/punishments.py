"""
The Phantom Bot - Punishment Command Handlers
/azotar, /castigar, /mis_castigos
"""
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.models import PunishmentType, TransactionType
from src.database.repositories import (
    CollarRepository,
    PunishmentRepository,
    TransactionRepository,
    UserRepository,
)
from src.utils.helpers import extract_username, format_time_ago

logger = logging.getLogger(__name__)

WHIP_COST = 50  # Cost to whip someone
PUNISH_COST = 100  # Cost to punish someone (longer duration)


async def azotar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /azotar command - whip someone (quick punishment)."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args_text = " ".join(context.args) if context.args else ""
    target_username = extract_username(args_text)

    if not target_username:
        await update.message.reply_text(
            "📝 Uso: /azotar @usuario\n"
            f"💰 Costo: {WHIP_COST} {settings.currency_name}"
        )
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)
        punishment_repo = PunishmentRepository(session)
        tx_repo = TransactionRepository(session)

        # Get punisher
        punisher = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not punisher:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Check balance
        if punisher.balance < WHIP_COST:
            await update.message.reply_text(
                f"❌ Necesitas {WHIP_COST} {settings.currency_name} para azotar.\n"
                f"Tu saldo: {punisher.balance} {settings.currency_name}"
            )
            return

        # Get target
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text("❌ Usuario no encontrado.")
            return

        # Check self-punishment
        if punisher.id == target.id:
            await update.message.reply_text("❌ No puedes azotarte a ti mismo.")
            return

        # Check if punisher owns target's collar (can punish for free if owned)
        collar = await collar_repo.get_by_sub(target.id)
        is_owner = collar and collar.owner_id == punisher.id
        cost = 0 if is_owner else WHIP_COST

        if cost > 0:
            # Deduct cost
            await user_repo.update_balance(punisher.id, -cost)

            # Record transaction
            await tx_repo.create(
                sender_id=punisher.id,
                recipient_id=target.id,
                amount=cost,
                transaction_type=TransactionType.PUNISHMENT,
                description=f"Azote a {target.display_name}",
            )

        # Create punishment (expires in 10 minutes)
        await punishment_repo.create(
            user_id=target.id,
            punisher_id=punisher.id,
            punishment_type=PunishmentType.WHIP,
            description="Azotado",
            cost=cost,
            expires_in_minutes=10,
        )

        logger.info(f"Whip: {punisher.display_name} whipped {target.display_name}")

        cost_msg = f"\n💰 -{cost} {settings.currency_name}" if cost > 0 else "\n(Gratis - es tu sumis@)"

    await update.message.reply_text(
        f"""🔥 **Azote**

{punisher.display_name} ha azotado a {target.display_name}
{cost_msg}"""
    )


async def castigar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /castigar command - punish someone (longer duration, more severe)."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []
    if len(args) < 2:
        await update.message.reply_text(
            "📝 Uso: /castigar @usuario [razón]\n"
            f"💰 Costo: {PUNISH_COST} {settings.currency_name}\n"
            "⏱️ Duración: 1 hora"
        )
        return

    target_username = extract_username(args[0])
    reason = " ".join(args[1:]) if len(args) > 1 else "Sin razón especificada"

    if not target_username:
        await update.message.reply_text("❌ Debes especificar un usuario.")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)
        punishment_repo = PunishmentRepository(session)
        tx_repo = TransactionRepository(session)

        # Get punisher
        punisher = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not punisher:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Check balance
        if punisher.balance < PUNISH_COST:
            await update.message.reply_text(
                f"❌ Necesitas {PUNISH_COST} {settings.currency_name} para castigar.\n"
                f"Tu saldo: {punisher.balance} {settings.currency_name}"
            )
            return

        # Get target
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text("❌ Usuario no encontrado.")
            return

        # Check self-punishment
        if punisher.id == target.id:
            await update.message.reply_text("❌ No puedes castigarte a ti mismo.")
            return

        # Check if punisher owns target's collar
        collar = await collar_repo.get_by_sub(target.id)
        is_owner = collar and collar.owner_id == punisher.id
        cost = 0 if is_owner else PUNISH_COST

        if cost > 0:
            # Deduct cost
            await user_repo.update_balance(punisher.id, -cost)

            # Record transaction
            await tx_repo.create(
                sender_id=punisher.id,
                recipient_id=target.id,
                amount=cost,
                transaction_type=TransactionType.PUNISHMENT,
                description=f"Castigo a {target.display_name}: {reason}",
            )

        # Create punishment (expires in 60 minutes)
        await punishment_repo.create(
            user_id=target.id,
            punisher_id=punisher.id,
            punishment_type=PunishmentType.PUNISHMENT,
            description=reason,
            cost=cost,
            expires_in_minutes=60,
        )

        logger.info(f"Punishment: {punisher.display_name} punished {target.display_name}: {reason}")

        cost_msg = f"\n💰 -{cost} {settings.currency_name}" if cost > 0 else "\n(Gratis - es tu sumis@)"

    await update.message.reply_text(
        f"""⛓️ **Castigo**

{punisher.display_name} ha castigado a {target.display_name}

📝 Razón: {reason}
⏱️ Duración: 1 hora
{cost_msg}"""
    )


async def mis_castigos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mis_castigos command - show active punishments."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        punishment_repo = PunishmentRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get active punishments
        punishments = await punishment_repo.get_active_by_user(user.id)

        if not punishments:
            await update.message.reply_text("✨ No tienes castigos activos.")
            return

        # Format list
        lines = []
        for i, p in enumerate(punishments, 1):
            time_left = p.expires_at - datetime.utcnow() if p.expires_at else None
            if time_left and time_left.total_seconds() > 0:
                minutes = int(time_left.total_seconds() / 60)
                time_str = f"{minutes} min restantes"
            else:
                time_str = "Expirando..."

            type_emoji = "🔥" if p.punishment_type == PunishmentType.WHIP else "⛓️"
            lines.append(
                f"{i}. {type_emoji} {p.description}\n"
                f"   Por: {p.punisher.display_name} | {time_str}"
            )

        punishments_list = "\n".join(lines)

    await update.message.reply_text(
        f"""⛓️ **Tus Castigos Activos**

{punishments_list}

Total: {len(punishments)} castigo(s)"""
    )


async def castigos_dados_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /castigos_dados command - show punishments you've given."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        punishment_repo = PunishmentRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get punishments given
        punishments = await punishment_repo.get_given_by_user(user.id)

        if not punishments:
            await update.message.reply_text("📋 No has dado ningún castigo activo.")
            return

        # Format list
        lines = []
        for i, p in enumerate(punishments, 1):
            time_left = p.expires_at - datetime.utcnow() if p.expires_at else None
            if time_left and time_left.total_seconds() > 0:
                minutes = int(time_left.total_seconds() / 60)
                time_str = f"{minutes} min restantes"
            else:
                time_str = "Expirando..."

            type_emoji = "🔥" if p.punishment_type == PunishmentType.WHIP else "⛓️"
            lines.append(
                f"{i}. {type_emoji} {p.user.display_name}\n"
                f"   {p.description} | {time_str}"
            )

        punishments_list = "\n".join(lines)

    await update.message.reply_text(
        f"""⛓️ **Castigos que has dado**

{punishments_list}

Total: {len(punishments)} castigo(s) activo(s)"""
    )
