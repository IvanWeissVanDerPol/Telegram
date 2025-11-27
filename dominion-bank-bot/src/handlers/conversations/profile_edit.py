"""
Profile Editing Conversation Handler
Multi-step conversation for editing user profiles.
"""
import logging
from enum import IntEnum, auto

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.config import settings
from src.database.connection import get_session
from src.database.repositories import ProfileRepository, UserRepository
from src.utils.validators import ValidationError, validate_age, validate_bio

logger = logging.getLogger(__name__)


class ProfileState(IntEnum):
    """States for profile editing conversation."""
    SELECTING_FIELD = auto()
    EDITING_BIO = auto()
    EDITING_AGE = auto()
    SELECTING_ROLE = auto()
    SELECTING_EXPERIENCE = auto()
    SELECTING_PRONOUNS = auto()


# Callback data prefixes
FIELD_PREFIX = "profile_field_"
ROLE_PREFIX = "profile_role_"
EXP_PREFIX = "profile_exp_"
PRONOUN_PREFIX = "profile_pronoun_"
CANCEL_CALLBACK = "profile_cancel"


def get_field_selection_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for selecting which field to edit."""
    keyboard = [
        [
            InlineKeyboardButton("Biografia", callback_data=f"{FIELD_PREFIX}bio"),
            InlineKeyboardButton("Edad", callback_data=f"{FIELD_PREFIX}age"),
        ],
        [
            InlineKeyboardButton("Rol", callback_data=f"{FIELD_PREFIX}role"),
            InlineKeyboardButton("Experiencia", callback_data=f"{FIELD_PREFIX}experience"),
        ],
        [
            InlineKeyboardButton("Pronombres", callback_data=f"{FIELD_PREFIX}pronouns"),
        ],
        [
            InlineKeyboardButton("Cancelar", callback_data=CANCEL_CALLBACK),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_role_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for role selection."""
    keyboard = [
        [
            InlineKeyboardButton("Dom", callback_data=f"{ROLE_PREFIX}dom"),
            InlineKeyboardButton("Sub", callback_data=f"{ROLE_PREFIX}sub"),
        ],
        [
            InlineKeyboardButton("Switch", callback_data=f"{ROLE_PREFIX}switch"),
            InlineKeyboardButton("Sin especificar", callback_data=f"{ROLE_PREFIX}none"),
        ],
        [
            InlineKeyboardButton("< Volver", callback_data=f"{FIELD_PREFIX}back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_experience_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for experience level selection."""
    keyboard = [
        [
            InlineKeyboardButton("Novato", callback_data=f"{EXP_PREFIX}novice"),
            InlineKeyboardButton("Intermedio", callback_data=f"{EXP_PREFIX}intermediate"),
        ],
        [
            InlineKeyboardButton("Experimentado", callback_data=f"{EXP_PREFIX}experienced"),
            InlineKeyboardButton("Experto", callback_data=f"{EXP_PREFIX}expert"),
        ],
        [
            InlineKeyboardButton("< Volver", callback_data=f"{FIELD_PREFIX}back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_pronouns_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for pronouns selection."""
    keyboard = [
        [
            InlineKeyboardButton("el/el", callback_data=f"{PRONOUN_PREFIX}he"),
            InlineKeyboardButton("ella/ella", callback_data=f"{PRONOUN_PREFIX}she"),
        ],
        [
            InlineKeyboardButton("elle/elle", callback_data=f"{PRONOUN_PREFIX}they"),
            InlineKeyboardButton("Prefiero no decir", callback_data=f"{PRONOUN_PREFIX}none"),
        ],
        [
            InlineKeyboardButton("< Volver", callback_data=f"{FIELD_PREFIX}back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_edit_profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Start the profile editing conversation."""
    if not update.effective_user or not update.message:
        return ConversationHandler.END

    user_id = update.effective_user.id

    # Check if user exists
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(user_id)

        if not user:
            await update.message.reply_text(
                "Primero debes registrarte con /start"
            )
            return ConversationHandler.END

        # Store user ID in context
        context.user_data["edit_user_id"] = user.id

    await update.message.reply_text(
        "**Editar Perfil**\n\n"
        "Selecciona que deseas editar:",
        reply_markup=get_field_selection_keyboard(),
    )

    return ProfileState.SELECTING_FIELD


async def handle_field_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle field selection from inline keyboard."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == CANCEL_CALLBACK:
        await query.edit_message_text("Edicion cancelada.")
        return ConversationHandler.END

    if data == f"{FIELD_PREFIX}back":
        await query.edit_message_text(
            "**Editar Perfil**\n\n"
            "Selecciona que deseas editar:",
            reply_markup=get_field_selection_keyboard(),
        )
        return ProfileState.SELECTING_FIELD

    field = data.replace(FIELD_PREFIX, "")

    if field == "bio":
        await query.edit_message_text(
            "**Editar Biografia**\n\n"
            "Escribe tu nueva biografia (maximo 500 caracteres):\n\n"
            "Escribe /cancelar para cancelar."
        )
        return ProfileState.EDITING_BIO

    elif field == "age":
        await query.edit_message_text(
            "**Editar Edad**\n\n"
            "Escribe tu edad (18-99):\n\n"
            "Escribe /cancelar para cancelar."
        )
        return ProfileState.EDITING_AGE

    elif field == "role":
        await query.edit_message_text(
            "**Seleccionar Rol**\n\n"
            "Elige tu rol:",
            reply_markup=get_role_keyboard(),
        )
        return ProfileState.SELECTING_ROLE

    elif field == "experience":
        await query.edit_message_text(
            "**Seleccionar Experiencia**\n\n"
            "Elige tu nivel de experiencia:",
            reply_markup=get_experience_keyboard(),
        )
        return ProfileState.SELECTING_EXPERIENCE

    elif field == "pronouns":
        await query.edit_message_text(
            "**Seleccionar Pronombres**\n\n"
            "Elige tus pronombres:",
            reply_markup=get_pronouns_keyboard(),
        )
        return ProfileState.SELECTING_PRONOUNS

    return ProfileState.SELECTING_FIELD


async def handle_bio_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle bio text input."""
    if not update.message or not update.message.text:
        return ProfileState.EDITING_BIO

    text = update.message.text

    if text.lower() == "/cancelar":
        await update.message.reply_text(
            "Edicion cancelada.",
        )
        return ConversationHandler.END

    # Validate bio
    try:
        bio = validate_bio(text, max_length=500)
    except ValidationError as e:
        await update.message.reply_text(f"{e.message}")
        return ProfileState.EDITING_BIO

    # Save bio
    user_db_id = context.user_data.get("edit_user_id")
    if not user_db_id:
        await update.message.reply_text("Error: usuario no encontrado.")
        return ConversationHandler.END

    async with get_session() as session:
        profile_repo = ProfileRepository(session)
        profile = await profile_repo.get_or_create(user_db_id)
        profile.bio = bio
        await session.commit()

    await update.message.reply_text(
        "Biografia actualizada.\n\n"
        "Quieres editar algo mas?",
        reply_markup=get_field_selection_keyboard(),
    )
    return ProfileState.SELECTING_FIELD


async def handle_age_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle age input."""
    if not update.message or not update.message.text:
        return ProfileState.EDITING_AGE

    text = update.message.text

    if text.lower() == "/cancelar":
        await update.message.reply_text("Edicion cancelada.")
        return ConversationHandler.END

    # Validate age
    try:
        age = validate_age(text)
    except ValidationError as e:
        await update.message.reply_text(f"{e.message}")
        return ProfileState.EDITING_AGE

    # Save age
    user_db_id = context.user_data.get("edit_user_id")
    if not user_db_id:
        await update.message.reply_text("Error: usuario no encontrado.")
        return ConversationHandler.END

    async with get_session() as session:
        profile_repo = ProfileRepository(session)
        profile = await profile_repo.get_or_create(user_db_id)
        profile.age = age
        await session.commit()

    await update.message.reply_text(
        f"Edad actualizada a {age}.\n\n"
        "Quieres editar algo mas?",
        reply_markup=get_field_selection_keyboard(),
    )
    return ProfileState.SELECTING_FIELD


async def handle_role_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle role selection from inline keyboard."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == f"{FIELD_PREFIX}back":
        await query.edit_message_text(
            "**Editar Perfil**\n\n"
            "Selecciona que deseas editar:",
            reply_markup=get_field_selection_keyboard(),
        )
        return ProfileState.SELECTING_FIELD

    role = data.replace(ROLE_PREFIX, "")

    # Map role values
    role_map = {
        "dom": "Dom",
        "sub": "Sub",
        "switch": "Switch",
        "none": None,
    }
    role_value = role_map.get(role)

    # Save role
    user_db_id = context.user_data.get("edit_user_id")
    if not user_db_id:
        await query.edit_message_text("Error: usuario no encontrado.")
        return ConversationHandler.END

    async with get_session() as session:
        profile_repo = ProfileRepository(session)
        profile = await profile_repo.get_or_create(user_db_id)
        profile.role = role_value
        await session.commit()

    role_display = role_value or "Sin especificar"
    await query.edit_message_text(
        f"Rol actualizado a: {role_display}\n\n"
        "Quieres editar algo mas?",
        reply_markup=get_field_selection_keyboard(),
    )
    return ProfileState.SELECTING_FIELD


async def handle_experience_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle experience selection from inline keyboard."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == f"{FIELD_PREFIX}back":
        await query.edit_message_text(
            "**Editar Perfil**\n\n"
            "Selecciona que deseas editar:",
            reply_markup=get_field_selection_keyboard(),
        )
        return ProfileState.SELECTING_FIELD

    exp = data.replace(EXP_PREFIX, "")

    # Map experience values
    exp_map = {
        "novice": "Novato",
        "intermediate": "Intermedio",
        "experienced": "Experimentado",
        "expert": "Experto",
    }
    exp_value = exp_map.get(exp, "Novato")

    # Save experience
    user_db_id = context.user_data.get("edit_user_id")
    if not user_db_id:
        await query.edit_message_text("Error: usuario no encontrado.")
        return ConversationHandler.END

    async with get_session() as session:
        profile_repo = ProfileRepository(session)
        profile = await profile_repo.get_or_create(user_db_id)
        profile.experience_level = exp_value
        await session.commit()

    await query.edit_message_text(
        f"Experiencia actualizada a: {exp_value}\n\n"
        "Quieres editar algo mas?",
        reply_markup=get_field_selection_keyboard(),
    )
    return ProfileState.SELECTING_FIELD


async def handle_pronouns_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle pronouns selection from inline keyboard."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == f"{FIELD_PREFIX}back":
        await query.edit_message_text(
            "**Editar Perfil**\n\n"
            "Selecciona que deseas editar:",
            reply_markup=get_field_selection_keyboard(),
        )
        return ProfileState.SELECTING_FIELD

    pronouns = data.replace(PRONOUN_PREFIX, "")

    # Map pronouns values
    pronouns_map = {
        "he": "el/el",
        "she": "ella/ella",
        "they": "elle/elle",
        "none": None,
    }
    pronouns_value = pronouns_map.get(pronouns)

    # Save pronouns
    user_db_id = context.user_data.get("edit_user_id")
    if not user_db_id:
        await query.edit_message_text("Error: usuario no encontrado.")
        return ConversationHandler.END

    async with get_session() as session:
        profile_repo = ProfileRepository(session)
        profile = await profile_repo.get_or_create(user_db_id)
        profile.pronouns = pronouns_value
        await session.commit()

    pronouns_display = pronouns_value or "Sin especificar"
    await query.edit_message_text(
        f"Pronombres actualizados a: {pronouns_display}\n\n"
        "Quieres editar algo mas?",
        reply_markup=get_field_selection_keyboard(),
    )
    return ProfileState.SELECTING_FIELD


async def cancel_edit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Cancel the conversation."""
    if update.message:
        await update.message.reply_text("Edicion cancelada.")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Edicion cancelada.")

    # Clean up context
    context.user_data.pop("edit_user_id", None)

    return ConversationHandler.END


async def timeout_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle conversation timeout."""
    if update.effective_user:
        try:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="La edicion de perfil ha expirado por inactividad.",
            )
        except Exception:
            pass

    context.user_data.pop("edit_user_id", None)
    return ConversationHandler.END


def get_profile_edit_conversation() -> ConversationHandler:
    """
    Create and return the profile editing ConversationHandler.

    This should be added to the application handlers.
    """
    return ConversationHandler(
        entry_points=[
            CommandHandler("editarperfil_wizard", start_edit_profile),
        ],
        states={
            ProfileState.SELECTING_FIELD: [
                CallbackQueryHandler(
                    handle_field_selection,
                    pattern=f"^({FIELD_PREFIX}|{CANCEL_CALLBACK})"
                ),
            ],
            ProfileState.EDITING_BIO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bio_input),
                CommandHandler("cancelar", cancel_edit),
            ],
            ProfileState.EDITING_AGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_age_input),
                CommandHandler("cancelar", cancel_edit),
            ],
            ProfileState.SELECTING_ROLE: [
                CallbackQueryHandler(
                    handle_role_selection,
                    pattern=f"^({ROLE_PREFIX}|{FIELD_PREFIX}back)"
                ),
            ],
            ProfileState.SELECTING_EXPERIENCE: [
                CallbackQueryHandler(
                    handle_experience_selection,
                    pattern=f"^({EXP_PREFIX}|{FIELD_PREFIX}back)"
                ),
            ],
            ProfileState.SELECTING_PRONOUNS: [
                CallbackQueryHandler(
                    handle_pronouns_selection,
                    pattern=f"^({PRONOUN_PREFIX}|{FIELD_PREFIX}back)"
                ),
            ],
            ConversationHandler.TIMEOUT: [
                MessageHandler(filters.ALL, timeout_handler),
            ],
        },
        fallbacks=[
            CommandHandler("cancelar", cancel_edit),
            CallbackQueryHandler(cancel_edit, pattern=f"^{CANCEL_CALLBACK}$"),
        ],
        conversation_timeout=300,  # 5 minutes
        name="profile_edit",
        persistent=False,
    )
