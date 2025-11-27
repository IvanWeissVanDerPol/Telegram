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
from src.utils.helpers import extract_username, parse_amount
from src.utils.messages import (
    DIVIDER,
    DIVIDER_LIGHT,
    EMOJI_BALANCE,
    EMOJI_ERROR,
    EMOJI_INFO,
    EMOJI_SUCCESS,
    format_currency,
)

logger = logging.getLogger(__name__)

# Custom emojis for auction system
EMOJI_AUCTION = "🔨"
EMOJI_BID = "💰"
EMOJI_TIMER = "⏱️"
EMOJI_SELLER = "👤"
EMOJI_TARGET = "🎯"
EMOJI_CROWN = "👑"

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
            f"""{EMOJI_AUCTION} **Crear Subasta**

{DIVIDER_LIGHT}

{EMOJI_INFO} **Uso:** /subasta @usuario precio [descripcion]

{EMOJI_BID} **Precio minimo:** {format_currency(MIN_BID)}
{EMOJI_BID} **Comision:** {format_currency(AUCTION_FEE)}
{EMOJI_TIMER} **Duracion:** {DEFAULT_AUCTION_HOURS} horas

{DIVIDER_LIGHT}

**Ejemplo:** /subasta @sumiso 100 Servicio por 1 hora"""
        )
        return

    # Parse arguments: @username price [description]
    target_username = extract_username(args[0])
    starting_price = parse_amount(args[1]) if len(args) > 1 else None
    description = " ".join(args[2:]) if len(args) > 2 else None

    if not target_username:
        await update.message.reply_text(
            f"{EMOJI_ERROR} Debes especificar un usuario (@usuario)."
        )
        return

    if starting_price is None or starting_price < MIN_BID:
        await update.message.reply_text(
            f"""{EMOJI_ERROR} **Precio Invalido**

{DIVIDER_LIGHT}

{EMOJI_BID} El precio minimo es {format_currency(MIN_BID)}"""
        )
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        auction_repo = AuctionRepository(session)
        tx_repo = TransactionRepository(session)

        # Get seller
        seller = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not seller:
            await update.message.reply_text(f"{EMOJI_ERROR} Debes registrarte primero con /start")
            return

        # Get target user
        target = await user_repo.get_by_username(target_username)
        if not target:
            await update.message.reply_text(f"{EMOJI_ERROR} Usuario @{target_username} no encontrado.")
            return

        # Can't auction yourself
        if seller.id == target.id:
            await update.message.reply_text(f"{EMOJI_ERROR} No puedes subastarte a ti mismo.")
            return

        # Check balance for fee
        if seller.balance < AUCTION_FEE:
            await update.message.reply_text(
                f"""{EMOJI_ERROR} **Saldo Insuficiente**

{DIVIDER_LIGHT}

{EMOJI_BALANCE} Tu saldo: {format_currency(seller.balance)}
{EMOJI_BID} Comision: {format_currency(AUCTION_FEE)}"""
            )
            return

        # Check if user already has an active auction
        existing = await auction_repo.get_active_by_seller(seller.id)
        if existing:
            await update.message.reply_text(
                f"""{EMOJI_ERROR} Ya tienes una subasta activa.

Cancelala primero con /cancelar_subasta"""
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
            description="Comision de subasta",
        )

        # Capture names before leaving session
        seller_name = seller.display_name
        target_name = target.display_name

        # Create auction
        auction = await auction_repo.create(
            seller_id=seller.id,
            starting_price=starting_price,
            hours=DEFAULT_AUCTION_HOURS,
            target_id=target.id,
            description=description,
        )

        logger.info(f"Auction created: {seller_name} auctioning {target_name} for {starting_price}")

    # Build description line
    desc_line = f"\n\n📝 _{description}_" if description else ""

    await update.message.reply_text(
        f"""{EMOJI_AUCTION} **Nueva Subasta** {EMOJI_CROWN}

{DIVIDER}

{EMOJI_SELLER} **Vendedor:** {seller_name}
{EMOJI_TARGET} **Subastado:** {target_name}{desc_line}

{DIVIDER_LIGHT}

🏷️ **ID:** #{auction.id}
{EMOJI_BID} **Precio inicial:** {format_currency(starting_price)}
{EMOJI_TIMER} **Termina en:** {DEFAULT_AUCTION_HOURS} horas

{DIVIDER_LIGHT}

{EMOJI_INFO} Para pujar: /pujar {auction.id} [cantidad]"""
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
            f"""{EMOJI_AUCTION} **Pujar en Subasta**

{DIVIDER_LIGHT}

{EMOJI_INFO} **Uso:** /pujar [id] [cantidad]

**Ejemplo:** /pujar 1 150"""
        )
        return

    auction_id = parse_amount(args[0])
    bid_amount = parse_amount(args[1])

    if auction_id is None:
        await update.message.reply_text(f"{EMOJI_ERROR} ID de subasta invalido.")
        return

    if bid_amount is None or bid_amount < MIN_BID:
        await update.message.reply_text(
            f"{EMOJI_ERROR} La puja minima es {format_currency(MIN_BID)}."
        )
        return

    async with get_session() as session:
        user_repo = UserRepository(session)
        auction_repo = AuctionRepository(session)

        # Get bidder
        bidder = await user_repo.get_by_telegram_id(update.effective_user.id)
        if not bidder:
            await update.message.reply_text(f"{EMOJI_ERROR} Debes registrarte primero con /start")
            return

        # Get auction
        auction = await auction_repo.get_by_id(auction_id)
        if not auction:
            await update.message.reply_text(f"{EMOJI_ERROR} Subasta no encontrada.")
            return

        # Check if auction is still active
        if auction.status != AuctionStatus.ACTIVE:
            await update.message.reply_text(f"{EMOJI_ERROR} Esta subasta ya no esta activa.")
            return

        # Check if expired
        if auction.ends_at < datetime.utcnow():
            await update.message.reply_text(f"{EMOJI_ERROR} Esta subasta ya termino.")
            return

        # Check if bidding on own auction
        if auction.seller_id == bidder.id:
            await update.message.reply_text(f"{EMOJI_ERROR} No puedes pujar en tu propia subasta.")
            return

        # Check balance
        if bidder.balance < bid_amount:
            await update.message.reply_text(
                f"""{EMOJI_ERROR} **Saldo Insuficiente**

{DIVIDER_LIGHT}

{EMOJI_BALANCE} Tu saldo: {format_currency(bidder.balance)}
{EMOJI_BID} Puja: {format_currency(bid_amount)}"""
            )
            return

        # Check if bid is higher than current
        min_required = max(auction.starting_price, (auction.current_bid or 0) + 1)
        if bid_amount < min_required:
            await update.message.reply_text(
                f"{EMOJI_ERROR} Tu puja debe ser al menos {format_currency(min_required)}."
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

        # Capture info before leaving session
        bidder_name = bidder.display_name
        target_name = auction.target.display_name if auction.target else None
        description = auction.description

        logger.info(f"Bid: {bidder_name} bid {bid_amount} on auction #{auction.id}")

    # Build target line
    target_line = f"\n{EMOJI_TARGET} **Subastado:** {target_name}" if target_name else ""
    desc_line = f"\n📝 _{description}_" if description else ""

    await update.message.reply_text(
        f"""{EMOJI_AUCTION} **Puja Realizada** {EMOJI_SUCCESS}

{DIVIDER}

🏷️ Subasta #{auction_id}{target_line}{desc_line}

{DIVIDER_LIGHT}

{EMOJI_BID} **Tu puja:** {format_currency(bid_amount)}

{DIVIDER_LIGHT}

{EMOJI_CROWN} Eres el pujador mas alto!"""
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
            await update.message.reply_text(
                f"""{EMOJI_AUCTION} **Subastas Activas**

{DIVIDER_LIGHT}

{EMOJI_INFO} No hay subastas activas.

Crea una con /subasta @usuario precio"""
            )
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
            target_info = f" {EMOJI_TARGET} {auction.target.display_name}" if auction.target else ""
            lines.append(
                f"{EMOJI_AUCTION} **#{auction.id}**{target_info}\n"
                f"   {EMOJI_SELLER} {auction.seller.display_name}\n"
                f"   {EMOJI_BID} {format_currency(current)} | {EMOJI_TIMER} {time_str}"
            )

        auctions_list = "\n\n".join(lines)

    await update.message.reply_text(
        f"""{EMOJI_AUCTION} **Subastas Activas** {EMOJI_CROWN}

{DIVIDER}

{auctions_list}

{DIVIDER_LIGHT}

{EMOJI_INFO} Para pujar: /pujar [id] [cantidad]"""
    )


async def ver_subasta_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ver_subasta command - view auction details."""
    if not settings.enable_bdsm_commands:
        return

    if not update.effective_user or not update.message:
        return

    args = context.args if context.args else []
    if not args:
        await update.message.reply_text(
            f"""{EMOJI_AUCTION} **Ver Subasta**

{DIVIDER_LIGHT}

{EMOJI_INFO} **Uso:** /ver_subasta [id]"""
        )
        return

    auction_id = parse_amount(args[0])
    if auction_id is None:
        await update.message.reply_text(f"{EMOJI_ERROR} ID de subasta invalido.")
        return

    async with get_session() as session:
        auction_repo = AuctionRepository(session)

        # Get auction
        auction = await auction_repo.get_by_id(auction_id)
        if not auction:
            await update.message.reply_text(f"{EMOJI_ERROR} Subasta no encontrada.")
            return

        # Format status
        status_emoji = {
            AuctionStatus.ACTIVE: "🟢 Activa",
            AuctionStatus.COMPLETED: "✅ Completada",
            AuctionStatus.CANCELLED: "❌ Cancelada",
        }
        status = status_emoji.get(auction.status, "? Desconocido")

        # Time info
        if auction.status == AuctionStatus.ACTIVE and auction.ends_at > datetime.utcnow():
            time_left = auction.ends_at - datetime.utcnow()
            hours = int(time_left.total_seconds() / 3600)
            minutes = int((time_left.total_seconds() % 3600) / 60)
            time_str = f"{EMOJI_TIMER} Termina en: {hours}h {minutes}m"
        else:
            time_str = f"{EMOJI_TIMER} Terminada"

        current = auction.current_bid or auction.starting_price
        bidder_name = auction.current_bidder.display_name if auction.current_bidder else "Nadie"
        seller_name = auction.seller.display_name
        target_name = auction.target.display_name if auction.target else None
        description = auction.description
        starting_price = auction.starting_price

    # Build target line
    target_line = f"\n{EMOJI_TARGET} **Subastado:** {target_name}" if target_name else ""
    desc_line = f"\n\n📝 _{description}_" if description else ""

    await update.message.reply_text(
        f"""{EMOJI_AUCTION} **Subasta #{auction_id}** {EMOJI_CROWN}

{DIVIDER}

{EMOJI_SELLER} **Vendedor:** {seller_name}{target_line}{desc_line}

{DIVIDER_LIGHT}

{EMOJI_BID} **Precio inicial:** {format_currency(starting_price)}
{EMOJI_BID} **Puja actual:** {format_currency(current)}
{EMOJI_SELLER} **Pujador:** {bidder_name}

{DIVIDER_LIGHT}

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
            await update.message.reply_text(f"{EMOJI_ERROR} Debes registrarte primero con /start")
            return

        # Get user's active auction
        auction = await auction_repo.get_active_by_seller(user.id)
        if not auction:
            await update.message.reply_text(f"{EMOJI_ERROR} No tienes ninguna subasta activa.")
            return

        # Capture info before changes
        auction_id = auction.id
        target_name = auction.target.display_name if auction.target else None
        user_name = user.display_name

        # Refund current bidder if any
        if auction.current_bidder_id and auction.current_bid:
            await user_repo.update_balance(auction.current_bidder_id, auction.current_bid)

        # Cancel auction
        await auction_repo.cancel(auction.id)

        logger.info(f"Auction cancelled: #{auction_id} by {user_name}")

    # Build target line
    target_line = f"\n{EMOJI_TARGET} **Subastado:** {target_name}" if target_name else ""

    await update.message.reply_text(
        f"""{EMOJI_AUCTION} **Subasta Cancelada**

{DIVIDER}

🏷️ Subasta #{auction_id} cancelada{target_line}

{DIVIDER_LIGHT}

{EMOJI_INFO} La comision de {format_currency(AUCTION_FEE)} no es reembolsable."""
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
            await update.message.reply_text(f"{EMOJI_ERROR} Debes registrarte primero con /start")
            return

        user_name = user.display_name

        # Get user's auctions (active and recent)
        auctions = await auction_repo.get_by_seller(user.id, limit=10)

        if not auctions:
            await update.message.reply_text(
                f"""{EMOJI_AUCTION} **Tus Subastas**

{DIVIDER_LIGHT}

{EMOJI_INFO} No tienes subastas.

Crea una con /subasta @usuario precio"""
            )
            return

        # Format list
        lines = []
        for auction in auctions:
            status_emoji = {
                AuctionStatus.ACTIVE: "🟢",
                AuctionStatus.COMPLETED: "✅",
                AuctionStatus.CANCELLED: "❌",
            }
            emoji = status_emoji.get(auction.status, "?")
            current = auction.current_bid or auction.starting_price
            target_info = f" {EMOJI_TARGET} {auction.target.display_name}" if auction.target else ""
            lines.append(
                f"{emoji} **#{auction.id}**{target_info}\n"
                f"   {EMOJI_BID} {format_currency(current)}"
            )

        auctions_list = "\n\n".join(lines)

    await update.message.reply_text(
        f"""{EMOJI_AUCTION} **Subastas de {user_name}**

{DIVIDER}

{auctions_list}"""
    )
