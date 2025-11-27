"""
The Phantom Bot - AI-Powered Game Commands
/ruleta, /dado_perverso, /verdad_reto, /prediccion
"""
import logging
import random

from telegram import Update
from telegram.ext import ContextTypes

from src.database.connection import get_session
from src.database.repositories import UserRepository
from src.services.ai_service import get_ai_service
from src.utils.helpers import get_user_info

logger = logging.getLogger(__name__)


async def ruleta_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ruleta command - BDSM roulette with random consequences."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    user_name = user_info.get("first_name", "Usuario")

    # Roulette wheel options with weights
    options = [
        ("reward", 15, "has ganado un premio"),
        ("punishment", 20, "recibes un castigo"),
        ("task", 25, "tienes una tarea"),
        ("dare", 20, "debes cumplir un reto"),
        ("skip", 10, "te has salvado... por ahora"),
        ("double", 5, "DOBLE o NADA"),
        ("mystery", 5, "el misterio te espera"),
    ]

    weights = [w for _, w, _ in options]
    result = random.choices(options, weights=weights, k=1)[0]
    category, _, description = result

    # Spinning animation message
    spin_msg = await update.message.reply_text("🎰 La ruleta gira...")

    # Generate AI content based on result
    ai = get_ai_service()

    if category == "reward":
        content = await ai.generate("reward", f"El usuario {user_name} ha ganado en la ruleta.")
        emoji = "🌟"
    elif category == "punishment":
        content = await ai.generate("punishment", f"El usuario {user_name} ha perdido en la ruleta.")
        emoji = "⚡"
    elif category == "task":
        content = await ai.generate("task", f"Genera una tarea para {user_name} que perdio en la ruleta.")
        emoji = "📝"
    elif category == "dare":
        content = await ai.generate("dare", f"Genera un reto para {user_name}.")
        emoji = "🔥"
    elif category == "skip":
        content = "La ruleta se detiene justo antes de caer en un castigo. Has tenido suerte... esta vez."
        emoji = "😅"
    elif category == "double":
        # Double or nothing - spin again with higher stakes
        second_spin = random.choice(["big_win", "big_loss"])
        if second_spin == "big_win":
            content = await ai.generate("reward", f"{user_name} apostó doble y GANÓ.")
            emoji = "🎉"
        else:
            content = await ai.generate("punishment", f"{user_name} apostó doble y PERDIÓ.")
            emoji = "💀"
    else:  # mystery
        mystery_type = random.choice(["prediction", "truth", "fantasy"])
        content = await ai.generate(mystery_type, f"Para {user_name}.")
        emoji = "🔮"

    # Build response
    response = f"""🎰 *RULETA DEL DESTINO* 🎰

{emoji} *{user_name}*, {description}!

{content}
"""

    await spin_msg.edit_text(response, parse_mode="Markdown")


async def dado_perverso_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /dado_perverso command - Perverse dice with AI interpretation."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    user_name = user_info.get("first_name", "Usuario")

    # Parse dice type from args
    dice_types = {
        "accion": ["Azotar", "Besar", "Acariciar", "Morder", "Atar", "Vendar"],
        "intensidad": ["Suave", "Moderado", "Intenso", "Extremo", "A eleccion del Dom", "Sorpresa"],
        "zona": ["Espalda", "Gluteos", "Piernas", "Cuello", "Manos", "A eleccion"],
        "duracion": ["1 minuto", "5 minutos", "10 minutos", "15 minutos", "30 minutos", "Hasta que el Dom decida"],
        "destino": ["Recompensa", "Castigo", "Tarea", "Reto", "Libertad", "Calabozo"],
    }

    dice_type = "destino"  # default
    if context.args:
        requested = context.args[0].lower()
        if requested in dice_types:
            dice_type = requested

    # Roll the dice
    dice_result = random.randint(1, 6)
    result_text = dice_types[dice_type][dice_result - 1]

    # Dice animation
    dice_faces = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
    rolling_msg = await update.message.reply_text("🎲 Lanzando el dado...")

    # Get AI interpretation
    ai = get_ai_service()
    interpretation = await ai.interpret_dice(
        dice_result,
        f"{dice_type}: {result_text}"
    )

    # Build response
    available_types = ", ".join(dice_types.keys())
    response = f"""🎲 *DADO PERVERSO* 🎲

{user_name} lanza el dado de *{dice_type.upper()}*...

{dice_faces[dice_result - 1]} El dado cae en: *{dice_result}*

📜 *Resultado:* {result_text}

{interpretation}

💡 _Tipos disponibles: {available_types}_
_Usa: /dado_perverso [tipo]_
"""

    await rolling_msg.edit_text(response, parse_mode="Markdown")


async def verdad_reto_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /verdad_reto command - Truth or Dare BDSM edition."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    user_name = user_info.get("first_name", "Usuario")

    # Check if user specified truth or dare
    choice = None
    if context.args:
        arg = context.args[0].lower()
        if arg in ["verdad", "v", "truth", "t"]:
            choice = "truth"
        elif arg in ["reto", "r", "dare", "d"]:
            choice = "dare"

    # If not specified, random choice
    if not choice:
        choice = random.choice(["truth", "dare"])

    ai = get_ai_service()

    if choice == "truth":
        content = await ai.generate_truth()
        emoji = "🔍"
        title = "VERDAD"
    else:
        content = await ai.generate_dare()
        emoji = "🔥"
        title = "RETO"

    response = f"""🎭 *VERDAD O RETO* 🎭

{emoji} *{user_name}*, te toca *{title}*!

{content}

💡 _Usa /verdad_reto [verdad|reto] para elegir_
"""

    await update.message.reply_text(response, parse_mode="Markdown")


async def prediccion_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /prediccion command - AI fortune telling."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    user_name = user_info.get("first_name", "Usuario")

    # Check if predicting for someone else
    target_name = user_name
    if context.args:
        target_name = " ".join(context.args).replace("@", "")

    # Crystal ball animation
    crystal_msg = await update.message.reply_text("🔮 Consultando el oraculo...")

    ai = get_ai_service()
    prediction = await ai.generate_prediction(target_name)

    # Random mystical elements
    mystical_symbols = ["✨", "🌙", "⭐", "🌟", "💫"]
    symbols = " ".join(random.sample(mystical_symbols, 3))

    response = f"""🔮 *EL ORACULO HABLA* 🔮

{symbols}

*Prediccion para {target_name}:*

{prediction}

{symbols}

_El destino esta escrito en las estrellas..._
"""

    await crystal_msg.edit_text(response, parse_mode="Markdown")


async def fantasia_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /fantasia command - Generate fantasy roleplay scenarios."""
    if not update.effective_user or not update.message:
        return

    user_info = get_user_info(update.effective_user)
    user_name = user_info.get("first_name", "Usuario")

    # Fantasy themes
    themes = ["medieval", "vampiros", "piratas", "mansion", "academia", "futuro"]
    theme = None
    if context.args:
        requested = context.args[0].lower()
        if requested in themes:
            theme = requested

    ai = get_ai_service()
    fantasy = await ai.generate_fantasy()

    response = f"""🌌 *ESCENARIO DE FANTASIA* 🌌

{fantasy}

💡 _Temas disponibles: {", ".join(themes)}_
_Usa: /fantasia [tema]_
"""

    await update.message.reply_text(response, parse_mode="Markdown")
