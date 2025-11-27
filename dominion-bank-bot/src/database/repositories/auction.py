"""
The Phantom Bot - Auction Repository
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

from sqlalchemy import and_, desc, func, select

from src.database.models import Auction, AuctionStatus, Bid
from src.database.repositories.base import BaseRepository


class AuctionRepository(BaseRepository[Auction]):
    """Repository for Auction operations."""

    model = Auction

    async def create(
        self,
        seller_id: int,
        starting_price: int,
        hours: int,
        target_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Auction:
        """Create a new auction."""
        ends_at = datetime.now(timezone.utc) + timedelta(hours=hours)
        auction = Auction(
            seller_id=seller_id,
            target_id=target_id,
            description=description,
            starting_price=starting_price,
            ends_at=ends_at,
        )
        self.session.add(auction)
        await self.session.flush()
        return auction

    async def get_all_active(self) -> Sequence[Auction]:
        """Get all active auctions."""
        result = await self.session.execute(
            select(Auction).where(
                and_(
                    Auction.status == AuctionStatus.ACTIVE,
                    Auction.ends_at > func.now(),
                )
            ).order_by(Auction.ends_at)
        )
        return result.scalars().all()

    async def get_active_by_seller(self, seller_id: int) -> Optional[Auction]:
        """Get active auction by seller."""
        result = await self.session.execute(
            select(Auction).where(
                and_(
                    Auction.seller_id == seller_id,
                    Auction.status == AuctionStatus.ACTIVE,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_seller(self, seller_id: int, limit: int = 10) -> Sequence[Auction]:
        """Get auctions by seller."""
        result = await self.session.execute(
            select(Auction)
            .where(Auction.seller_id == seller_id)
            .order_by(desc(Auction.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def place_bid(
        self,
        auction_id: int,
        bidder_id: int,
        amount: int,
    ) -> Optional[Bid]:
        """Place a bid on an auction."""
        auction = await self.get_by_id(auction_id)
        if not auction or auction.status != AuctionStatus.ACTIVE:
            return None

        bid = Bid(
            auction_id=auction_id,
            bidder_id=bidder_id,
            amount=amount,
        )
        self.session.add(bid)

        auction.current_bid = amount
        auction.current_bidder_id = bidder_id

        await self.session.flush()
        return bid

    async def complete(self, auction_id: int) -> bool:
        """Mark auction as completed."""
        auction = await self.get_by_id(auction_id)
        if auction:
            auction.status = AuctionStatus.COMPLETED
            await self.session.flush()
            return True
        return False

    async def cancel(self, auction_id: int) -> bool:
        """Cancel an auction."""
        auction = await self.get_by_id(auction_id)
        if auction and auction.status == AuctionStatus.ACTIVE:
            auction.status = AuctionStatus.CANCELLED
            await self.session.flush()
            return True
        return False

    async def get_expired_active_auctions(self) -> Sequence[Auction]:
        """Get active auctions that have ended."""
        result = await self.session.execute(
            select(Auction).where(
                and_(
                    Auction.status == AuctionStatus.ACTIVE,
                    Auction.ends_at <= func.now(),
                )
            )
        )
        return result.scalars().all()
