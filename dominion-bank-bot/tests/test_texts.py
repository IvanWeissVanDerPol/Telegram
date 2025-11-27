"""
Tests for the YAML text loader system.
Tests the text loading, caching, formatting, and helper functions.
"""
import pytest
import os

# Set test database URL BEFORE importing
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"


class TestTextLoader:
    """Test the TextLoader class and YAML loading."""

    def test_loader_is_singleton(self):
        """Test that TextLoader returns same instance."""
        from src.utils.texts import TextLoader

        loader1 = TextLoader()
        loader2 = TextLoader()
        assert loader1 is loader2

    def test_loader_loads_all_yaml_files(self):
        """Test that all YAML files are loaded."""
        from src.utils.texts import texts

        # Check all expected categories are loaded
        assert texts.emojis is not None
        assert texts.errors is not None
        assert texts.core is not None
        assert texts.bdsm is not None
        assert texts.help is not None
        assert texts.ai_responses is not None

    def test_emojis_loaded_correctly(self):
        """Test emoji categories are loaded."""
        from src.utils.texts import texts

        emojis = texts.emojis
        assert "status" in emojis
        assert "features" in emojis
        assert "bdsm" in emojis
        assert "roles" in emojis
        assert "dividers" in emojis

    def test_errors_loaded_correctly(self):
        """Test error messages are loaded."""
        from src.utils.texts import texts

        errors = texts.errors
        assert "errors" in errors
        assert "bdsm_errors" in errors
        assert "warnings" in errors
        assert "info" in errors
        assert "usage" in errors


class TestGetEmoji:
    """Test the get_emoji helper function."""

    def test_get_status_emoji(self):
        """Test getting status emojis."""
        from src.utils.texts import get_emoji

        success = get_emoji("status", "success")
        error = get_emoji("status", "error")
        warning = get_emoji("status", "warning")

        assert success == "✅"
        assert error == "❌"
        assert warning == "⚠️"

    def test_get_feature_emoji(self):
        """Test getting feature emojis."""
        from src.utils.texts import get_emoji

        balance = get_emoji("features", "balance")
        transfer = get_emoji("features", "transfer")

        assert balance == "💰"
        assert transfer == "💸"

    def test_get_bdsm_emoji(self):
        """Test getting BDSM emojis."""
        from src.utils.texts import get_emoji

        collar = get_emoji("bdsm", "collar")
        whip = get_emoji("bdsm", "whip")
        dungeon = get_emoji("bdsm", "dungeon")

        assert collar == "⛓️"
        assert whip == "🔥"
        assert dungeon == "🏰"

    def test_get_nonexistent_emoji_returns_empty(self):
        """Test getting non-existent emoji returns empty string."""
        from src.utils.texts import get_emoji

        result = get_emoji("nonexistent", "emoji")
        assert result == ""


class TestGetDivider:
    """Test the get_divider helper function."""

    def test_get_default_divider(self):
        """Test getting default divider."""
        from src.utils.texts import get_divider

        divider = get_divider()
        assert "━" in divider

    def test_get_light_divider(self):
        """Test getting light divider."""
        from src.utils.texts import get_divider

        divider = get_divider("light")
        assert "┈" in divider

    def test_get_double_divider(self):
        """Test getting double divider."""
        from src.utils.texts import get_divider

        divider = get_divider("double")
        assert "═" in divider


class TestGetError:
    """Test the get_error helper function."""

    def test_get_error_not_registered(self):
        """Test getting not registered error."""
        from src.utils.texts import get_error

        error = get_error("not_registered")
        assert "registr" in error.lower()
        assert "❌" in error

    def test_get_error_user_not_found(self):
        """Test getting user not found error."""
        from src.utils.texts import get_error

        error = get_error("user_not_found")
        assert "usuario" in error.lower() or "encontr" in error.lower()

    def test_get_error_insufficient_balance(self):
        """Test getting insufficient balance error."""
        from src.utils.texts import get_error

        error = get_error("insufficient_balance")
        assert "saldo" in error.lower() or "insuficiente" in error.lower()


class TestGetCoreMessage:
    """Test the get_core_message helper function."""

    def test_get_welcome_new_user(self):
        """Test getting welcome message for new user."""
        from src.utils.texts import get_core_message

        msg = get_core_message(
            "welcome", "new_user",
            bot_name="TestBot",
            display_name="TestUser",
            balance="100 Gemas"
        )
        assert "TestBot" in msg or "Bienvenido" in msg

    def test_get_balance_check_positive(self):
        """Test getting positive balance message."""
        from src.utils.texts import get_core_message

        msg = get_core_message("balance", "check_positive", balance="500 Gemas")
        assert "500" in msg or "saldo" in msg.lower()


class TestGetBdsmMessage:
    """Test the get_bdsm_message helper function."""

    def test_get_collar_request_sent(self):
        """Test getting collar request sent message."""
        from src.utils.texts import get_bdsm_message

        msg = get_bdsm_message(
            "collars", "request_sent",
            target="TestUser",
            cost="300 Gemas"
        )
        assert "collar" in msg.lower() or "solicitud" in msg.lower()

    def test_get_dungeon_locked(self):
        """Test getting dungeon locked message."""
        from src.utils.texts import get_bdsm_message

        msg = get_bdsm_message(
            "dungeon", "locked",
            jailer="Dom",
            prisoner="Sub",
            hours=24,
            cost="200 Gemas"
        )
        assert "calabozo" in msg.lower() or "encerr" in msg.lower()


class TestGetAiResponse:
    """Test the get_ai_response helper function."""

    def test_get_roulette_response(self):
        """Test getting roulette response template."""
        from src.utils.texts import get_ai_response

        msg = get_ai_response("roulette", "response", user="TestUser")
        assert "ruleta" in msg.lower() or "destino" in msg.lower()

    def test_get_dice_response(self):
        """Test getting dice response template."""
        from src.utils.texts import get_ai_response

        msg = get_ai_response("dice", "response", user="TestUser", dice_type="sumiso")
        assert "dado" in msg.lower()


class TestGetAiData:
    """Test the get_ai_data helper function."""

    def test_get_dice_types(self):
        """Test getting dice types dict."""
        from src.utils.texts import get_ai_data

        dice_types = get_ai_data("dice", "types")
        assert dice_types is not None
        assert isinstance(dice_types, dict)
        assert "accion" in dice_types
        assert "intensidad" in dice_types
        assert isinstance(dice_types["accion"], list)

    def test_get_roulette_options(self):
        """Test getting roulette options."""
        from src.utils.texts import get_ai_data

        options = get_ai_data("roulette", "options")
        assert options is not None
        assert isinstance(options, dict)
        assert "reward" in options
        assert "punishment" in options


class TestFormatText:
    """Test the internal _format_text function."""

    def test_format_replaces_emoji_placeholders(self):
        """Test that emoji placeholders are replaced."""
        from src.utils.texts import get_error

        # Error messages use placeholders like {error}
        error = get_error("not_registered")
        # Should have actual emoji, not placeholder
        assert "{error}" not in error
        assert "❌" in error

    def test_format_with_custom_kwargs(self):
        """Test formatting with custom kwargs."""
        from src.utils.texts import get_core_message

        msg = get_core_message(
            "transfer", "success_sender",
            amount="100 Gemas",
            recipient="@TestUser",
            new_balance="400 Gemas"
        )
        # Custom values should be in message
        assert "TestUser" in msg or "100" in msg


class TestTextLoaderGet:
    """Test the TextLoader.get and get_nested methods."""

    def test_get_existing_key(self):
        """Test getting existing key."""
        from src.utils.texts import texts

        result = texts.get("emojis", "status")
        assert result is not None
        assert isinstance(result, dict)

    def test_get_nonexistent_key_returns_default(self):
        """Test getting non-existent key returns default."""
        from src.utils.texts import texts

        result = texts.get("nonexistent", "key", default="fallback")
        assert result == "fallback"

    def test_get_nested_value(self):
        """Test getting nested value."""
        from src.utils.texts import texts

        result = texts.get_nested("emojis", "status", "success")
        assert result == "✅"

    def test_get_nested_nonexistent_returns_default(self):
        """Test getting non-existent nested value returns default."""
        from src.utils.texts import texts

        result = texts.get_nested("nonexistent", "path", "here", default="nope")
        assert result == "nope"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
