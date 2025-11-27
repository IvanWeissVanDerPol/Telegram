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
from src.utils.messages import (
    DIVIDER_LIGHT,
    EMOJI_BALANCE,
    EMOJI_COLLAR,
    EMOJI_CONTRACT,
    EMOJI_DOM,
    EMOJI_ERROR,
    EMOJI_FRIENDS,
    EMOJI_INFO,
    EMOJI_PRIVATE,
    EMOJI_PROFILE,
    EMOJI_PUBLIC,
    EMOJI_SUB,
    EMOJI_SUCCESS,
    EMOJI_SWITCH,
    format_currency,
)

logger = logging.getLogger(__name__)

# Role display mappings with emojis
ROLE_DISPLAY = {
    MainRole.DOM: f"{EMOJI_DOM} Dominante",
    MainRole.SUB: f"{EMOJI_SUB} Sumis@",
    MainRole.SWITCH: f"{EMOJI_SWITCH} Switch",
}

# Experience display mappings
EXPERIENCE_DISPLAY = {
    ExperienceLevel.PRINCIPIANTE: "🌱 Principiante",
    ExperienceLevel.INTERMEDIO: "📘 Intermedio",
    ExperienceLevel.AVANZADO: "📙 Avanzado",
    ExperienceLevel.EXPERTO: "📕 Experto",
}

# Privacy display mappings (matches actual PrivacyLevel enum: PUBLIC, MEMBERS, VERIFIED, PRIVATE)
PRIVACY_DISPLAY = {
    PrivacyLevel.PUBLIC: f"{EMOJI_PUBLIC} Publico",
    PrivacyLevel.MEMBERS: f"{EMOJI_FRIENDS} Solo miembros",
    PrivacyLevel.VERIFIED: "✓ Solo verificados",
    PrivacyLevel.PRIVATE: f"{EMOJI_PRIVATE} Privado",
}


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
            await update.message.reply_text(f"{EMOJI_ERROR} Debes registrarte primero con /start")
            return

        # Get target (self or specified user)
        if target_username:
            target = await user_repo.get_by_username(target_username)
            if not target:
                await update.message.reply_text(f"{EMOJI_ERROR} Usuario no encontrado.")
                return
            is_self = False
        else:
            target = viewer
            is_self = True

        # Check privacy settings
        target_settings = await settings_repo.get_or_create(target.id)
        if not is_self and target_settings.profile_privacy == PrivacyLevel.PRIVATE:
            await update.message.reply_text(f"{EMOJI_PRIVATE} Este perfil es privado.")
            return

        # Get profile
        profile = await profile_repo.get_or_create(target.id)

        # Get collar status
        collar = await collar_repo.get_by_sub(target.id)
        if collar:
            collar_status = f"{EMOJI_COLLAR} Lleva el collar de **{collar.owner.display_name}**"
        else:
            collar_status = f"{EMOJI_PUBLIC} Libre"

        # Get collared subs
        subs = await collar_repo.get_by_owner(target.id)
        subs_count = len(subs) if subs else 0

        # Get active contracts
        contracts = await contract_repo.get_active_by_user(target.id)
        contracts_count = len(contracts) if contracts else 0

        # Format role with emoji
        role = ROLE_DISPLAY.get(profile.main_role, "❓ Sin definir")

        # Format experience
        experience = EXPERIENCE_DISPLAY.get(profile.experience_level, "🌱 Principiante")

        # Format pronouns
        pronouns_display = f" ({profile.pronouns})" if profile.pronouns else ""

        # Format bio
        bio = profile.bio if profile.bio else "Sin biografía"

        # Format age
        age_display = f"\n🎂 {profile.age} años" if profile.age else ""

        # Edit hint for self
        edit_hint = f"\n\n{EMOJI_INFO} /editarperfil para modificar" if is_self else ""

        # Capture values before leaving session context
        target_display = target.display_name
        target_balance = target.balance

        await update.message.reply_text(
            f"""{EMOJI_PROFILE} **Perfil de {target_display}**{pronouns_display}

{role} │ {experience}{age_display}

{DIVIDER_LIGHT}

📝 {bio}

{DIVIDER_LIGHT}

{EMOJI_BALANCE} **Saldo:** {format_currency(target_balance)}
{collar_status}
{EMOJI_SUB} **Sumis@s:** {subs_count}
{EMOJI_CONTRACT} **Contratos:** {contracts_count}{edit_hint}"""
        )


async def editarperfil_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /editarperfil command - edit profile."""
    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []

    # Show help if no args
    if not args:
        await update.message.reply_text(
            f"""{EMOJI_PROFILE} **Editar Perfil**

{DIVIDER_LIGHT}

**Comandos disponibles:**

{EMOJI_INFO} /editarperfil bio [texto]
   Ejemplo: /editarperfil bio Me encanta el cuero

{EMOJI_INFO} /editarperfil rol [dom/sub/switch]
   Ejemplo: /editarperfil rol dom

{EMOJI_INFO} /editarperfil experiencia [nivel]
   Niveles: novato, principiante, intermedio, avanzado, experto
   Ejemplo: /editarperfil experiencia intermedio

{EMOJI_INFO} /editarperfil edad [numero]
   Ejemplo: /editarperfil edad 25

{EMOJI_INFO} /editarperfil pronombres [texto]
   Ejemplo: /editarperfil pronombres el/ellos"""
        )
        return

    field = args[0].lower()
    value = " ".join(args[1:]) if len(args) > 1 else None

    if not value:
        await update.message.reply_text(f"{EMOJI_ERROR} Debes especificar un valor para **{field}**")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        profile_repo = ProfileRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text(f"{EMOJI_ERROR} Debes registrarte primero con /start")
            return

        # Get profile
        profile = await profile_repo.get_or_create(user.id)

        # Update field
        if field == "bio":
            if len(value) > 500:
                await update.message.reply_text(f"{EMOJI_ERROR} La bio es muy larga (max 500 caracteres)")
                return
            await profile_repo.update(profile.user_id, bio=value)
            msg = f"""{EMOJI_SUCCESS} **Bio actualizada**

📝 {value}"""

        elif field == "rol":
            role_map = {
                "dom": MainRole.DOM,
                "dominante": MainRole.DOM,
                "sub": MainRole.SUB,
                "sumiso": MainRole.SUB,
                "sumisa": MainRole.SUB,
                "switch": MainRole.SWITCH,
            }
            role = role_map.get(value.lower())
            if not role:
                await update.message.reply_text(f"{EMOJI_ERROR} Rol invalido. Usa: **dom**, **sub**, o **switch**")
                return
            await profile_repo.update(profile.user_id, main_role=role)
            role_display = ROLE_DISPLAY.get(role, "")
            msg = f"""{EMOJI_SUCCESS} **Rol actualizado**

{role_display}"""

        elif field == "experiencia":
            exp_map = {
                "novato": ExperienceLevel.PRINCIPIANTE,
                "principiante": ExperienceLevel.PRINCIPIANTE,
                "intermedio": ExperienceLevel.INTERMEDIO,
                "avanzado": ExperienceLevel.AVANZADO,
                "experto": ExperienceLevel.EXPERTO,
            }
            exp = exp_map.get(value.lower())
            if not exp:
                await update.message.reply_text(
                    f"{EMOJI_ERROR} Nivel invalido.\n\nUsa: novato, principiante, intermedio, avanzado, experto"
                )
                return
            await profile_repo.update(profile.user_id, experience_level=exp)
            exp_display = EXPERIENCE_DISPLAY.get(exp, "")
            msg = f"""{EMOJI_SUCCESS} **Experiencia actualizada**

{exp_display}"""

        elif field == "edad":
            try:
                age = int(value)
                if age < 18 or age > 100:
                    await update.message.reply_text(f"{EMOJI_ERROR} La edad debe ser entre 18 y 100")
                    return
                await profile_repo.update(profile.user_id, age=age)
                msg = f"""{EMOJI_SUCCESS} **Edad actualizada**

🎂 {age} anos"""
            except ValueError:
                await update.message.reply_text(f"{EMOJI_ERROR} La edad debe ser un numero")
                return

        elif field == "pronombres":
            if len(value) > 20:
                await update.message.reply_text(f"{EMOJI_ERROR} Los pronombres son muy largos (max 20 caracteres)")
                return
            await profile_repo.update(profile.user_id, pronouns=value)
            msg = f"""{EMOJI_SUCCESS} **Pronombres actualizados**

({value})"""

        else:
            await update.message.reply_text(
                f"""{EMOJI_ERROR} Campo desconocido: **{field}**

Campos validos: bio, rol, experiencia, edad, pronombres"""
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
            await update.message.reply_text(f"{EMOJI_ERROR} Debes registrarte primero con /start")
            return

        # Get settings
        user_settings = await settings_repo.get_or_create(user.id)

        # Show settings if no args
        if not args:
            profile_privacy = PRIVACY_DISPLAY.get(user_settings.privacy_level, f"{EMOJI_PUBLIC} Publico")

            await update.message.reply_text(
                f"""⚙️ **Configuracion**

{DIVIDER_LIGHT}

{EMOJI_PROFILE} **Privacidad:** {profile_privacy}
🔔 **Notif. Transferencias:** {"✅" if user_settings.notify_transfers else "❌"}
📢 **Notif. Menciones:** {"✅" if user_settings.notify_mentions else "❌"}
⛓️ **Notif. BDSM:** {"✅" if user_settings.notify_bdsm else "❌"}

{DIVIDER_LIGHT}

**Para cambiar:**
/configuracion privacidad [publico/miembros/verificados/privado]
/configuracion notificaciones [on/off]"""
            )
            return

        # Update setting
        setting = args[0].lower()
        value = args[1].lower() if len(args) > 1 else None

        if not value:
            await update.message.reply_text(f"{EMOJI_ERROR} Debes especificar un valor")
            return

        if setting == "perfil":
            privacy_map = {
                "publico": PrivacyLevel.PUBLIC,
                "público": PrivacyLevel.PUBLIC,
                "miembros": PrivacyLevel.MEMBERS,
                "verificados": PrivacyLevel.VERIFIED,
                "privado": PrivacyLevel.PRIVATE,
            }
            privacy = privacy_map.get(value)
            if not privacy:
                await update.message.reply_text(f"{EMOJI_ERROR} Valor invalido. Usa: publico, miembros, verificados, privado")
                return
            await settings_repo.update(user.id, profile_privacy=privacy)
            privacy_display = PRIVACY_DISPLAY.get(privacy, "")
            msg = f"""{EMOJI_SUCCESS} **Privacidad del perfil actualizada**

{privacy_display}"""

        elif setting == "historial":
            privacy_map = {
                "publico": PrivacyLevel.PUBLIC,
                "público": PrivacyLevel.PUBLIC,
                "miembros": PrivacyLevel.MEMBERS,
                "verificados": PrivacyLevel.VERIFIED,
                "privado": PrivacyLevel.PRIVATE,
            }
            privacy = privacy_map.get(value)
            if not privacy:
                await update.message.reply_text(f"{EMOJI_ERROR} Valor invalido. Usa: publico, miembros, verificados, privado")
                return
            await settings_repo.update(user.id, transaction_privacy=privacy)
            privacy_display = PRIVACY_DISPLAY.get(privacy, "")
            msg = f"""{EMOJI_SUCCESS} **Privacidad del historial actualizada**

{privacy_display}"""

        elif setting == "notificaciones":
            if value in ("on", "activar", "si", "sí"):
                await settings_repo.update(user.id, notifications_enabled=True)
                msg = f"""{EMOJI_SUCCESS} **Notificaciones activadas**

🔔 Recibiras notificaciones"""
            elif value in ("off", "desactivar", "no"):
                await settings_repo.update(user.id, notifications_enabled=False)
                msg = f"""{EMOJI_SUCCESS} **Notificaciones desactivadas**

🔕 No recibiras notificaciones"""
            else:
                await update.message.reply_text(f"{EMOJI_ERROR} Valor invalido. Usa: on/off")
                return

        else:
            await update.message.reply_text(
                f"""{EMOJI_ERROR} Configuracion desconocida: **{setting}**

Opciones: perfil, historial, notificaciones"""
            )
            return

        logger.info(f"Settings updated: {user.display_name} - {setting}")

    await update.message.reply_text(msg)
