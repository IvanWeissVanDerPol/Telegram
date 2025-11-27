"""
The Phantom Bot - Profile Command Handlers
/perfil, /editarperfil, /configuracion
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.models import MainRole, ExperienceLevel, PrivacyLevel
from src.database.repositories import (
    CollarRepository,
    ContractRepository,
    ProfileRepository,
    UserRepository,
    UserSettingsRepository,
)
from src.utils.helpers import extract_username

logger = logging.getLogger(__name__)


async def perfil_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /perfil command - view profile."""
    if not update.effective_user or not update.message:
        return

    args_text = " ".join(context.args) if context.args else ""
    target_username = extract_username(args_text) if args_text else None

    async with get_session() as session:
        user_repo = UserRepository(session)
        profile_repo = ProfileRepository(session)
        collar_repo = CollarRepository(session)
        contract_repo = ContractRepository(session)
        settings_repo = UserSettingsRepository(session)

        # Get viewer
        viewer = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not viewer:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get target (self or specified user)
        if target_username:
            target = await user_repo.get_by_username(target_username)
            if not target:
                await update.message.reply_text("❌ Usuario no encontrado.")
                return
            is_self = False
        else:
            target = viewer
            is_self = True

        # Check privacy settings
        target_settings = await settings_repo.get_or_create(target.id)
        if not is_self and target_settings.profile_privacy == PrivacyLevel.PRIVATE:
            await update.message.reply_text("🔒 Este perfil es privado.")
            return

        # Get profile
        profile = await profile_repo.get_or_create(target.id)

        # Get collar status
        collar = await collar_repo.get_by_sub(target.id)
        collar_status = f"⛓️ Lleva el collar de {collar.owner.display_name}" if collar else "🔓 Libre"

        # Get collared subs
        subs = await collar_repo.get_by_owner(target.id)
        subs_count = len(subs) if subs else 0

        # Get active contracts
        contracts = await contract_repo.get_active_by_user(target.id)
        contracts_count = len(contracts) if contracts else 0

        # Format role
        role_display = {
            MainRole.DOMINANT: "👑 Dominante",
            MainRole.SUBMISSIVE: "🔗 Sumis@",
            MainRole.SWITCH: "🔄 Switch",
            MainRole.UNDEFINED: "❓ Sin definir",
        }
        role = role_display.get(profile.main_role, "❓ Sin definir")

        # Format experience
        exp_display = {
            ExperienceLevel.NOVICE: "🌱 Novato",
            ExperienceLevel.BEGINNER: "📗 Principiante",
            ExperienceLevel.INTERMEDIATE: "📘 Intermedio",
            ExperienceLevel.ADVANCED: "📙 Avanzado",
            ExperienceLevel.EXPERT: "📕 Experto",
        }
        experience = exp_display.get(profile.experience_level, "🌱 Novato")

        # Format pronouns
        pronouns = f"({profile.pronouns})" if profile.pronouns else ""

        # Format bio
        bio = profile.bio if profile.bio else "Sin biografía"

        # Format age
        age_str = f"🎂 {profile.age} años" if profile.age else ""

        # Edit hint for self
        edit_hint = "\n\n✏️ /editarperfil para modificar" if is_self else ""

    await update.message.reply_text(
        f"""👤 **Perfil de {target.display_name}** {pronouns}

{role} | {experience}
{age_str}

📝 {bio}

💰 Saldo: {target.balance} {settings.currency_name}
{collar_status}
👥 Sumis@s: {subs_count}
📜 Contratos activos: {contracts_count}
{edit_hint}"""
    )


async def editarperfil_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /editarperfil command - edit profile."""
    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []

    # Show help if no args
    if not args:
        await update.message.reply_text(
            """✏️ **Editar Perfil**

Comandos disponibles:

/editarperfil bio [texto]
  Ejemplo: /editarperfil bio Me encanta el cuero

/editarperfil rol [dom/sub/switch]
  Ejemplo: /editarperfil rol dom

/editarperfil experiencia [novato/principiante/intermedio/avanzado/experto]
  Ejemplo: /editarperfil experiencia intermedio

/editarperfil edad [número]
  Ejemplo: /editarperfil edad 25

/editarperfil pronombres [texto]
  Ejemplo: /editarperfil pronombres él/ellos"""
        )
        return

    field = args[0].lower()
    value = " ".join(args[1:]) if len(args) > 1 else None

    if not value:
        await update.message.reply_text(f"❌ Debes especificar un valor para {field}")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        profile_repo = ProfileRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get profile
        profile = await profile_repo.get_or_create(user.id)

        # Update field
        if field == "bio":
            if len(value) > 500:
                await update.message.reply_text("❌ La bio es muy larga (máx 500 caracteres)")
                return
            await profile_repo.update(profile.user_id, bio=value)
            msg = f"✅ Bio actualizada: {value}"

        elif field == "rol":
            role_map = {
                "dom": MainRole.DOMINANT,
                "dominante": MainRole.DOMINANT,
                "sub": MainRole.SUBMISSIVE,
                "sumiso": MainRole.SUBMISSIVE,
                "sumisa": MainRole.SUBMISSIVE,
                "switch": MainRole.SWITCH,
            }
            role = role_map.get(value.lower())
            if not role:
                await update.message.reply_text("❌ Rol inválido. Usa: dom, sub, o switch")
                return
            await profile_repo.update(profile.user_id, main_role=role)
            msg = f"✅ Rol actualizado"

        elif field == "experiencia":
            exp_map = {
                "novato": ExperienceLevel.NOVICE,
                "principiante": ExperienceLevel.BEGINNER,
                "intermedio": ExperienceLevel.INTERMEDIATE,
                "avanzado": ExperienceLevel.ADVANCED,
                "experto": ExperienceLevel.EXPERT,
            }
            exp = exp_map.get(value.lower())
            if not exp:
                await update.message.reply_text(
                    "❌ Nivel inválido. Usa: novato, principiante, intermedio, avanzado, experto"
                )
                return
            await profile_repo.update(profile.user_id, experience_level=exp)
            msg = f"✅ Experiencia actualizada"

        elif field == "edad":
            try:
                age = int(value)
                if age < 18 or age > 100:
                    await update.message.reply_text("❌ La edad debe ser entre 18 y 100")
                    return
                await profile_repo.update(profile.user_id, age=age)
                msg = f"✅ Edad actualizada: {age}"
            except ValueError:
                await update.message.reply_text("❌ La edad debe ser un número")
                return

        elif field == "pronombres":
            if len(value) > 20:
                await update.message.reply_text("❌ Los pronombres son muy largos")
                return
            await profile_repo.update(profile.user_id, pronouns=value)
            msg = f"✅ Pronombres actualizados: {value}"

        else:
            await update.message.reply_text(
                f"❌ Campo desconocido: {field}\n"
                "Campos válidos: bio, rol, experiencia, edad, pronombres"
            )
            return

        logger.info(f"Profile updated: {user.display_name} - {field}")

    await update.message.reply_text(msg)


async def configuracion_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /configuracion command - manage privacy settings."""
    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []

    async with get_session() as session:
        user_repo = UserRepository(session)
        settings_repo = UserSettingsRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get settings
        user_settings = await settings_repo.get_or_create(user.id)

        # Show settings if no args
        if not args:
            privacy_display = {
                PrivacyLevel.PUBLIC: "🌍 Público",
                PrivacyLevel.FRIENDS: "👥 Solo amigos",
                PrivacyLevel.PRIVATE: "🔒 Privado",
            }
            profile_privacy = privacy_display.get(user_settings.profile_privacy, "🌍 Público")
            history_privacy = privacy_display.get(user_settings.transaction_privacy, "🌍 Público")

            notifications = "🔔 Activadas" if user_settings.notifications_enabled else "🔕 Desactivadas"

            await update.message.reply_text(
                f"""⚙️ **Configuración**

📝 Perfil: {profile_privacy}
💰 Historial: {history_privacy}
🔔 Notificaciones: {notifications}

Para cambiar:
/configuracion perfil [publico/amigos/privado]
/configuracion historial [publico/amigos/privado]
/configuracion notificaciones [on/off]"""
            )
            return

        # Update setting
        setting = args[0].lower()
        value = args[1].lower() if len(args) > 1 else None

        if not value:
            await update.message.reply_text(f"❌ Debes especificar un valor")
            return

        if setting == "perfil":
            privacy_map = {
                "publico": PrivacyLevel.PUBLIC,
                "público": PrivacyLevel.PUBLIC,
                "amigos": PrivacyLevel.FRIENDS,
                "privado": PrivacyLevel.PRIVATE,
            }
            privacy = privacy_map.get(value)
            if not privacy:
                await update.message.reply_text("❌ Valor inválido. Usa: publico, amigos, privado")
                return
            await settings_repo.update(user.id, profile_privacy=privacy)
            msg = "✅ Privacidad del perfil actualizada"

        elif setting == "historial":
            privacy_map = {
                "publico": PrivacyLevel.PUBLIC,
                "público": PrivacyLevel.PUBLIC,
                "amigos": PrivacyLevel.FRIENDS,
                "privado": PrivacyLevel.PRIVATE,
            }
            privacy = privacy_map.get(value)
            if not privacy:
                await update.message.reply_text("❌ Valor inválido. Usa: publico, amigos, privado")
                return
            await settings_repo.update(user.id, transaction_privacy=privacy)
            msg = "✅ Privacidad del historial actualizada"

        elif setting == "notificaciones":
            if value in ("on", "activar", "si", "sí"):
                await settings_repo.update(user.id, notifications_enabled=True)
                msg = "✅ Notificaciones activadas"
            elif value in ("off", "desactivar", "no"):
                await settings_repo.update(user.id, notifications_enabled=False)
                msg = "✅ Notificaciones desactivadas"
            else:
                await update.message.reply_text("❌ Valor inválido. Usa: on/off")
                return

        else:
            await update.message.reply_text(
                f"❌ Configuración desconocida: {setting}\n"
                "Opciones: perfil, historial, notificaciones"
            )
            return

        logger.info(f"Settings updated: {user.display_name} - {setting}")

    await update.message.reply_text(msg)
