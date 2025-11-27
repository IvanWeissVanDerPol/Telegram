"""
The Phantom Bot - Core Command Handlers
/start, /ver, /dar
"""
import logging
from datetime import datetime, timezone

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
            remaining = (cooldown_expires - datetime.now(timezone.utc)).total_seconds()
            await update.message.reply_text(
                ERROR_COOLDOWN.format(seconds=int(max(0, remaining)))
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

        # Extract all values BEFORE leaving session context to avoid detached object issues
        sender_balance = sender.balance
        sender_display = sender.display_name
        recipient_balance = recipient.balance
        recipient_display = recipient.display_name
        recipient_telegram_id = recipient.telegram_id

        logger.info(f"Transfer: {sender_display} -> {recipient_display}: {amount}")

    # Send confirmation to sender (using extracted values, not detached objects)
    await update.message.reply_text(
        transfer_success_sender(amount, recipient_display, sender_balance)
    )

    # Try to notify recipient (may fail if bot can't message them)
    try:
        await context.bot.send_message(
            chat_id=recipient_telegram_id,
            text=transfer_success_recipient(amount, sender_display, recipient_balance),
        )
    except Exception as e:
        logger.warning(f"Could not notify recipient: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - show available commands based on user role."""
    if not update.message or not update.effective_user:
        return

    # Check if user is admin
    is_admin = False
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if user:
            is_admin = user.is_admin

    # Build help text based on enabled features and user role
    help_sections = []

    # Header
    if is_admin:
        help_sections.append(f"🎭 {settings.bot_name} - Comandos (Admin)\n")
    else:
        help_sections.append(f"🎭 {settings.bot_name} - Comandos\n")

    # Basic commands
    help_sections.append(f"""💰 BÁSICOS:
/start - Registrarse en el bot
/ver - Ver tu saldo actual
/dar @user cantidad - Enviar {settings.currency_name}
/ranking - Top 10 usuarios
/historial - Tus últimas transacciones
/stats - Estadísticas generales""")

    # Profile commands
    help_sections.append("""👤 PERFIL:
/perfil - Ver tu perfil (o /perfil @user)
/editarperfil - Modificar tu perfil
/configuracion - Ajustes de privacidad""")

    # BDSM commands (only if enabled)
    if settings.enable_bdsm_commands:
        help_sections.append("""🔗 COLLARES:
/collar @user - Poner collar (300 💎)
/liberar @user - Liberar sumiso
/exhibir - Ver tus collares
/amo - Ver tu Amo/Ama
/aceptar_collar - Aceptar collar pendiente
/rechazar_collar - Rechazar collar
/suplicar_libertad - Pedir libertad""")

        help_sections.append("""⚡ CASTIGOS:
/azotar @user [razón] - Azotar (50 💎)
/castigar @user tipo razón - Castigar
/mis_castigos - Ver castigos recibidos
/castigos_dados - Ver castigos dados""")

        help_sections.append("""🏰 CALABOZO:
/calabozo @user [horas] - Encerrar (200 💎)
/liberar_calabozo @user - Liberar preso
/mi_calabozo - Ver tu estado
/presos - Ver presos actuales
/suplicar_libertad_calabozo - Pedir salir""")

        help_sections.append("""🔨 SUBASTAS:
/subasta @user precio_inicial - Subastar
/pujar subasta_id cantidad - Hacer puja
/subastas - Ver subastas activas
/ver_subasta id - Detalles de subasta
/mis_subastas - Tus subastas
/cancelar_subasta id - Cancelar""")

        help_sections.append("""📜 CONTRATOS:
/contrato @user términos - Proponer
/firmar_contrato id - Firmar contrato
/rechazar_contrato id - Rechazar
/romper_contrato id - Romper (500 💎)
/mis_contratos - Ver tus contratos
/ver_contrato id - Detalles""")

        help_sections.append("""🛐 TRIBUTOS:
/tributo @user cantidad - Dar tributo
/adorar @user - Adorar (gratis)
/altar @user - Ver altar de alguien
/mi_altar - Ver tu altar
/devotos - Ver tus devotos""")

    # Admin commands - only show to admins
    if is_admin:
        help_sections.append(f"""👑 ADMIN:
/dar_admin @user cantidad - Dar {settings.currency_name}
/quitar @user cantidad - Quitar {settings.currency_name}
/consultar @user - Ver saldo de usuario
/setadmin @user - Hacer admin
/removeadmin @user - Quitar admin
/syncadmins - Sincronizar admins del grupo
/importar - Importar datos (Excel)
/exportar - Exportar datos (Excel)

🧪 TESTING:
/runtest - Ejecutar tests automáticos
/testdb - Test rápido de sistema""")

    help_text = "\n\n".join(help_sections)
    await update.message.reply_text(help_text)
