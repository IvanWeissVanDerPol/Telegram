"""
The Phantom Bot - Pending Request Repository
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import and_, func, select

from src.database.models import CollarType, PendingRequest, RequestType
from src.database.repositories.base import BaseRepository


class PendingRequestRepository(BaseRepository[PendingRequest]):
    """Repository for PendingRequest operations."""

    model = PendingRequest

    async def create_collar_request(
        self,
        from_user_id: int,
        to_user_id: int,
        collar_type: CollarType,
        expires_in_minutes: int = 5,
    ) -> PendingRequest:
        """Create a collar request."""
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        request = PendingRequest(
            request_type=RequestType.COLLAR,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            collar_type=collar_type,
            expires_at=expires_at,
        )
        self.session.add(request)
        await self.session.flush()
        return request

    async def get_pending_collar(self, to_user_id: int) -> Optional[PendingRequest]:
        """Get pending collar request for a user."""
        result = await self.session.execute(
            select(PendingRequest).where(
                and_(
                    PendingRequest.to_user_id == to_user_id,
                    PendingRequest.request_type == RequestType.COLLAR,
                    PendingRequest.expires_at > func.now(),
                )
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, request_id: int) -> bool:
        """Delete a pending request."""
        request = await self.session.get(PendingRequest, request_id)
        if request:
            await self.session.delete(request)
            await self.session.flush()
            return True
        return False

    async def clear_expired(self) -> int:
        """Clear expired requests."""
        result = await self.session.execute(
            select(PendingRequest).where(PendingRequest.expires_at <= func.now())
        )
        requests = result.scalars().all()
        for req in requests:
            await self.session.delete(req)
        await self.session.flush()
        return len(requests)

    async def create_contract_request(
        self,
        from_user_id: int,
        to_user_id: int,
        terms: str,
        duration_days: int,
        expires_in_minutes: int = 60,
    ) -> PendingRequest:
        """Create a contract request."""
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        request = PendingRequest(
            request_type=RequestType.CONTRACT,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            terms=terms,
            duration_days=duration_days,
            expires_at=expires_at,
        )
        self.session.add(request)
        await self.session.flush()
        return request

    async def get_pending_contract(self, to_user_id: int) -> Optional[PendingRequest]:
        """Get pending contract request for a user."""
        result = await self.session.execute(
            select(PendingRequest).where(
                and_(
                    PendingRequest.to_user_id == to_user_id,
                    PendingRequest.request_type == RequestType.CONTRACT,
                    PendingRequest.expires_at > func.now(),
                )
            )
        )
        return result.scalar_one_or_none()
