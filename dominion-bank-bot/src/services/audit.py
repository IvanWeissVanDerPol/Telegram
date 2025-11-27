"""
Audit Logging Service
Tracks admin actions and important events for security and accountability.
"""
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session
from src.database.models import Base

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Types of auditable actions."""
    # Admin actions
    ADMIN_GIVE = "admin_give"
    ADMIN_REMOVE = "admin_remove"
    ADMIN_SET = "admin_set"
    ADMIN_UNSET = "admin_unset"

    # Database actions
    DB_CLEAN = "db_clean"
    DB_EXPORT = "db_export"
    DB_IMPORT = "db_import"

    # User actions
    USER_BAN = "user_ban"
    USER_UNBAN = "user_unban"

    # BDSM actions
    COLLAR_PLACE = "collar_place"
    COLLAR_RELEASE = "collar_release"
    CONTRACT_CREATE = "contract_create"
    CONTRACT_BREAK = "contract_break"
    AUCTION_CREATE = "auction_create"
    AUCTION_CANCEL = "auction_cancel"
    DUNGEON_LOCK = "dungeon_lock"
    DUNGEON_RELEASE = "dungeon_release"

    # System actions
    BOT_START = "bot_start"
    BOT_STOP = "bot_stop"
    CONFIG_CHANGE = "config_change"
    ERROR = "error"


class AuditLog(Base):
    """Model for audit log entries."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    action = Column(String(50), nullable=False, index=True)
    actor_id = Column(Integer, nullable=True, index=True)  # Telegram user ID
    actor_name = Column(String(100), nullable=True)
    target_id = Column(Integer, nullable=True, index=True)  # Target user ID
    target_name = Column(String(100), nullable=True)
    chat_id = Column(Integer, nullable=True, index=True)
    details = Column(Text, nullable=True)  # JSON data
    ip_address = Column(String(45), nullable=True)


class AuditService:
    """Service for logging and querying audit events."""

    @staticmethod
    async def log(
        action: AuditAction,
        actor_id: Optional[int] = None,
        actor_name: Optional[str] = None,
        target_id: Optional[int] = None,
        target_name: Optional[str] = None,
        chat_id: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Log an audit event.

        Args:
            action: The action type
            actor_id: Telegram ID of the user performing the action
            actor_name: Display name of the actor
            target_id: Telegram ID of the target user (if applicable)
            target_name: Display name of the target
            chat_id: Chat where the action occurred
            details: Additional details as a dictionary
        """
        try:
            async with get_session() as session:
                entry = AuditLog(
                    action=action.value,
                    actor_id=actor_id,
                    actor_name=actor_name,
                    target_id=target_id,
                    target_name=target_name,
                    chat_id=chat_id,
                    details=json.dumps(details) if details else None,
                )
                session.add(entry)
                await session.commit()

                logger.info(
                    f"Audit: {action.value} | "
                    f"actor={actor_id}({actor_name}) | "
                    f"target={target_id}({target_name}) | "
                    f"chat={chat_id}"
                )

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

    @staticmethod
    async def log_admin_action(
        action: AuditAction,
        admin_id: int,
        admin_name: str,
        target_id: Optional[int] = None,
        target_name: Optional[str] = None,
        amount: Optional[int] = None,
        reason: Optional[str] = None,
        chat_id: Optional[int] = None,
    ) -> None:
        """
        Convenience method for logging admin actions.
        """
        details = {}
        if amount is not None:
            details["amount"] = amount
        if reason:
            details["reason"] = reason

        await AuditService.log(
            action=action,
            actor_id=admin_id,
            actor_name=admin_name,
            target_id=target_id,
            target_name=target_name,
            chat_id=chat_id,
            details=details if details else None,
        )

    @staticmethod
    async def get_logs(
        action: Optional[AuditAction] = None,
        actor_id: Optional[int] = None,
        target_id: Optional[int] = None,
        chat_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        """
        Query audit logs with filters.

        Returns:
            List of AuditLog entries
        """
        from sqlalchemy import select, desc

        async with get_session() as session:
            query = select(AuditLog)

            if action:
                query = query.where(AuditLog.action == action.value)
            if actor_id:
                query = query.where(AuditLog.actor_id == actor_id)
            if target_id:
                query = query.where(AuditLog.target_id == target_id)
            if chat_id:
                query = query.where(AuditLog.chat_id == chat_id)

            query = query.order_by(desc(AuditLog.timestamp))
            query = query.limit(limit).offset(offset)

            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def get_admin_activity(
        admin_id: int,
        days: int = 7,
        limit: int = 100,
    ) -> list[AuditLog]:
        """
        Get recent activity for a specific admin.

        Args:
            admin_id: Telegram ID of the admin
            days: Number of days to look back
            limit: Maximum entries to return

        Returns:
            List of AuditLog entries
        """
        from sqlalchemy import select, desc
        from datetime import timedelta

        async with get_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)

            query = (
                select(AuditLog)
                .where(AuditLog.actor_id == admin_id)
                .where(AuditLog.timestamp >= cutoff)
                .order_by(desc(AuditLog.timestamp))
                .limit(limit)
            )

            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def format_log_entry(entry: AuditLog) -> str:
        """Format an audit log entry for display."""
        timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        actor = entry.actor_name or f"ID:{entry.actor_id}" or "Sistema"
        target = entry.target_name or f"ID:{entry.target_id}" if entry.target_id else "-"

        details_str = ""
        if entry.details:
            try:
                details = json.loads(entry.details)
                details_str = " | " + ", ".join(
                    f"{k}={v}" for k, v in details.items()
                )
            except json.JSONDecodeError:
                details_str = f" | {entry.details}"

        return f"[{timestamp}] {entry.action}: {actor} -> {target}{details_str}"


# Convenience function for quick logging
async def audit_log(
    action: AuditAction,
    actor_id: Optional[int] = None,
    actor_name: Optional[str] = None,
    target_id: Optional[int] = None,
    target_name: Optional[str] = None,
    chat_id: Optional[int] = None,
    details: Optional[dict[str, Any]] = None,
) -> None:
    """Quick access to audit logging."""
    await AuditService.log(
        action=action,
        actor_id=actor_id,
        actor_name=actor_name,
        target_id=target_id,
        target_name=target_name,
        chat_id=chat_id,
        details=details,
    )
