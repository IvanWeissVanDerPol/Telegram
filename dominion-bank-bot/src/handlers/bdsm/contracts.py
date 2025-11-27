"""
The Phantom Bot - Contract Command Handlers
/contrato, /firmar_contrato, /romper_contrato, /mis_contratos
"""
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.models import ContractStatus, RequestType
from src.database.repositories import (
    ContractRepository,
    PendingRequestRepository,
    UserRepository,
)
from src.utils.helpers import extract_username, parse_amount

logger = logging.getLogger(__name__)

CONTRACT_BREAK_PENALTY = 500  # Penalty for breaking a contract


async def contrato_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /contrato command - propose a contract to someone."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []
    if len(args) < 3:
        await update.message.reply_text(
            "📝 Uso: /contrato @usuario [días] [términos]\n"
            f"⚠️ Penalización por romper: {CONTRACT_BREAK_PENALTY} {settings.currency_name}\n\n"
            "Ejemplo: /contrato @sumiso 30 Obediencia total y servicio diario"
        )
        return

    target_username = extract_username(args[0])
    duration_days = parse_amount(args[1])
    terms = " ".join(args[2:])

    if not target_username:
        await update.message.reply_text("❌ Debes especificar un usuario.")
        return

    if duration_days is None or duration_days < 1 or duration_days > 365:
        await update.message.reply_text("❌ La duración debe ser entre 1 y 365 días.")
        return

    if len(terms) < 10:
        await update.message.reply_text("❌ Los términos son muy cortos.")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        contract_repo = ContractRepository(session)
        request_repo = PendingRequestRepository(session)

        # Get dom (proposer)
        dom = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not dom:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get sub (target)
        sub = await user_repo.get_by_username(target_username)
        if not sub:
            await update.message.reply_text("❌ Usuario no encontrado.")
            return

        # Check self-contract
        if dom.id == sub.id:
            await update.message.reply_text("❌ No puedes hacer un contrato contigo mismo.")
            return

        # Check if already have an active contract together
        existing = await contract_repo.get_active_between(dom.id, sub.id)
        if existing:
            await update.message.reply_text(
                f"❌ Ya tienes un contrato activo con {sub.display_name}."
            )
            return

        # Create pending contract request
        await request_repo.create_contract_request(
            from_user_id=dom.id,
            to_user_id=sub.id,
            terms=terms,
            duration_days=duration_days,
            expires_in_minutes=60,
        )

        logger.info(f"Contract proposal: {dom.display_name} -> {sub.display_name}")

    await update.message.reply_text(
        f"""📜 **Propuesta de Contrato**

{dom.display_name} propone un contrato a {sub.display_name}

📝 Términos:
{terms}

⏱️ Duración: {duration_days} días
⚠️ Penalización por romper: {CONTRACT_BREAK_PENALTY} {settings.currency_name}

{sub.display_name} tiene 1 hora para responder:
/firmar_contrato - Aceptar
/rechazar_contrato - Rechazar"""
    )


async def firmar_contrato_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /firmar_contrato command - sign a pending contract."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        contract_repo = ContractRepository(session)
        request_repo = PendingRequestRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get pending contract request
        request = await request_repo.get_pending_contract(user.id)
        if not request:
            await update.message.reply_text("❌ No tienes propuestas de contrato pendientes.")
            return

        # Get dom
        dom = await user_repo.get_by_id(request.from_user_id)
        if not dom:
            await update.message.reply_text("❌ Error: Usuario no encontrado.")
            return

        # Create contract
        ends_at = datetime.utcnow() + timedelta(days=request.duration_days or 30)
        contract = await contract_repo.create(
            dom_id=dom.id,
            sub_id=user.id,
            terms=request.terms or "Términos no especificados",
            ends_at=ends_at,
        )

        # Delete request
        await request_repo.delete(request.id)

        logger.info(f"Contract signed: {dom.display_name} <-> {user.display_name}")

    await update.message.reply_text(
        f"""📜 **Contrato Firmado**

{user.display_name} ha firmado el contrato con {dom.display_name}

📝 Términos: {contract.terms}
⏱️ Duración: {request.duration_days} días
📅 Termina: {contract.ends_at.strftime('%Y-%m-%d')}

⚠️ Romper el contrato costará {CONTRACT_BREAK_PENALTY} {settings.currency_name}"""
    )


async def rechazar_contrato_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /rechazar_contrato command - reject a contract proposal."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        request_repo = PendingRequestRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get pending contract request
        request = await request_repo.get_pending_contract(user.id)
        if not request:
            await update.message.reply_text("❌ No tienes propuestas de contrato pendientes.")
            return

        dom_name = request.from_user.display_name

        # Delete request
        await request_repo.delete(request.id)

        logger.info(f"Contract rejected by {user.display_name}")

    await update.message.reply_text(
        f"📜 Has rechazado el contrato de {dom_name}."
    )


async def romper_contrato_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /romper_contrato command - break an active contract."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []
    if not args:
        await update.message.reply_text(
            f"📝 Uso: /romper_contrato [id]\n"
            f"⚠️ Penalización: {CONTRACT_BREAK_PENALTY} {settings.currency_name}\n\n"
            "Ver tus contratos: /mis_contratos"
        )
        return

    contract_id = parse_amount(args[0])
    if contract_id is None:
        await update.message.reply_text("❌ ID de contrato inválido.")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        contract_repo = ContractRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get contract
        contract = await contract_repo.get_by_id(contract_id)
        if not contract:
            await update.message.reply_text("❌ Contrato no encontrado.")
            return

        # Check if user is part of the contract
        if contract.dom_id != user.id and contract.sub_id != user.id:
            await update.message.reply_text("❌ No eres parte de este contrato.")
            return

        # Check if contract is active
        if contract.status != ContractStatus.ACTIVE:
            await update.message.reply_text("❌ Este contrato no está activo.")
            return

        # Check balance for penalty
        if user.balance < CONTRACT_BREAK_PENALTY:
            await update.message.reply_text(
                f"❌ Necesitas {CONTRACT_BREAK_PENALTY} {settings.currency_name} para romper el contrato.\n"
                f"Tu saldo: {user.balance} {settings.currency_name}"
            )
            return

        # Get the other party
        other_party_id = contract.sub_id if contract.dom_id == user.id else contract.dom_id
        other_party = await user_repo.get_by_id(other_party_id)

        # Apply penalty: deduct from breaker, give to other party
        await user_repo.update_balance(user.id, -CONTRACT_BREAK_PENALTY)
        if other_party:
            await user_repo.update_balance(other_party.id, CONTRACT_BREAK_PENALTY)

        # Break contract
        await contract_repo.break_contract(contract.id, user.id)

        other_name = other_party.display_name if other_party else "el otro usuario"
        logger.info(f"Contract broken: #{contract.id} by {user.display_name}")

    await update.message.reply_text(
        f"""📜 **Contrato Roto**

{user.display_name} ha roto el contrato con {other_name}

💰 Penalización pagada: {CONTRACT_BREAK_PENALTY} {settings.currency_name}"""
    )


async def mis_contratos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mis_contratos command - show your contracts."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        contract_repo = ContractRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get user's contracts
        contracts = await contract_repo.get_by_user(user.id)

        if not contracts:
            await update.message.reply_text("📜 No tienes contratos.")
            return

        # Format list
        lines = []
        for contract in contracts:
            status_emoji = {
                ContractStatus.ACTIVE: "🟢",
                ContractStatus.COMPLETED: "✅",
                ContractStatus.BROKEN: "💔",
            }
            emoji = status_emoji.get(contract.status, "❓")

            # Determine role and other party
            if contract.dom_id == user.id:
                role = "Dom"
                other = contract.sub.display_name if contract.sub else "?"
            else:
                role = "Sub"
                other = contract.dom.display_name if contract.dom else "?"

            # Time remaining for active contracts
            if contract.status == ContractStatus.ACTIVE and contract.ends_at:
                time_left = contract.ends_at - datetime.utcnow()
                days_left = max(0, time_left.days)
                time_str = f"| {days_left}d restantes"
            else:
                time_str = ""

            lines.append(
                f"{emoji} #{contract.id} ({role}) con {other} {time_str}\n"
                f"   📝 {contract.terms[:40]}..."
            )

        contracts_list = "\n".join(lines)

    await update.message.reply_text(
        f"""📜 **Tus Contratos**

{contracts_list}

Para romper: /romper_contrato [id]"""
    )


async def ver_contrato_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ver_contrato command - view contract details."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []
    if not args:
        await update.message.reply_text("📝 Uso: /ver_contrato [id]")
        return

    contract_id = parse_amount(args[0])
    if contract_id is None:
        await update.message.reply_text("❌ ID de contrato inválido.")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        contract_repo = ContractRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get contract
        contract = await contract_repo.get_by_id(contract_id)
        if not contract:
            await update.message.reply_text("❌ Contrato no encontrado.")
            return

        # Check if user is part of the contract
        if contract.dom_id != user.id and contract.sub_id != user.id:
            await update.message.reply_text("❌ No eres parte de este contrato.")
            return

        # Format status
        status_text = {
            ContractStatus.ACTIVE: "🟢 Activo",
            ContractStatus.COMPLETED: "✅ Completado",
            ContractStatus.BROKEN: "💔 Roto",
        }
        status = status_text.get(contract.status, "❓ Desconocido")

        # Time info
        if contract.status == ContractStatus.ACTIVE and contract.ends_at:
            time_left = contract.ends_at - datetime.utcnow()
            days_left = max(0, time_left.days)
            time_str = f"⏱️ {days_left} días restantes"
        else:
            time_str = f"📅 Terminó: {contract.ends_at.strftime('%Y-%m-%d') if contract.ends_at else 'N/A'}"

        dom_name = contract.dom.display_name if contract.dom else "?"
        sub_name = contract.sub.display_name if contract.sub else "?"

    await update.message.reply_text(
        f"""📜 **Contrato #{contract.id}**

👑 Dom: {dom_name}
🔗 Sub: {sub_name}

📝 Términos:
{contract.terms}

{status}
{time_str}

📅 Firmado: {contract.starts_at.strftime('%Y-%m-%d') if contract.starts_at else 'N/A'}"""
    )
