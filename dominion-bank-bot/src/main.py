"""
The Phantom Bot - Main Entry Point
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings, LOGS_DIR
from src.bot.application import create_application


def setup_logging() -> None:
    """Configure logging for the application."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Create formatter
    if settings.log_format == "json":
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", '
            '"name": "%(name)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # File handler
    log_file = LOGS_DIR / "phantom.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Reduce noise from libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)


def main() -> None:
    """Main entry point."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 50)
    logger.info(f"Starting {settings.bot_name}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug: {settings.debug}")
    logger.info("=" * 50)

    # Create and run application
    application = create_application()

    # Run the bot
    logger.info("Starting bot polling...")
    application.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
