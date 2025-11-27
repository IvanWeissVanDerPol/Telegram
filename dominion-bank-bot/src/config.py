"""
The Phantom Bot - Configuration
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")

    # Telegram Bot
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    telegram_api_id: Optional[str] = Field(default=None, alias="TELEGRAM_API_ID")
    telegram_api_hash: Optional[str] = Field(default=None, alias="TELEGRAM_API_HASH")

    # Bot Identity
    bot_name: str = Field(default="The Phantom", alias="BOT_NAME")
    bot_username: str = Field(default="ThePhantomSadoBot", alias="BOT_USERNAME")
    currency_name: str = Field(default="SadoCoins", alias="CURRENCY_NAME")
    currency_symbol: str = Field(default="SC", alias="CURRENCY_SYMBOL")
    currency_emoji: str = Field(default="⛓️", alias="CURRENCY_EMOJI")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/phantom.db",
        alias="DATABASE_URL"
    )
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # Admin Configuration
    super_admins: str = Field(default="", alias="SUPER_ADMINS")
    default_balance: int = Field(default=0, alias="DEFAULT_BALANCE")
    max_transfer_amount: int = Field(default=1000000, alias="MAX_TRANSFER_AMOUNT")
    min_transfer_amount: int = Field(default=1, alias="MIN_TRANSFER_AMOUNT")

    # Rate Limiting
    transfer_cooldown: int = Field(default=5, alias="TRANSFER_COOLDOWN")
    rate_limit_commands: int = Field(default=30, alias="RATE_LIMIT_COMMANDS")
    ranking_cache_ttl: int = Field(default=60, alias="RANKING_CACHE_TTL")

    # Feature Flags
    enable_transfers: bool = Field(default=True, alias="ENABLE_TRANSFERS")
    enable_ranking: bool = Field(default=True, alias="ENABLE_RANKING")
    enable_history: bool = Field(default=True, alias="ENABLE_HISTORY")
    enable_bdsm_commands: bool = Field(default=False, alias="ENABLE_BDSM_COMMANDS")
    enable_excel_import: bool = Field(default=True, alias="ENABLE_EXCEL_IMPORT")

    # Security
    allow_debt: bool = Field(default=False, alias="ALLOW_DEBT")
    max_debt_amount: int = Field(default=0, alias="MAX_DEBT_AMOUNT")

    # Logging
    log_level: str = Field(default="DEBUG", alias="LOG_LEVEL")
    log_format: str = Field(default="text", alias="LOG_FORMAT")

    # Localization
    default_language: str = Field(default="es", alias="DEFAULT_LANGUAGE")
    timezone: str = Field(default="America/Asuncion", alias="TIMEZONE")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def super_admin_ids(self) -> list[int]:
        """Parse super admin IDs from comma-separated string."""
        if not self.super_admins:
            return []
        return [int(id.strip()) for id in self.super_admins.split(",") if id.strip()]

    def is_super_admin(self, user_id: int) -> bool:
        """Check if user is a super admin."""
        return user_id in self.super_admin_ids


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Load settings
def get_settings() -> Settings:
    """Get application settings instance."""
    # Try multiple .env locations
    env_paths = [
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "phantom.env",
        PROJECT_ROOT / "config.env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            return Settings(_env_file=str(env_path))

    return Settings()


settings = get_settings()
