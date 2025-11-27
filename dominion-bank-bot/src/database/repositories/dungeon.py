"""
The Phantom Bot - Dungeon Repository
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

from sqlalchemy import and_, func, select

from src.database.models import Dungeon, DungeonType
from src.database.repositories.base import BaseRepository


class DungeonRepository(BaseRepository[Dungeon]):
    """Repository for Dungeon operations."""

    model = Dungeon

    async def lock(
        self,
        user_id: int,
        locked_by_id: int,
        dungeon_type: DungeonType,
        hours: int,
        reason: Optional[str] = None,
    ) -> Dungeon:
        """Lock a user in dungeon."""
        expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)
        dungeon = Dungeon(
            user_id=user_id,
            locked_by=locked_by_id,
            dungeon_type=dungeon_type,
            reason=reason,
            expires_at=expires_at,
        )
        self.session.add(dungeon)
        await self.session.flush()
        return dungeon

    async def get_by_user(self, user_id: int) -> Optional[Dungeon]:
        """Get dungeon entry for a user if they're locked."""
        result = await self.session.execute(
            select(Dungeon).where(
                and_(
                    Dungeon.user_id == user_id,
                    Dungeon.expires_at > func.now(),
                )
            )
        )
        return result.scalar_one_or_none()

    async def is_locked(self, user_id: int) -> bool:
        """Check if user is locked in dungeon."""
        dungeon = await self.get_by_user(user_id)
        return dungeon is not None

    async def release(self, user_id: int) -> bool:
        """Release a user from dungeon."""
        result = await self.session.execute(
            select(Dungeon).where(Dungeon.user_id == user_id)
        )
        dungeon = result.scalar_one_or_none()
        if dungeon:
            await self.session.delete(dungeon)
            await self.session.flush()
            return True
        return False

    async def get_all_locked(self) -> Sequence[Dungeon]:
        """Get all currently locked users."""
        result = await self.session.execute(
            select(Dungeon).where(Dungeon.expires_at > func.now())
        )
        return result.scalars().all()

    async def clear_expired(self) -> int:
        """Release all users with expired dungeon time."""
        result = await self.session.execute(
            select(Dungeon).where(Dungeon.expires_at <= func.now())
        )
        dungeons = result.scalars().all()
        for d in dungeons:
            await self.session.delete(d)
        return len(dungeons)
