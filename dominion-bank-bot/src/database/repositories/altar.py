"""
The Phantom Bot - Altar Repository
"""
from typing import Sequence

from sqlalchemy import and_, desc, func, select

from src.database.models import Transaction, TransactionType, User
from src.database.repositories.base import BaseRepository


class AltarRepository(BaseRepository[Transaction]):
    """Repository for Altar (tribute tracking) operations."""

    model = Transaction

    async def add_tribute(
        self,
        recipient_id: int,
        from_user_id: int,
        amount: int,
    ) -> None:
        """Record a tribute. Updates totals for tracking."""
        # For now, tributes are tracked in transactions table
        # This method is a placeholder for future tribute-specific tracking
        pass

    async def get_total_received(self, user_id: int) -> int:
        """Get total tributes received by user."""
        result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                and_(
                    Transaction.recipient_id == user_id,
                    Transaction.transaction_type == TransactionType.TRIBUTE,
                )
            )
        )
        return result.scalar_one()

    async def get_total_given(self, user_id: int) -> int:
        """Get total tributes given by user."""
        result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                and_(
                    Transaction.sender_id == user_id,
                    Transaction.transaction_type == TransactionType.TRIBUTE,
                )
            )
        )
        return result.scalar_one()

    async def get_devotee_count(self, user_id: int) -> int:
        """Get count of unique devotees (people who have paid tribute)."""
        result = await self.session.execute(
            select(func.count(func.distinct(Transaction.sender_id))).where(
                and_(
                    Transaction.recipient_id == user_id,
                    Transaction.transaction_type == TransactionType.TRIBUTE,
                )
            )
        )
        return result.scalar_one()

    async def get_top_receivers(self, limit: int = 10) -> Sequence[tuple]:
        """Get top tribute receivers."""
        result = await self.session.execute(
            select(User, func.sum(Transaction.amount).label("total"))
            .join(Transaction, Transaction.recipient_id == User.id)
            .where(Transaction.transaction_type == TransactionType.TRIBUTE)
            .group_by(User.id)
            .order_by(desc("total"))
            .limit(limit)
        )
        return result.all()

    async def get_devotees(self, user_id: int, limit: int = 10) -> Sequence[tuple]:
        """Get top devotees for a user."""
        result = await self.session.execute(
            select(User, func.sum(Transaction.amount).label("total"))
            .join(Transaction, Transaction.sender_id == User.id)
            .where(
                and_(
                    Transaction.recipient_id == user_id,
                    Transaction.transaction_type == TransactionType.TRIBUTE,
                )
            )
            .group_by(User.id)
            .order_by(desc("total"))
            .limit(limit)
        )
        return result.all()
