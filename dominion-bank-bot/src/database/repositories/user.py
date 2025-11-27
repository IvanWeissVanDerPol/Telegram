"""
The Phantom Bot - User Repository
"""
import logging
from typing import Optional, Sequence

from sqlalchemy import desc, func, select, update

from src.database.models import User, UserStatus
from src.database.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for User operations."""

    model = User

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username (case-insensitive)."""
        username = username.lstrip("@").lower()
        result = await self.session.execute(
            select(User).where(func.lower(User.username) == username)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        default_balance: int = 0,
    ) -> tuple[User, bool]:
        """Get existing user or create new one. Returns (user, created)."""
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            updated = False
            if username and user.username != username:
                user.username = username
                updated = True
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if last_name and user.last_name != last_name:
                user.last_name = last_name
                updated = True
            if updated:
                await self.session.flush()
            return user, False

        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            balance=default_balance,
        )
        self.session.add(user)
        await self.session.flush()
        logger.info(f"Created new user: {user}")
        return user, True

    async def update_balance(
        self,
        user_id: int,
        amount: int,
        allow_negative: bool = False,
    ) -> bool:
        """Update user balance atomically. Returns True if successful."""
        user = await self.session.get(User, user_id)
        if not user:
            return False

        new_balance = user.balance + amount
        if not allow_negative and new_balance < 0:
            return False

        user.balance = new_balance
        await self.session.flush()
        return True

    async def get_ranking(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[User]:
        """Get users sorted by balance (descending)."""
        result = await self.session.execute(
            select(User)
            .where(User.status == UserStatus.ACTIVE)
            .order_by(desc(User.balance))
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_rank(self, telegram_id: int) -> Optional[int]:
        """Get user's rank in the leaderboard."""
        subquery = (
            select(
                User.telegram_id,
                func.row_number()
                .over(order_by=desc(User.balance))
                .label("rank"),
            )
            .where(User.status == UserStatus.ACTIVE)
            .subquery()
        )

        result = await self.session.execute(
            select(subquery.c.rank).where(subquery.c.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def count_active_users(self) -> int:
        """Count total active users."""
        result = await self.session.execute(
            select(func.count(User.id)).where(User.status == UserStatus.ACTIVE)
        )
        return result.scalar_one()

    async def set_admin(self, user_id: int, is_admin: bool) -> bool:
        """Set user admin status."""
        result = await self.session.execute(
            update(User).where(User.id == user_id).values(is_admin=is_admin)
        )
        return result.rowcount > 0

    async def get_all(self) -> Sequence[User]:
        """Get all users."""
        result = await self.session.execute(
            select(User).order_by(desc(User.balance))
        )
        return result.scalars().all()

    async def create_placeholder(
        self,
        username: str,
        first_name: Optional[str] = None,
        balance: int = 0,
    ) -> User:
        """Create a placeholder user (imported from Excel, no telegram_id yet)."""
        user = User(
            telegram_id=0,
            username=username,
            first_name=first_name,
            balance=balance,
        )
        self.session.add(user)
        await self.session.flush()
        return user
