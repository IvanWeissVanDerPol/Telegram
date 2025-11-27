"""
The Phantom Bot - Transaction Repository
"""
from typing import Optional, Sequence

from sqlalchemy import desc, func, or_, select

from src.database.models import Transaction, TransactionType
from src.database.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction operations."""

    model = Transaction

    async def create(
        self,
        recipient_id: int,
        amount: int,
        transaction_type: TransactionType,
        sender_id: Optional[int] = None,
        admin_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Transaction:
        """Create a new transaction record."""
        transaction = Transaction(
            sender_id=sender_id,
            recipient_id=recipient_id,
            amount=amount,
            transaction_type=transaction_type,
            admin_id=admin_id,
            description=description,
        )
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_user_history(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[Transaction]:
        """Get transaction history for a user."""
        result = await self.session.execute(
            select(Transaction)
            .where(
                or_(
                    Transaction.sender_id == user_id,
                    Transaction.recipient_id == user_id,
                )
            )
            .order_by(desc(Transaction.created_at))
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def count_user_transactions(self, user_id: int) -> int:
        """Count total transactions for a user."""
        result = await self.session.execute(
            select(func.count(Transaction.id)).where(
                or_(
                    Transaction.sender_id == user_id,
                    Transaction.recipient_id == user_id,
                )
            )
        )
        return result.scalar_one()
