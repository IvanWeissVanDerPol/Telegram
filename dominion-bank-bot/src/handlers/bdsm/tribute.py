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
from src.utils.messages import (
    DIVIDER,
    DIVIDER_LIGHT,
    EMOJI_BALANCE,
    EMOJI_ERROR,
    EMOJI_INFO,
    EMOJI_SUCCESS,
    format_currency,
)

logger = logging.getLogger(__name__)

# Custom emojis for tribute system
EMOJI_TRIBUTE = "💎"
EMOJI_CROWN = "👑"
EMOJI_DEVOTEE = "🙇"
EMOJI_ALTAR = "🏛️"
EMOJI_WORSHIP = "✨"

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
            f"""{EMOJI_TRIBUTE} **Pagar Tributo**

{DIVIDER_LIGHT}

{EMOJI_INFO} **Uso:** /tributo @usuario cantidad

{EMOJI_BALANCE} **Mínimo:** {format_currency(MIN_TRIBUTE)}

**Ejemplo:** /tributo @Amo 100"""
        )
        return

    target_username = extract_username(args[0])
    amount = parse_amount(args[1]) if len(args) > 1 else None

    if not target_username:
        await update.message.reply_text(f"{EMOJI_ERROR} Debes especificar un usuario.")
        return

    if amount is None or amount < MIN_TRIBUTE:
        await update.message.reply_text(
            f"{EMOJI_ERROR} El tributo mínimo es {format_currency(MIN_TRIBUTE)}."
        )
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        altar_repo = AltarRepository(session)
        tx_repo = TransactionRepository(session)

        # Get tribute payer
        payer = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not payer:
            await update.message.reply_text(f"{EMOJI_ERROR} Debes registrarte primero con /start")
            return

        # Check balance
        if payer.balance < amount:
            await update.message.reply_text(
                f"""{EMOJI_ERROR} **Saldo Insuficiente**

{DIVIDER_LIGHT}

{EMOJI_BALANCE} Tu saldo: {format_currency(payer.balance)}
{EMOJI_TRIBUTE} Tributo: {format_currency(amount)}"""
            )
            return

        # Get recipient
        recipient = await user_repo.get_by_username(target_username)
        if not recipient:
            await update.message.reply_text(f"{EMOJI_ERROR} Usuario no encontrado.")
            return

        # Check self-tribute
        if payer.id == recipient.id:
            await update.message.reply_text(f"{EMOJI_ERROR} No puedes pagarte tributo a ti mismo.")
            return

        # Capture names before leaving session
        payer_name = payer.display_name
        recipient_name = recipient.display_name
        new_payer_balance = payer.balance - amount

        # Transfer the tribute
        await user_repo.update_balance(payer.id, -amount)
        await user_repo.update_balance(recipient.id, amount)

        # Record transaction
        await tx_repo.create(
            sender_id=payer.id,
            recipient_id=recipient.id,
            amount=amount,
            transaction_type=TransactionType.TRIBUTE,
            description=f"Tributo de {payer_name}",
        )

        # Update altar stats
        await altar_repo.add_tribute(recipient.id, payer.id, amount)

        logger.info(f"Tribute: {payer_name} paid {amount} to {recipient_name}")

    await update.message.reply_text(
        f"""{EMOJI_TRIBUTE} **Tributo Pagado** {EMOJI_WORSHIP}

{DIVIDER}

{EMOJI_DEVOTEE} **{payer_name}** se arrodilla ante **{recipient_name}**

{DIVIDER_LIGHT}

{EMOJI_BALANCE} **Cantidad:** {format_currency(amount)}

{DIVIDER_LIGHT}

{payer_name}: {format_currency(new_payer_balance)}
{recipient_name}: +{format_currency(amount)}

{EMOJI_CROWN} Gloria a {recipient_name}!"""
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
            f"""{EMOJI_DEVOTEE} **Adorar**

{DIVIDER_LIGHT}

{EMOJI_INFO} **Uso:** /adorar @usuario [mensaje]

**Ejemplo:** /adorar @Ama Es la mas poderosa"""
        )
        return

    target_username = extract_username(args[0])
    message = " ".join(args[1:]) if len(args) > 1 else "Te adoro, mi senor/a"

    if not target_username:
        await update.message.reply_text(f"{EMOJI_ERROR} Debes especificar un usuario.")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)

        # Get worshipper
        worshipper = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not worshipper:
            await update.message.reply_text(f"{EMOJI_ERROR} Debes registrarte primero con /start")
            return

        # Get target
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text(f"{EMOJI_ERROR} Usuario no encontrado.")
            return

        # Check self-worship
        if worshipper.id == target.id:
            await update.message.reply_text(f"{EMOJI_ERROR} No puedes adorarte a ti mismo.")
            return

        # Check if worshipper wears target's collar (special message)
        collar = await collar_repo.get_by_sub(worshipper.id)
        is_collared = collar and collar.owner_id == target.id

        # Capture names before leaving session
        worshipper_name = worshipper.display_name
        target_name = target.display_name

        collar_msg = "\n\n⛓️ _(Lleva su collar)_" if is_collared else ""

        logger.info(f"Worship: {worshipper_name} worshipped {target_name}")

    await update.message.reply_text(
        f"""{EMOJI_DEVOTEE} **Adoracion** {EMOJI_WORSHIP}

{DIVIDER}

**{worshipper_name}** se arrodilla ante **{target_name}**{collar_msg}

{DIVIDER_LIGHT}

💬 _"{message}"_

{DIVIDER_LIGHT}

{EMOJI_CROWN} Gloria a **{target_name}**!"""
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
            await update.message.reply_text(
                f"""{EMOJI_ALTAR} **Altar de Tributos**

{DIVIDER_LIGHT}

{EMOJI_INFO} Aun no se han pagado tributos.

Se el primero en rendir tributo con /tributo"""
            )
            return

        # Format leaderboard
        lines = []
        medals = [f"{EMOJI_CROWN}", f"{EMOJI_TRIBUTE}", f"{EMOJI_WORSHIP}"]
        for i, (user, total) in enumerate(top_receivers, 1):
            medal = medals[i - 1] if i <= 3 else f"`{i}.`"
            lines.append(f"{medal} **{user.display_name}**: {format_currency(total)}")

        leaderboard = "\n".join(lines)

    await update.message.reply_text(
        f"""{EMOJI_ALTAR} **Altar de Tributos** {EMOJI_TRIBUTE}

{DIVIDER}

**Los mas adorados:**

{DIVIDER_LIGHT}

{leaderboard}

{DIVIDER_LIGHT}

{EMOJI_DEVOTEE} Rinde tributo con /tributo @usuario cantidad"""
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
            await update.message.reply_text(f"{EMOJI_ERROR} Debes registrarte primero con /start")
            return

        # Get altar stats
        received = await altar_repo.get_total_received(user.id)
        given = await altar_repo.get_total_given(user.id)
        devotees = await altar_repo.get_devotee_count(user.id)

        user_name = user.display_name

    # Determine status based on stats
    if received > given:
        status = f"{EMOJI_CROWN} **Status:** Adorado/a"
    elif given > received:
        status = f"{EMOJI_DEVOTEE} **Status:** Devoto/a"
    else:
        status = f"{EMOJI_WORSHIP} **Status:** Neutral"

    await update.message.reply_text(
        f"""{EMOJI_ALTAR} **Altar de {user_name}** {EMOJI_TRIBUTE}

{DIVIDER}

{status}

{DIVIDER_LIGHT}

{EMOJI_CROWN} **Tributos recibidos:** {format_currency(received)}
{EMOJI_DEVOTEE} **Devotos unicos:** {devotees}
{EMOJI_BALANCE} **Tributos pagados:** {format_currency(given)}

{DIVIDER_LIGHT}

{EMOJI_INFO} Ver tus devotos: /devotos"""
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
            await update.message.reply_text(f"{EMOJI_ERROR} Debes registrarte primero con /start")
            return

        user_name = user.display_name

        # Get devotees
        devotees = await altar_repo.get_devotees(user.id, limit=10)

        if not devotees:
            await update.message.reply_text(
                f"""{EMOJI_DEVOTEE} **Tus Devotos**

{DIVIDER_LIGHT}

{EMOJI_INFO} Aun no tienes devotos.

Comparte tu perfil para que otros te rindan tributo!"""
            )
            return

        # Format list
        lines = []
        medals = [f"{EMOJI_CROWN}", f"{EMOJI_TRIBUTE}", f"{EMOJI_WORSHIP}"]
        for i, (devotee, total) in enumerate(devotees, 1):
            medal = medals[i - 1] if i <= 3 else f"`{i}.`"
            lines.append(f"{medal} **{devotee.display_name}**: {format_currency(total)}")

        devotees_list = "\n".join(lines)

    await update.message.reply_text(
        f"""{EMOJI_DEVOTEE} **Devotos de {user_name}** {EMOJI_CROWN}

{DIVIDER}

**Los que mas te adoran:**

{DIVIDER_LIGHT}

{devotees_list}

{DIVIDER_LIGHT}

{EMOJI_TRIBUTE} Estos son los que te han pagado mas tributos."""
    )
