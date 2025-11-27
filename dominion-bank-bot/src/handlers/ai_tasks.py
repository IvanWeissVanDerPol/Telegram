"""
The Phantom Bot - AI-Powered Task & Challenge Commands
/tarea, /reto, /castigo_creativo, /recompensa
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.database.connection import get_session
from src.database.repositories import UserRepository, CollarRepository
from src.services.ai_service import get_ai_service
from src.utils.helpers import get_user_info, extract_username

logger = logging.getLogger(__name__)


async def tarea_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tarea command - Generate AI task for a sub."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    dom_name = user_info.get("first_name", "Dom")

    # Check if targeting someone specific
    target_name = None
    if context.args:
        target_name = extract_username(" ".join(context.args))

    async with get_session() as session:
        user_repo = UserRepository(session)
        collar_repo = CollarRepository(session)

        # Get the dom user
        dom = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not dom:
            await update.message.reply_text("Debes registrarte primero con /start")
            return

        # If no target specified, check if they have subs
        if not target_name:
            collars = await collar_repo.get_dom_collars(dom.id)
            if collars:
                # Pick a random sub to assign task
                import random
                collar = random.choice(collars)
                sub = await user_repo.get_by_id(collar.sub_id)
                target_name = sub.display_name if sub else "sumis@"
            else:
                target_name = "sumis@"

    ai = get_ai_service()
    task = await ai.generate_task(target_name, dom_name)

    response = f"""📝 *NUEVA TAREA* 📝

👑 *{dom_name}* ordena:

{task}

🎯 _Para: {target_name}_
"""

    await update.message.reply_text(response, parse_mode="Markdown")


async def reto_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /reto command - Generate AI challenge between users."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    challenger_name = user_info.get("first_name", "Usuario")

    # Get target
    target_name = "alguien"
    if context.args:
        target_name = extract_username(" ".join(context.args))

    ai = get_ai_service()
    challenge = await ai.generate_challenge(challenger_name, target_name)

    response = f"""⚔️ *RETO LANZADO* ⚔️

{challenger_name} reta a {target_name}!

{challenge}

🔥 _El honor esta en juego..._
"""

    await update.message.reply_text(response, parse_mode="Markdown")


async def castigo_creativo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /castigo_creativo command - Generate creative AI punishment."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    dom_name = user_info.get("first_name", "Dom")

    # Parse target and optional reason
    target_name = "el/la desobediente"
    reason = None

    if context.args:
        parts = " ".join(context.args).split(" por ", 1)
        target_name = extract_username(parts[0])
        if len(parts) > 1:
            reason = parts[1]

    ai = get_ai_service()
    punishment = await ai.generate_punishment(dom_name, target_name, reason)

    response = f"""⚡ *CASTIGO DECRETADO* ⚡

👑 *{dom_name}* castiga a *{target_name}*
"""

    if reason:
        response += f"\n📜 _Razon: {reason}_\n"

    response += f"""
{punishment}

⛓️ _Que sirva de leccion..._
"""

    await update.message.reply_text(response, parse_mode="Markdown")


async def recompensa_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /recompensa command - Generate AI reward for good behavior."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    dom_name = user_info.get("first_name", "Dom")

    # Get target
    target_name = "el/la obediente"
    if context.args:
        target_name = extract_username(" ".join(context.args))

    ai = get_ai_service()
    reward = await ai.generate_reward(dom_name, target_name)

    response = f"""🌟 *RECOMPENSA OTORGADA* 🌟

👑 *{dom_name}* recompensa a *{target_name}*

{reward}

💎 _La obediencia tiene sus frutos..._
"""

    await update.message.reply_text(response, parse_mode="Markdown")


async def protocolo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /protocolo command - Generate AI protocol rules for a sub."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)

    # Get target
    target_name = "sumis@"
    if context.args:
        target_name = extract_username(" ".join(context.args))

    ai = get_ai_service()
    protocol = await ai.generate_protocol(target_name)

    response = f"""📜 *PROTOCOLO DE COMPORTAMIENTO* 📜

Para: *{target_name}*

{protocol}

⚠️ _El incumplimiento tendra consecuencias..._
"""

    await update.message.reply_text(response, parse_mode="Markdown")
