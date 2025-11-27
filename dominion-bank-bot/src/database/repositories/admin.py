"""
The Phantom Bot - Admin Repository
"""
from typing import Optional

from sqlalchemy import and_, select

from src.database.models import Admin
from src.database.repositories.base import BaseRepository


class AdminRepository(BaseRepository[Admin]):
    """Repository for Admin operations."""

    model = Admin

    async def is_admin(self, user_id: int, group_id: int) -> bool:
        """Check if user is admin in a group."""
        result = await self.session.execute(
            select(Admin).where(
                and_(Admin.user_id == user_id, Admin.group_id == group_id)
            )
        )
        return result.scalar_one_or_none() is not None

    async def add_admin(
        self,
        user_id: int,
        group_id: int,
        granted_by: Optional[int] = None,
    ) -> Admin:
        """Add a user as admin in a group."""
        admin = Admin(
            user_id=user_id,
            group_id=group_id,
            granted_by=granted_by,
        )
        self.session.add(admin)
        await self.session.flush()
        return admin

    async def remove_admin(self, user_id: int, group_id: int) -> bool:
        """Remove admin status from user in a group."""
        result = await self.session.execute(
            select(Admin).where(
                and_(Admin.user_id == user_id, Admin.group_id == group_id)
            )
        )
        admin = result.scalar_one_or_none()
        if admin:
            await self.session.delete(admin)
            await self.session.flush()
            return True
        return False
