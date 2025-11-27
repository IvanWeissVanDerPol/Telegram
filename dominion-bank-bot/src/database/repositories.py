"""
The Phantom Bot - Database Repositories
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Sequence

from sqlalchemy import and_, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
    Admin,
    Altar,
    Auction,
    AuctionStatus,
    Bid,
    Collar,
    CollarType,
    Contract,
    ContractStatus,
    Cooldown,
    Dungeon,
    DungeonType,
    Kink,
    PendingRequest,
    Profile,
    Punishment,
    PunishmentType,
    RequestType,
    Transaction,
    TransactionType,
    User,
    UserKink,
    UserLimit,
    UserSettings,
    UserStatus,
)

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username (case-insensitive)."""
        # Remove @ if present
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
            # Update user info if changed
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

        # Create new user
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
        # Subquery to get all users ordered by balance
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

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by internal ID."""
        return await self.session.get(User, user_id)

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
            telegram_id=0,  # Will be updated when user /starts
            username=username,
            first_name=first_name,
            balance=balance,
        )
        self.session.add(user)
        await self.session.flush()
        return user


class TransactionRepository:
    """Repository for Transaction operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        recipient_id: int,
        amount: int,
        transaction_type: TransactionType,
        sender_id: Optional[int] = None,
        admin_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Transaction:
        """Create a new transaction record."""
        transaction = Transaction(
            sender_id=sender_id,
            recipient_id=recipient_id,
            amount=amount,
            transaction_type=transaction_type,
            admin_id=admin_id,
            description=description,
        )
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_user_history(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[Transaction]:
        """Get transaction history for a user."""
        result = await self.session.execute(
            select(Transaction)
            .where(
                or_(
                    Transaction.sender_id == user_id,
                    Transaction.recipient_id == user_id,
                )
            )
            .order_by(desc(Transaction.created_at))
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def count_user_transactions(self, user_id: int) -> int:
        """Count total transactions for a user."""
        result = await self.session.execute(
            select(func.count(Transaction.id)).where(
                or_(
                    Transaction.sender_id == user_id,
                    Transaction.recipient_id == user_id,
                )
            )
        )
        return result.scalar_one()


class AdminRepository:
    """Repository for Admin operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

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
            return True
        return False


class CooldownRepository:
    """Repository for Cooldown operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

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
        expires_at = datetime.utcnow() + timedelta(seconds=duration_seconds)

        # Update existing or create new
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


# =============================================================================
# BDSM REPOSITORIES
# =============================================================================

class CollarRepository:
    """Repository for Collar operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

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
            return True
        return False

    async def is_collared(self, sub_id: int) -> bool:
        """Check if user is collared."""
        collar = await self.get_by_sub(sub_id)
        return collar is not None


class PendingRequestRepository:
    """Repository for PendingRequest operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_collar_request(
        self,
        from_user_id: int,
        to_user_id: int,
        collar_type: CollarType,
        expires_in_minutes: int = 5,
    ) -> PendingRequest:
        """Create a collar request."""
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
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
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
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


class PunishmentRepository:
    """Repository for Punishment operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

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
            expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)

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


class DungeonRepository:
    """Repository for Dungeon operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def lock(
        self,
        user_id: int,
        locked_by_id: int,
        dungeon_type: DungeonType,
        hours: int,
        reason: Optional[str] = None,
    ) -> Dungeon:
        """Lock a user in dungeon."""
        expires_at = datetime.utcnow() + timedelta(hours=hours)
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


class AuctionRepository:
    """Repository for Auction operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        seller_id: int,
        description: str,
        starting_price: int,
        hours: int,
    ) -> Auction:
        """Create a new auction."""
        ends_at = datetime.utcnow() + timedelta(hours=hours)
        auction = Auction(
            seller_id=seller_id,
            description=description,
            starting_price=starting_price,
            ends_at=ends_at,
        )
        self.session.add(auction)
        await self.session.flush()
        return auction

    async def get_by_id(self, auction_id: int) -> Optional[Auction]:
        """Get auction by ID."""
        return await self.session.get(Auction, auction_id)

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

        # Create bid
        bid = Bid(
            auction_id=auction_id,
            bidder_id=bidder_id,
            amount=amount,
        )
        self.session.add(bid)

        # Update auction
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


class ContractRepository:
    """Repository for Contract operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        dom_id: int,
        sub_id: int,
        terms: str,
        ends_at: Optional[datetime] = None,
    ) -> Contract:
        """Create a new contract."""
        contract = Contract(
            dom_id=dom_id,
            sub_id=sub_id,
            terms=terms,
            starts_at=datetime.utcnow(),
            ends_at=ends_at,
            status=ContractStatus.ACTIVE,
        )
        self.session.add(contract)
        await self.session.flush()
        return contract

    async def get_by_id(self, contract_id: int) -> Optional[Contract]:
        """Get contract by ID."""
        return await self.session.get(Contract, contract_id)

    async def get_active_between(self, user1_id: int, user2_id: int) -> Optional[Contract]:
        """Get active contract between two users."""
        result = await self.session.execute(
            select(Contract).where(
                and_(
                    or_(
                        and_(Contract.dom_id == user1_id, Contract.sub_id == user2_id),
                        and_(Contract.dom_id == user2_id, Contract.sub_id == user1_id),
                    ),
                    Contract.status == ContractStatus.ACTIVE,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> Sequence[Contract]:
        """Get all contracts for a user (as dom or sub)."""
        result = await self.session.execute(
            select(Contract)
            .where(or_(Contract.dom_id == user_id, Contract.sub_id == user_id))
            .order_by(desc(Contract.created_at))
        )
        return result.scalars().all()

    async def get_active_by_user(self, user_id: int) -> Sequence[Contract]:
        """Get active contracts for a user (as dom or sub)."""
        result = await self.session.execute(
            select(Contract).where(
                and_(
                    or_(Contract.dom_id == user_id, Contract.sub_id == user_id),
                    Contract.status == ContractStatus.ACTIVE,
                )
            )
        )
        return result.scalars().all()

    async def sign(self, contract_id: int) -> bool:
        """Sign (activate) a contract."""
        contract = await self.get_by_id(contract_id)
        if contract and contract.status == ContractStatus.PENDING:
            contract.status = ContractStatus.ACTIVE
            contract.starts_at = datetime.utcnow()
            await self.session.flush()
            return True
        return False

    async def break_contract(self, contract_id: int, broken_by: int) -> bool:
        """Break a contract."""
        contract = await self.get_by_id(contract_id)
        if contract and contract.status == ContractStatus.ACTIVE:
            contract.status = ContractStatus.BROKEN
            contract.broken_by = broken_by
            await self.session.flush()
            return True
        return False


class ProfileRepository:
    """Repository for Profile operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, user_id: int) -> Profile:
        """Get or create profile for user."""
        profile = await self.session.get(Profile, user_id)
        if profile:
            return profile

        profile = Profile(user_id=user_id)
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def update(
        self,
        user_id: int,
        **kwargs,
    ) -> Optional[Profile]:
        """Update profile fields."""
        profile = await self.session.get(Profile, user_id)
        if not profile:
            return None

        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        # Calculate completeness
        fields = ['display_name', 'pronouns', 'age', 'location', 'main_role',
                  'experience_level', 'bio', 'looking_for']
        filled = sum(1 for f in fields if getattr(profile, f, None))
        profile.profile_completeness = int((filled / len(fields)) * 100)

        await self.session.flush()
        return profile


class UserSettingsRepository:
    """Repository for UserSettings operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, user_id: int) -> UserSettings:
        """Get or create settings for user."""
        settings = await self.session.get(UserSettings, user_id)
        if settings:
            return settings

        settings = UserSettings(user_id=user_id)
        self.session.add(settings)
        await self.session.flush()
        return settings

    async def update(
        self,
        user_id: int,
        **kwargs,
    ) -> Optional[UserSettings]:
        """Update settings fields."""
        settings = await self.session.get(UserSettings, user_id)
        if not settings:
            return None

        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        await self.session.flush()
        return settings


class AltarRepository:
    """Repository for Altar (tribute tracking) operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_tribute(
        self,
        recipient_id: int,
        from_user_id: int,
        amount: int,
    ) -> None:
        """Record a tribute. Updates totals for tracking."""
        # For now, tributes are tracked in transactions table
        # This method is a placeholder for future tribute-specific tracking
        pass

    async def get_total_received(self, user_id: int) -> int:
        """Get total tributes received by user."""
        result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                and_(
                    Transaction.recipient_id == user_id,
                    Transaction.transaction_type == TransactionType.TRIBUTE,
                )
            )
        )
        return result.scalar_one()

    async def get_total_given(self, user_id: int) -> int:
        """Get total tributes given by user."""
        result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                and_(
                    Transaction.sender_id == user_id,
                    Transaction.transaction_type == TransactionType.TRIBUTE,
                )
            )
        )
        return result.scalar_one()

    async def get_devotee_count(self, user_id: int) -> int:
        """Get count of unique devotees (people who have paid tribute)."""
        result = await self.session.execute(
            select(func.count(func.distinct(Transaction.sender_id))).where(
                and_(
                    Transaction.recipient_id == user_id,
                    Transaction.transaction_type == TransactionType.TRIBUTE,
                )
            )
        )
        return result.scalar_one()

    async def get_top_receivers(self, limit: int = 10) -> Sequence[tuple]:
        """Get top tribute receivers."""
        result = await self.session.execute(
            select(User, func.sum(Transaction.amount).label("total"))
            .join(Transaction, Transaction.recipient_id == User.id)
            .where(Transaction.transaction_type == TransactionType.TRIBUTE)
            .group_by(User.id)
            .order_by(desc("total"))
            .limit(limit)
        )
        return result.all()

    async def get_devotees(self, user_id: int, limit: int = 10) -> Sequence[tuple]:
        """Get top devotees for a user."""
        result = await self.session.execute(
            select(User, func.sum(Transaction.amount).label("total"))
            .join(Transaction, Transaction.sender_id == User.id)
            .where(
                and_(
                    Transaction.recipient_id == user_id,
                    Transaction.transaction_type == TransactionType.TRIBUTE,
                )
            )
            .group_by(User.id)
            .order_by(desc("total"))
            .limit(limit)
        )
        return result.all()
