"""
The Phantom Bot - Database Repositories Module

This module provides modular repository classes for database operations.
Each repository handles a specific domain entity.
"""

from src.database.repositories.admin import AdminRepository
from src.database.repositories.altar import AltarRepository
from src.database.repositories.auction import AuctionRepository
from src.database.repositories.base import BaseRepository
from src.database.repositories.collar import CollarRepository
from src.database.repositories.contract import ContractRepository
from src.database.repositories.cooldown import CooldownRepository
from src.database.repositories.dungeon import DungeonRepository
from src.database.repositories.pending_request import PendingRequestRepository
from src.database.repositories.profile import ProfileRepository, UserSettingsRepository
from src.database.repositories.punishment import PunishmentRepository
from src.database.repositories.transaction import TransactionRepository
from src.database.repositories.user import UserRepository

__all__ = [
    # Base
    "BaseRepository",
    # Core
    "UserRepository",
    "TransactionRepository",
    "AdminRepository",
    "CooldownRepository",
    # BDSM
    "CollarRepository",
    "PendingRequestRepository",
    "PunishmentRepository",
    "DungeonRepository",
    "AuctionRepository",
    "ContractRepository",
    # Profile
    "ProfileRepository",
    "UserSettingsRepository",
    # Economy
    "AltarRepository",
]
