"""
The Phantom Bot - Transfer Service
Business logic for coin transfers between users.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.models import TransactionType
from src.database.repositories import (
    CooldownRepository,
    TransactionRepository,
    UserRepository,
)

logger = logging.getLogger(__name__)


class TransferError(Enum):
    """Transfer operation error types."""
    SENDER_NOT_FOUND = "sender_not_found"
    RECIPIENT_NOT_FOUND = "recipient_not_found"
    SELF_TRANSFER = "self_transfer"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    COOLDOWN_ACTIVE = "cooldown_active"
    AMOUNT_TOO_LOW = "amount_too_low"
    AMOUNT_TOO_HIGH = "amount_too_high"
    INVALID_AMOUNT = "invalid_amount"


@dataclass
class TransferResult:
    """Result of a transfer operation."""
    success: bool
    error: Optional[TransferError] = None
    cooldown_remaining: Optional[int] = None
    # Data for success case
    sender_balance: Optional[int] = None
    sender_display: Optional[str] = None
    recipient_balance: Optional[int] = None
    recipient_display: Optional[str] = None
    recipient_telegram_id: Optional[int] = None
    amount: Optional[int] = None


class TransferService:
    """Service for handling coin transfers between users."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.tx_repo = TransactionRepository(session)
        self.cooldown_repo = CooldownRepository(session)

    async def transfer(
        self,
        sender_telegram_id: int,
        recipient_username: str,
        amount: int,
    ) -> TransferResult:
        """
        Transfer coins from sender to recipient.

        Args:
            sender_telegram_id: Telegram ID of the sender
            recipient_username: Username of the recipient (with or without @)
            amount: Amount to transfer

        Returns:
            TransferResult with success status and relevant data
        """
        # Validate amount
        if amount < settings.min_transfer_amount:
            return TransferResult(success=False, error=TransferError.AMOUNT_TOO_LOW)

        if amount > settings.max_transfer_amount:
            return TransferResult(success=False, error=TransferError.AMOUNT_TOO_HIGH)

        # Get sender
        sender = await self.user_repo.get_by_telegram_id(sender_telegram_id)
        if not sender:
            return TransferResult(success=False, error=TransferError.SENDER_NOT_FOUND)

        # Check cooldown
        cooldown_expires = await self.cooldown_repo.is_on_cooldown(sender.id, "transfer")
        if cooldown_expires:
            remaining = (cooldown_expires - datetime.now(timezone.utc)).total_seconds()
            return TransferResult(
                success=False,
                error=TransferError.COOLDOWN_ACTIVE,
                cooldown_remaining=int(max(0, remaining)),
            )

        # Get recipient
        recipient = await self.user_repo.get_by_username(recipient_username)
        if not recipient:
            return TransferResult(success=False, error=TransferError.RECIPIENT_NOT_FOUND)

        # Check self-transfer
        if sender.telegram_id == recipient.telegram_id:
            return TransferResult(success=False, error=TransferError.SELF_TRANSFER)

        # Check balance
        if sender.balance < amount:
            return TransferResult(success=False, error=TransferError.INSUFFICIENT_BALANCE)

        # Perform transfer atomically
        await self.user_repo.update_balance(sender.id, -amount)
        await self.user_repo.update_balance(recipient.id, amount)

        # Record transaction
        await self.tx_repo.create(
            sender_id=sender.id,
            recipient_id=recipient.id,
            amount=amount,
            transaction_type=TransactionType.TRANSFER,
        )

        # Set cooldown
        await self.cooldown_repo.set_cooldown(
            sender.id, "transfer", settings.transfer_cooldown
        )

        # Refresh to get updated balances
        await self.session.refresh(sender)
        await self.session.refresh(recipient)

        # Extract values for result
        result = TransferResult(
            success=True,
            sender_balance=sender.balance,
            sender_display=sender.display_name,
            recipient_balance=recipient.balance,
            recipient_display=recipient.display_name,
            recipient_telegram_id=recipient.telegram_id,
            amount=amount,
        )

        logger.info(
            f"Transfer: {result.sender_display} -> {result.recipient_display}: {amount}"
        )

        return result
