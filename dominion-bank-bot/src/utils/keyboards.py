"""
Inline Keyboard Utilities
Provides reusable keyboard layouts and callback handling.
"""
import json
import logging
from typing import Any, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


# Callback data prefixes for routing
class CallbackPrefix:
    """Prefixes for callback data to identify action types."""
    CONFIRM = "confirm"
    CANCEL = "cancel"
    PAGINATE = "page"
    MENU = "menu"
    SELECT = "select"
    EDIT = "edit"
    DELETE = "delete"


def build_callback_data(prefix: str, action: str, **kwargs) -> str:
    """
    Build callback data string.

    Format: prefix:action:json_data

    Args:
        prefix: Action prefix (from CallbackPrefix)
        action: Specific action name
        **kwargs: Additional data to encode

    Returns:
        str: Callback data string (max 64 bytes)
    """
    data = {"a": action}  # 'a' for action to save space
    data.update(kwargs)

    # Encode as compact JSON
    json_data = json.dumps(data, separators=(",", ":"))

    result = f"{prefix}:{json_data}"

    # Telegram limit is 64 bytes
    if len(result.encode("utf-8")) > 64:
        logger.warning(f"Callback data too long: {result}")
        # Truncate data if needed
        result = result[:64]

    return result


def parse_callback_data(data: str) -> tuple[str, dict[str, Any]]:
    """
    Parse callback data string.

    Returns:
        tuple: (prefix, parsed_data_dict)
    """
    try:
        parts = data.split(":", 1)
        if len(parts) == 2:
            prefix = parts[0]
            payload = json.loads(parts[1])
            return prefix, payload
        return parts[0], {}
    except (json.JSONDecodeError, ValueError):
        return data, {}


def confirmation_keyboard(
    action: str,
    item_id: Optional[int] = None,
    confirm_text: str = "Confirmar",
    cancel_text: str = "Cancelar",
) -> InlineKeyboardMarkup:
    """
    Create a confirmation dialog keyboard.

    Args:
        action: The action to confirm
        item_id: Optional ID of the item being confirmed
        confirm_text: Text for confirm button
        cancel_text: Text for cancel button

    Returns:
        InlineKeyboardMarkup
    """
    confirm_data = build_callback_data(
        CallbackPrefix.CONFIRM,
        action,
        id=item_id,
    ) if item_id else build_callback_data(CallbackPrefix.CONFIRM, action)

    cancel_data = build_callback_data(CallbackPrefix.CANCEL, action)

    keyboard = [
        [
            InlineKeyboardButton(confirm_text, callback_data=confirm_data),
            InlineKeyboardButton(cancel_text, callback_data=cancel_data),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def yes_no_keyboard(
    action: str,
    item_id: Optional[int] = None,
) -> InlineKeyboardMarkup:
    """Create a simple Yes/No keyboard."""
    return confirmation_keyboard(
        action=action,
        item_id=item_id,
        confirm_text="Si",
        cancel_text="No",
    )


def pagination_keyboard(
    current_page: int,
    total_pages: int,
    action: str,
    extra_data: Optional[dict] = None,
) -> InlineKeyboardMarkup:
    """
    Create a pagination keyboard.

    Args:
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
        action: Action name for callback
        extra_data: Additional data to include

    Returns:
        InlineKeyboardMarkup
    """
    buttons = []

    # Previous button
    if current_page > 1:
        data = {"p": current_page - 1}
        if extra_data:
            data.update(extra_data)
        buttons.append(InlineKeyboardButton(
            "< Anterior",
            callback_data=build_callback_data(
                CallbackPrefix.PAGINATE,
                action,
                **data
            )
        ))

    # Page indicator
    buttons.append(InlineKeyboardButton(
        f"{current_page}/{total_pages}",
        callback_data="noop"
    ))

    # Next button
    if current_page < total_pages:
        data = {"p": current_page + 1}
        if extra_data:
            data.update(extra_data)
        buttons.append(InlineKeyboardButton(
            "Siguiente >",
            callback_data=build_callback_data(
                CallbackPrefix.PAGINATE,
                action,
                **data
            )
        ))

    return InlineKeyboardMarkup([buttons])


def menu_keyboard(
    options: list[tuple[str, str]],
    columns: int = 2,
    action: str = "menu",
) -> InlineKeyboardMarkup:
    """
    Create a menu keyboard with multiple options.

    Args:
        options: List of (button_text, option_value) tuples
        columns: Number of columns for layout
        action: Action name for callback

    Returns:
        InlineKeyboardMarkup
    """
    buttons = []
    row = []

    for text, value in options:
        callback_data = build_callback_data(
            CallbackPrefix.MENU,
            action,
            v=value
        )
        row.append(InlineKeyboardButton(text, callback_data=callback_data))

        if len(row) >= columns:
            buttons.append(row)
            row = []

    # Add remaining buttons
    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(buttons)


def back_button(action: str = "back") -> InlineKeyboardMarkup:
    """Create a simple back button keyboard."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "< Volver",
            callback_data=build_callback_data(CallbackPrefix.MENU, action)
        )
    ]])


def close_button() -> InlineKeyboardMarkup:
    """Create a close/dismiss button keyboard."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "Cerrar",
            callback_data=build_callback_data(CallbackPrefix.CANCEL, "close")
        )
    ]])


# Pre-built common keyboards
CONFIRM_DELETE = confirmation_keyboard(
    "delete",
    confirm_text="Eliminar",
    cancel_text="Cancelar"
)

CONFIRM_CLEANDB = confirmation_keyboard(
    "cleandb",
    confirm_text="Si, limpiar todo",
    cancel_text="No, cancelar"
)

CONFIRM_QUITAR = confirmation_keyboard(
    "quitar",
    confirm_text="Si, quitar",
    cancel_text="No, cancelar"
)


def profile_edit_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for profile editing options."""
    options = [
        ("Biografia", "bio"),
        ("Edad", "age"),
        ("Rol", "role"),
        ("Experiencia", "experience"),
        ("Pronombres", "pronouns"),
    ]
    keyboard = menu_keyboard(options, columns=2, action="edit_profile")

    # Add cancel button
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            "Cancelar",
            callback_data=build_callback_data(CallbackPrefix.CANCEL, "edit_profile")
        )
    ])

    return keyboard


def role_selection_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for role selection."""
    roles = [
        ("Dom", "dom"),
        ("Sub", "sub"),
        ("Switch", "switch"),
        ("Sin especificar", "none"),
    ]
    return menu_keyboard(roles, columns=2, action="select_role")


def experience_selection_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for experience level selection."""
    levels = [
        ("Novato", "novice"),
        ("Intermedio", "intermediate"),
        ("Experimentado", "experienced"),
        ("Experto", "expert"),
    ]
    return menu_keyboard(levels, columns=2, action="select_experience")


def pronouns_selection_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for pronouns selection."""
    pronouns = [
        ("el/el", "he"),
        ("ella/ella", "she"),
        ("elle/elle", "they"),
        ("Prefiero no decir", "none"),
    ]
    return menu_keyboard(pronouns, columns=2, action="select_pronouns")
