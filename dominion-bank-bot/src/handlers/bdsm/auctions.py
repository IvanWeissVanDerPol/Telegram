"""
The Phantom Bot - Auction Command Handlers
/subasta, /pujar, /subastas, /cancelar_subasta
"""
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.database.connection import get_session
from src.database.models import AuctionStatus, TransactionType
from src.database.repositories import (
    AuctionRepository,
    TransactionRepository,
    UserRepository,
)
from src.utils.helpers import parse_amount

logger = logging.getLogger(__name__)

AUCTION_FEE = 50  # Fee to start an auction
DEFAULT_AUCTION_HOURS = 24  # Default auction duration
MIN_BID = 10  # Minimum bid amount


async def subasta_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /subasta command - start an auction."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []
    if len(args) < 2:
        await update.message.reply_text(
            "📝 Uso: /subasta [precio_inicial] [descripción]\n"
            f"💰 Comisión: {AUCTION_FEE} {settings.currency_name}\n"
            f"⏱️ Duración: {DEFAULT_AUCTION_HOURS} horas\n\n"
            "Ejemplo: /subasta 100 1 hora de servicio exclusivo"
        )
        return

    starting_price = parse_amount(args[0])
    description = " ".join(args[1:])

    if starting_price is None or starting_price < MIN_BID:
        await update.message.reply_text(
            f"❌ El precio inicial mínimo es {MIN_BID} {settings.currency_name}."
        )
        return

    if len(description) < 5:
        await update.message.reply_text("❌ La descripción es muy corta.")
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        auction_repo = AuctionRepository(session)
        tx_repo = TransactionRepository(session)

        # Get seller
        seller = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not seller:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Check balance for fee
        if seller.balance < AUCTION_FEE:
            await update.message.reply_text(
                f"❌ Necesitas {AUCTION_FEE} {settings.currency_name} para iniciar una subasta.\n"
                f"Tu saldo: {seller.balance} {settings.currency_name}"
            )
            return

        # Check if user already has an active auction
        existing = await auction_repo.get_active_by_seller(seller.id)
        if existing:
            await update.message.reply_text(
                "❌ Ya tienes una subasta activa. Cancélala primero con /cancelar_subasta"
            )
            return

        # Deduct fee
        await user_repo.update_balance(seller.id, -AUCTION_FEE)

        # Record fee transaction
        await tx_repo.create(
            sender_id=seller.id,
            recipient_id=None,
            amount=AUCTION_FEE,
            transaction_type=TransactionType.FEE,
            description="Comisión de subasta",
        )

        # Create auction
        auction = await auction_repo.create(
            seller_id=seller.id,
            description=description,
            starting_price=starting_price,
            hours=DEFAULT_AUCTION_HOURS,
        )

        logger.info(f"Auction created: {seller.display_name} - {description}")

    await update.message.reply_text(
        f"""🔨 **Nueva Subasta**

🏷️ ID: #{auction.id}
👤 Vendedor: {seller.display_name}
📝 {description}

💰 Precio inicial: {starting_price} {settings.currency_name}
⏱️ Termina en: {DEFAULT_AUCTION_HOURS} horas

Para pujar: /pujar {auction.id} [cantidad]"""
    )


async def pujar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /pujar command - place a bid on an auction."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []
    if len(args) < 2:
        await update.message.reply_text(
            "📝 Uso: /pujar [id_subasta] [cantidad]\n"
            "Ejemplo: /pujar 1 150"
        )
        return

    auction_id = parse_amount(args[0])
    bid_amount = parse_amount(args[1])

    if auction_id is None:
        await update.message.reply_text("❌ ID de subasta inválido.")
        return

    if bid_amount is None or bid_amount < MIN_BID:
        await update.message.reply_text(
            f"❌ La puja mínima es {MIN_BID} {settings.currency_name}."
        )
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        auction_repo = AuctionRepository(session)

        # Get bidder
        bidder = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not bidder:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get auction
        auction = await auction_repo.get_by_id(auction_id)
        if not auction:
            await update.message.reply_text("❌ Subasta no encontrada.")
            return

        # Check if auction is still active
        if auction.status != AuctionStatus.ACTIVE:
            await update.message.reply_text("❌ Esta subasta ya no está activa.")
            return

        # Check if expired
        if auction.ends_at < datetime.utcnow():
            await update.message.reply_text("❌ Esta subasta ya terminó.")
            return

        # Check if bidding on own auction
        if auction.seller_id == bidder.id:
            await update.message.reply_text("❌ No puedes pujar en tu propia subasta.")
            return

        # Check balance
        if bidder.balance < bid_amount:
            await update.message.reply_text(
                f"❌ No tienes suficiente saldo.\n"
                f"Tu saldo: {bidder.balance} {settings.currency_name}"
            )
            return

        # Check if bid is higher than current
        min_required = max(auction.starting_price, (auction.current_bid or 0) + 1)
        if bid_amount < min_required:
            await update.message.reply_text(
                f"❌ Tu puja debe ser al menos {min_required} {settings.currency_name}."
            )
            return

        # Refund previous bidder if any
        if auction.current_bidder_id:
            prev_bidder = await user_repo.get_by_id(auction.current_bidder_id)
            if prev_bidder and auction.current_bid:
                await user_repo.update_balance(prev_bidder.id, auction.current_bid)

        # Deduct from new bidder
        await user_repo.update_balance(bidder.id, -bid_amount)

        # Place bid
        await auction_repo.place_bid(auction.id, bidder.id, bid_amount)

        logger.info(f"Bid: {bidder.display_name} bid {bid_amount} on auction #{auction.id}")

    await update.message.reply_text(
        f"""🔨 **Puja Realizada**

Subasta #{auction.id}
📝 {auction.description}

💰 Tu puja: {bid_amount} {settings.currency_name}

¡Eres el pujador más alto!"""
    )


async def subastas_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /subastas command - list active auctions."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        auction_repo = AuctionRepository(session)

        # Get active auctions
        auctions = await auction_repo.get_all_active()

        if not auctions:
            await update.message.reply_text("🔨 No hay subastas activas.")
            return

        # Format list
        lines = []
        for auction in auctions:
            time_left = auction.ends_at - datetime.utcnow()
            if time_left.total_seconds() > 0:
                hours = int(time_left.total_seconds() / 3600)
                minutes = int((time_left.total_seconds() % 3600) / 60)
                if hours > 0:
                    time_str = f"{hours}h {minutes}m"
                else:
                    time_str = f"{minutes}m"
            else:
                time_str = "Terminando..."

            current = auction.current_bid or auction.starting_price
            lines.append(
                f"🔨 **#{auction.id}** - {auction.seller.display_name}\n"
                f"   📝 {auction.description[:50]}...\n"
                f"   💰 Actual: {current} | ⏱️ {time_str}\n"
            )

        auctions_list = "\n".join(lines)

    await update.message.reply_text(
        f"""🔨 **Subastas Activas**

{auctions_list}

Para pujar: /pujar [id] [cantidad]"""
    )


async def ver_subasta_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ver_subasta command - view auction details."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []
    if not args:
        await update.message.reply_text("📝 Uso: /ver_subasta [id]")
        return

    auction_id = parse_amount(args[0])
    if auction_id is None:
        await update.message.reply_text("❌ ID de subasta inválido.")
        return

    async with get_session() as session:
        auction_repo = AuctionRepository(session)

        # Get auction
        auction = await auction_repo.get_by_id(auction_id)
        if not auction:
            await update.message.reply_text("❌ Subasta no encontrada.")
            return

        # Format status
        status_emoji = {
            AuctionStatus.ACTIVE: "🟢 Activa",
            AuctionStatus.COMPLETED: "✅ Completada",
            AuctionStatus.CANCELLED: "❌ Cancelada",
        }
        status = status_emoji.get(auction.status, "❓ Desconocido")

        # Time info
        if auction.status == AuctionStatus.ACTIVE and auction.ends_at > datetime.utcnow():
            time_left = auction.ends_at - datetime.utcnow()
            hours = int(time_left.total_seconds() / 3600)
            minutes = int((time_left.total_seconds() % 3600) / 60)
            time_str = f"⏱️ Termina en: {hours}h {minutes}m"
        else:
            time_str = "⏱️ Terminada"

        current = auction.current_bid or auction.starting_price
        bidder_name = auction.current_bidder.display_name if auction.current_bidder else "Nadie"

    await update.message.reply_text(
        f"""🔨 **Subasta #{auction.id}**

👤 Vendedor: {auction.seller.display_name}
📝 {auction.description}

💰 Precio inicial: {auction.starting_price} {settings.currency_name}
💰 Puja actual: {current} {settings.currency_name}
👤 Pujador: {bidder_name}

{status}
{time_str}"""
    )


async def cancelar_subasta_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancelar_subasta command - cancel your auction."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        auction_repo = AuctionRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get user's active auction
        auction = await auction_repo.get_active_by_seller(user.id)
        if not auction:
            await update.message.reply_text("❌ No tienes ninguna subasta activa.")
            return

        # Refund current bidder if any
        if auction.current_bidder_id and auction.current_bid:
            await user_repo.update_balance(auction.current_bidder_id, auction.current_bid)

        # Cancel auction
        await auction_repo.cancel(auction.id)

        logger.info(f"Auction cancelled: #{auction.id} by {user.display_name}")

    await update.message.reply_text(
        f"""🔨 **Subasta Cancelada**

Tu subasta #{auction.id} ha sido cancelada.

Nota: La comisión de {AUCTION_FEE} {settings.currency_name} no es reembolsable."""
    )


async def mis_subastas_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mis_subastas command - show your auctions."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        auction_repo = AuctionRepository(session)

        # Get user
        user = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("❌ Debes registrarte primero con /start")
            return

        # Get user's auctions (active and recent)
        auctions = await auction_repo.get_by_seller(user.id, limit=10)

        if not auctions:
            await update.message.reply_text("🔨 No tienes subastas.")
            return

        # Format list
        lines = []
        for auction in auctions:
            status_emoji = {
                AuctionStatus.ACTIVE: "🟢",
                AuctionStatus.COMPLETED: "✅",
                AuctionStatus.CANCELLED: "❌",
            }
            emoji = status_emoji.get(auction.status, "❓")
            current = auction.current_bid or auction.starting_price
            lines.append(
                f"{emoji} #{auction.id} - {auction.description[:30]}...\n"
                f"   💰 {current} {settings.currency_name}"
            )

        auctions_list = "\n".join(lines)

    await update.message.reply_text(
        f"""🔨 **Tus Subastas**

{auctions_list}"""
    )
