"""
Interactive Help System
Provides paginated help with inline keyboard navigation.
"""
import logging
from enum import Enum
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.repositories import UserRepository

logger = logging.getLogger(__name__)


class HelpCategory(str, Enum):
    """Help categories for navigation."""
    MAIN = "help_main"
    BASIC = "help_basic"
    PROFILE = "help_profile"
    COLLARS = "help_collars"
    PUNISHMENTS = "help_punishments"
    DUNGEON = "help_dungeon"
    AUCTIONS = "help_auctions"
    CONTRACTS = "help_contracts"
    TRIBUTES = "help_tributes"
    ADMIN = "help_admin"


# Help content for each category
HELP_CONTENT = {
    HelpCategory.BASIC: {
        "title": "Comandos Basicos",
        "icon": "money_bag",
        "content": """/start - Registrarse en el bot
/ver - Ver tu saldo actual
/dar @user cantidad - Enviar {currency}
/ranking - Top 10 usuarios
/historial - Tus ultimas transacciones
/stats - Estadisticas generales

Aliases:
- /saldo = /ver
- /enviar = /dar
- /top = /ranking
- /historia = /historial"""
    },
    HelpCategory.PROFILE: {
        "title": "Perfil",
        "icon": "bust_in_silhouette",
        "content": """/perfil - Ver tu perfil
/perfil @user - Ver perfil de otro usuario
/editarperfil - Modificar tu perfil (wizard)
/editarperfil_wizard - Editor interactivo de perfil
/configuracion - Ajustes de privacidad

El perfil muestra tu rol, experiencia,
biografia, y otros datos personales."""
    },
    HelpCategory.COLLARS: {
        "title": "Sistema de Collares",
        "icon": "link",
        "content": """/collar @user - Poner collar (costo: 300)
/liberar @user - Liberar a tu sumiso
/exhibir - Ver tus collares
/miscollares - (alias de /exhibir)
/amo - Ver quien es tu Amo/Ama
/ama - (alias de /amo)
/aceptar_collar - Aceptar collar pendiente
/rechazar_collar - Rechazar collar pendiente
/suplicar_libertad - Pedir libertad a tu Amo

El collar representa una relacion D/s.
Solo puedes tener un Amo/Ama a la vez."""
    },
    HelpCategory.PUNISHMENTS: {
        "title": "Sistema de Castigos",
        "icon": "high_voltage",
        "content": """/azotar @user [razon] - Azotar (costo: 50)
/castigar @user tipo razon - Aplicar castigo
/mis_castigos - Ver castigos recibidos
/miscastigos - (alias)
/castigos_dados - Ver castigos que has dado

Tipos de castigo disponibles:
- Azote (basico)
- Restriccion
- Humillacion
- Tarea
- Silencio"""
    },
    HelpCategory.DUNGEON: {
        "title": "El Calabozo",
        "icon": "european_castle",
        "content": """/calabozo @user [horas] - Encerrar (costo: 200)
/encerrar - (alias de /calabozo)
/liberar_calabozo @user - Liberar preso
/mi_calabozo - Ver tu estado de encierro
/micalbozo - (alias)
/presos - Ver todos los presos
/suplicar_libertad_calabozo - Pedir salir

Los presos no pueden usar ciertos comandos.
Duracion maxima: 168 horas (1 semana)."""
    },
    HelpCategory.AUCTIONS: {
        "title": "Sistema de Subastas",
        "icon": "hammer",
        "content": """/subasta @user precio_inicial - Iniciar subasta
/pujar subasta_id cantidad - Hacer una puja
/subastas - Ver subastas activas
/ver_subasta id - Ver detalles de subasta
/mis_subastas - Ver tus subastas
/cancelar_subasta id - Cancelar tu subasta

Las subastas duran 24 horas por defecto.
El ganador recibe un collar temporal."""
    },
    HelpCategory.CONTRACTS: {
        "title": "Sistema de Contratos",
        "icon": "scroll",
        "content": """/contrato @user terminos - Proponer contrato
/firmar_contrato id - Firmar un contrato
/rechazar_contrato id - Rechazar propuesta
/romper_contrato id - Romper contrato (costo: 500)
/mis_contratos - Ver tus contratos
/miscontratos - (alias)
/ver_contrato id - Ver detalles

Los contratos son acuerdos formales D/s.
Romper un contrato tiene penalizacion."""
    },
    HelpCategory.TRIBUTES: {
        "title": "Sistema de Tributos",
        "icon": "pray",
        "content": """/tributo @user cantidad - Dar tributo
/adorar @user - Adorar (gratis)
/altar @user - Ver altar de alguien
/mi_altar - Ver tu propio altar
/mialtar - (alias)
/devotos - Ver tus devotos

Los tributos se acumulan en el altar.
Adorar aumenta el nivel de devocion."""
    },
    HelpCategory.ADMIN: {
        "title": "Administracion",
        "icon": "crown",
        "content": """/dar_admin @user cantidad - Dar {currency}
/daradmin - (alias)
/quitar @user cantidad - Quitar {currency}
/consultar @user - Ver saldo de usuario
/setadmin @user - Hacer admin
/removeadmin @user - Quitar admin
/syncadmins - Sincronizar admins del grupo

/importar - Importar datos (Excel)
/exportar - Exportar datos (Excel)
/cleandb - Limpiar base de datos

Testing:
/runtest - Ejecutar tests automaticos
/testdb - Test rapido de conexion
/health - Estado del bot
/ping - Verificar respuesta"""
    },
}


def get_main_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Create main help menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                "Basicos",
                callback_data=HelpCategory.BASIC
            ),
            InlineKeyboardButton(
                "Perfil",
                callback_data=HelpCategory.PROFILE
            ),
        ],
    ]

    # BDSM commands if enabled
    if settings.enable_bdsm_commands:
        keyboard.extend([
            [
                InlineKeyboardButton(
                    "Collares",
                    callback_data=HelpCategory.COLLARS
                ),
                InlineKeyboardButton(
                    "Castigos",
                    callback_data=HelpCategory.PUNISHMENTS
                ),
            ],
            [
                InlineKeyboardButton(
                    "Calabozo",
                    callback_data=HelpCategory.DUNGEON
                ),
                InlineKeyboardButton(
                    "Subastas",
                    callback_data=HelpCategory.AUCTIONS
                ),
            ],
            [
                InlineKeyboardButton(
                    "Contratos",
                    callback_data=HelpCategory.CONTRACTS
                ),
                InlineKeyboardButton(
                    "Tributos",
                    callback_data=HelpCategory.TRIBUTES
                ),
            ],
        ])

    # Admin section only for admins
    if is_admin:
        keyboard.append([
            InlineKeyboardButton(
                "Admin",
                callback_data=HelpCategory.ADMIN
            ),
        ])

    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Create back button keyboard."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("< Volver al menu", callback_data=HelpCategory.MAIN)
    ]])


def format_help_content(category: HelpCategory) -> str:
    """Format help content for display."""
    if category not in HELP_CONTENT:
        return "Categoria no encontrada."

    content_data = HELP_CONTENT[category]
    title = content_data["title"]
    content = content_data["content"]

    # Replace placeholders
    content = content.format(currency=settings.currency_name)

    return f"**{title}**\n\n{content}"


def get_main_help_text(is_admin: bool = False) -> str:
    """Get main help menu text."""
    admin_note = " (Admin)" if is_admin else ""
    return (
        f"**{settings.bot_name} - Ayuda{admin_note}**\n\n"
        "Selecciona una categoria para ver los comandos disponibles:\n\n"
        f"Moneda: {settings.currency_name} ({settings.currency_symbol})\n"
        f"Saldo inicial: {settings.default_balance} {settings.currency_symbol}"
    )


async def interactive_help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /ayuda command with interactive menu."""
    if not update.message or not update.effective_user:
        return

    # Check if user is admin
    is_admin = False
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if user:
            is_admin = user.is_admin or settings.is_super_admin(update.effective_user.id)

    await update.message.reply_text(
        get_main_help_text(is_admin),
        reply_markup=get_main_keyboard(is_admin),
    )


async def handle_help_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle help category selection callbacks."""
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    category = query.data

    # Check admin status for proper menu
    is_admin = False
    if update.effective_user:
        async with get_session() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(update.effective_user.id)
            if user:
                is_admin = user.is_admin or settings.is_super_admin(update.effective_user.id)

    if category == HelpCategory.MAIN:
        await query.edit_message_text(
            get_main_help_text(is_admin),
            reply_markup=get_main_keyboard(is_admin),
        )
    elif category in [c.value for c in HelpCategory if c != HelpCategory.MAIN]:
        # Hide admin section from non-admins
        if category == HelpCategory.ADMIN and not is_admin:
            await query.answer("Solo administradores.", show_alert=True)
            return

        try:
            cat_enum = HelpCategory(category)
            await query.edit_message_text(
                format_help_content(cat_enum),
                reply_markup=get_back_keyboard(),
            )
        except ValueError:
            await query.answer("Categoria no valida.", show_alert=True)


def get_help_callback_handler() -> CallbackQueryHandler:
    """Get the callback handler for help navigation."""
    return CallbackQueryHandler(
        handle_help_callback,
        pattern=r"^help_"
    )
