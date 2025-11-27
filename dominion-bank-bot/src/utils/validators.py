"""
Input Validation Utilities
Provides functions for validating and sanitizing user input.
"""
import html
import logging
import re
from typing import Optional, Union

from telegram import Update, User

from src.config import settings

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input text.

    - Escapes HTML entities
    - Strips leading/trailing whitespace
    - Limits length
    - Removes null bytes
    """
    if not text:
        return ""

    # Remove null bytes
    text = text.replace("\x00", "")

    # Strip whitespace
    text = text.strip()

    # Escape HTML
    text = html.escape(text)

    # Limit length
    if len(text) > max_length:
        text = text[:max_length]

    return text


def sanitize_username(username: str) -> str:
    """
    Sanitize and validate a Telegram username.

    - Removes @ prefix if present
    - Validates format (alphanumeric + underscore)
    - Length between 5-32 characters
    """
    if not username:
        raise ValidationError("Username cannot be empty", "username")

    # Remove @ prefix
    username = username.lstrip("@")

    # Validate format
    if not re.match(r"^[a-zA-Z0-9_]{5,32}$", username):
        raise ValidationError(
            "Username invalido. Debe tener 5-32 caracteres (letras, numeros, _)",
            "username"
        )

    return username


def validate_amount(
    value: Union[str, int, float],
    min_amount: Optional[int] = None,
    max_amount: Optional[int] = None,
    allow_negative: bool = False,
) -> int:
    """
    Validate and parse a currency amount.

    Args:
        value: The amount to validate
        min_amount: Minimum allowed (default: settings.min_transfer_amount)
        max_amount: Maximum allowed (default: settings.max_transfer_amount)
        allow_negative: Whether to allow negative amounts

    Returns:
        int: The validated amount

    Raises:
        ValidationError: If validation fails
    """
    min_amount = min_amount if min_amount is not None else settings.min_transfer_amount
    max_amount = max_amount if max_amount is not None else settings.max_transfer_amount

    # Parse string
    if isinstance(value, str):
        value = value.strip().replace(",", "").replace(".", "")

        # Remove currency symbols
        value = re.sub(r"[^\d-]", "", value)

        if not value or value == "-":
            raise ValidationError(
                "Cantidad invalida. Introduce un numero.",
                "amount"
            )

        try:
            value = int(value)
        except ValueError:
            raise ValidationError(
                "Cantidad invalida. Introduce un numero entero.",
                "amount"
            )

    # Convert float to int
    if isinstance(value, float):
        value = int(value)

    # Validate negative
    if not allow_negative and value < 0:
        raise ValidationError(
            "La cantidad no puede ser negativa.",
            "amount"
        )

    # Validate minimum
    if value < min_amount:
        raise ValidationError(
            f"La cantidad minima es {min_amount} {settings.currency_name}.",
            "amount"
        )

    # Validate maximum
    if value > max_amount:
        raise ValidationError(
            f"La cantidad maxima es {max_amount} {settings.currency_name}.",
            "amount"
        )

    return value


def validate_age(value: Union[str, int]) -> int:
    """
    Validate an age value.

    Returns:
        int: The validated age (18-99)

    Raises:
        ValidationError: If validation fails
    """
    if isinstance(value, str):
        value = value.strip()
        if not value.isdigit():
            raise ValidationError("Edad invalida. Introduce un numero.", "age")
        value = int(value)

    if value < 18:
        raise ValidationError("Debes ser mayor de 18 anos.", "age")

    if value > 99:
        raise ValidationError("Edad invalida.", "age")

    return value


def validate_bio(text: str, max_length: int = 500) -> str:
    """
    Validate and sanitize a bio/description.

    Returns:
        str: The sanitized bio

    Raises:
        ValidationError: If validation fails
    """
    text = sanitize_text(text, max_length)

    if len(text) < 1:
        raise ValidationError("La biografia no puede estar vacia.", "bio")

    return text


def parse_user_mention(
    update: Update,
    args: list[str],
    context_bot,
) -> Optional[User]:
    """
    Parse a user from message arguments or reply.

    Supports:
    - Reply to a message
    - @username mention
    - User ID

    Returns:
        User object or None if not found
    """
    # Check reply first
    if update.message and update.message.reply_to_message:
        return update.message.reply_to_message.from_user

    if not args:
        return None

    target = args[0]

    # Try as username
    if target.startswith("@"):
        # Note: Can't resolve username without additional API calls
        # Return None and let caller handle
        return None

    # Try as user ID
    try:
        user_id = int(target)
        # Note: Need to fetch user info from database or Telegram
        return None
    except ValueError:
        pass

    return None


def validate_duration(
    value: Union[str, int],
    min_hours: int = 1,
    max_hours: int = 168,
) -> int:
    """
    Validate a duration in hours.

    Returns:
        int: The validated duration in hours

    Raises:
        ValidationError: If validation fails
    """
    if isinstance(value, str):
        value = value.strip()

        # Parse common formats
        match = re.match(r"^(\d+)\s*(h|hrs?|hours?)?$", value, re.IGNORECASE)
        if match:
            value = int(match.group(1))
        else:
            try:
                value = int(value)
            except ValueError:
                raise ValidationError(
                    "Duracion invalida. Usa un numero de horas.",
                    "duration"
                )

    if value < min_hours:
        raise ValidationError(
            f"La duracion minima es {min_hours} hora(s).",
            "duration"
        )

    if value > max_hours:
        raise ValidationError(
            f"La duracion maxima es {max_hours} horas ({max_hours // 24} dias).",
            "duration"
        )

    return value


def validate_message_length(
    text: str,
    max_length: int = 4096,
    field_name: str = "mensaje",
) -> str:
    """
    Validate message length for Telegram limits.

    Returns:
        str: The validated text

    Raises:
        ValidationError: If too long
    """
    if len(text) > max_length:
        raise ValidationError(
            f"El {field_name} es demasiado largo. "
            f"Maximo {max_length} caracteres.",
            field_name
        )
    return text


def validate_command_args(
    args: list[str],
    required: int = 0,
    max_args: Optional[int] = None,
    command_name: str = "comando",
) -> list[str]:
    """
    Validate command arguments count.

    Args:
        args: List of arguments
        required: Minimum required arguments
        max_args: Maximum allowed arguments
        command_name: Name of the command for error messages

    Returns:
        list: The validated arguments

    Raises:
        ValidationError: If validation fails
    """
    if len(args) < required:
        raise ValidationError(
            f"Faltan argumentos. El comando {command_name} requiere "
            f"{required} argumento(s).",
            "args"
        )

    if max_args is not None and len(args) > max_args:
        raise ValidationError(
            f"Demasiados argumentos. El comando {command_name} acepta "
            f"maximo {max_args} argumento(s).",
            "args"
        )

    return args


# Regex patterns for common validations
PATTERNS = {
    "username": re.compile(r"^@?[a-zA-Z0-9_]{5,32}$"),
    "user_id": re.compile(r"^\d{5,15}$"),
    "amount": re.compile(r"^\d+$"),
    "duration": re.compile(r"^\d+\s*(h|hrs?|hours?)?$", re.IGNORECASE),
    "safe_text": re.compile(r"^[\w\s\.,!?()-]+$", re.UNICODE),
}


def matches_pattern(value: str, pattern_name: str) -> bool:
    """Check if value matches a predefined pattern."""
    pattern = PATTERNS.get(pattern_name)
    if not pattern:
        return False
    return bool(pattern.match(value))
