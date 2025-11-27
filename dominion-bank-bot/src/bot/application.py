"""
The Phantom Bot - Application Setup
"""
import html
import logging
import traceback

from telegram import BotCommand, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.config import settings
from src.database.connection import close_database, init_database
from src.services.cache import close_cache, init_cache
from src.handlers.core import (
    dar_command,
    help_command,
    start_command,
    ver_command,
)
from src.handlers.admin import (
    consultar_command,
    dar_admin_command,
    quitar_command,
    remove_admin_command,
    set_admin_command,
)
from src.handlers.info import (
    historial_command,
    ranking_command,
    stats_command,
)
from src.handlers.group import (
    on_bot_added_to_group,
    on_chat_member_update,
    syncadmins_command,
)
from src.handlers.profiles import (
    configuracion_command,
    editarperfil_command,
    perfil_command,
)
from src.handlers.excel_import import (
    exportar_command,
    handle_excel_document,
    importar_command,
)
from src.handlers.testing import (
    cleandb_command,
    run_tests_command,
    test_db_command,
)
from src.handlers.health import (
    health_command,
    ping_command,
)
from src.handlers.conversations import get_profile_edit_conversation
from src.handlers.help_interactive import (
    get_help_callback_handler,
    interactive_help_command,
)
from src.handlers.bdsm import (
    # Collars
    aceptar_collar_command,
    amo_command,
    collar_command,
    exhibir_command,
    liberar_command,
    rechazar_collar_command,
    suplicar_libertad_command,
    # Punishments
    azotar_command,
    castigar_command,
    castigos_dados_command,
    mis_castigos_command,
    # Dungeon
    calabozo_command,
    liberar_calabozo_command,
    mi_calabozo_command,
    presos_command,
    suplicar_libertad_calabozo_command,
    # Auctions
    cancelar_subasta_command,
    mis_subastas_command,
    pujar_command,
    subasta_command,
    subastas_command,
    ver_subasta_command,
    # Contracts
    contrato_command,
    firmar_contrato_command,
    mis_contratos_command,
    rechazar_contrato_command,
    romper_contrato_command,
    ver_contrato_command,
    # Tribute
    adorar_command,
    altar_command,
    devotos_command,
    mi_altar_command,
    tributo_command,
)

logger = logging.getLogger(__name__)


def setup_handlers(application: Application) -> None:
    """Register all command handlers."""

    # Core commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ver", ver_command))
    application.add_handler(CommandHandler("saldo", ver_command))  # Alias
    application.add_handler(CommandHandler("dar", dar_command))
    application.add_handler(CommandHandler("enviar", dar_command))  # Alias
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ayuda", interactive_help_command))  # Interactive version
    application.add_handler(get_help_callback_handler())  # Help menu navigation

    # Info commands
    application.add_handler(CommandHandler("ranking", ranking_command))
    application.add_handler(CommandHandler("top", ranking_command))  # Alias
    application.add_handler(CommandHandler("historial", historial_command))
    application.add_handler(CommandHandler("historia", historial_command))  # Alias
    application.add_handler(CommandHandler("stats", stats_command))

    # Admin commands
    application.add_handler(CommandHandler("dar_admin", dar_admin_command))
    application.add_handler(CommandHandler("daradmin", dar_admin_command))  # Alias
    application.add_handler(CommandHandler("quitar", quitar_command))
    application.add_handler(CommandHandler("consultar", consultar_command))
    application.add_handler(CommandHandler("setadmin", set_admin_command))
    application.add_handler(CommandHandler("removeadmin", remove_admin_command))
    application.add_handler(CommandHandler("syncadmins", syncadmins_command))

    # Profile commands
    application.add_handler(CommandHandler("perfil", perfil_command))
    application.add_handler(CommandHandler("editarperfil", editarperfil_command))
    application.add_handler(CommandHandler("configuracion", configuracion_command))
    application.add_handler(CommandHandler("config", configuracion_command))  # Alias

    # ConversationHandlers (multi-step flows)
    application.add_handler(get_profile_edit_conversation())

    # Excel import/export commands (admin only)
    application.add_handler(CommandHandler("importar", importar_command))
    application.add_handler(CommandHandler("exportar", exportar_command))
    application.add_handler(
        MessageHandler(filters.Document.ALL, handle_excel_document)
    )

    # Testing commands (admin only)
    application.add_handler(CommandHandler("runtest", run_tests_command))
    application.add_handler(CommandHandler("runtests", run_tests_command))  # Alias
    application.add_handler(CommandHandler("testdb", test_db_command))
    application.add_handler(CommandHandler("cleandb", cleandb_command))
    # Health check commands
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("ping", ping_command))

    # BDSM commands (only if enabled)
    if settings.enable_bdsm_commands:
        # Collar commands
        application.add_handler(CommandHandler("collar", collar_command))
        application.add_handler(CommandHandler("liberar", liberar_command))
        application.add_handler(CommandHandler("exhibir", exhibir_command))
        application.add_handler(CommandHandler("miscollares", exhibir_command))  # Alias
        application.add_handler(CommandHandler("amo", amo_command))
        application.add_handler(CommandHandler("ama", amo_command))  # Alias
        application.add_handler(CommandHandler("aceptar_collar", aceptar_collar_command))
        application.add_handler(CommandHandler("rechazar_collar", rechazar_collar_command))
        application.add_handler(CommandHandler("suplicar_libertad", suplicar_libertad_command))

        # Punishment commands
        application.add_handler(CommandHandler("azotar", azotar_command))
        application.add_handler(CommandHandler("castigar", castigar_command))
        application.add_handler(CommandHandler("mis_castigos", mis_castigos_command))
        application.add_handler(CommandHandler("miscastigos", mis_castigos_command))  # Alias
        application.add_handler(CommandHandler("castigos_dados", castigos_dados_command))

        # Dungeon commands
        application.add_handler(CommandHandler("calabozo", calabozo_command))
        application.add_handler(CommandHandler("encerrar", calabozo_command))  # Alias
        application.add_handler(CommandHandler("liberar_calabozo", liberar_calabozo_command))
        application.add_handler(CommandHandler("presos", presos_command))
        application.add_handler(CommandHandler("mi_calabozo", mi_calabozo_command))
        application.add_handler(CommandHandler("micalbozo", mi_calabozo_command))  # Alias (typo-friendly)
        application.add_handler(CommandHandler("suplicar_libertad_calabozo", suplicar_libertad_calabozo_command))

        # Auction commands
        application.add_handler(CommandHandler("subasta", subasta_command))
        application.add_handler(CommandHandler("pujar", pujar_command))
        application.add_handler(CommandHandler("subastas", subastas_command))
        application.add_handler(CommandHandler("ver_subasta", ver_subasta_command))
        application.add_handler(CommandHandler("cancelar_subasta", cancelar_subasta_command))
        application.add_handler(CommandHandler("mis_subastas", mis_subastas_command))

        # Contract commands
        application.add_handler(CommandHandler("contrato", contrato_command))
        application.add_handler(CommandHandler("firmar_contrato", firmar_contrato_command))
        application.add_handler(CommandHandler("rechazar_contrato", rechazar_contrato_command))
        application.add_handler(CommandHandler("romper_contrato", romper_contrato_command))
        application.add_handler(CommandHandler("mis_contratos", mis_contratos_command))
        application.add_handler(CommandHandler("miscontratos", mis_contratos_command))  # Alias
        application.add_handler(CommandHandler("ver_contrato", ver_contrato_command))

        # Tribute/worship commands
        application.add_handler(CommandHandler("tributo", tributo_command))
        application.add_handler(CommandHandler("adorar", adorar_command))
        application.add_handler(CommandHandler("altar", altar_command))
        application.add_handler(CommandHandler("mi_altar", mi_altar_command))
        application.add_handler(CommandHandler("mialtar", mi_altar_command))  # Alias
        application.add_handler(CommandHandler("devotos", devotos_command))

        logger.info("BDSM commands registered")

    # Group handlers - auto-sync admins
    application.add_handler(
        ChatMemberHandler(on_bot_added_to_group, ChatMemberHandler.MY_CHAT_MEMBER)
    )
    application.add_handler(
        ChatMemberHandler(on_chat_member_update, ChatMemberHandler.CHAT_MEMBER)
    )

    logger.info("All handlers registered")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors occurring in the dispatcher."""
    logger.error("Exception while handling an update:", exc_info=context.error)

    # Format the traceback
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the error message
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    error_message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(str(update_str)[:1000])}</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string[:3000])}</pre>"
    )

    # Log full error for debugging
    logger.error(f"Update: {update_str}")
    logger.error(f"Error: {tb_string}")

    # Notify super admins if configured
    for admin_id in settings.super_admin_ids:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=error_message[:4000],  # Telegram message limit
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

    # Send generic error message to user if possible
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Ocurrió un error inesperado. El equipo técnico ha sido notificado."
            )
        except Exception:
            pass  # Can't notify user, already logged


async def post_init(application: Application) -> None:
    """Initialize database and cache after application startup."""
    await init_database()
    logger.info("Database initialized")
    await init_cache()
    logger.info("Cache initialized")

    # Register bot commands with Telegram
    commands = [
        BotCommand("start", "Registrarse en el bot"),
        BotCommand("ver", "Ver tu saldo"),
        BotCommand("dar", "Enviar monedas a otro usuario"),
        BotCommand("ranking", "Ver los top usuarios"),
        BotCommand("historial", "Ver tu historial de transacciones"),
        BotCommand("perfil", "Ver tu perfil o el de otro usuario"),
        BotCommand("help", "Ver ayuda"),
    ]

    # Admin commands (not shown to regular users but available)
    admin_commands = commands + [
        BotCommand("dar_admin", "Dar monedas (admin)"),
        BotCommand("quitar", "Quitar monedas (admin)"),
        BotCommand("consultar", "Ver saldo de usuario (admin)"),
        BotCommand("runtest", "Ejecutar tests (admin)"),
        BotCommand("testdb", "Test de base de datos (admin)"),
        BotCommand("cleandb", "Limpiar base de datos (admin)"),
        BotCommand("syncadmins", "Sincronizar admins del grupo"),
    ]

    # BDSM commands if enabled
    if settings.enable_bdsm_commands:
        bdsm_commands = [
            BotCommand("collar", "Poner collar a alguien"),
            BotCommand("liberar", "Liberar a alguien"),
            BotCommand("tributo", "Pagar tributo"),
            BotCommand("adorar", "Adorar a alguien"),
            BotCommand("mis_contratos", "Ver tus contratos"),
        ]
        commands.extend(bdsm_commands)
        admin_commands.extend(bdsm_commands)

    try:
        await application.bot.set_my_commands(commands)
        logger.info("Bot commands registered with Telegram")
    except Exception as e:
        logger.error(f"Failed to register bot commands: {e}")


async def post_shutdown(application: Application) -> None:
    """Cleanup on shutdown."""
    await close_cache()
    logger.info("Cache stopped")
    await close_database()
    logger.info("Database connection closed")


def create_application() -> Application:
    """Create and configure the bot application."""

    # Build application
    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Setup handlers
    setup_handlers(application)

    # Register global error handler
    application.add_error_handler(error_handler)

    logger.info(f"Bot application created: {settings.bot_name}")
    return application
