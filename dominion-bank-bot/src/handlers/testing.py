"""
The Phantom Bot - Testing Command Handler
Allows admins to run automated tests from the chat
"""
import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

from telegram import Update, ChatMember
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.repositories import AdminRepository, UserRepository

# Database path for cleaning
DATABASE_PATH = Path(__file__).parent.parent.parent / "data" / "phantom.db"


async def is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if the user is an admin (super admin, global admin, or group admin)."""
    if not update.effective_user:
        return False

    user_id = update.effective_user.id

    # Check super admin first
    if settings.is_super_admin(user_id):
        return True

    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(user_id)

        if user:
            # Check global is_admin flag
            if user.is_admin:
                return True

            # Check if admin in current group (from bot database)
            if update.effective_chat and update.effective_chat.type in ("group", "supergroup"):
                admin_repo = AdminRepository(session)
                if await admin_repo.is_admin(user.id, update.effective_chat.id):
                    return True

    # Also check Telegram admin status directly
    if update.effective_chat and update.effective_chat.type in ("group", "supergroup"):
        try:
            member = await context.bot.get_chat_member(
                update.effective_chat.id, user_id
            )
            if member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
                return True
        except Exception:
            pass

    return False

logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


async def run_tests_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /runtest command - run automated tests and report results."""
    if not update.message or not update.effective_user:
        return

    # Check if user is admin (super admin, global admin, or group admin)
    if not await is_user_admin(update, context):
        await update.message.reply_text("❌ Solo los administradores pueden ejecutar tests.")
        return

    # Send initial message
    status_msg = await update.message.reply_text(
        "🧪 Ejecutando tests...\n\n"
        "⏳ Esto puede tomar unos segundos..."
    )

    try:
        # Run pytest in subprocess
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(PROJECT_ROOT / "tests"),
                    "-v",
                    "--tb=short",
                    "-q",
                ],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(PROJECT_ROOT),
            )
        )

        # Parse output
        output = result.stdout + result.stderr
        return_code = result.returncode

        # Extract summary from pytest output
        lines = output.split('\n')

        # Find test results
        passed = 0
        failed = 0
        errors = 0
        failed_tests = []

        for line in lines:
            if 'passed' in line.lower() and ('failed' in line.lower() or 'error' in line.lower() or line.strip().startswith('=')):
                # This is likely the summary line
                import re
                passed_match = re.search(r'(\d+)\s+passed', line)
                failed_match = re.search(r'(\d+)\s+failed', line)
                error_match = re.search(r'(\d+)\s+error', line)

                if passed_match:
                    passed = int(passed_match.group(1))
                if failed_match:
                    failed = int(failed_match.group(1))
                if error_match:
                    errors = int(error_match.group(1))
            elif 'PASSED' in line:
                passed += 1
            elif 'FAILED' in line:
                failed += 1
                # Extract test name
                test_name = line.split('::')[-1].split(' ')[0] if '::' in line else line
                failed_tests.append(test_name[:50])
            elif 'ERROR' in line and '::' in line:
                errors += 1

        # Build result message
        total = passed + failed + errors

        if return_code == 0:
            status_emoji = "✅"
            status_text = "TODOS LOS TESTS PASARON"
        else:
            status_emoji = "❌"
            status_text = "ALGUNOS TESTS FALLARON"

        result_msg = f"""🧪 **Resultados de Tests**

{status_emoji} {status_text}

📊 **Resumen:**
• Total: {total} tests
• ✅ Pasados: {passed}
• ❌ Fallidos: {failed}
• ⚠️ Errores: {errors}
"""

        if failed_tests:
            result_msg += "\n🔴 **Tests fallidos:**\n"
            for test in failed_tests[:5]:  # Show max 5
                result_msg += f"• {test}\n"
            if len(failed_tests) > 5:
                result_msg += f"... y {len(failed_tests) - 5} más\n"

        # Add timing info if available
        for line in lines:
            if 'seconds' in line and ('passed' in line or 'failed' in line):
                import re
                time_match = re.search(r'in\s+([\d.]+)s', line)
                if time_match:
                    result_msg += f"\n⏱️ Tiempo: {time_match.group(1)}s"
                break

        await status_msg.edit_text(result_msg)

        user_name = update.effective_user.first_name or update.effective_user.username or "Admin"
        logger.info(f"Tests executed by {user_name}: {passed} passed, {failed} failed")

    except subprocess.TimeoutExpired:
        await status_msg.edit_text(
            "❌ **Tests Timeout**\n\n"
            "Los tests tardaron demasiado (>120s).\n"
            "Intenta de nuevo más tarde."
        )
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        await status_msg.edit_text(
            f"❌ **Error ejecutando tests**\n\n"
            f"Error: {str(e)[:100]}"
        )


async def test_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /testdb command - quick database connectivity test."""
    if not update.message or not update.effective_user:
        return

    # Check if user is admin (super admin, global admin, or group admin)
    if not await is_user_admin(update, context):
        await update.message.reply_text("❌ Solo los administradores pueden ejecutar tests.")
        return

    results = []

    try:
        # Test 1: Database connection
        async with get_session() as session:
            user_repo = UserRepository(session)

            # Count users
            users = await user_repo.get_ranking(limit=1)
            results.append("✅ Conexión a base de datos")

            # Count total users
            all_users = await user_repo.get_all()
            results.append(f"✅ Usuarios registrados: {len(all_users)}")

        # Test 2: Check tables exist
        from src.database.models import (
            User, Transaction, Collar, Punishment,
            Dungeon, Auction, Contract, Profile
        )
        results.append("✅ Modelos cargados correctamente")

        # Test 3: Settings
        results.append(f"✅ Bot: {settings.bot_name}")
        results.append(f"✅ Moneda: {settings.currency_name}")
        results.append(f"✅ BDSM habilitado: {'Sí' if settings.enable_bdsm_commands else 'No'}")

        status = "✅ SISTEMA OK"

    except Exception as e:
        results.append(f"❌ Error: {str(e)[:50]}")
        status = "❌ ERROR EN SISTEMA"

    result_msg = f"""🔧 **Test de Sistema**

{status}

📋 **Resultados:**
{chr(10).join(results)}
"""

    await update.message.reply_text(result_msg)


async def cleandb_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cleandb command - clean database for fresh test runs."""
    if not update.message or not update.effective_user:
        return

    # Only super admins can clean the database
    if not settings.is_super_admin(update.effective_user.id):
        await update.message.reply_text("❌ Solo super administradores pueden limpiar la base de datos.")
        return

    try:
        # Close existing database connections
        from src.database.connection import close_database
        await close_database()

        # Remove database file
        if DATABASE_PATH.exists():
            os.remove(DATABASE_PATH)
            message = f"✅ Base de datos eliminada: {DATABASE_PATH.name}"
        else:
            message = f"ℹ️ La base de datos no existe: {DATABASE_PATH.name}"

        # Reinitialize database
        from src.database.connection import init_database
        await init_database()

        # Re-register the super admin who cleaned the database
        admin_count = 0
        async with get_session() as session:
            user_repo = UserRepository(session)

            # Register all super admins from settings
            for admin_id in settings.super_admin_ids:
                user, _ = await user_repo.get_or_create(
                    telegram_id=admin_id,
                    username=None,
                    first_name="SuperAdmin",
                    default_balance=settings.default_balance,
                )
                if user:
                    await user_repo.set_admin(user.id, True)
                    admin_count += 1

        await update.message.reply_text(
            f"""🧹 **Base de Datos Limpiada**

{message}

✅ Base de datos reinicializada
👑 Super admins restaurados: {admin_count}
ℹ️ Todos los datos han sido eliminados
⚠️ Los usuarios deberán registrarse de nuevo"""
        )

        logger.info(f"Database cleaned by {update.effective_user.id}, {admin_count} admins restored")

    except Exception as e:
        logger.error(f"Error cleaning database: {e}")
        await update.message.reply_text(f"❌ Error al limpiar la base de datos: {str(e)[:100]}")
