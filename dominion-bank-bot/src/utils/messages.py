"""
The Phantom Bot - Message Templates
Beautiful, consistent message formatting for Telegram
"""
from src.config import settings


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATTING CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Visual dividers
DIVIDER = "━━━━━━━━━━━━━━━━━━━━"
DIVIDER_LIGHT = "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈"
DIVIDER_DOUBLE = "══════════════════════"

# Status emojis
EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_INFO = "ℹ️"
EMOJI_LOADING = "⏳"
EMOJI_GIFT = "🎁"

# Feature emojis
EMOJI_BALANCE = "💰"
EMOJI_CURRENCY = settings.currency_emoji
EMOJI_TRANSFER = "💸"
EMOJI_RANKING = "🏆"
EMOJI_HISTORY = "📜"
EMOJI_PROFILE = "👤"
EMOJI_ADMIN = "👑"
EMOJI_BOT = "🎭"

# BDSM emojis
EMOJI_COLLAR = "⛓️"
EMOJI_WHIP = "🔥"
EMOJI_DUNGEON = "🏰"
EMOJI_AUCTION = "🔨"
EMOJI_TRIBUTE = "💎"
EMOJI_CONTRACT = "📜"

# Role emojis
EMOJI_DOM = "👑"
EMOJI_SUB = "🔗"
EMOJI_SWITCH = "🔄"

# Privacy emojis
EMOJI_PUBLIC = "🌍"
EMOJI_FRIENDS = "👥"
EMOJI_PRIVATE = "🔒"

# Medal emojis for ranking
MEDALS = ["👑", "🥈", "🥉"]


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATTING UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def format_balance(amount: int) -> str:
    """Format balance with thousands separator (Spanish format)."""
    return f"{amount:,}".replace(",", ".")


def format_header(emoji: str, title: str) -> str:
    """Format a message header consistently."""
    return f"{emoji} **{title}**"


def format_section(title: str, content: str) -> str:
    """Format a section with title and content."""
    return f"**{title}:**\n{content}"


def format_balance_line(balance: int, prefix: str = "Saldo") -> str:
    """Format a balance display line."""
    return f"{EMOJI_BALANCE} {prefix}: {format_balance(balance)} {settings.currency_name}"


def format_currency(amount: int) -> str:
    """Format amount with currency name."""
    return f"{format_balance(amount)} {settings.currency_name}"


# ═══════════════════════════════════════════════════════════════════════════════
# WELCOME & REGISTRATION MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

def welcome_message(balance: int, username: str) -> str:
    """Welcome message for new users."""
    display_name = f"@{username}" if username else "usuario"
    return f"""{EMOJI_BOT} **¡Bienvenido/a a {settings.bot_name}!**

Hola {display_name}, soy tu compañero para gestionar
{settings.currency_name} {EMOJI_CURRENCY} en el grupo.

{DIVIDER}
{EMOJI_BALANCE} **Tu saldo inicial:** {format_currency(balance)}
{DIVIDER}

{EMOJI_INFO} **Comandos básicos:**
• /ver — Consulta tu saldo
• /dar @user cantidad — Envía {settings.currency_name}
• /ranking — Top usuarios
• /historial — Tus movimientos
• /perfil — Tu perfil

{EMOJI_COLLAR} /help — Ver todos los comandos"""


def welcome_back_message(balance: int, username: str) -> str:
    """Welcome back message for returning users."""
    display_name = f"@{username}" if username else "usuario"
    return f"""{EMOJI_BOT} **¡Hola de nuevo!**

Bienvenido/a de vuelta, {display_name}

{DIVIDER}
{EMOJI_BALANCE} **Tu saldo:** {format_currency(balance)}
{DIVIDER}"""


# ═══════════════════════════════════════════════════════════════════════════════
# BALANCE MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

def balance_message(balance: int) -> str:
    """Balance check message."""
    if balance == 0:
        return f"""{EMOJI_CURRENCY} **Tu saldo**

{EMOJI_BALANCE} 0 {settings.currency_name}

{DIVIDER_LIGHT}
{EMOJI_INFO} Aún no tienes {settings.currency_name}.
Pide a alguien que te envíe o usa /help"""

    return f"""{EMOJI_CURRENCY} **Tu saldo**

{EMOJI_BALANCE} {format_currency(balance)}"""


def balance_query_message(username: str, balance: int) -> str:
    """Balance query for another user."""
    return f"""{EMOJI_PROFILE} **Consulta de saldo**

{EMOJI_BALANCE} @{username} tiene:
**{format_currency(balance)}**"""


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSFER MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

def transfer_success_sender(amount: int, recipient: str, new_balance: int) -> str:
    """Transfer success message for sender."""
    return f"""{EMOJI_SUCCESS} **Transferencia exitosa**

{EMOJI_TRANSFER} Enviaste **{format_currency(amount)}**
{EMOJI_PROFILE} Destinatario: {recipient}

{DIVIDER_LIGHT}
{format_balance_line(new_balance, "Tu nuevo saldo")}"""


def transfer_success_recipient(amount: int, sender: str, new_balance: int) -> str:
    """Transfer success message for recipient."""
    return f"""{EMOJI_GIFT} **¡Has recibido {settings.currency_name}!**

{EMOJI_TRANSFER} **{format_currency(amount)}**
{EMOJI_PROFILE} De: {sender}

{DIVIDER_LIGHT}
{format_balance_line(new_balance, "Tu nuevo saldo")}"""


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

def admin_give_message(amount: int, recipient: str, admin: str, new_balance: int) -> str:
    """Admin give coins message."""
    return f"""{EMOJI_ADMIN} **{settings.currency_name} otorgados**

{EMOJI_TRANSFER} +**{format_currency(amount)}**
{EMOJI_PROFILE} Para: {recipient}
{EMOJI_ADMIN} Por: {admin}

{DIVIDER_LIGHT}
{format_balance_line(new_balance, f"Nuevo saldo de {recipient}")}"""


def admin_remove_message(amount: int, target: str, admin: str, new_balance: int) -> str:
    """Admin remove coins message."""
    return f"""{EMOJI_ADMIN} **{settings.currency_name} removidos**

{EMOJI_TRANSFER} -**{format_currency(amount)}**
{EMOJI_PROFILE} De: {target}
{EMOJI_ADMIN} Por: {admin}

{DIVIDER_LIGHT}
{format_balance_line(new_balance, f"Nuevo saldo de {target}")}"""


def admin_set_message(username: str, is_admin: bool) -> str:
    """Admin status change message."""
    if is_admin:
        return f"""{EMOJI_SUCCESS} **Administrador asignado**

{EMOJI_ADMIN} @{username} ahora es administrador"""
    else:
        return f"""{EMOJI_SUCCESS} **Administrador removido**

{EMOJI_PROFILE} @{username} ya no es administrador"""


# ═══════════════════════════════════════════════════════════════════════════════
# RANKING MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

def ranking_message(
    users: list[tuple[int, str, int]],
    user_position: int | None,
    user_balance: int,
) -> str:
    """Ranking leaderboard message."""
    lines = [f"{EMOJI_RANKING} **Ranking de {settings.currency_name}**\n"]

    for i, (_, name, balance) in enumerate(users):
        medal = MEDALS[i] if i < 3 else f"**{i + 1}.**"
        lines.append(f"{medal} {name}")
        lines.append(f"    └─ {format_currency(balance)}")

    lines.append(f"\n{DIVIDER}")

    if user_position:
        lines.append(f"📍 **Tu posición:** #{user_position}")
        lines.append(f"{EMOJI_BALANCE} {format_currency(user_balance)}")
    else:
        lines.append(format_balance_line(user_balance))

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# HISTORY MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

def history_message(
    transactions: list[dict],
    current_balance: int,
) -> str:
    """Transaction history message."""
    if not transactions:
        return f"""{EMOJI_HISTORY} **Tu historial**

{EMOJI_INFO} No tienes transacciones aún.

{DIVIDER}
{format_balance_line(current_balance, "Saldo actual")}"""

    lines = [f"{EMOJI_HISTORY} **Tu historial**\n"]

    for i, tx in enumerate(transactions, 1):
        if tx["type"] == "sent":
            lines.append(f"**{i}.** {EMOJI_TRANSFER} -{format_currency(tx['amount'])}")
            lines.append(f"    └─ → {tx['other']} • {tx['time']}")
        elif tx["type"] == "received":
            lines.append(f"**{i}.** {EMOJI_GIFT} +{format_currency(tx['amount'])}")
            lines.append(f"    └─ ← {tx['other']} • {tx['time']}")
        elif tx["type"] == "admin_give":
            lines.append(f"**{i}.** {EMOJI_ADMIN} +{format_currency(tx['amount'])}")
            lines.append(f"    └─ Admin • {tx['time']}")
        elif tx["type"] == "admin_remove":
            lines.append(f"**{i}.** {EMOJI_WARNING} -{format_currency(tx['amount'])}")
            lines.append(f"    └─ Admin • {tx['time']}")
        else:
            lines.append(f"**{i}.** {EMOJI_INFO} {tx['amount']}")
            lines.append(f"    └─ {tx['time']}")

    lines.append(f"\n{DIVIDER}")
    lines.append(format_balance_line(current_balance, "Saldo actual"))

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

def profile_message(
    display_name: str,
    pronouns: str | None,
    role: str,
    experience: str,
    age: int | None,
    bio: str | None,
    balance: int,
    collar_status: str,
    subs_count: int,
    contracts_count: int,
    is_self: bool = False,
) -> str:
    """User profile message."""
    pronouns_display = f" ({pronouns})" if pronouns else ""
    age_display = f"\n🎂 {age} años" if age else ""
    bio_display = bio if bio else "Sin biografía"
    edit_hint = f"\n\n{EMOJI_INFO} /editarperfil para modificar" if is_self else ""

    return f"""{EMOJI_PROFILE} **Perfil de {display_name}**{pronouns_display}

{role} │ {experience}{age_display}

{DIVIDER_LIGHT}

📝 {bio_display}

{DIVIDER_LIGHT}

{EMOJI_BALANCE} **Saldo:** {format_currency(balance)}
{collar_status}
{EMOJI_SUB} **Sumis@s:** {subs_count}
{EMOJI_CONTRACT} **Contratos:** {contracts_count}{edit_hint}"""


# ═══════════════════════════════════════════════════════════════════════════════
# BDSM MESSAGES - COLLARS
# ═══════════════════════════════════════════════════════════════════════════════

def collar_request_sent(target: str, cost: int) -> str:
    """Collar request sent message."""
    return f"""{EMOJI_COLLAR} **Solicitud de collar enviada**

{EMOJI_PROFILE} Para: {target}
{EMOJI_BALANCE} Costo: {format_currency(cost)}

{EMOJI_LOADING} Esperando respuesta..."""


def collar_request_received(owner: str, request_id: int) -> str:
    """Collar request received message."""
    return f"""{EMOJI_COLLAR} **¡Solicitud de collar!**

{EMOJI_DOM} {owner} quiere ponerte su collar

{DIVIDER_LIGHT}

{EMOJI_SUCCESS} /aceptar_collar {request_id} — Aceptar
{EMOJI_ERROR} /rechazar_collar {request_id} — Rechazar

{EMOJI_LOADING} Tienes 5 minutos para responder"""


def collar_accepted(owner: str, sub: str, cost: int) -> str:
    """Collar accepted message."""
    return f"""{EMOJI_COLLAR} **¡Collar aceptado!**

{EMOJI_SUB} {sub} ahora lleva el collar de {EMOJI_DOM} {owner}

{DIVIDER_LIGHT}
{EMOJI_BALANCE} -{format_currency(cost)}"""


def collar_rejected(owner: str, sub: str) -> str:
    """Collar rejected message."""
    return f"""{EMOJI_ERROR} **Collar rechazado**

{EMOJI_SUB} {sub} ha rechazado el collar de {owner}"""


def collar_removed(owner: str, sub: str) -> str:
    """Collar removed message."""
    return f"""{EMOJI_COLLAR} **Collar removido**

{EMOJI_SUB} {sub} ya no lleva el collar de {EMOJI_DOM} {owner}"""


def collar_status_free() -> str:
    """No collar status message."""
    return f"""{EMOJI_COLLAR} **Estado de collar**

{EMOJI_PUBLIC} Estás libre, sin collar."""


def collar_status_owned(owner: str, since: str) -> str:
    """Has collar status message."""
    return f"""{EMOJI_COLLAR} **Tu collar**

{EMOJI_DOM} Llevas el collar de **{owner}**
{EMOJI_LOADING} Desde hace {since}"""


def collar_subs_list(owner: str, subs: list[tuple[str, str]]) -> str:
    """List of collared subs."""
    if not subs:
        return f"""{EMOJI_COLLAR} **Tus sumis@s**

{EMOJI_INFO} No tienes a nadie con tu collar."""

    lines = [f"{EMOJI_COLLAR} **Sumis@s de {owner}**\n"]
    for i, (name, since) in enumerate(subs, 1):
        lines.append(f"**{i}.** {EMOJI_SUB} {name}")
        lines.append(f"    └─ Desde hace {since}")

    lines.append(f"\n{DIVIDER_LIGHT}")
    lines.append(f"**Total:** {len(subs)} sumis@(s)")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# BDSM MESSAGES - PUNISHMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def punishment_given(punisher: str, target: str, punishment_type: str, reason: str | None, cost: int) -> str:
    """Punishment given message."""
    reason_display = f"\n📝 **Razón:** {reason}" if reason else ""
    return f"""{EMOJI_WHIP} **¡Castigo aplicado!**

{EMOJI_DOM} {punisher} ha castigado a {EMOJI_SUB} {target}

{DIVIDER_LIGHT}

🎭 **Tipo:** {punishment_type}{reason_display}
{EMOJI_BALANCE} **Costo:** -{format_currency(cost)}"""


def punishment_list(user: str, punishments: list[dict], as_dom: bool = True) -> str:
    """List of punishments given/received."""
    role = "dados" if as_dom else "recibidos"
    emoji = EMOJI_DOM if as_dom else EMOJI_SUB

    if not punishments:
        return f"""{EMOJI_WHIP} **Castigos {role}**

{EMOJI_INFO} No hay castigos registrados."""

    lines = [f"{EMOJI_WHIP} **Castigos {role} por {user}**\n"]

    for i, p in enumerate(punishments[:10], 1):
        target_or_from = p.get("target") or p.get("from", "???")
        lines.append(f"**{i}.** {emoji} {target_or_from}")
        if p.get("reason"):
            lines.append(f"    └─ {p['reason'][:30]}...")
        lines.append(f"    └─ {p.get('time', '')}")

    if len(punishments) > 10:
        lines.append(f"\n{EMOJI_INFO} ... y {len(punishments) - 10} más")

    lines.append(f"\n{DIVIDER_LIGHT}")
    lines.append(f"**Total:** {len(punishments)} castigo(s)")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# BDSM MESSAGES - DUNGEON
# ═══════════════════════════════════════════════════════════════════════════════

def dungeon_locked(jailer: str, prisoner: str, hours: int, reason: str | None, cost: int) -> str:
    """Dungeon lock message."""
    reason_display = f"\n📝 **Razón:** {reason}" if reason else ""
    return f"""{EMOJI_DUNGEON} **¡Al calabozo!**

{EMOJI_DOM} {jailer} ha encerrado a {EMOJI_SUB} {prisoner}

{DIVIDER_LIGHT}

{EMOJI_LOADING} **Duración:** {hours} horas{reason_display}
{EMOJI_BALANCE} **Costo:** -{format_currency(cost)}"""


def dungeon_released(prisoner: str) -> str:
    """Dungeon release message."""
    return f"""{EMOJI_DUNGEON} **¡Libertad!**

{EMOJI_SUCCESS} {prisoner} ha sido liberado del calabozo"""


def dungeon_status_free() -> str:
    """Not in dungeon message."""
    return f"""{EMOJI_DUNGEON} **Estado del calabozo**

{EMOJI_SUCCESS} Estás libre, no estás en el calabozo."""


def dungeon_status_locked(jailer: str, remaining: str, reason: str | None) -> str:
    """In dungeon status message."""
    reason_display = f"\n📝 **Razón:** {reason}" if reason else ""
    return f"""{EMOJI_DUNGEON} **Estás en el calabozo**

{EMOJI_DOM} Encerrado/a por: **{jailer}**
{EMOJI_LOADING} Tiempo restante: **{remaining}**{reason_display}"""


# ═══════════════════════════════════════════════════════════════════════════════
# BDSM MESSAGES - AUCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def auction_created(auction_id: int, item: str, starting_bid: int, duration_hours: int) -> str:
    """Auction created message."""
    return f"""{EMOJI_AUCTION} **Nueva subasta creada**

🏷️ **ID:** #{auction_id}
📦 **Artículo:** {item}
{EMOJI_BALANCE} **Puja inicial:** {format_currency(starting_bid)}
{EMOJI_LOADING} **Duración:** {duration_hours} horas

{DIVIDER_LIGHT}
{EMOJI_INFO} /pujar {auction_id} [cantidad] — Para pujar"""


def auction_bid(auction_id: int, bidder: str, amount: int) -> str:
    """Auction bid message."""
    return f"""{EMOJI_AUCTION} **¡Nueva puja!**

🏷️ **Subasta:** #{auction_id}
{EMOJI_PROFILE} **Pujador:** {bidder}
{EMOJI_BALANCE} **Cantidad:** {format_currency(amount)}"""


def auction_won(auction_id: int, winner: str, item: str, amount: int) -> str:
    """Auction won message."""
    return f"""{EMOJI_AUCTION} **¡Subasta finalizada!**

🏷️ **Subasta:** #{auction_id}
📦 **Artículo:** {item}

{DIVIDER_LIGHT}

{EMOJI_SUCCESS} **Ganador:** {winner}
{EMOJI_BALANCE} **Precio final:** {format_currency(amount)}"""


def auction_list(auctions: list[dict]) -> str:
    """List active auctions."""
    if not auctions:
        return f"""{EMOJI_AUCTION} **Subastas activas**

{EMOJI_INFO} No hay subastas activas en este momento."""

    lines = [f"{EMOJI_AUCTION} **Subastas activas**\n"]

    for a in auctions[:10]:
        lines.append(f"**#{a['id']}** — {a['item']}")
        lines.append(f"    └─ Puja actual: {format_currency(a['current_bid'])}")
        lines.append(f"    └─ Termina: {a['ends']}")

    if len(auctions) > 10:
        lines.append(f"\n{EMOJI_INFO} ... y {len(auctions) - 10} más")

    lines.append(f"\n{DIVIDER_LIGHT}")
    lines.append(f"{EMOJI_INFO} /pujar [id] [cantidad] — Para participar")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# BDSM MESSAGES - TRIBUTES
# ═══════════════════════════════════════════════════════════════════════════════

def tribute_paid(payer: str, recipient: str, amount: int, message: str | None) -> str:
    """Tribute paid message."""
    message_display = f"\n💌 \"{message}\"" if message else ""
    return f"""{EMOJI_TRIBUTE} **Tributo pagado**

{EMOJI_SUB} {payer} ha tributado a {EMOJI_DOM} {recipient}

{DIVIDER_LIGHT}

{EMOJI_BALANCE} **Cantidad:** {format_currency(amount)}{message_display}"""


def tribute_received(payer: str, amount: int, message: str | None) -> str:
    """Tribute received notification."""
    message_display = f"\n💌 \"{message}\"" if message else ""
    return f"""{EMOJI_TRIBUTE} **¡Has recibido un tributo!**

{EMOJI_SUB} {payer} te ha tributado
{EMOJI_BALANCE} **{format_currency(amount)}**{message_display}"""


# ═══════════════════════════════════════════════════════════════════════════════
# BDSM MESSAGES - CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

def contract_created(contract_id: int, dom: str, sub: str, terms: str, duration_days: int) -> str:
    """Contract created message."""
    return f"""{EMOJI_CONTRACT} **Contrato creado**

📋 **ID:** #{contract_id}
{EMOJI_DOM} **Dominante:** {dom}
{EMOJI_SUB} **Sumis@:** {sub}

{DIVIDER_LIGHT}

📝 **Términos:**
{terms}

{EMOJI_LOADING} **Duración:** {duration_days} días"""


def contract_signed(contract_id: int, dom: str, sub: str) -> str:
    """Contract signed message."""
    return f"""{EMOJI_SUCCESS} **¡Contrato firmado!**

📋 **Contrato #{contract_id}**

{EMOJI_DOM} {dom} y {EMOJI_SUB} {sub}
han firmado el contrato."""


def contract_broken(contract_id: int, breaker: str, penalty: int) -> str:
    """Contract broken message."""
    return f"""{EMOJI_ERROR} **Contrato roto**

📋 **Contrato #{contract_id}**

{EMOJI_WARNING} {breaker} ha roto el contrato
{EMOJI_BALANCE} **Penalización:** -{format_currency(penalty)}"""


def contract_list(contracts: list[dict], user: str) -> str:
    """List user contracts."""
    if not contracts:
        return f"""{EMOJI_CONTRACT} **Tus contratos**

{EMOJI_INFO} No tienes contratos activos."""

    lines = [f"{EMOJI_CONTRACT} **Contratos de {user}**\n"]

    for c in contracts[:5]:
        role = EMOJI_DOM if c.get("is_dom") else EMOJI_SUB
        partner = c.get("partner", "???")
        lines.append(f"**#{c['id']}** — {role} con {partner}")
        lines.append(f"    └─ Expira: {c.get('expires', 'N/A')}")

    if len(contracts) > 5:
        lines.append(f"\n{EMOJI_INFO} ... y {len(contracts) - 5} más")

    lines.append(f"\n{DIVIDER_LIGHT}")
    lines.append(f"**Total:** {len(contracts)} contrato(s) activo(s)")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# HELP MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

def help_main() -> str:
    """Main help message."""
    bdsm_section = f"""
{EMOJI_COLLAR} **Comandos BDSM:**
• /collar — Sistema de collares
• /castigo — Castigos y disciplina
• /calabozo — Encerrar usuarios
• /subasta — Subastas
• /tributo — Pagar tributos
• /contrato — Contratos D/s
""" if settings.enable_bdsm_commands else ""

    return f"""{EMOJI_BOT} **{settings.bot_name} — Ayuda**

{DIVIDER}

{EMOJI_BALANCE} **Comandos básicos:**
• /start — Registrarse
• /ver — Ver tu saldo
• /dar @user cantidad — Enviar {settings.currency_name}
• /ranking — Top usuarios
• /historial — Tus movimientos

{EMOJI_PROFILE} **Perfil:**
• /perfil — Ver tu perfil
• /editarperfil — Modificar perfil
• /configuracion — Ajustes de privacidad
{bdsm_section}
{EMOJI_ADMIN} **Admin:**
• /dar_admin @user cantidad — Dar {settings.currency_name}
• /quitar @user cantidad — Quitar {settings.currency_name}
• /consultar @user — Ver saldo de otro
• /setadmin / /removeadmin — Gestionar admins

{DIVIDER}
{EMOJI_INFO} Usa /help [comando] para más detalles"""


# ═══════════════════════════════════════════════════════════════════════════════
# ERROR MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

ERROR_NOT_REGISTERED = f"{EMOJI_ERROR} No estás registrado. Usa /start primero."
ERROR_USER_NOT_FOUND = f"{EMOJI_ERROR} Usuario no encontrado."
ERROR_INVALID_AMOUNT = f"{EMOJI_ERROR} Cantidad inválida. Debe ser un número positivo."
ERROR_INSUFFICIENT_BALANCE = f"{EMOJI_ERROR} Saldo insuficiente."
ERROR_SELF_TRANSFER = f"{EMOJI_ERROR} No puedes enviarte a ti mismo."
ERROR_NOT_ADMIN = f"{EMOJI_ERROR} No tienes permisos de administrador."
ERROR_COOLDOWN = f"{EMOJI_LOADING} Espera {{seconds}} segundos antes de volver a transferir."
ERROR_MIN_AMOUNT = f"{EMOJI_ERROR} La cantidad mínima es {settings.min_transfer_amount} {settings.currency_name}."
ERROR_MAX_AMOUNT = f"{EMOJI_ERROR} La cantidad máxima es {format_balance(settings.max_transfer_amount)} {settings.currency_name}."
ERROR_GENERIC = f"{EMOJI_ERROR} Ocurrió un error inesperado. Intenta de nuevo."
ERROR_PERMISSION_DENIED = f"{EMOJI_ERROR} No tienes permiso para hacer esto."
ERROR_INVALID_USER = f"{EMOJI_ERROR} Usuario inválido o no especificado."
ERROR_FEATURE_DISABLED = f"{EMOJI_ERROR} Esta función está deshabilitada."

# Warning messages
WARNING_DEBT = f"{EMOJI_WARNING} Esto te dejará en deuda. ¿Estás seguro?"
WARNING_IRREVERSIBLE = f"{EMOJI_WARNING} Esta acción es irreversible."

# Info messages
INFO_NO_CHANGES = f"{EMOJI_INFO} No hay cambios que guardar."
INFO_LOADING = f"{EMOJI_LOADING} Cargando..."
INFO_PROCESSING = f"{EMOJI_LOADING} Procesando..."


# ═══════════════════════════════════════════════════════════════════════════════
# USAGE MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

USAGE_DAR = f"""{EMOJI_INFO} **Cómo usar /dar**

**Formato:** /dar @usuario cantidad

**Ejemplo:** /dar @maria 100

{DIVIDER_LIGHT}
Envía {settings.currency_name} a otro usuario."""

USAGE_DAR_ADMIN = f"""{EMOJI_INFO} **Cómo usar /dar_admin**

**Formato:** /dar_admin @usuario cantidad

**Ejemplo:** /dar_admin @maria 500

{DIVIDER_LIGHT}
{EMOJI_ADMIN} Solo administradores."""

USAGE_QUITAR = f"""{EMOJI_INFO} **Cómo usar /quitar**

**Formato:** /quitar @usuario cantidad

**Ejemplo:** /quitar @maria 100

{DIVIDER_LIGHT}
{EMOJI_ADMIN} Solo administradores."""

USAGE_CONSULTAR = f"""{EMOJI_INFO} **Cómo usar /consultar**

**Formato:** /consultar @usuario

**Ejemplo:** /consultar @maria

{DIVIDER_LIGHT}
{EMOJI_ADMIN} Solo administradores."""
