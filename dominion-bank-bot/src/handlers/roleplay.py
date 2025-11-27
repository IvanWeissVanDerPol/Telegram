"""
The Phantom Bot - AI-Powered Roleplay Commands
/escena, /ritual, /ambiente
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.database.connection import get_session
from src.database.repositories import UserRepository
from src.services.ai_service import get_ai_service
from src.utils.helpers import get_user_info, extract_username

logger = logging.getLogger(__name__)


async def escena_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /escena command - Generate atmospheric scene description."""
    if not update.effective_user or not update.message:
        return

    # Get theme from args
    theme = None
    if context.args:
        theme = " ".join(context.args)

    # Default themes if not specified
    default_themes = [
        "mazmorra oscura",
        "salon elegante",
        "habitacion secreta",
        "jardin nocturno",
        "biblioteca privada",
    ]

    if not theme:
        import random
        theme = random.choice(default_themes)

    ai = get_ai_service()
    scene = await ai.generate_scene(theme)

    response = f"""🏰 *AMBIENTACION* 🏰

📍 _{theme.title()}_

{scene}

💡 _Usa /escena [tema] para especificar_
"""

    await update.message.reply_text(response, parse_mode="Markdown")


async def ritual_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ritual command - Generate ritual/ceremony description."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    dom_name = user_info.get("first_name", "Dom")

    # Parse args for sub name and ritual type
    sub_name = "sumis@"
    ritual_type = "sumision"

    if context.args:
        args = " ".join(context.args)
        # Check for ritual type keywords
        ritual_types = ["sumision", "collar", "castigo", "recompensa", "iniciacion", "devucion"]
        for rt in ritual_types:
            if rt in args.lower():
                ritual_type = rt
                args = args.lower().replace(rt, "").strip()
                break
        if args:
            sub_name = extract_username(args)

    ai = get_ai_service()
    ritual = await ai.generate_ritual(dom_name, sub_name, ritual_type)

    # Ritual type emojis
    ritual_emojis = {
        "sumision": "🛐",
        "collar": "⭕",
        "castigo": "⚡",
        "recompensa": "🌟",
        "iniciacion": "🔥",
        "devocion": "💎",
    }
    emoji = ritual_emojis.get(ritual_type, "🕯️")

    response = f"""{emoji} *RITUAL DE {ritual_type.upper()}* {emoji}

👑 *{dom_name}* y 🧎 *{sub_name}*

{ritual}

🕯️ _El ritual ha sido completado..._
"""

    await update.message.reply_text(response, parse_mode="Markdown")


async def titulo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /titulo command - Generate noble/BDSM title for user."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    user_name = user_info.get("first_name", "Usuario")

    # Get role from args or default
    role = "switch"  # default
    if context.args:
        arg = context.args[0].lower()
        if arg in ["dom", "dominante", "amo", "ama"]:
            role = "Dominante"
        elif arg in ["sub", "sumiso", "sumisa"]:
            role = "Sumis@"
        elif arg in ["switch"]:
            role = "Switch"

    ai = get_ai_service()
    title = await ai.generate_title(user_name, role)

    response = f"""👑 *TITULO OTORGADO* 👑

*{user_name}* ({role})

{title}

📜 _Que este titulo sea tu emblema..._
"""

    await update.message.reply_text(response, parse_mode="Markdown")


async def descripcion_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /descripcion_ai command - Generate AI bio for profile."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    user_name = user_info.get("first_name", "Usuario")

    # Get role from args
    role = "misterios@"
    if context.args:
        role = " ".join(context.args)

    ai = get_ai_service()
    bio = await ai.generate_bio(user_name, role)

    response = f"""✍️ *BIOGRAFIA GENERADA* ✍️

Para: *{user_name}* ({role})

{bio}

💡 _Puedes copiar esto para tu perfil con /editarperfil_
"""

    await update.message.reply_text(response, parse_mode="Markdown")


async def compatibilidad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /compatibilidad command - Analyze compatibility between two users."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    user1_name = user_info.get("first_name", "Usuario")
    user1_role = "Desconocido"

    # Parse second user from args
    if not context.args:
        await update.message.reply_text(
            "Uso: /compatibilidad @usuario [tu_rol] [su_rol]\n"
            "Ejemplo: /compatibilidad @persona dom sub"
        )
        return

    args = context.args
    user2_name = extract_username(args[0])
    user2_role = "Desconocido"

    # Parse roles if provided
    if len(args) >= 2:
        user1_role = args[1].capitalize()
    if len(args) >= 3:
        user2_role = args[2].capitalize()

    # Loading message
    loading_msg = await update.message.reply_text("💕 Analizando compatibilidad...")

    ai = get_ai_service()
    analysis = await ai.analyze_compatibility(user1_name, user1_role, user2_name, user2_role)

    response = f"""💕 *ANALISIS DE COMPATIBILIDAD* 💕

👤 *{user1_name}* ({user1_role})
     ❤️
👤 *{user2_name}* ({user2_role})

{analysis}

✨ _Los astros han hablado..._
"""

    await loading_msg.edit_text(response, parse_mode="Markdown")
