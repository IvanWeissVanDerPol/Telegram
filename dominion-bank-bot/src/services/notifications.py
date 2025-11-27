"""
Notification Service
Handles sending notifications to users for various events.
"""
import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Optional

from telegram import Bot
from telegram.error import TelegramError

from src.config import settings

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Types of notifications."""
    # Collar notifications
    COLLAR_REQUEST = "collar_request"
    COLLAR_ACCEPTED = "collar_accepted"
    COLLAR_REJECTED = "collar_rejected"
    COLLAR_RELEASED = "collar_released"
    COLLAR_FREEDOM_REQUEST = "collar_freedom_request"

    # Contract notifications
    CONTRACT_OFFER = "contract_offer"
    CONTRACT_SIGNED = "contract_signed"
    CONTRACT_REJECTED = "contract_rejected"
    CONTRACT_BROKEN = "contract_broken"
    CONTRACT_EXPIRING = "contract_expiring"

    # Auction notifications
    AUCTION_OUTBID = "auction_outbid"
    AUCTION_WON = "auction_won"
    AUCTION_LOST = "auction_lost"
    AUCTION_ENDING = "auction_ending"
    AUCTION_CANCELLED = "auction_cancelled"

    # Dungeon notifications
    DUNGEON_LOCKED = "dungeon_locked"
    DUNGEON_RELEASED = "dungeon_released"
    DUNGEON_EXPIRING = "dungeon_expiring"

    # Transfer notifications
    TRANSFER_RECEIVED = "transfer_received"
    TRIBUTE_RECEIVED = "tribute_received"

    # System notifications
    WELCOME = "welcome"
    ADMIN_MESSAGE = "admin_message"


# Notification templates
TEMPLATES = {
    NotificationType.COLLAR_REQUEST: (
        "{actor_name} quiere ponerte un collar.\n"
        "Usa /aceptar_collar o /rechazar_collar para responder."
    ),
    NotificationType.COLLAR_ACCEPTED: (
        "{target_name} ha aceptado tu collar."
    ),
    NotificationType.COLLAR_REJECTED: (
        "{target_name} ha rechazado tu collar."
    ),
    NotificationType.COLLAR_RELEASED: (
        "{actor_name} te ha liberado del collar."
    ),
    NotificationType.COLLAR_FREEDOM_REQUEST: (
        "{actor_name} suplica por su libertad."
    ),

    NotificationType.CONTRACT_OFFER: (
        "{actor_name} te ha enviado un contrato.\n"
        "Usa /ver_contrato {contract_id} para verlo."
    ),
    NotificationType.CONTRACT_SIGNED: (
        "{target_name} ha firmado tu contrato."
    ),
    NotificationType.CONTRACT_REJECTED: (
        "{target_name} ha rechazado tu contrato."
    ),
    NotificationType.CONTRACT_BROKEN: (
        "{actor_name} ha roto el contrato."
    ),
    NotificationType.CONTRACT_EXPIRING: (
        "Tu contrato con {target_name} expira en 24 horas."
    ),

    NotificationType.AUCTION_OUTBID: (
        "Has sido superado en la subasta de {target_name}.\n"
        "La puja actual es {amount} {currency}."
    ),
    NotificationType.AUCTION_WON: (
        "Has ganado la subasta de {target_name} por {amount} {currency}."
    ),
    NotificationType.AUCTION_LOST: (
        "Has perdido la subasta de {target_name}."
    ),
    NotificationType.AUCTION_ENDING: (
        "La subasta de {target_name} termina en 1 hora."
    ),
    NotificationType.AUCTION_CANCELLED: (
        "La subasta de {target_name} ha sido cancelada."
    ),

    NotificationType.DUNGEON_LOCKED: (
        "{actor_name} te ha encerrado en el calabozo por {hours} horas."
    ),
    NotificationType.DUNGEON_RELEASED: (
        "Has sido liberado del calabozo."
    ),
    NotificationType.DUNGEON_EXPIRING: (
        "Seras liberado del calabozo en 1 hora."
    ),

    NotificationType.TRANSFER_RECEIVED: (
        "Has recibido {amount} {currency} de {actor_name}."
    ),
    NotificationType.TRIBUTE_RECEIVED: (
        "{actor_name} te ha pagado un tributo de {amount} {currency}."
    ),

    NotificationType.WELCOME: (
        "Bienvenido a {bot_name}!\n"
        "Has recibido {amount} {currency} para empezar.\n"
        "Usa /help para ver los comandos disponibles."
    ),
    NotificationType.ADMIN_MESSAGE: (
        "Mensaje del administrador:\n{message}"
    ),
}


class NotificationService:
    """Service for sending notifications to users."""

    def __init__(self, bot: Optional[Bot] = None):
        self.bot = bot
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    def set_bot(self, bot: Bot) -> None:
        """Set the bot instance for sending messages."""
        self.bot = bot

    async def send(
        self,
        user_id: int,
        notification_type: NotificationType,
        **kwargs
    ) -> bool:
        """
        Send a notification to a user.

        Args:
            user_id: Telegram user ID
            notification_type: Type of notification
            **kwargs: Variables for template substitution

        Returns:
            bool: True if sent successfully
        """
        if not self.bot:
            logger.error("Bot not set for notification service")
            return False

        # Get template
        template = TEMPLATES.get(notification_type)
        if not template:
            logger.error(f"No template for notification type: {notification_type}")
            return False

        # Add common variables
        kwargs.setdefault("currency", settings.currency_name)
        kwargs.setdefault("bot_name", settings.bot_name)

        # Format message
        try:
            message = template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            return False

        # Send message
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
            )
            logger.info(f"Notification sent: {notification_type} -> {user_id}")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send notification to {user_id}: {e}")
            return False

    async def send_to_admins(
        self,
        message: str,
        exclude_id: Optional[int] = None,
    ) -> int:
        """
        Send a message to all super admins.

        Args:
            message: The message to send
            exclude_id: Admin ID to exclude (e.g., the sender)

        Returns:
            int: Number of admins notified
        """
        if not self.bot:
            return 0

        count = 0
        for admin_id in settings.super_admin_ids:
            if exclude_id and admin_id == exclude_id:
                continue

            try:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text=message,
                )
                count += 1
            except TelegramError as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")

        return count

    async def notify_transfer(
        self,
        recipient_id: int,
        sender_name: str,
        amount: int,
    ) -> bool:
        """Notify user of received transfer."""
        return await self.send(
            user_id=recipient_id,
            notification_type=NotificationType.TRANSFER_RECEIVED,
            actor_name=sender_name,
            amount=amount,
        )

    async def notify_collar_request(
        self,
        target_id: int,
        owner_name: str,
    ) -> bool:
        """Notify user of collar request."""
        return await self.send(
            user_id=target_id,
            notification_type=NotificationType.COLLAR_REQUEST,
            actor_name=owner_name,
        )

    async def notify_auction_outbid(
        self,
        user_id: int,
        target_name: str,
        current_bid: int,
    ) -> bool:
        """Notify user they've been outbid."""
        return await self.send(
            user_id=user_id,
            notification_type=NotificationType.AUCTION_OUTBID,
            target_name=target_name,
            amount=current_bid,
        )

    async def notify_welcome(
        self,
        user_id: int,
        initial_balance: int,
    ) -> bool:
        """Send welcome notification to new user."""
        return await self.send(
            user_id=user_id,
            notification_type=NotificationType.WELCOME,
            amount=initial_balance,
        )


# Global notification service instance
notification_service = NotificationService()


def get_notification_service() -> NotificationService:
    """Get the global notification service instance."""
    return notification_service
