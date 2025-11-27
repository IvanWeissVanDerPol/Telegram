"""
Tests for Profile, Settings, Cooldown, and Admin repositories.
"""
import pytest
from datetime import datetime, timezone

from src.database.connection import get_session
from src.database.models import PrivacyLevel, MainRole, ExperienceLevel
from src.database.repositories import (
    UserRepository, ProfileRepository, UserSettingsRepository,
    CooldownRepository, AdminRepository,
)


class TestProfileRepository:
    """Test ProfileRepository operations."""

    @pytest.mark.asyncio
    async def test_get_or_create_profile(self):
        """Test getting or creating a profile."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            profile_repo = ProfileRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=82345,
                username="profileuser1",
                first_name="ProfileUser",
            )
            await session.flush()

            profile = await profile_repo.get_or_create(user.id)
            assert profile is not None
            assert profile.user_id == user.id
            await session.commit()

    @pytest.mark.asyncio
    async def test_update_profile(self):
        """Test updating a profile."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            profile_repo = ProfileRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=82346,
                username="profileuser2",
                first_name="ProfileUser2",
            )
            await session.flush()

            await profile_repo.get_or_create(user.id)
            await session.flush()

            updated = await profile_repo.update(
                user.id,
                bio="Updated bio",
            )
            assert updated is not None
            assert updated.bio == "Updated bio"
            await session.commit()

    @pytest.mark.asyncio
    async def test_update_profile_role(self):
        """Test updating profile role."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            profile_repo = ProfileRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=82350,
                username="roleprofile",
                first_name="RoleProfile",
            )
            await session.flush()

            await profile_repo.get_or_create(user.id)
            await session.flush()

            updated = await profile_repo.update(
                user.id,
                main_role=MainRole.DOM,
            )
            assert updated.main_role == MainRole.DOM
            await session.commit()

    @pytest.mark.asyncio
    async def test_update_profile_experience(self):
        """Test updating profile experience level."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            profile_repo = ProfileRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=82351,
                username="expprofile",
                first_name="ExpProfile",
            )
            await session.flush()

            await profile_repo.get_or_create(user.id)
            await session.flush()

            updated = await profile_repo.update(
                user.id,
                experience_level=ExperienceLevel.AVANZADO,
            )
            assert updated.experience_level == ExperienceLevel.AVANZADO
            await session.commit()

    @pytest.mark.asyncio
    async def test_profile_completeness(self):
        """Test profile completeness calculation."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            profile_repo = ProfileRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=82360,
                username="completeprofile",
                first_name="CompleteProfile",
            )
            await session.flush()

            await profile_repo.get_or_create(user.id)
            await session.flush()

            # Update multiple fields
            updated = await profile_repo.update(
                user.id,
                bio="My bio",
                main_role=MainRole.SWITCH,
                experience_level=ExperienceLevel.INTERMEDIO,
                age=25,
            )
            # Profile completeness should increase
            assert updated.profile_completeness > 0
            await session.commit()


class TestUserSettingsRepository:
    """Test UserSettingsRepository operations."""

    @pytest.mark.asyncio
    async def test_get_or_create_settings(self):
        """Test getting or creating settings."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            settings_repo = UserSettingsRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=92345,
                username="settingsuser1",
                first_name="SettingsUser",
            )
            await session.flush()

            settings = await settings_repo.get_or_create(user.id)
            assert settings is not None
            assert settings.user_id == user.id
            assert settings.privacy_level == PrivacyLevel.MEMBERS  # Default
            await session.commit()

    @pytest.mark.asyncio
    async def test_update_privacy(self):
        """Test updating privacy settings."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            settings_repo = UserSettingsRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=92350,
                username="privacyuser",
                first_name="PrivacyUser",
            )
            await session.flush()

            await settings_repo.get_or_create(user.id)
            await session.flush()

            updated = await settings_repo.update(
                user.id,
                privacy_level=PrivacyLevel.PRIVATE,
            )
            assert updated.privacy_level == PrivacyLevel.PRIVATE
            await session.commit()

    @pytest.mark.asyncio
    async def test_update_notifications(self):
        """Test updating notification settings."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            settings_repo = UserSettingsRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=92351,
                username="notifuser",
                first_name="NotifUser",
            )
            await session.flush()

            await settings_repo.get_or_create(user.id)
            await session.flush()

            updated = await settings_repo.update(
                user.id,
                notify_transfers=False,
            )
            assert updated.notify_transfers is False
            await session.commit()


class TestCooldownRepository:
    """Test CooldownRepository operations."""

    @pytest.mark.asyncio
    async def test_set_and_check_cooldown(self):
        """Test setting and checking a cooldown."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            cooldown_repo = CooldownRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=102345,
                username="cooldownuser",
                first_name="CooldownUser",
            )
            await session.flush()

            # Set cooldown for 60 seconds
            await cooldown_repo.set_cooldown(user.id, "transfer", 60)
            await session.flush()

            # Check cooldown
            expires = await cooldown_repo.is_on_cooldown(user.id, "transfer")
            assert expires is not None
            # Make expires timezone-aware if it isn't already for comparison
            now = datetime.now(timezone.utc)
            if expires.tzinfo is None:
                expires_aware = expires.replace(tzinfo=timezone.utc)
            else:
                expires_aware = expires
            assert expires_aware > now
            await session.commit()

    @pytest.mark.asyncio
    async def test_no_cooldown(self):
        """Test user with no cooldown."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            cooldown_repo = CooldownRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=102350,
                username="nocooldownuser",
                first_name="NoCooldownUser",
            )
            await session.flush()

            # Check non-existent cooldown
            expires = await cooldown_repo.is_on_cooldown(user.id, "transfer")
            assert expires is None
            await session.commit()


class TestAdminRepository:
    """Test AdminRepository operations."""

    @pytest.mark.asyncio
    async def test_add_and_check_admin(self):
        """Test adding and checking admin status."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            admin_repo = AdminRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=500001, username="admincheck", first_name="AdminCheck"
            )
            await session.flush()

            group_id = -100012345

            # Initially not admin
            is_admin = await admin_repo.is_admin(user.id, group_id)
            assert is_admin is False

            # Add as admin
            await admin_repo.add_admin(user.id, group_id)
            await session.flush()

            # Now is admin
            is_admin = await admin_repo.is_admin(user.id, group_id)
            assert is_admin is True
            await session.commit()

    @pytest.mark.asyncio
    async def test_remove_admin(self):
        """Test removing admin status."""
        async with get_session() as session:
            user_repo = UserRepository(session)
            admin_repo = AdminRepository(session)

            user, _ = await user_repo.get_or_create(
                telegram_id=500010, username="removeadmin", first_name="RemoveAdmin"
            )
            await session.flush()

            group_id = -100054321

            await admin_repo.add_admin(user.id, group_id)
            await session.flush()

            # Remove admin
            success = await admin_repo.remove_admin(user.id, group_id)
            assert success is True

            # Verify removed
            is_admin = await admin_repo.is_admin(user.id, group_id)
            assert is_admin is False
            await session.commit()
