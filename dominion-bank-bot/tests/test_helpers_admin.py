"""
Tests for the is_admin helper function and profile import/export handlers.
"""
import os
import pytest
from unittest.mock import patch, AsyncMock

# Set test database URL BEFORE importing anything
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from src.database.connection import get_session
from src.database.repositories import UserRepository


# =============================================================================
# IS_ADMIN HELPER TESTS
# =============================================================================

class TestIsAdminHelper:
    """Test the is_admin helper function."""

    @pytest.mark.asyncio
    async def test_is_admin_super_admin(self):
        """Test that super admins are recognized as admin."""
        from src.utils.helpers import is_admin

        # Mock the settings object at the config module level
        with patch("src.config.settings") as mock_settings:
            mock_settings.super_admin_ids = [123456]

            result = await is_admin(123456)
            assert result is True

    @pytest.mark.asyncio
    async def test_is_admin_not_super_admin_not_db_admin(self):
        """Test that regular users are not recognized as admin."""
        from src.utils.helpers import is_admin

        # Mock settings with empty super_admin_ids
        with patch("src.config.settings") as mock_settings:
            mock_settings.super_admin_ids = []

            # User doesn't exist in database
            result = await is_admin(999999)
            assert result is False

    @pytest.mark.asyncio
    async def test_is_admin_database_admin(self):
        """Test that database admins are recognized as admin."""
        from src.utils.helpers import is_admin

        # Create a user with is_admin=True in the database
        async with get_session() as session:
            user_repo = UserRepository(session)
            user, _ = await user_repo.get_or_create(
                telegram_id=111111,
                username="dbadmin",
                first_name="DB Admin"
            )
            await user_repo.set_admin(user.id, True)

        # Mock settings with empty super_admin_ids (not a super admin)
        with patch("src.config.settings") as mock_settings:
            mock_settings.super_admin_ids = []

            result = await is_admin(111111)
            assert result is True

    @pytest.mark.asyncio
    async def test_is_admin_user_exists_but_not_admin(self):
        """Test that existing users without admin flag are not admins."""
        from src.utils.helpers import is_admin

        # Create a regular user (is_admin=False by default)
        async with get_session() as session:
            user_repo = UserRepository(session)
            await user_repo.get_or_create(
                telegram_id=222222,
                username="regularuser",
                first_name="Regular User"
            )

        # Mock settings with empty super_admin_ids
        with patch("src.config.settings") as mock_settings:
            mock_settings.super_admin_ids = []

            result = await is_admin(222222)
            assert result is False

    @pytest.mark.asyncio
    async def test_is_admin_super_admin_takes_priority(self):
        """Test that super admin status takes priority over DB check."""
        from src.utils.helpers import is_admin

        # Mock settings to include test user as super admin
        with patch("src.config.settings") as mock_settings:
            mock_settings.super_admin_ids = [333333]

            # User doesn't exist in DB but is super admin
            result = await is_admin(333333)
            assert result is True


# =============================================================================
# PROFILE IMPORT/EXPORT HANDLER TESTS
# =============================================================================

class TestProfileImportExportHandlers:
    """Test profile import/export command handlers."""

    @pytest.mark.asyncio
    async def test_plantilla_perfiles_requires_admin(self):
        """Test that plantilla_perfiles requires admin permissions."""
        from src.handlers.profile_import import plantilla_perfiles_command
        from conftest import create_mock_update, create_mock_context

        update = create_mock_update(user_id=999999, username="regularuser")
        context = create_mock_context()

        # Mock is_admin to return False
        with patch("src.handlers.profile_import.is_admin", new_callable=AsyncMock) as mock_is_admin:
            mock_is_admin.return_value = False

            await plantilla_perfiles_command(update, context)

            # Should show error message
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "administradores" in call_args.lower()

    @pytest.mark.asyncio
    async def test_exportar_perfiles_requires_admin(self):
        """Test that exportar_perfiles requires admin permissions."""
        from src.handlers.profile_import import exportar_perfiles_command
        from conftest import create_mock_update, create_mock_context

        update = create_mock_update(user_id=999999, username="regularuser")
        context = create_mock_context()

        # Mock is_admin to return False
        with patch("src.handlers.profile_import.is_admin", new_callable=AsyncMock) as mock_is_admin:
            mock_is_admin.return_value = False

            await exportar_perfiles_command(update, context)

            # Should show error message
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "administradores" in call_args.lower()

    @pytest.mark.asyncio
    async def test_importar_perfiles_requires_admin(self):
        """Test that importar_perfiles requires admin permissions."""
        from src.handlers.profile_import import importar_perfiles_command
        from conftest import create_mock_update, create_mock_context

        update = create_mock_update(user_id=999999, username="regularuser")
        context = create_mock_context()

        # Mock is_admin to return False
        with patch("src.handlers.profile_import.is_admin", new_callable=AsyncMock) as mock_is_admin:
            mock_is_admin.return_value = False

            await importar_perfiles_command(update, context)

            # Should show error message
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "administradores" in call_args.lower()

    @pytest.mark.asyncio
    async def test_importar_perfiles_shows_instructions(self):
        """Test that importar_perfiles shows instructions for admins."""
        from src.handlers.profile_import import importar_perfiles_command
        from conftest import create_mock_update, create_mock_context

        update = create_mock_update(user_id=111111, username="admin")
        context = create_mock_context()

        # Mock is_admin to return True
        with patch("src.handlers.profile_import.is_admin", new_callable=AsyncMock) as mock_is_admin:
            mock_is_admin.return_value = True

            await importar_perfiles_command(update, context)

            # Should show instructions
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "Importar Perfiles" in call_args


# =============================================================================
# EXCEL IMPORT/EXPORT HANDLER TESTS
# =============================================================================

class TestExcelImportExportHandlers:
    """Test excel import/export command handlers."""

    @pytest.mark.asyncio
    async def test_importar_requires_admin(self):
        """Test that importar requires admin permissions."""
        from src.handlers.excel_import import importar_command
        from conftest import create_mock_update, create_mock_context

        update = create_mock_update(user_id=999999, username="regularuser")
        context = create_mock_context()

        # Mock is_admin to return False
        with patch("src.handlers.excel_import.is_admin", new_callable=AsyncMock) as mock_is_admin:
            mock_is_admin.return_value = False

            await importar_command(update, context)

            # Should show error message
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "administradores" in call_args.lower()

    @pytest.mark.asyncio
    async def test_exportar_requires_admin(self):
        """Test that exportar requires admin permissions."""
        from src.handlers.excel_import import exportar_command
        from conftest import create_mock_update, create_mock_context

        update = create_mock_update(user_id=999999, username="regularuser")
        context = create_mock_context()

        # Mock is_admin to return False
        with patch("src.handlers.excel_import.is_admin", new_callable=AsyncMock) as mock_is_admin:
            mock_is_admin.return_value = False

            await exportar_command(update, context)

            # Should show error message
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "administradores" in call_args.lower()

    @pytest.mark.asyncio
    async def test_importar_shows_instructions(self):
        """Test that importar shows instructions for admins."""
        from src.handlers.excel_import import importar_command
        from conftest import create_mock_update, create_mock_context

        update = create_mock_update(user_id=111111, username="admin")
        context = create_mock_context()

        # Mock is_admin to return True
        with patch("src.handlers.excel_import.is_admin", new_callable=AsyncMock) as mock_is_admin:
            mock_is_admin.return_value = True

            await importar_command(update, context)

            # Should show instructions
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "Importar desde Excel" in call_args
