"""
The Phantom Bot - Cooldown Repository
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import and_, func, select

from src.database.models import Cooldown
from src.database.repositories.base import BaseRepository


class CooldownRepository(BaseRepository[Cooldown]):
    """Repository for Cooldown operations."""

    model = Cooldown

    async def is_on_cooldown(self, user_id: int, action: str) -> Optional[datetime]:
        """Check if user is on cooldown. Returns expiry time if on cooldown."""
        result = await self.session.execute(
            select(Cooldown).where(
                and_(
                    Cooldown.user_id == user_id,
                    Cooldown.action == action,
                    Cooldown.expires_at > func.now(),
                )
            )
        )
        cooldown = result.scalar_one_or_none()
        return cooldown.expires_at if cooldown else None

    async def set_cooldown(
        self,
        user_id: int,
        action: str,
        duration_seconds: int,
    ) -> Cooldown:
        """Set a cooldown for a user action."""
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)

        result = await self.session.execute(
            select(Cooldown).where(
                and_(Cooldown.user_id == user_id, Cooldown.action == action)
            )
        )
        cooldown = result.scalar_one_or_none()

        if cooldown:
            cooldown.expires_at = expires_at
        else:
            cooldown = Cooldown(
                user_id=user_id,
                action=action,
                expires_at=expires_at,
            )
            self.session.add(cooldown)

        await self.session.flush()
        return cooldown

    async def clear_expired(self) -> int:
        """Clear expired cooldowns. Returns count of cleared."""
        result = await self.session.execute(
            select(Cooldown).where(Cooldown.expires_at <= func.now())
        )
        cooldowns = result.scalars().all()
        for cd in cooldowns:
            await self.session.delete(cd)
        return len(cooldowns)
