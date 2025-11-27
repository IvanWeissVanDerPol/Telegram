"""
Pytest configuration and fixtures for test isolation.
Uses an in-memory SQLite database to ensure test isolation.
"""
import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

# Set test database URL BEFORE importing the database module
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_test_database():
    """Setup a fresh in-memory database for each test."""
    # Import here to use the patched DATABASE_URL
    from src.database.connection import init_database, close_database, _engine

    # Reset the engine to None to force re-creation with test URL
    import src.database.connection as conn_module
    conn_module._engine = None

    # Initialize fresh database
    await init_database()

    yield

    # Cleanup
    await close_database()
    conn_module._engine = None


# =============================================================================
# MOCK HELPERS
# =============================================================================

def create_mock_update(user_id: int, username: str, chat_id: int = None, args: list = None):
    """Create a mock Telegram Update object."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = user_id
    update.effective_user.username = username
    update.effective_user.first_name = f"User{user_id}"
    update.effective_user.last_name = None

    update.effective_chat = MagicMock()
    update.effective_chat.id = chat_id or user_id
    update.effective_chat.type = "private"

    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_html = AsyncMock()

    return update


def create_mock_context(args: list = None):
    """Create a mock Context object."""
    context = MagicMock()
    context.args = args or []
    context.bot = MagicMock()
    context.bot.get_chat_member = AsyncMock()
    context.bot.send_message = AsyncMock()
    return context
