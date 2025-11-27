"""
The Phantom Bot - Collar Repository
"""
from typing import Optional, Sequence

from sqlalchemy import select

from src.database.models import Collar, CollarType
from src.database.repositories.base import BaseRepository


class CollarRepository(BaseRepository[Collar]):
    """Repository for Collar operations."""

    model = Collar

    async def get_by_sub(self, sub_id: int) -> Optional[Collar]:
        """Get collar by sub's user ID."""
        result = await self.session.execute(
            select(Collar).where(Collar.sub_id == sub_id)
        )
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: int) -> Sequence[Collar]:
        """Get all collars owned by a user."""
        result = await self.session.execute(
            select(Collar).where(Collar.owner_id == owner_id)
        )
        return result.scalars().all()

    async def create(
        self,
        owner_id: int,
        sub_id: int,
        collar_type: CollarType = CollarType.FORMAL,
        public: bool = True,
    ) -> Collar:
        """Create a new collar relationship."""
        collar = Collar(
            owner_id=owner_id,
            sub_id=sub_id,
            collar_type=collar_type,
            public=public,
        )
        self.session.add(collar)
        await self.session.flush()
        return collar

    async def remove(self, collar_id: int) -> bool:
        """Remove a collar."""
        collar = await self.session.get(Collar, collar_id)
        if collar:
            await self.session.delete(collar)
            return True
        return False

    async def remove_by_sub(self, sub_id: int) -> bool:
        """Remove collar by sub ID."""
        collar = await self.get_by_sub(sub_id)
        if collar:
            await self.session.delete(collar)
            await self.session.flush()
            return True
        return False

    async def is_collared(self, sub_id: int) -> bool:
        """Check if user is collared."""
        collar = await self.get_by_sub(sub_id)
        return collar is not None
