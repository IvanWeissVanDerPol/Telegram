"""
The Phantom Bot - Authorization Service
Centralized authorization and permission checking.
"""
import logging
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.repositories import AdminRepository, UserRepository

logger = logging.getLogger(__name__)


@dataclass
class AuthorizationResult:
    """Result of an authorization check."""
    is_authorized: bool
    is_super_admin: bool = False
    is_global_admin: bool = False
    is_group_admin: bool = False
    user_id: Optional[int] = None
    reason: Optional[str] = None


class AuthorizationService:
    """Service for handling authorization and permission checks."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.admin_repo = AdminRepository(session)

    async def check_admin(
        self,
        telegram_id: int,
        group_id: Optional[int] = None,
    ) -> AuthorizationResult:
        """
        Check if a user has admin privileges.

        Checks in order:
        1. Super admin (from config)
        2. Global admin (is_admin flag in database)
        3. Group admin (from Admin table for specific group)

        Args:
            telegram_id: User's Telegram ID
            group_id: Optional group ID for group-specific admin check

        Returns:
            AuthorizationResult with authorization details
        """
        # Check super admin first (from config)
        if settings.is_super_admin(telegram_id):
            return AuthorizationResult(
                is_authorized=True,
                is_super_admin=True,
                is_global_admin=True,
            )

        # Get user from database
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return AuthorizationResult(
                is_authorized=False,
                reason="User not registered",
            )

        # Check global admin flag
        if user.is_admin:
            return AuthorizationResult(
                is_authorized=True,
                is_super_admin=False,
                is_global_admin=True,
                user_id=user.id,
            )

        # Check group-specific admin if group_id provided
        if group_id:
            is_group_admin = await self.admin_repo.is_admin(user.id, group_id)
            if is_group_admin:
                return AuthorizationResult(
                    is_authorized=True,
                    is_super_admin=False,
                    is_global_admin=False,
                    is_group_admin=True,
                    user_id=user.id,
                )

        return AuthorizationResult(
            is_authorized=False,
            user_id=user.id,
            reason="Insufficient permissions",
        )

    async def require_admin(
        self,
        telegram_id: int,
        group_id: Optional[int] = None,
    ) -> AuthorizationResult:
        """
        Check admin authorization and raise if not authorized.

        Same as check_admin but intended for use where authorization is required.

        Args:
            telegram_id: User's Telegram ID
            group_id: Optional group ID for group-specific admin check

        Returns:
            AuthorizationResult (always authorized, or raises)

        Raises:
            PermissionError: If user is not authorized
        """
        result = await self.check_admin(telegram_id, group_id)
        if not result.is_authorized:
            raise PermissionError(result.reason or "Not authorized")
        return result

    async def require_super_admin(self, telegram_id: int) -> AuthorizationResult:
        """
        Check that user is a super admin.

        Args:
            telegram_id: User's Telegram ID

        Returns:
            AuthorizationResult (always super admin, or raises)

        Raises:
            PermissionError: If user is not a super admin
        """
        if not settings.is_super_admin(telegram_id):
            raise PermissionError("Super admin privileges required")

        return AuthorizationResult(
            is_authorized=True,
            is_super_admin=True,
            is_global_admin=True,
        )

    async def is_registered(self, telegram_id: int) -> bool:
        """Check if a user is registered in the system."""
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        return user is not None

    async def get_user_id(self, telegram_id: int) -> Optional[int]:
        """Get internal user ID from Telegram ID."""
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        return user.id if user else None
