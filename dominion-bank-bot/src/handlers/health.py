"""
The Phantom Bot - Health Check Handler
System health and diagnostics endpoints.
"""
import logging
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.repositories import UserRepository
from src.services.cache import get_cache

logger = logging.getLogger(__name__)


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /health command - show system health status.

    Only available to super admins.
    """
    if not update.message or not update.effective_user:
        return

    # Check if super admin
    if not settings.is_super_admin(update.effective_user.id):
        await update.message.reply_text("❌ Este comando es solo para super admins.")
        return

    health_status = []
    health_status.append("🏥 **Estado del Sistema**\n")

    # Bot info
    health_status.append(f"🤖 Bot: {settings.bot_name}")
    health_status.append(f"🌍 Entorno: {settings.environment}")
    health_status.append(f"⏰ Hora: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")

    # Database check
    db_status = "✅"
    db_details = ""
    try:
        async with get_session() as session:
            user_repo = UserRepository(session)
            user_count = await user_repo.count_active_users()
            db_details = f" ({user_count} usuarios activos)"
    except Exception as e:
        db_status = "❌"
        db_details = f" Error: {str(e)[:50]}"
        logger.error(f"Health check - Database error: {e}")

    health_status.append(f"\n📊 **Componentes:**")
    health_status.append(f"{db_status} Base de datos{db_details}")

    # Cache check
    cache = get_cache()
    cache_status = "✅" if cache else "❌"
    cache_size = cache.size if cache else 0
    health_status.append(f"{cache_status} Cache ({cache_size} entradas)")

    # Configuration summary
    health_status.append(f"\n⚙️ **Configuración:**")
    health_status.append(f"• Moneda: {settings.currency_name} {settings.currency_emoji}")
    health_status.append(f"• Transferencias: {'✅' if settings.enable_transfers else '❌'}")
    health_status.append(f"• BDSM Commands: {'✅' if settings.enable_bdsm_commands else '❌'}")
    health_status.append(f"• Excel Import: {'✅' if settings.enable_excel_import else '❌'}")
    health_status.append(f"• Cooldown: {settings.transfer_cooldown}s")
    health_status.append(f"• Max Transfer: {settings.max_transfer_amount:,}")

    # Overall status
    all_ok = db_status == "✅" and cache_status == "✅"
    overall = "✅ Sistema funcionando correctamente" if all_ok else "⚠️ Sistema con problemas"
    health_status.append(f"\n{overall}")

    await update.message.reply_text("\n".join(health_status))


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /ping command - simple availability check.

    Available to all users.
    """
    if not update.message:
        return

    await update.message.reply_text("🏓 Pong!")
