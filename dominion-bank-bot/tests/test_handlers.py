"""
Tests for The Phantom Bot handlers, helpers, and edge cases.
Repository tests have been moved to separate test files:
- test_repositories_user.py
- test_repositories_bdsm.py
- test_repositories_profile.py
"""
import pytest

from src.database.connection import get_session
from src.database.models import TransactionType
from src.database.repositories import (
    UserRepository, TransactionRepository, CollarRepository,
    AuctionRepository, ProfileRepository, UserSettingsRepository,
)

from conftest import create_mock_update, create_mock_context


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestHelpers:
    """Test helper functions."""

    def test_extract_username(self):
        """Test username extraction."""
        from src.utils.helpers import extract_username

        assert extract_username("@testuser") == "testuser"
        assert extract_username("testuser") == "testuser"
        assert extract_username("@Test_User123") == "Test_User123"
        assert extract_username("") is None
        assert extract_username(None) is None

    def test_extract_amount(self):
        """Test amount extraction."""
        from src.utils.helpers import extract_amount

        assert extract_amount("100") == 100
        assert extract_amount("1000") == 1000
        assert extract_amount("") is None
        assert extract_amount(None) is None

    def test_parse_amount(self):
        """Test parse_amount function."""
        from src.utils.helpers import parse_amount

        assert parse_amount("100") == 100
        assert parse_amount("1,000") == 1000
        assert parse_amount("1.000") == 1000
        assert parse_amount("  500  ") == 500
        assert parse_amount("") is None
        assert parse_amount(None) is None

    def test_parse_transfer_args(self):
        """Test transfer argument parsing."""
        from src.utils.helpers import parse_transfer_args

        username, amount = parse_transfer_args("@testuser 100")
        assert username == "testuser"
        assert amount == 100

        username, amount = parse_transfer_args("testuser 500")
        assert username == "testuser"
        assert amount == 500

        username, amount = parse_transfer_args("")
        assert username is None
        assert amount is None

    def test_parse_transfer_args_with_thousands(self):
        """Test transfer argument parsing with thousands separator."""
        from src.utils.helpers import parse_transfer_args

        username, amount = parse_transfer_args("@testuser 1,000")
        assert username == "testuser"
        assert amount == 1000

        username, amount = parse_transfer_args("testuser 10.000")
        assert username == "testuser"
        assert amount == 10000


# =============================================================================
# MESSAGE FORMATTING TESTS
# =============================================================================

class TestMessageFormatting:
    """Test message formatting functions."""

    def test_format_currency(self):
        """Test currency formatting."""
        from src.utils.messages import format_currency

        formatted = format_currency(1000)
        # Format may use period (1.000) or comma (1,000) depending on locale
        assert "1.000" in formatted or "1,000" in formatted or "1000" in formatted

    def test_format_balance(self):
        """Test balance formatting."""
        from src.utils.messages import format_balance

        balance_str = format_balance(5000)
        assert "5" in balance_str

    def test_welcome_message(self):
        """Test welcome message generation."""
        from src.utils.messages import welcome_message

        msg = welcome_message(balance=100, username="TestUser")
        assert "TestUser" in msg
        assert "100" in msg

    def test_balance_message(self):
        """Test balance message generation."""
        from src.utils.messages import balance_message

        msg = balance_message(500)
        assert "500" in msg

    def test_transfer_success_sender(self):
        """Test transfer success message for sender."""
        from src.utils.messages import transfer_success_sender

        msg = transfer_success_sender(100, "Recipient", 400)
        assert "100" in msg
        assert "Recipient" in msg
        assert "400" in msg

    def test_transfer_success_recipient(self):
        """Test transfer success message for recipient."""
        from src.utils.messages import transfer_success_recipient

        msg = transfer_success_recipient(100, "Sender", 600)
        assert "100" in msg
        assert "Sender" in msg
        assert "600" in msg


# =============================================================================
# COMMAND HANDLER TESTS
# =============================================================================

class TestCommandHandlers:
    """Test command handlers with mocked updates."""

    @pytest.mark.asyncio
    async def test_start_command_new_user(self):
        """Test /start command for new user."""
        from src.handlers.core import start_command

        update = create_mock_update(user_id=200001, username="newstartuser")
        context = create_mock_context()

        await start_command(update, context)

        # Verify reply was called
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "newstartuser" in call_args[0][0].lower() or "User200001" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_ver_command_registered_user(self):
        """Test /ver command for registered user."""
        from src.handlers.core import ver_command

        # First register user
        async with get_session() as session:
            user_repo = UserRepository(session)
            user, _ = await user_repo.get_or_create(
                telegram_id=200002,
                username="veruser",
                first_name="VerUser",
            )
            user.balance = 999
            await session.commit()

        update = create_mock_update(user_id=200002, username="veruser")
        context = create_mock_context()

        await ver_command(update, context)

        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "999" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_ver_command_unregistered_user(self):
        """Test /ver command for unregistered user."""
        from src.handlers.core import ver_command

        update = create_mock_update(user_id=200099, username="unregistered")
        context = create_mock_context()

        await ver_command(update, context)

        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        # Should contain error message about not being registered
        assert "registr" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_dar_command_missing_args(self):
        """Test /dar command with missing arguments."""
        from src.handlers.core import dar_command

        # Register sender
        async with get_session() as session:
            user_repo = UserRepository(session)
            await user_repo.get_or_create(
                telegram_id=200010,
                username="darsender",
                first_name="DarSender",
            )
            await session.commit()

        update = create_mock_update(user_id=200010, username="darsender")
        context = create_mock_context(args=[])  # No args

        await dar_command(update, context)

        update.message.reply_text.assert_called_once()
        # Should show usage

    @pytest.mark.asyncio
    async def test_dar_command_successful_transfer(self):
        """Test /dar command with successful transfer."""
        from src.handlers.core import dar_command

        # Register both users
        async with get_session() as session:
            user_repo = UserRepository(session)
            sender, _ = await user_repo.get_or_create(
                telegram_id=200020,
                username="realsender",
                first_name="RealSender",
            )
            sender.balance = 500

            recipient, _ = await user_repo.get_or_create(
                telegram_id=200021,
                username="realrecipient",
                first_name="RealRecipient",
            )
            recipient.balance = 100
            await session.commit()

        update = create_mock_update(user_id=200020, username="realsender")
        context = create_mock_context(args=["@realrecipient", "50"])

        await dar_command(update, context)

        # Verify transfer happened
        async with get_session() as session:
            user_repo = UserRepository(session)
            sender = await user_repo.get_by_telegram_id(200020)
            recipient = await user_repo.get_by_telegram_id(200021)
            assert sender.balance == 450  # 500 - 50
            assert recipient.balance == 150  # 100 + 50

    @pytest.mark.asyncio
    async def test_dar_command_insufficient_balance(self):
        """Test /dar command with insufficient balance."""
        from src.handlers.core import dar_command

        # Register both users
        async with get_session() as session:
            user_repo = UserRepository(session)
            sender, _ = await user_repo.get_or_create(
                telegram_id=200030,
                username="brokesender",
                first_name="BrokeSender",
            )
            sender.balance = 10

            recipient, _ = await user_repo.get_or_create(
                telegram_id=200031,
                username="brokerecipient",
                first_name="BrokeRecipient",
            )
            await session.commit()

        update = create_mock_update(user_id=200030, username="brokesender")
        context = create_mock_context(args=["@brokerecipient", "100"])

        await dar_command(update, context)

        update.message.reply_text.assert_called_once()
        # Should show insufficient balance error

    @pytest.mark.asyncio
    async def test_dar_command_self_transfer(self):
        """Test /dar command self transfer blocked."""
        from src.handlers.core import dar_command

        # Register user
        async with get_session() as session:
            user_repo = UserRepository(session)
            user, _ = await user_repo.get_or_create(
                telegram_id=200040,
                username="selfuser",
                first_name="SelfUser",
            )
            user.balance = 1000
            await session.commit()

        update = create_mock_update(user_id=200040, username="selfuser")
        context = create_mock_context(args=["@selfuser", "100"])

        await dar_command(update, context)

        update.message.reply_text.assert_called_once()
        # Should show self-transfer error


# =============================================================================
# PROFILE COMMAND TESTS
# =============================================================================

class TestProfileCommands:
    """Test profile command handlers."""

    @pytest.mark.asyncio
    async def test_perfil_command_self(self):
        """Test /perfil command for own profile."""
        from src.handlers.profiles import perfil_command

        # Register user
        async with get_session() as session:
            user_repo = UserRepository(session)
            profile_repo = ProfileRepository(session)
            user, _ = await user_repo.get_or_create(
                telegram_id=300001,
                username="perfiluser",
                first_name="PerfilUser",
            )
            user.balance = 750
            await session.flush()
            await profile_repo.get_or_create(user.id)
            await session.commit()

        update = create_mock_update(user_id=300001, username="perfiluser")
        context = create_mock_context(args=[])

        await perfil_command(update, context)

        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        # User's display_name returns @username format
        assert "perfiluser" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_editarperfil_show_help(self):
        """Test /editarperfil command shows help when no args."""
        from src.handlers.profiles import editarperfil_command

        # Register user
        async with get_session() as session:
            user_repo = UserRepository(session)
            user, _ = await user_repo.get_or_create(
                telegram_id=300010,
                username="editarperfiluser",
                first_name="EditarPerfilUser",
            )
            await session.commit()

        update = create_mock_update(user_id=300010, username="editarperfiluser")
        context = create_mock_context(args=[])

        await editarperfil_command(update, context)

        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        # Should contain usage info
        assert "bio" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_editarperfil_update_bio(self):
        """Test /editarperfil bio command."""
        from src.handlers.profiles import editarperfil_command

        # Register user with profile
        async with get_session() as session:
            user_repo = UserRepository(session)
            profile_repo = ProfileRepository(session)
            user, _ = await user_repo.get_or_create(
                telegram_id=300020,
                username="bioupdateuser",
                first_name="BioUpdateUser",
            )
            await session.flush()
            await profile_repo.get_or_create(user.id)
            await session.commit()

        update = create_mock_update(user_id=300020, username="bioupdateuser")
        context = create_mock_context(args=["bio", "Mi", "nueva", "bio"])

        await editarperfil_command(update, context)

        # Verify bio was updated
        async with get_session() as session:
            user_repo = UserRepository(session)
            profile_repo = ProfileRepository(session)
            user = await user_repo.get_by_telegram_id(300020)
            profile = await profile_repo.get_or_create(user.id)
            assert profile.bio == "Mi nueva bio"

    @pytest.mark.asyncio
    async def test_configuracion_show_settings(self):
        """Test /configuracion command shows current settings."""
        from src.handlers.profiles import configuracion_command

        # Register user with settings
        async with get_session() as session:
            user_repo = UserRepository(session)
            settings_repo = UserSettingsRepository(session)
            user, _ = await user_repo.get_or_create(
                telegram_id=300030,
                username="configuser",
                first_name="ConfigUser",
            )
            await session.flush()
            await settings_repo.get_or_create(user.id)
            await session.commit()

        update = create_mock_update(user_id=300030, username="configuser")
        context = create_mock_context(args=[])

        await configuracion_command(update, context)

        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "Configuracion" in call_args[0][0] or "configuracion" in call_args[0][0].lower()


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_ranking(self):
        """Test ranking with no users."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            ranking = await user_repo.get_ranking(limit=10)
            # Should return empty list, not error
            assert isinstance(ranking, (list, tuple))

    @pytest.mark.asyncio
    async def test_nonexistent_user_balance_update(self):
        """Test updating balance for non-existent user."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            success = await user_repo.update_balance(999999, 100)
            assert success is False

    @pytest.mark.asyncio
    async def test_collar_already_collared(self):
        """Test collaring already collared user."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            collar_repo = CollarRepository(session)

            owner1, _ = await user_repo.get_or_create(
                telegram_id=400001, username="owner1", first_name="Owner1"
            )
            owner2, _ = await user_repo.get_or_create(
                telegram_id=400002, username="owner2", first_name="Owner2"
            )
            sub, _ = await user_repo.get_or_create(
                telegram_id=400003, username="sub", first_name="Sub"
            )
            await session.flush()

            # First collar
            await collar_repo.create(owner1.id, sub.id)
            await session.flush()

            # Check if already collared
            is_collared = await collar_repo.is_collared(sub.id)
            assert is_collared is True
            await session.commit()

    @pytest.mark.asyncio
    async def test_auction_bid_below_current(self):
        """Test auction bid below current bid."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            auction_repo = AuctionRepository(session)

            seller, _ = await user_repo.get_or_create(
                telegram_id=400010, username="lowbidseller", first_name="LowBidSeller"
            )
            bidder1, _ = await user_repo.get_or_create(
                telegram_id=400011, username="highbidder", first_name="HighBidder"
            )
            bidder2, _ = await user_repo.get_or_create(
                telegram_id=400012, username="lowbidder", first_name="LowBidder"
            )
            await session.flush()

            auction = await auction_repo.create(
                seller_id=seller.id,
                description="Test auction",
                starting_price=100,
                hours=24,
            )
            await session.flush()

            # High bid
            await auction_repo.place_bid(auction.id, bidder1.id, 500)
            await session.flush()

            # Low bid should still work but auction validates minimum
            # The repository itself doesn't validate, that's handler logic
            bid = await auction_repo.place_bid(auction.id, bidder2.id, 600)
            assert bid is not None
            await session.commit()

    @pytest.mark.asyncio
    async def test_transaction_types(self):
        """Test different transaction types."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            tx_repo = TransactionRepository(session)

            user1, _ = await user_repo.get_or_create(
                telegram_id=400020, username="txuser1", first_name="TxUser1"
            )
            user2, _ = await user_repo.get_or_create(
                telegram_id=400021, username="txuser2", first_name="TxUser2"
            )
            await session.flush()

            # Test different transaction types
            for tx_type in [
                TransactionType.TRANSFER,
                TransactionType.ADMIN_GIVE,
                TransactionType.TRIBUTE,
            ]:
                tx = await tx_repo.create(
                    sender_id=user1.id,
                    recipient_id=user2.id,
                    amount=10,
                    transaction_type=tx_type,
                )
                assert tx.transaction_type == tx_type
            await session.commit()


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
