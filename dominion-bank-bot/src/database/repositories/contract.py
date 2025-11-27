"""
The Phantom Bot - Contract Repository
"""
from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy import and_, desc, or_, select

from src.database.models import Contract, ContractStatus
from src.database.repositories.base import BaseRepository


class ContractRepository(BaseRepository[Contract]):
    """Repository for Contract operations."""

    model = Contract

    async def create(
        self,
        dom_id: int,
        sub_id: int,
        terms: str,
        ends_at: Optional[datetime] = None,
    ) -> Contract:
        """Create a new contract."""
        contract = Contract(
            dom_id=dom_id,
            sub_id=sub_id,
            terms=terms,
            starts_at=datetime.now(timezone.utc),
            ends_at=ends_at,
            status=ContractStatus.ACTIVE,
        )
        self.session.add(contract)
        await self.session.flush()
        return contract

    async def get_active_between(self, user1_id: int, user2_id: int) -> Optional[Contract]:
        """Get active contract between two users."""
        result = await self.session.execute(
            select(Contract).where(
                and_(
                    or_(
                        and_(Contract.dom_id == user1_id, Contract.sub_id == user2_id),
                        and_(Contract.dom_id == user2_id, Contract.sub_id == user1_id),
                    ),
                    Contract.status == ContractStatus.ACTIVE,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> Sequence[Contract]:
        """Get all contracts for a user (as dom or sub)."""
        result = await self.session.execute(
            select(Contract)
            .where(or_(Contract.dom_id == user_id, Contract.sub_id == user_id))
            .order_by(desc(Contract.created_at))
        )
        return result.scalars().all()

    async def get_active_by_user(self, user_id: int) -> Sequence[Contract]:
        """Get active contracts for a user (as dom or sub)."""
        result = await self.session.execute(
            select(Contract).where(
                and_(
                    or_(Contract.dom_id == user_id, Contract.sub_id == user_id),
                    Contract.status == ContractStatus.ACTIVE,
                )
            )
        )
        return result.scalars().all()

    async def sign(self, contract_id: int) -> bool:
        """Sign (activate) a contract."""
        contract = await self.get_by_id(contract_id)
        if contract and contract.status == ContractStatus.PENDING:
            contract.status = ContractStatus.ACTIVE
            contract.starts_at = datetime.now(timezone.utc)
            await self.session.flush()
            return True
        return False

    async def break_contract(self, contract_id: int, broken_by: int) -> bool:
        """Break a contract."""
        contract = await self.get_by_id(contract_id)
        if contract and contract.status == ContractStatus.ACTIVE:
            contract.status = ContractStatus.BROKEN
            contract.broken_by = broken_by
            await self.session.flush()
            return True
        return False
