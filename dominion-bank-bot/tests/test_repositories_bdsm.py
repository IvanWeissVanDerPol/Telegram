"""
Tests for BDSM-related repositories (Collar, Punishment, Dungeon, Auction, Contract).
"""
import pytest
from datetime import datetime, timedelta, timezone

from src.database.connection import get_session
from src.database.models import (
    PunishmentType, DungeonType, AuctionStatus, ContractStatus,
)
from src.database.repositories import (
    UserRepository, CollarRepository, PunishmentRepository,
    DungeonRepository, AuctionRepository, ContractRepository,
)


class TestCollarRepository:
    """Test CollarRepository operations."""

    @pytest.mark.asyncio
    async def test_create_collar(self):
        """Test creating a collar."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            collar_repo = CollarRepository(session)

            owner, _ = await user_repo.get_or_create(
                telegram_id=32345,
                username="owner1",
                first_name="Owner",
            )
            sub, _ = await user_repo.get_or_create(
                telegram_id=32346,
                username="sub1",
                first_name="Sub",
            )
            await session.flush()

            collar = await collar_repo.create(owner.id, sub.id)
            assert collar is not None
            assert collar.owner_id == owner.id
            assert collar.sub_id == sub.id
            await session.commit()

    @pytest.mark.asyncio
    async def test_get_collar_by_sub(self):
        """Test getting collar by sub."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            collar_repo = CollarRepository(session)

            owner, _ = await user_repo.get_or_create(
                telegram_id=32347,
                username="owner2",
                first_name="Owner2",
            )
            sub, _ = await user_repo.get_or_create(
                telegram_id=32348,
                username="sub2",
                first_name="Sub2",
            )
            await session.flush()

            await collar_repo.create(owner.id, sub.id)
            await session.flush()

            collar = await collar_repo.get_by_sub(sub.id)
            assert collar is not None
            assert collar.owner_id == owner.id
            await session.commit()

    @pytest.mark.asyncio
    async def test_get_collars_by_owner(self):
        """Test getting all collars owned by a user."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            collar_repo = CollarRepository(session)

            owner, _ = await user_repo.get_or_create(
                telegram_id=32349,
                username="bigowner",
                first_name="BigOwner",
            )
            await session.flush()

            # Create 3 subs
            subs = []
            for i in range(3):
                sub, _ = await user_repo.get_or_create(
                    telegram_id=32350 + i,
                    username=f"multisub{i}",
                    first_name=f"MultiSub{i}",
                )
                subs.append(sub)
            await session.flush()

            # Collar all subs
            for sub in subs:
                await collar_repo.create(owner.id, sub.id)
            await session.flush()

            # Get by owner
            collars = await collar_repo.get_by_owner(owner.id)
            assert len(collars) == 3
            await session.commit()

    @pytest.mark.asyncio
    async def test_remove_collar(self):
        """Test removing a collar."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            collar_repo = CollarRepository(session)

            owner, _ = await user_repo.get_or_create(
                telegram_id=32360,
                username="removeowner",
                first_name="RemoveOwner",
            )
            sub, _ = await user_repo.get_or_create(
                telegram_id=32361,
                username="removesub",
                first_name="RemoveSub",
            )
            await session.flush()

            await collar_repo.create(owner.id, sub.id)
            await session.flush()

            # Remove by sub
            success = await collar_repo.remove_by_sub(sub.id)
            assert success is True

            # Verify removed
            collar = await collar_repo.get_by_sub(sub.id)
            assert collar is None
            await session.commit()

    @pytest.mark.asyncio
    async def test_is_collared(self):
        """Test checking if user is collared."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            collar_repo = CollarRepository(session)

            owner, _ = await user_repo.get_or_create(
                telegram_id=32370,
                username="checkowner",
                first_name="CheckOwner",
            )
            sub, _ = await user_repo.get_or_create(
                telegram_id=32371,
                username="checksub",
                first_name="CheckSub",
            )
            free, _ = await user_repo.get_or_create(
                telegram_id=32372,
                username="freeuser",
                first_name="FreeUser",
            )
            await session.flush()

            await collar_repo.create(owner.id, sub.id)
            await session.flush()

            assert await collar_repo.is_collared(sub.id) is True
            assert await collar_repo.is_collared(free.id) is False
            await session.commit()


class TestPunishmentRepository:
    """Test PunishmentRepository operations."""

    @pytest.mark.asyncio
    async def test_create_punishment(self):
        """Test creating a punishment."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            punishment_repo = PunishmentRepository(session)

            punisher, _ = await user_repo.get_or_create(
                telegram_id=42345,
                username="punisher1",
                first_name="Punisher",
            )
            victim, _ = await user_repo.get_or_create(
                telegram_id=42346,
                username="victim1",
                first_name="Victim",
            )
            await session.flush()

            punishment = await punishment_repo.create(
                user_id=victim.id,
                punisher_id=punisher.id,
                punishment_type=PunishmentType.WHIP,
                description="Test whip",
                cost=50,
                expires_in_minutes=10,
            )
            assert punishment is not None
            assert punishment.punishment_type == PunishmentType.WHIP
            assert punishment.cost == 50
            await session.commit()

    @pytest.mark.asyncio
    async def test_get_active_punishments(self):
        """Test getting active punishments."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            punishment_repo = PunishmentRepository(session)

            punisher, _ = await user_repo.get_or_create(
                telegram_id=42347,
                username="punisher2",
                first_name="Punisher2",
            )
            victim, _ = await user_repo.get_or_create(
                telegram_id=42348,
                username="victim2",
                first_name="Victim2",
            )
            await session.flush()

            await punishment_repo.create(
                user_id=victim.id,
                punisher_id=punisher.id,
                punishment_type=PunishmentType.PENITENCIA,
                description="Active punishment",
                expires_in_minutes=60,
            )
            await session.flush()

            punishments = await punishment_repo.get_active_by_user(victim.id)
            assert len(punishments) >= 1
            await session.commit()

    @pytest.mark.asyncio
    async def test_multiple_punishments(self):
        """Test multiple punishments for same user."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            punishment_repo = PunishmentRepository(session)

            punisher, _ = await user_repo.get_or_create(
                telegram_id=42350,
                username="multipunisher",
                first_name="MultiPunisher",
            )
            victim, _ = await user_repo.get_or_create(
                telegram_id=42351,
                username="multivictim",
                first_name="MultiVictim",
            )
            await session.flush()

            # Create multiple punishment types
            for ptype in [PunishmentType.WHIP, PunishmentType.PENITENCIA]:
                await punishment_repo.create(
                    user_id=victim.id,
                    punisher_id=punisher.id,
                    punishment_type=ptype,
                    description=f"Test {ptype.name}",
                    expires_in_minutes=60,
                )
            await session.flush()

            punishments = await punishment_repo.get_active_by_user(victim.id)
            assert len(punishments) >= 2
            await session.commit()

    @pytest.mark.asyncio
    async def test_complete_punishment(self):
        """Test completing a punishment."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            punishment_repo = PunishmentRepository(session)

            punisher, _ = await user_repo.get_or_create(
                telegram_id=42360,
                username="completepunisher",
                first_name="CompletePunisher",
            )
            victim, _ = await user_repo.get_or_create(
                telegram_id=42361,
                username="completevictim",
                first_name="CompleteVictim",
            )
            await session.flush()

            punishment = await punishment_repo.create(
                user_id=victim.id,
                punisher_id=punisher.id,
                punishment_type=PunishmentType.WHIP,
                description="To be completed",
                expires_in_minutes=60,
            )
            await session.flush()

            # Complete it
            success = await punishment_repo.complete_punishment(punishment.id)
            assert success is True

            # Should no longer appear in active
            active = await punishment_repo.get_active_by_user(victim.id)
            assert all(p.id != punishment.id for p in active)
            await session.commit()


class TestDungeonRepository:
    """Test DungeonRepository operations."""

    @pytest.mark.asyncio
    async def test_lock_user(self):
        """Test locking a user in dungeon."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            dungeon_repo = DungeonRepository(session)

            jailer, _ = await user_repo.get_or_create(
                telegram_id=52345,
                username="jailer1",
                first_name="Jailer",
            )
            prisoner, _ = await user_repo.get_or_create(
                telegram_id=52346,
                username="prisoner1",
                first_name="Prisoner",
            )
            await session.flush()

            dungeon = await dungeon_repo.lock(
                user_id=prisoner.id,
                locked_by_id=jailer.id,
                dungeon_type=DungeonType.CALABOZO,
                hours=24,
                reason="Test lock",
            )
            assert dungeon is not None
            assert dungeon.user_id == prisoner.id
            await session.commit()

    @pytest.mark.asyncio
    async def test_is_locked(self):
        """Test checking if user is locked."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            dungeon_repo = DungeonRepository(session)

            jailer, _ = await user_repo.get_or_create(
                telegram_id=52347,
                username="jailer2",
                first_name="Jailer2",
            )
            prisoner, _ = await user_repo.get_or_create(
                telegram_id=52348,
                username="prisoner2",
                first_name="Prisoner2",
            )
            await session.flush()

            await dungeon_repo.lock(
                user_id=prisoner.id,
                locked_by_id=jailer.id,
                dungeon_type=DungeonType.CALABOZO,
                hours=24,
            )
            await session.flush()

            is_locked = await dungeon_repo.is_locked(prisoner.id)
            assert is_locked is True
            await session.commit()

    @pytest.mark.asyncio
    async def test_release_user(self):
        """Test releasing a user from dungeon."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            dungeon_repo = DungeonRepository(session)

            jailer, _ = await user_repo.get_or_create(
                telegram_id=52350,
                username="releasejailer",
                first_name="ReleaseJailer",
            )
            prisoner, _ = await user_repo.get_or_create(
                telegram_id=52351,
                username="releaseprisoner",
                first_name="ReleasePrisoner",
            )
            await session.flush()

            await dungeon_repo.lock(
                user_id=prisoner.id,
                locked_by_id=jailer.id,
                dungeon_type=DungeonType.CALABOZO,
                hours=24,
            )
            await session.flush()

            # Verify locked
            assert await dungeon_repo.is_locked(prisoner.id) is True

            # Release
            success = await dungeon_repo.release(prisoner.id)
            assert success is True

            # Verify released
            assert await dungeon_repo.is_locked(prisoner.id) is False
            await session.commit()

    @pytest.mark.asyncio
    async def test_get_all_locked(self):
        """Test getting all locked users."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            dungeon_repo = DungeonRepository(session)

            jailer, _ = await user_repo.get_or_create(
                telegram_id=52360,
                username="massjailer",
                first_name="MassJailer",
            )
            await session.flush()

            # Lock 3 users
            for i in range(3):
                prisoner, _ = await user_repo.get_or_create(
                    telegram_id=52361 + i,
                    username=f"massprisoner{i}",
                    first_name=f"MassPrisoner{i}",
                )
                await session.flush()
                await dungeon_repo.lock(
                    user_id=prisoner.id,
                    locked_by_id=jailer.id,
                    dungeon_type=DungeonType.CALABOZO,
                    hours=24,
                )
            await session.flush()

            locked = await dungeon_repo.get_all_locked()
            assert len(locked) >= 3
            await session.commit()


class TestAuctionRepository:
    """Test AuctionRepository operations."""

    @pytest.mark.asyncio
    async def test_create_auction(self):
        """Test creating an auction."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            auction_repo = AuctionRepository(session)

            seller, _ = await user_repo.get_or_create(
                telegram_id=62345,
                username="seller1",
                first_name="Seller",
            )
            await session.flush()

            auction = await auction_repo.create(
                seller_id=seller.id,
                description="Test auction item",
                starting_price=100,
                hours=24,
            )
            assert auction is not None
            assert auction.starting_price == 100
            assert auction.status == AuctionStatus.ACTIVE
            await session.commit()

    @pytest.mark.asyncio
    async def test_place_bid(self):
        """Test placing a bid."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            auction_repo = AuctionRepository(session)

            seller, _ = await user_repo.get_or_create(
                telegram_id=62347,
                username="seller2",
                first_name="Seller2",
            )
            bidder, _ = await user_repo.get_or_create(
                telegram_id=62348,
                username="bidder1",
                first_name="Bidder",
            )
            await session.flush()

            auction = await auction_repo.create(
                seller_id=seller.id,
                description="Auction for bidding",
                starting_price=100,
                hours=24,
            )
            await session.flush()

            bid = await auction_repo.place_bid(auction.id, bidder.id, 150)
            assert bid is not None
            assert bid.amount == 150

            # Check auction updated
            updated_auction = await auction_repo.get_by_id(auction.id)
            assert updated_auction.current_bid == 150
            assert updated_auction.current_bidder_id == bidder.id
            await session.commit()

    @pytest.mark.asyncio
    async def test_outbid(self):
        """Test outbidding another user."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            auction_repo = AuctionRepository(session)

            seller, _ = await user_repo.get_or_create(
                telegram_id=62360,
                username="outbidseller",
                first_name="OutbidSeller",
            )
            bidder1, _ = await user_repo.get_or_create(
                telegram_id=62361,
                username="outbidbidder1",
                first_name="OutbidBidder1",
            )
            bidder2, _ = await user_repo.get_or_create(
                telegram_id=62362,
                username="outbidbidder2",
                first_name="OutbidBidder2",
            )
            await session.flush()

            auction = await auction_repo.create(
                seller_id=seller.id,
                description="Auction for outbid test",
                starting_price=100,
                hours=24,
            )
            await session.flush()

            # First bid
            await auction_repo.place_bid(auction.id, bidder1.id, 150)
            await session.flush()

            # Second bid (outbid)
            await auction_repo.place_bid(auction.id, bidder2.id, 200)
            await session.flush()

            auction = await auction_repo.get_by_id(auction.id)
            assert auction.current_bid == 200
            assert auction.current_bidder_id == bidder2.id
            await session.commit()

    @pytest.mark.asyncio
    async def test_get_all_active_auctions(self):
        """Test getting all active auctions."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            auction_repo = AuctionRepository(session)

            # Create 3 sellers with auctions
            for i in range(3):
                seller, _ = await user_repo.get_or_create(
                    telegram_id=62370 + i,
                    username=f"multiaucseller{i}",
                    first_name=f"MultiAucSeller{i}",
                )
                await session.flush()
                await auction_repo.create(
                    seller_id=seller.id,
                    description=f"Multi auction {i}",
                    starting_price=100 + i * 50,
                    hours=24,
                )
            await session.flush()

            active = await auction_repo.get_all_active()
            assert len(active) >= 3
            await session.commit()

    @pytest.mark.asyncio
    async def test_cancel_auction(self):
        """Test cancelling an auction."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            auction_repo = AuctionRepository(session)

            seller, _ = await user_repo.get_or_create(
                telegram_id=62380,
                username="cancelseller",
                first_name="CancelSeller",
            )
            await session.flush()

            auction = await auction_repo.create(
                seller_id=seller.id,
                description="Auction to cancel",
                starting_price=100,
                hours=24,
            )
            await session.flush()

            success = await auction_repo.cancel(auction.id)
            assert success is True

            cancelled = await auction_repo.get_by_id(auction.id)
            assert cancelled.status == AuctionStatus.CANCELLED
            await session.commit()


class TestContractRepository:
    """Test ContractRepository operations."""

    @pytest.mark.asyncio
    async def test_create_contract(self):
        """Test creating a contract."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            contract_repo = ContractRepository(session)

            dom, _ = await user_repo.get_or_create(
                telegram_id=72345,
                username="dom1",
                first_name="Dom",
            )
            sub, _ = await user_repo.get_or_create(
                telegram_id=72346,
                username="sub1",
                first_name="Sub",
            )
            await session.flush()

            contract = await contract_repo.create(
                dom_id=dom.id,
                sub_id=sub.id,
                terms="Test contract terms",
                ends_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
            assert contract is not None
            assert contract.status == ContractStatus.ACTIVE
            await session.commit()

    @pytest.mark.asyncio
    async def test_break_contract(self):
        """Test breaking a contract."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            contract_repo = ContractRepository(session)

            dom, _ = await user_repo.get_or_create(
                telegram_id=72347,
                username="dom2",
                first_name="Dom2",
            )
            sub, _ = await user_repo.get_or_create(
                telegram_id=72348,
                username="sub2",
                first_name="Sub2",
            )
            await session.flush()

            contract = await contract_repo.create(
                dom_id=dom.id,
                sub_id=sub.id,
                terms="Contract to break",
            )
            await session.flush()

            success = await contract_repo.break_contract(contract.id, sub.id)
            assert success is True

            broken_contract = await contract_repo.get_by_id(contract.id)
            assert broken_contract.status == ContractStatus.BROKEN
            await session.commit()

    @pytest.mark.asyncio
    async def test_get_active_contracts_by_user(self):
        """Test getting active contracts for a user."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            contract_repo = ContractRepository(session)

            dom, _ = await user_repo.get_or_create(
                telegram_id=72360,
                username="activedom",
                first_name="ActiveDom",
            )
            await session.flush()

            # Create 3 contracts with different subs
            for i in range(3):
                sub, _ = await user_repo.get_or_create(
                    telegram_id=72361 + i,
                    username=f"activesub{i}",
                    first_name=f"ActiveSub{i}",
                )
                await session.flush()
                await contract_repo.create(
                    dom_id=dom.id,
                    sub_id=sub.id,
                    terms=f"Contract {i}",
                )
            await session.flush()

            contracts = await contract_repo.get_active_by_user(dom.id)
            assert len(contracts) >= 3
            await session.commit()

    @pytest.mark.asyncio
    async def test_get_active_contract_between(self):
        """Test getting active contract between two specific users."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            contract_repo = ContractRepository(session)

            dom, _ = await user_repo.get_or_create(
                telegram_id=72370,
                username="betweendom",
                first_name="BetweenDom",
            )
            sub, _ = await user_repo.get_or_create(
                telegram_id=72371,
                username="betweensub",
                first_name="BetweenSub",
            )
            other, _ = await user_repo.get_or_create(
                telegram_id=72372,
                username="betweenother",
                first_name="BetweenOther",
            )
            await session.flush()

            await contract_repo.create(
                dom_id=dom.id,
                sub_id=sub.id,
                terms="Specific contract",
            )
            await session.flush()

            # Should find contract
            found = await contract_repo.get_active_between(dom.id, sub.id)
            assert found is not None

            # Should not find with other user
            not_found = await contract_repo.get_active_between(dom.id, other.id)
            assert not_found is None
            await session.commit()
