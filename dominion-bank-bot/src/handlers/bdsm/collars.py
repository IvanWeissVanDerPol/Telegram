"""
The Phantom Bot - Collar Command Handlers
/collar, /liberar, /exhibir, /amo, /aceptar_collar, /rechazar_collar
"""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.models import CollarType, TransactionType
from src.database.repositories import (
    CollarRepository,
    PendingRequestRepository,
    TransactionRepository,
    UserRepository,
)
from src.utils.helpers import extract_username, format_time_ago

logger = logging.getLogger(__name__)

COLLAR_COST = 300  # Cost to collar someone


async def collar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /collar command - request to collar someone."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args_text = " ".join(context.args) if context.args else ""
    target_username = extract_username(args_text)

    if not target_username:
        await update.message.reply_text(
            "📝 Uso: /collar @usuario\n"
            f"💰 Costo: {COLLAR_COST} {settings.currency_name}"
        )
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)
        request_repo = PendingRequestRepository(session)

        # Get owner (command sender)
        owner = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not owner:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Check balance
        if owner.balance < COLLAR_COST:
            await update.message.reply_text(
                f"❌ Necesitas {COLLAR_COST} {settings.currency_name} para poner un collar.\n"
                f"Tu saldo: {owner.balance} {settings.currency_name}"
            )
            return

        # Get target
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text("❌ Usuario no encontrado.")
            return

        # Check if target is already collared
        if await collar_repo.is_collared(target.id):
            await update.message.reply_text("❌ Este usuario ya lleva un collar.")
            return

        # Check self-collar
        if owner.id == target.id:
            await update.message.reply_text("❌ No puedes ponerte un collar a ti mismo.")
            return

        # Create pending request
        await request_repo.create_collar_request(
            from_user_id=owner.id,
            to_user_id=target.id,
            collar_type=CollarType.FORMAL,
            expires_in_minutes=5,
        )

        logger.info(f"Collar request: {owner.display_name} -> {target.display_name}")

    await update.message.reply_text(
        f"""⛓️ **Solicitud de Collar**

{owner.display_name} quiere ponerte su collar, {target.display_name}

💰 Costo para {owner.display_name}: {COLLAR_COST} {settings.currency_name}

Responde en 5 minutos:
/aceptar_collar - Aceptar
/rechazar_collar - Rechazar"""
    )


async def aceptar_collar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /aceptar_collar command - accept a collar request."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)
        request_repo = PendingRequestRepository(session)
        tx_repo = TransactionRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get pending request
        request = await request_repo.get_pending_collar(user.id)
        if not request:
            await update.message.reply_text("❌ No tienes solicitudes de collar pendientes.")
            return

        # Get owner
        owner = await user_repo.get_by_telegram_id(request.from_user.telegram_id)
        if not owner:
            await update.message.reply_text("❌ Error: Usuario no encontrado.")
            return

        # Check owner still has balance
        if owner.balance < COLLAR_COST:
            await request_repo.delete(request.id)
            await update.message.reply_text(
                f"❌ {owner.display_name} ya no tiene suficiente saldo."
            )
            return

        # Deduct cost from owner
        await user_repo.update_balance(owner.id, -COLLAR_COST)

        # Create collar
        await collar_repo.create(
            owner_id=owner.id,
            sub_id=user.id,
            collar_type=request.collar_type or CollarType.FORMAL,
        )

        # Record transaction
        await tx_repo.create(
            sender_id=owner.id,
            recipient_id=user.id,
            amount=COLLAR_COST,
            transaction_type=TransactionType.COLLAR,
            description=f"Collar para {user.display_name}",
        )

        # Delete request
        await request_repo.delete(request.id)

        logger.info(f"Collar accepted: {owner.display_name} collared {user.display_name}")

    await update.message.reply_text(
        f"""⛓️ **Collar Aceptado**

{user.display_name} ahora lleva el collar de {owner.display_name}

💰 -{COLLAR_COST} {settings.currency_name} ({owner.display_name})"""
    )


async def rechazar_collar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /rechazar_collar command - reject a collar request."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        request_repo = PendingRequestRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get pending request
        request = await request_repo.get_pending_collar(user.id)
        if not request:
            await update.message.reply_text("❌ No tienes solicitudes de collar pendientes.")
            return

        owner_name = request.from_user.display_name

        # Delete request
        await request_repo.delete(request.id)

        logger.info(f"Collar rejected by {user.display_name}")

    await update.message.reply_text(
        f"⛓️ Has rechazado el collar de {owner_name}."
    )


async def liberar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /liberar command - release someone from your collar."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args_text = " ".join(context.args) if context.args else ""
    target_username = extract_username(args_text)

    if not target_username:
        await update.message.reply_text("📝 Uso: /liberar @usuario")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)

        # Get owner
        owner = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not owner:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get target
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text("❌ Usuario no encontrado.")
            return

        # Get collar
        collar = await collar_repo.get_by_sub(target.id)
        if not collar:
            await update.message.reply_text(f"❌ {target.display_name} no lleva ningún collar.")
            return

        # Check ownership
        if collar.owner_id != owner.id:
            await update.message.reply_text(f"❌ {target.display_name} no lleva tu collar.")
            return

        # Remove collar
        await collar_repo.remove(collar.id)

        logger.info(f"Collar removed: {owner.display_name} released {target.display_name}")

    await update.message.reply_text(
        f"""⛓️ **Collar Removido**

{owner.display_name} ha liberado a {target.display_name}"""
    )


async def exhibir_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /exhibir command - show who wears your collar."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)

        # Get owner
        owner = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not owner:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get all collars owned
        collars = await collar_repo.get_by_owner(owner.id)

        if not collars:
            await update.message.reply_text("⛓️ No tienes a nadie con tu collar.")
            return

        # Format list
        lines = []
        for i, collar in enumerate(collars, 1):
            time_ago = format_time_ago(collar.created_at)
            lines.append(f"{i}. {collar.sub.display_name} (desde hace {time_ago})")

        subs_list = "\n".join(lines)

    await update.message.reply_text(
        f"""⛓️ **Propiedad de {owner.display_name}**

{subs_list}

Total: {len(collars)} sumis@s"""
    )


async def amo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /amo command - show who owns you."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get collar
        collar = await collar_repo.get_by_sub(user.id)

        if not collar:
            await update.message.reply_text(
                """⛓️ **Estás libre**

No llevas el collar de nadie."""
            )
            return

        time_ago = format_time_ago(collar.created_at)

    await update.message.reply_text(
        f"""⛓️ **Tu Dueño/a**

Llevas el collar de {collar.owner.display_name} desde hace {time_ago}."""
    )


async def suplicar_libertad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /suplicar_libertad command - request to be freed."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get collar
        collar = await collar_repo.get_by_sub(user.id)

        if not collar:
            await update.message.reply_text("⛓️ No llevas ningún collar.")
            return

        owner_name = collar.owner.display_name

    await update.message.reply_text(
        f"""⛓️ **Súplica de Libertad**

{user.display_name} suplica a {owner_name} que le libere.

{owner_name} puede usar: /liberar {user.display_name}"""
    )
