"""
Tests for User and Transaction repositories.
"""
import pytest
from datetime import datetime, timezone

from src.database.connection import get_session
from src.database.models import TransactionType
from src.database.repositories import UserRepository, TransactionRepository


class TestUserRepository:
    """Test UserRepository operations."""

    @pytest.mark.asyncio
    async def test_create_user(self):
        """Test creating a new user."""
        async with get_session() as session:
            repo = UserRepository(session)
            user, created = await repo.get_or_create(
                telegram_id=12345,
                username="testuser1",
                first_name="Test",
            )
            assert user is not None
            assert user.telegram_id == 12345
            assert user.username == "testuser1"
            assert user.balance == 0
            assert created is True
            await session.commit()

    @pytest.mark.asyncio
    async def test_get_existing_user(self):
        """Test getting an existing user."""
        async with get_session() as session:
            repo = UserRepository(session)
            # Create user
            user1, created1 = await repo.get_or_create(
                telegram_id=12346,
                username="testuser2",
                first_name="Test2",
            )
            await session.commit()

            # Get same user again
            user2, created2 = await repo.get_or_create(
                telegram_id=12346,
                username="testuser2",
                first_name="Test2",
            )
            assert user1.id == user2.id
            assert created2 is False

    @pytest.mark.asyncio
    async def test_update_balance(self):
        """Test updating user balance."""
        async with get_session() as session:
            repo = UserRepository(session)
            user, _ = await repo.get_or_create(
                telegram_id=12347,
                username="testuser3",
                first_name="Test3",
            )

            # Add balance
            success = await repo.update_balance(user.id, 100)
            assert success is True

            # Refresh and check
            updated_user = await repo.get_by_telegram_id(12347)
            assert updated_user.balance == 100
            await session.commit()

    @pytest.mark.asyncio
    async def test_get_by_username(self):
        """Test getting user by username."""
        async with get_session() as session:
            repo = UserRepository(session)
            user, _ = await repo.get_or_create(
                telegram_id=12348,
                username="FindMeUser",
                first_name="Findable",
            )
            await session.commit()

            # Test case-insensitive search
            found = await repo.get_by_username("findmeuser")
            assert found is not None
            assert found.id == user.id

            # Test with @ prefix
            found2 = await repo.get_by_username("@FindMeUser")
            assert found2 is not None
            assert found2.id == user.id

    @pytest.mark.asyncio
    async def test_set_admin(self):
        """Test setting admin status."""
        async with get_session() as session:
            repo = UserRepository(session)
            user, _ = await repo.get_or_create(
                telegram_id=12349,
                username="adminuser",
                first_name="Admin",
            )
            await session.flush()

            # Set as admin
            success = await repo.set_admin(user.id, True)
            assert success is True

            # Verify
            updated = await repo.get_by_id(user.id)
            assert updated.is_admin is True

            # Remove admin
            await repo.set_admin(user.id, False)
            updated = await repo.get_by_id(user.id)
            assert updated.is_admin is False
            await session.commit()

    @pytest.mark.asyncio
    async def test_get_ranking(self):
        """Test getting user ranking."""
        async with get_session() as session:
            repo = UserRepository(session)
            # Create users with different balances
            for i, bal in enumerate([100, 500, 250, 1000, 50]):
                user, _ = await repo.get_or_create(
                    telegram_id=13000 + i,
                    username=f"rankuser{i}",
                    first_name=f"Rank{i}",
                )
                user.balance = bal
            await session.flush()

            ranking = await repo.get_ranking(limit=5)
            assert len(ranking) == 5
            # Should be ordered by balance descending
            balances = [u.balance for u in ranking]
            assert balances == sorted(balances, reverse=True)
            await session.commit()

    @pytest.mark.asyncio
    async def test_update_balance_negative_blocked(self):
        """Test that negative balance is blocked by default."""
        async with get_session() as session:
            repo = UserRepository(session)
            user, _ = await repo.get_or_create(
                telegram_id=12350,
                username="nobalance",
                first_name="NoBalance",
            )
            user.balance = 50
            await session.flush()

            # Try to subtract more than available
            success = await repo.update_balance(user.id, -100, allow_negative=False)
            assert success is False

            # Balance should be unchanged
            updated = await repo.get_by_id(user.id)
            assert updated.balance == 50
            await session.commit()


class TestTransactionRepository:
    """Test TransactionRepository operations."""

    @pytest.mark.asyncio
    async def test_create_transaction(self):
        """Test creating a transaction."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            tx_repo = TransactionRepository(session)

            # Create users
            sender, _ = await user_repo.get_or_create(
                telegram_id=22345,
                username="sender1",
                first_name="Sender",
            )
            sender.balance = 1000

            recipient, _ = await user_repo.get_or_create(
                telegram_id=22346,
                username="recipient1",
                first_name="Recipient",
            )
            await session.flush()

            # Create transaction
            tx = await tx_repo.create(
                sender_id=sender.id,
                recipient_id=recipient.id,
                amount=100,
                transaction_type=TransactionType.TRANSFER,
            )
            assert tx is not None
            assert tx.amount == 100
            await session.commit()

    @pytest.mark.asyncio
    async def test_get_user_history(self):
        """Test getting transaction history for a user."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            tx_repo = TransactionRepository(session)

            sender, _ = await user_repo.get_or_create(
                telegram_id=22347,
                username="histsender",
                first_name="HistSender",
            )
            sender.balance = 5000

            recipient, _ = await user_repo.get_or_create(
                telegram_id=22348,
                username="histrecipient",
                first_name="HistRecipient",
            )
            await session.flush()

            # Create multiple transactions
            for i in range(5):
                await tx_repo.create(
                    sender_id=sender.id,
                    recipient_id=recipient.id,
                    amount=100 * (i + 1),
                    transaction_type=TransactionType.TRANSFER,
                )
            await session.flush()

            # Get history for sender
            history = await tx_repo.get_user_history(sender.id, limit=10)
            assert len(history) >= 5

            # Get history for recipient
            rec_history = await tx_repo.get_user_history(recipient.id, limit=10)
            assert len(rec_history) >= 5
            await session.commit()

    @pytest.mark.asyncio
    async def test_count_user_transactions(self):
        """Test counting user transactions."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            tx_repo = TransactionRepository(session)

            user1, _ = await user_repo.get_or_create(
                telegram_id=22349,
                username="countuser1",
                first_name="Count1",
            )
            user2, _ = await user_repo.get_or_create(
                telegram_id=22350,
                username="countuser2",
                first_name="Count2",
            )
            await session.flush()

            # Create 3 transactions
            for _ in range(3):
                await tx_repo.create(
                    sender_id=user1.id,
                    recipient_id=user2.id,
                    amount=50,
                    transaction_type=TransactionType.TRANSFER,
                )
            await session.flush()

            count = await tx_repo.count_user_transactions(user1.id)
            assert count >= 3
            await session.commit()


class TestMultiUserTransfers:
    """Test complex multi-user transfer scenarios."""

    @pytest.mark.asyncio
    async def test_chain_transfer(self):
        """Test transferring coins through a chain of users."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            tx_repo = TransactionRepository(session)

            # Create 3 users
            alice, _ = await user_repo.get_or_create(
                telegram_id=30001, username="alice", first_name="Alice"
            )
            alice.balance = 1000

            bob, _ = await user_repo.get_or_create(
                telegram_id=30002, username="bob", first_name="Bob"
            )
            bob.balance = 500

            charlie, _ = await user_repo.get_or_create(
                telegram_id=30003, username="charlie", first_name="Charlie"
            )
            charlie.balance = 200
            await session.flush()

            # Alice -> Bob (300)
            await user_repo.update_balance(alice.id, -300)
            await user_repo.update_balance(bob.id, 300)
            await tx_repo.create(
                sender_id=alice.id, recipient_id=bob.id, amount=300,
                transaction_type=TransactionType.TRANSFER
            )

            # Bob -> Charlie (400)
            await user_repo.update_balance(bob.id, -400)
            await user_repo.update_balance(charlie.id, 400)
            await tx_repo.create(
                sender_id=bob.id, recipient_id=charlie.id, amount=400,
                transaction_type=TransactionType.TRANSFER
            )

            await session.flush()

            # Verify final balances
            alice = await user_repo.get_by_id(alice.id)
            bob = await user_repo.get_by_id(bob.id)
            charlie = await user_repo.get_by_id(charlie.id)

            assert alice.balance == 700   # 1000 - 300
            assert bob.balance == 400     # 500 + 300 - 400
            assert charlie.balance == 600 # 200 + 400
            await session.commit()

    @pytest.mark.asyncio
    async def test_multiple_simultaneous_transfers(self):
        """Test multiple users transferring to the same recipient."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            tx_repo = TransactionRepository(session)

            # Create recipient
            recipient, _ = await user_repo.get_or_create(
                telegram_id=30010, username="recipient", first_name="Recipient"
            )
            recipient.balance = 0

            # Create 5 senders
            senders = []
            for i in range(5):
                sender, _ = await user_repo.get_or_create(
                    telegram_id=30011 + i, username=f"sender{i}", first_name=f"Sender{i}"
                )
                sender.balance = 1000
                senders.append(sender)
            await session.flush()

            # Each sender sends 100 to recipient
            for sender in senders:
                await user_repo.update_balance(sender.id, -100)
                await user_repo.update_balance(recipient.id, 100)
                await tx_repo.create(
                    sender_id=sender.id, recipient_id=recipient.id, amount=100,
                    transaction_type=TransactionType.TRANSFER
                )
            await session.flush()

            # Verify recipient balance
            recipient = await user_repo.get_by_id(recipient.id)
            assert recipient.balance == 500  # 5 * 100
            await session.commit()
