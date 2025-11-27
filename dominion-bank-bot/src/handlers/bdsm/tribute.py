"""
The Phantom Bot - Tribute/Worship Command Handlers
/tributo, /adorar, /altar
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.models import TransactionType
from src.database.repositories import (
    AltarRepository,
    CollarRepository,
    TransactionRepository,
    UserRepository,
)
from src.utils.helpers import extract_username, parse_amount

logger = logging.getLogger(__name__)

MIN_TRIBUTE = 10  # Minimum tribute amount


async def tributo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tributo command - pay tribute to someone."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []
    if len(args) < 2:
        await update.message.reply_text(
            "📝 Uso: /tributo @usuario cantidad\n"
            f"💰 Mínimo: {MIN_TRIBUTE} {settings.currency_name}\n"
            "Ejemplo: /tributo @Amo 100"
        )
        return

    target_username = extract_username(args[0])
    amount = parse_amount(args[1]) if len(args) > 1 else None

    if not target_username:
        await update.message.reply_text("❌ Debes especificar un usuario.")
        return

    if amount is None or amount < MIN_TRIBUTE:
        await update.message.reply_text(
            f"❌ El tributo mínimo es {MIN_TRIBUTE} {settings.currency_name}."
        )
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        altar_repo = AltarRepository(session)
        tx_repo = TransactionRepository(session)

        # Get tribute payer
        payer = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not payer:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Check balance
        if payer.balance < amount:
            await update.message.reply_text(
                f"❌ No tienes suficiente saldo.\n"
                f"Tu saldo: {payer.balance} {settings.currency_name}\n"
                f"Tributo: {amount} {settings.currency_name}"
            )
            return

        # Get recipient
        recipient = await user_repo.get_by_username(target_username)
        if not recipient:
            await update.message.reply_text("❌ Usuario no encontrado.")
            return

        # Check self-tribute
        if payer.id == recipient.id:
            await update.message.reply_text("❌ No puedes pagarte tributo a ti mismo.")
            return

        # Transfer the tribute
        await user_repo.update_balance(payer.id, -amount)
        await user_repo.update_balance(recipient.id, amount)

        # Record transaction
        await tx_repo.create(
            sender_id=payer.id,
            recipient_id=recipient.id,
            amount=amount,
            transaction_type=TransactionType.TRIBUTE,
            description=f"Tributo de {payer.display_name}",
        )

        # Update altar stats
        await altar_repo.add_tribute(recipient.id, payer.id, amount)

        logger.info(f"Tribute: {payer.display_name} paid {amount} to {recipient.display_name}")

    await update.message.reply_text(
        f"""💎 **Tributo Pagado**

{payer.display_name} ha pagado tributo a {recipient.display_name}

💰 Cantidad: {amount} {settings.currency_name}

{payer.display_name}: {payer.balance - amount} {settings.currency_name}
{recipient.display_name}: +{amount} {settings.currency_name}"""
    )


async def adorar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /adorar command - worship someone publicly."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []
    if not args:
        await update.message.reply_text(
            "📝 Uso: /adorar @usuario [mensaje]\n"
            "Ejemplo: /adorar @Ama Es la más poderosa"
        )
        return

    target_username = extract_username(args[0])
    message = " ".join(args[1:]) if len(args) > 1 else "Te adoro, mi señor/a"

    if not target_username:
        await update.message.reply_text("❌ Debes especificar un usuario.")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)

        # Get worshipper
        worshipper = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not worshipper:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get target
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text("❌ Usuario no encontrado.")
            return

        # Check self-worship
        if worshipper.id == target.id:
            await update.message.reply_text("❌ No puedes adorarte a ti mismo. 😏")
            return

        # Check if worshipper wears target's collar (special message)
        collar = await collar_repo.get_by_sub(worshipper.id)
        is_collared = collar and collar.owner_id == target.id

        collar_msg = "\n⛓️ (Lleva su collar)" if is_collared else ""

        logger.info(f"Worship: {worshipper.display_name} worshipped {target.display_name}")

    await update.message.reply_text(
        f"""🙇 **Adoración**

{worshipper.display_name} se arrodilla ante {target.display_name}{collar_msg}

💬 "{message}"

Gloria a {target.display_name}! 👑"""
    )


async def altar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /altar command - show tribute leaderboard."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        altar_repo = AltarRepository(session)

        # Get top tribute receivers
        top_receivers = await altar_repo.get_top_receivers(limit=10)

        if not top_receivers:
            await update.message.reply_text("💎 Aún no se han pagado tributos.")
            return

        # Format leaderboard
        lines = []
        medals = ["👑", "💎", "✨"]
        for i, (user, total) in enumerate(top_receivers, 1):
            medal = medals[i - 1] if i <= 3 else f"{i}."
            lines.append(f"{medal} {user.display_name}: {total} {settings.currency_name}")

        leaderboard = "\n".join(lines)

    await update.message.reply_text(
        f"""💎 **Altar de Tributos**

Los más adorados:

{leaderboard}"""
    )


async def mi_altar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mi_altar command - show your tribute stats."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        altar_repo = AltarRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get altar stats
        received = await altar_repo.get_total_received(user.id)
        given = await altar_repo.get_total_given(user.id)
        devotees = await altar_repo.get_devotee_count(user.id)

    await update.message.reply_text(
        f"""💎 **Tu Altar**

👑 Tributos recibidos: {received} {settings.currency_name}
🙇 Devotos únicos: {devotees}
💰 Tributos pagados: {given} {settings.currency_name}"""
    )


async def devotos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /devotos command - show your devotees."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        altar_repo = AltarRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get devotees
        devotees = await altar_repo.get_devotees(user.id, limit=10)

        if not devotees:
            await update.message.reply_text("💎 Aún no tienes devotos.")
            return

        # Format list
        lines = []
        for i, (devotee, total) in enumerate(devotees, 1):
            lines.append(f"{i}. {devotee.display_name}: {total} {settings.currency_name}")

        devotees_list = "\n".join(lines)

    await update.message.reply_text(
        f"""🙇 **Tus Devotos**

{devotees_list}

Estos son los que te han pagado más tributos."""
    )
