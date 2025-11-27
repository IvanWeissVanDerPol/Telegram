"""
The Phantom Bot - Message Templates
"""
from src.config import settings


def format_balance(amount: int) -> str:
    """Format balance with thousands separator."""
    return f"{amount:,}".replace(",", ".")


def welcome_message(balance: int, username: str) -> str:
    """Welcome message for new users."""
    return f"""🎭 ¡Bienvenido/a a {settings.bot_name}!

Tu wallet de {settings.currency_name} {settings.currency_emoji}

📜 Comandos:
/ver - Tu saldo
/dar @user cantidad - Enviar
/ranking - Top usuarios
/historial - Tus movimientos

💰 Tu saldo: {format_balance(balance)} {settings.currency_name}"""


def balance_message(balance: int) -> str:
    """Balance check message."""
    if balance == 0:
        return f"""{settings.currency_emoji} Tu saldo: 0 {settings.currency_name}

Aún no tienes {settings.currency_name}."""

    return f"{settings.currency_emoji} Tu saldo: {format_balance(balance)} {settings.currency_name}"


def transfer_success_sender(amount: int, recipient: str, new_balance: int) -> str:
    """Transfer success message for sender."""
    return f"""✅ Transferencia exitosa

{settings.currency_emoji} Enviaste {format_balance(amount)} {settings.currency_name} a {recipient}
💰 Tu nuevo saldo: {format_balance(new_balance)} {settings.currency_name}"""


def transfer_success_recipient(amount: int, sender: str, new_balance: int) -> str:
    """Transfer success message for recipient."""
    return f"""🎁 ¡Has recibido {settings.currency_name}!

{settings.currency_emoji} {sender} te envió {format_balance(amount)} {settings.currency_name}
💰 Tu nuevo saldo: {format_balance(new_balance)} {settings.currency_name}"""


def admin_give_message(amount: int, recipient: str, admin: str, new_balance: int) -> str:
    """Admin give coins message."""
    return f"""✅ {settings.currency_name} otorgados

{settings.currency_emoji} {admin} dio {format_balance(amount)} {settings.currency_name} a {recipient}
💰 Nuevo saldo de {recipient}: {format_balance(new_balance)} {settings.currency_name}"""


def admin_remove_message(amount: int, target: str, admin: str, new_balance: int) -> str:
    """Admin remove coins message."""
    return f"""✅ {settings.currency_name} removidos

{settings.currency_emoji} {admin} quitó {format_balance(amount)} {settings.currency_name} a {target}
💰 Nuevo saldo de {target}: {format_balance(new_balance)} {settings.currency_name}"""


def ranking_message(
    users: list[tuple[int, str, int]],
    user_position: int | None,
    user_balance: int,
) -> str:
    """Ranking leaderboard message."""
    lines = [f"🏆 Ranking de {settings.currency_name}\n"]

    medals = ["👑", "🥈", "🥉"]

    for i, (_, name, balance) in enumerate(users):
        medal = medals[i] if i < 3 else f"{i + 1}."
        lines.append(f"{medal} {name} — {format_balance(balance)} {settings.currency_emoji}")

    lines.append("\n━━━━━━━━━━━━━━━━")

    if user_position:
        lines.append(
            f"📍 Tu posición: {user_position} con {format_balance(user_balance)} {settings.currency_name}"
        )
    else:
        lines.append(f"💰 Tu saldo: {format_balance(user_balance)} {settings.currency_name}")

    return "\n".join(lines)


def history_message(
    transactions: list[dict],
    current_balance: int,
) -> str:
    """Transaction history message."""
    if not transactions:
        return f"""📜 Tu historial

No tienes transacciones aún.

💰 Saldo actual: {format_balance(current_balance)} {settings.currency_name}"""

    lines = ["📜 Tu historial\n"]

    for i, tx in enumerate(transactions, 1):
        if tx["type"] == "sent":
            lines.append(f"{i}. ➡️ -{format_balance(tx['amount'])} → {tx['other']} ({tx['time']})")
        elif tx["type"] == "received":
            lines.append(f"{i}. ⬅️ +{format_balance(tx['amount'])} ← {tx['other']} ({tx['time']})")
        elif tx["type"] == "admin_give":
            lines.append(f"{i}. 🎁 +{format_balance(tx['amount'])} Admin ({tx['time']})")
        elif tx["type"] == "admin_remove":
            lines.append(f"{i}. 😈 -{format_balance(tx['amount'])} Admin ({tx['time']})")
        else:
            lines.append(f"{i}. 📝 {tx['amount']} ({tx['time']})")

    lines.append("\n━━━━━━━━━━━━━━━━")
    lines.append(f"💰 Saldo actual: {format_balance(current_balance)} {settings.currency_name}")

    return "\n".join(lines)


# Error messages
ERROR_NOT_REGISTERED = "❌ No estás registrado. Usa /start primero."
ERROR_USER_NOT_FOUND = "❌ Usuario no encontrado."
ERROR_INVALID_AMOUNT = "❌ Cantidad inválida. Debe ser un número positivo."
ERROR_INSUFFICIENT_BALANCE = "❌ Saldo insuficiente."
ERROR_SELF_TRANSFER = "❌ No puedes enviarte a ti mismo."
ERROR_NOT_ADMIN = "❌ No tienes permisos de administrador."
ERROR_COOLDOWN = "⏳ Espera {seconds} segundos antes de volver a transferir."
ERROR_MIN_AMOUNT = f"❌ La cantidad mínima es {settings.min_transfer_amount} {settings.currency_name}."
ERROR_MAX_AMOUNT = f"❌ La cantidad máxima es {format_balance(settings.max_transfer_amount)} {settings.currency_name}."

# Usage messages
USAGE_DAR = f"📝 Uso: /dar @usuario cantidad\n\nEjemplo: /dar @maria 100"
USAGE_DAR_ADMIN = f"📝 Uso: /dar_admin @usuario cantidad\n\nEjemplo: /dar_admin @maria 500"
USAGE_QUITAR = f"📝 Uso: /quitar @usuario cantidad\n\nEjemplo: /quitar @maria 100"
USAGE_CONSULTAR = f"📝 Uso: /consultar @usuario\n\nEjemplo: /consultar @maria"
