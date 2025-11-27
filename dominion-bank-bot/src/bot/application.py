"""
The Phantom Bot - Application Setup
"""
import logging
from telegram.ext import (
    Application,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.config import settings
from src.database.connection import init_database, close_database
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
    application.add_handler(CommandHandler("ayuda", help_command))  # Alias

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

    # Excel import/export commands (admin only)
    application.add_handler(CommandHandler("importar", importar_command))
    application.add_handler(CommandHandler("exportar", exportar_command))
    application.add_handler(
        MessageHandler(filters.Document.ALL, handle_excel_document)
    )

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


async def post_init(application: Application) -> None:
    """Initialize database after application startup."""
    await init_database()
    logger.info("Database initialized")


async def post_shutdown(application: Application) -> None:
    """Cleanup on shutdown."""
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

    logger.info(f"Bot application created: {settings.bot_name}")
    return application
