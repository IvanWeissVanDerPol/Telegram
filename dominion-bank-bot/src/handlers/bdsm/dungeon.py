"""
The Phantom Bot - Dungeon Command Handlers
/calabozo, /liberar_calabozo, /presos
"""
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.models import DungeonType, TransactionType
from src.database.repositories import (
    CollarRepository,
    DungeonRepository,
    TransactionRepository,
    UserRepository,
)
from src.utils.helpers import extract_username, format_time_ago

logger = logging.getLogger(__name__)

DUNGEON_COST = 200  # Cost to lock someone in dungeon
DUNGEON_DURATION_HOURS = 24  # Default dungeon duration


async def calabozo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /calabozo command - lock someone in the dungeon."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []
    if not args:
        await update.message.reply_text(
            "📝 Uso: /calabozo @usuario [razón]\n"
            f"💰 Costo: {DUNGEON_COST} {settings.currency_name}\n"
            f"⏱️ Duración: {DUNGEON_DURATION_HOURS} horas"
        )
        return

    target_username = extract_username(args[0])
    reason = " ".join(args[1:]) if len(args) > 1 else "Por orden del amo/a"

    if not target_username:
        await update.message.reply_text("❌ Debes especificar un usuario.")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)
        dungeon_repo = DungeonRepository(session)
        tx_repo = TransactionRepository(session)

        # Get jailer
        jailer = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not jailer:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Check balance
        if jailer.balance < DUNGEON_COST:
            await update.message.reply_text(
                f"❌ Necesitas {DUNGEON_COST} {settings.currency_name} para encerrar a alguien.\n"
                f"Tu saldo: {jailer.balance} {settings.currency_name}"
            )
            return

        # Get target
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text("❌ Usuario no encontrado.")
            return

        # Check self-lock
        if jailer.id == target.id:
            await update.message.reply_text("❌ No puedes encerrarte a ti mismo.")
            return

        # Check if target is already in dungeon
        existing = await dungeon_repo.get_by_user(target.id)
        if existing:
            await update.message.reply_text(
                f"❌ {target.display_name} ya está en el calabozo."
            )
            return

        # Check if jailer owns target's collar (free if owned)
        collar = await collar_repo.get_by_sub(target.id)
        is_owner = collar and collar.owner_id == jailer.id
        cost = 0 if is_owner else DUNGEON_COST

        if cost > 0:
            # Deduct cost
            await user_repo.update_balance(jailer.id, -cost)

            # Record transaction
            await tx_repo.create(
                sender_id=jailer.id,
                recipient_id=target.id,
                amount=cost,
                transaction_type=TransactionType.DUNGEON,
                description=f"Calabozo para {target.display_name}",
            )

        # Lock in dungeon
        await dungeon_repo.lock(
            user_id=target.id,
            locked_by_id=jailer.id,
            dungeon_type=DungeonType.STANDARD,
            reason=reason,
            hours=DUNGEON_DURATION_HOURS,
        )

        logger.info(f"Dungeon: {jailer.display_name} locked {target.display_name}")

        cost_msg = f"\n💰 -{cost} {settings.currency_name}" if cost > 0 else "\n(Gratis - es tu sumis@)"

    await update.message.reply_text(
        f"""🔒 **Calabozo**

{jailer.display_name} ha encerrado a {target.display_name}

📝 Razón: {reason}
⏱️ Duración: {DUNGEON_DURATION_HOURS} horas
{cost_msg}"""
    )


async def liberar_calabozo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /liberar_calabozo command - release someone from dungeon."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args_text = " ".join(context.args) if context.args else ""
    target_username = extract_username(args_text)

    if not target_username:
        await update.message.reply_text("📝 Uso: /liberar_calabozo @usuario")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        dungeon_repo = DungeonRepository(session)

        # Get releaser
        releaser = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not releaser:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get target
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text("❌ Usuario no encontrado.")
            return

        # Check if target is in dungeon
        dungeon = await dungeon_repo.get_by_user(target.id)
        if not dungeon:
            await update.message.reply_text(
                f"❌ {target.display_name} no está en el calabozo."
            )
            return

        # Check if releaser is the one who locked them
        if dungeon.locked_by != releaser.id:
            locker = await user_repo.get_by_id(dungeon.locked_by)
            locker_name = locker.display_name if locker else "Desconocido"
            await update.message.reply_text(
                f"❌ Solo {locker_name} puede liberar a {target.display_name}."
            )
            return

        # Release from dungeon
        await dungeon_repo.release(target.id)

        logger.info(f"Dungeon release: {releaser.display_name} released {target.display_name}")

    await update.message.reply_text(
        f"""🔓 **Liberado del Calabozo**

{releaser.display_name} ha liberado a {target.display_name} del calabozo."""
    )


async def presos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /presos command - list everyone in the dungeon."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        dungeon_repo = DungeonRepository(session)

        # Get all prisoners
        prisoners = await dungeon_repo.get_all_locked()

        if not prisoners:
            await update.message.reply_text("🔓 El calabozo está vacío.")
            return

        # Format list
        lines = []
        for i, p in enumerate(prisoners, 1):
            time_left = p.expires_at - datetime.utcnow() if p.expires_at else None
            if time_left and time_left.total_seconds() > 0:
                hours = int(time_left.total_seconds() / 3600)
                minutes = int((time_left.total_seconds() % 3600) / 60)
                if hours > 0:
                    time_str = f"{hours}h {minutes}m restantes"
                else:
                    time_str = f"{minutes}m restantes"
            else:
                time_str = "Liberación pendiente..."

            lines.append(
                f"{i}. {p.user.display_name}\n"
                f"   Por: {p.jailer.display_name} | {time_str}\n"
                f"   📝 {p.reason}"
            )

        prisoners_list = "\n".join(lines)

    await update.message.reply_text(
        f"""🔒 **Calabozo - Presos Actuales**

{prisoners_list}

Total: {len(prisoners)} preso(s)"""
    )


async def mi_calabozo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mi_calabozo command - check your dungeon status."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        dungeon_repo = DungeonRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Check if in dungeon
        dungeon = await dungeon_repo.get_by_user(user.id)

        if not dungeon:
            await update.message.reply_text("🔓 No estás en el calabozo. ¡Eres libre!")
            return

        time_left = dungeon.expires_at - datetime.utcnow() if dungeon.expires_at else None
        if time_left and time_left.total_seconds() > 0:
            hours = int(time_left.total_seconds() / 3600)
            minutes = int((time_left.total_seconds() % 3600) / 60)
            if hours > 0:
                time_str = f"{hours}h {minutes}m"
            else:
                time_str = f"{minutes} minutos"
        else:
            time_str = "Liberación inminente..."

        jailer = await user_repo.get_by_id(dungeon.locked_by)
        jailer_name = jailer.display_name if jailer else "Desconocido"

    await update.message.reply_text(
        f"""🔒 **Tu Estado en el Calabozo**

Encerrado por: {jailer_name}
Tiempo restante: {time_str}
Razón: {dungeon.reason}

Puedes suplicar libertad con /suplicar_libertad_calabozo"""
    )


async def suplicar_libertad_calabozo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /suplicar_libertad_calabozo command - beg to be released."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        dungeon_repo = DungeonRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Check if in dungeon
        dungeon = await dungeon_repo.get_by_user(user.id)

        if not dungeon:
            await update.message.reply_text("🔓 No estás en el calabozo.")
            return

        jailer = await user_repo.get_by_id(dungeon.locked_by)
        jailer_name = jailer.display_name if jailer else "Desconocido"

    await update.message.reply_text(
        f"""🔒 **Súplica de Libertad**

{user.display_name} suplica a {jailer_name} que le libere del calabozo.

{jailer_name} puede usar: /liberar_calabozo @{user.username or user.display_name}"""
    )
