"""
The Phantom Bot - Punishment Repository
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

from sqlalchemy import and_, func, or_, select

from src.database.models import Punishment, PunishmentType
from src.database.repositories.base import BaseRepository


class PunishmentRepository(BaseRepository[Punishment]):
    """Repository for Punishment operations."""

    model = Punishment

    async def create(
        self,
        user_id: int,
        punisher_id: int,
        punishment_type: PunishmentType,
        description: Optional[str] = None,
        cost: int = 0,
        expires_in_minutes: Optional[int] = None,
    ) -> Punishment:
        """Create a new punishment."""
        expires_at = None
        if expires_in_minutes:
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)

        punishment = Punishment(
            user_id=user_id,
            punisher_id=punisher_id,
            punishment_type=punishment_type,
            description=description,
            cost=cost,
            expires_at=expires_at,
        )
        self.session.add(punishment)
        await self.session.flush()
        return punishment

    async def get_active_by_user(self, user_id: int) -> Sequence[Punishment]:
        """Get active (non-expired, non-completed) punishments for a user."""
        result = await self.session.execute(
            select(Punishment).where(
                and_(
                    Punishment.user_id == user_id,
                    Punishment.completed == False,
                    or_(
                        Punishment.expires_at.is_(None),
                        Punishment.expires_at > func.now(),
                    ),
                )
            )
        )
        return result.scalars().all()

    async def get_given_by_user(self, punisher_id: int) -> Sequence[Punishment]:
        """Get active punishments given by a user."""
        result = await self.session.execute(
            select(Punishment).where(
                and_(
                    Punishment.punisher_id == punisher_id,
                    Punishment.completed == False,
                    or_(
                        Punishment.expires_at.is_(None),
                        Punishment.expires_at > func.now(),
                    ),
                )
            )
        )
        return result.scalars().all()

    async def complete_punishment(self, punishment_id: int) -> bool:
        """Mark a punishment as completed."""
        punishment = await self.session.get(Punishment, punishment_id)
        if punishment:
            punishment.completed = True
            await self.session.flush()
            return True
        return False
