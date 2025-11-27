"""
The Phantom Bot - Database Models
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# =============================================================================
# ENUMS
# =============================================================================

class TransactionType(str, Enum):
    """Types of transactions."""
    TRANSFER = "transfer"
    ADMIN_GIVE = "admin_give"
    ADMIN_REMOVE = "admin_remove"
    PUNISHMENT = "punishment"
    REWARD = "reward"
    AUCTION = "auction"
    IMPORT = "import"
    COLLAR = "collar"
    TRIBUTE = "tribute"
    DUNGEON = "dungeon"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    DEACTIVATED = "deactivated"


class CollarType(str, Enum):
    """Types of collars."""
    CONSIDERATION = "consideration"
    TRAINING = "training"
    FORMAL = "formal"


class PunishmentType(str, Enum):
    """Types of punishments."""
    HUMILIATION = "humiliation"
    PENITENCIA = "penitencia"
    TITLE = "title"
    WHIP = "whip"


class DungeonType(str, Enum):
    """Types of dungeon confinement."""
    CALABOZO = "calabozo"
    JAULA = "jaula"
    ENCADENADO = "encadenado"


class AuctionStatus(str, Enum):
    """Auction statuses."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ContractStatus(str, Enum):
    """Contract statuses."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    BROKEN = "broken"
    EXPIRED = "expired"


class RequestType(str, Enum):
    """Types of pending requests."""
    COLLAR = "collar"
    CONTRACT = "contract"


class MainRole(str, Enum):
    """Main BDSM roles."""
    DOM = "dom"
    SUB = "sub"
    SWITCH = "switch"


class ExperienceLevel(str, Enum):
    """Experience levels."""
    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"
    EXPERTO = "experto"


class PrivacyLevel(str, Enum):
    """Profile privacy levels."""
    PUBLIC = "public"
    MEMBERS = "members"
    VERIFIED = "verified"
    PRIVATE = "private"


class LimitType(str, Enum):
    """Types of limits."""
    HARD = "hard"
    SOFT = "soft"


# =============================================================================
# CORE MODELS
# =============================================================================

class User(Base):
    """User model - represents a Telegram user."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    balance: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    sent_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.sender_id",
        back_populates="sender",
        lazy="dynamic"
    )
    received_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.recipient_id",
        back_populates="recipient",
        lazy="dynamic"
    )
    profile: Mapped[Optional["Profile"]] = relationship(
        "Profile",
        back_populates="user",
        uselist=False
    )
    settings: Mapped[Optional["UserSettings"]] = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False
    )

    @property
    def display_name(self) -> str:
        """Get user display name."""
        if self.username:
            return f"@{self.username}"
        elif self.first_name:
            return self.first_name
        return f"User#{self.telegram_id}"

    @property
    def full_name(self) -> str:
        """Get user full name."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else self.display_name

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username}, balance={self.balance})>"


class Transaction(Base):
    """Transaction model - records all balance changes."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )
    recipient_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType),
        nullable=False,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    admin_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
        index=True
    )

    # Relationships
    sender: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_transactions"
    )
    recipient: Mapped["User"] = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="received_transactions"
    )
    admin: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[admin_id]
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"


class Admin(Base):
    """Admin model - tracks group admins."""
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    granted_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<Admin(user_id={self.user_id}, group_id={self.group_id})>"


class Cooldown(Base):
    """Cooldown model - tracks user cooldowns."""
    __tablename__ = "cooldowns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<Cooldown(user_id={self.user_id}, action={self.action}, expires_at={self.expires_at})>"


# =============================================================================
# BDSM MODELS
# =============================================================================

class Collar(Base):
    """Collar model - ownership relationships."""
    __tablename__ = "collars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    sub_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True,  # A sub can only have one collar
        index=True
    )
    collar_type: Mapped[CollarType] = mapped_column(
        SQLEnum(CollarType),
        default=CollarType.FORMAL,
        nullable=False
    )
    public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id])
    sub: Mapped["User"] = relationship("User", foreign_keys=[sub_id])

    def __repr__(self) -> str:
        return f"<Collar(owner_id={self.owner_id}, sub_id={self.sub_id}, type={self.collar_type})>"


class PendingRequest(Base):
    """Pending requests for collars/contracts."""
    __tablename__ = "pending_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_type: Mapped[RequestType] = mapped_column(
        SQLEnum(RequestType),
        nullable=False
    )
    from_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    to_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    reference_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    collar_type: Mapped[Optional[CollarType]] = mapped_column(
        SQLEnum(CollarType),
        nullable=True
    )
    # Contract request fields
    terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    # Relationships
    from_user: Mapped["User"] = relationship("User", foreign_keys=[from_user_id])
    to_user: Mapped["User"] = relationship("User", foreign_keys=[to_user_id])

    def __repr__(self) -> str:
        return f"<PendingRequest(type={self.request_type}, from={self.from_user_id}, to={self.to_user_id})>"


class Punishment(Base):
    """Punishment model - humiliations, penitencias, titles."""
    __tablename__ = "punishments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    punisher_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    punishment_type: Mapped[PunishmentType] = mapped_column(
        SQLEnum(PunishmentType),
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    punisher: Mapped["User"] = relationship("User", foreign_keys=[punisher_id])

    def __repr__(self) -> str:
        return f"<Punishment(id={self.id}, type={self.punishment_type}, user_id={self.user_id})>"


class Dungeon(Base):
    """Dungeon model - users locked in calabozo/jaula."""
    __tablename__ = "dungeon"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        primary_key=True
    )
    locked_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    dungeon_type: Mapped[DungeonType] = mapped_column(
        SQLEnum(DungeonType),
        nullable=False
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    locker: Mapped["User"] = relationship("User", foreign_keys=[locked_by])

    def __repr__(self) -> str:
        return f"<Dungeon(user_id={self.user_id}, type={self.dungeon_type})>"


class Auction(Base):
    """Auction model - users auctioning other users or services."""
    __tablename__ = "auctions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    target_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    starting_price: Mapped[int] = mapped_column(Integer, nullable=False)
    current_bid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_bidder_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[AuctionStatus] = mapped_column(
        SQLEnum(AuctionStatus),
        default=AuctionStatus.ACTIVE,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    # Relationships
    seller: Mapped["User"] = relationship("User", foreign_keys=[seller_id])
    target: Mapped[Optional["User"]] = relationship("User", foreign_keys=[target_id])
    current_bidder: Mapped[Optional["User"]] = relationship("User", foreign_keys=[current_bidder_id])
    bids: Mapped[list["Bid"]] = relationship("Bid", back_populates="auction")

    def __repr__(self) -> str:
        return f"<Auction(id={self.id}, seller_id={self.seller_id}, status={self.status})>"


class Bid(Base):
    """Bid model - bids on auctions."""
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    auction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("auctions.id"),
        nullable=False,
        index=True
    )
    bidder_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    # Relationships
    auction: Mapped["Auction"] = relationship("Auction", back_populates="bids")
    bidder: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<Bid(id={self.id}, auction_id={self.auction_id}, amount={self.amount})>"


class Contract(Base):
    """Contract model - formal agreements between users."""
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dom_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    sub_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    terms: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ContractStatus] = mapped_column(
        SQLEnum(ContractStatus),
        default=ContractStatus.PENDING,
        nullable=False
    )
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    broken_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    # Relationships
    dom: Mapped["User"] = relationship("User", foreign_keys=[dom_id])
    sub: Mapped["User"] = relationship("User", foreign_keys=[sub_id])
    breaker: Mapped[Optional["User"]] = relationship("User", foreign_keys=[broken_by])

    def __repr__(self) -> str:
        return f"<Contract(id={self.id}, dom_id={self.dom_id}, sub_id={self.sub_id}, status={self.status})>"


class Altar(Base):
    """Altar model - passive income altars."""
    __tablename__ = "altars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    for_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )
    built_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    daily_amount: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    # Relationships
    for_user: Mapped["User"] = relationship("User", foreign_keys=[for_user_id])
    builder: Mapped["User"] = relationship("User", foreign_keys=[built_by])

    def __repr__(self) -> str:
        return f"<Altar(for_user_id={self.for_user_id}, daily_amount={self.daily_amount})>"


# =============================================================================
# PROFILE MODELS
# =============================================================================

class Profile(Base):
    """Extended user profile information."""
    __tablename__ = "profiles"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        primary_key=True
    )
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pronouns: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    show_age: Mapped[str] = mapped_column(String(20), default="exact", nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    main_role: Mapped[Optional[MainRole]] = mapped_column(
        SQLEnum(MainRole),
        nullable=True
    )
    sub_roles: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    experience_level: Mapped[Optional[ExperienceLevel]] = mapped_column(
        SQLEnum(ExperienceLevel),
        nullable=True
    )
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    looking_for: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    availability: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    profile_completeness: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    kinks: Mapped[list["UserKink"]] = relationship("UserKink", back_populates="profile")
    limits: Mapped[list["UserLimit"]] = relationship("UserLimit", back_populates="profile")

    def __repr__(self) -> str:
        return f"<Profile(user_id={self.user_id}, role={self.main_role})>"


class Kink(Base):
    """Reference table for predefined kinks."""
    __tablename__ = "kinks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Kink(id={self.id}, name={self.name}, category={self.category})>"


class UserKink(Base):
    """User's kink preferences."""
    __tablename__ = "user_kinks"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("profiles.user_id"),
        primary_key=True
    )
    kink_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("kinks.id"),
        primary_key=True
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-3 stars
    direction: Mapped[str] = mapped_column(String(20), nullable=False)  # give/receive/both
    curious: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="kinks")
    kink: Mapped["Kink"] = relationship("Kink")

    def __repr__(self) -> str:
        return f"<UserKink(user_id={self.user_id}, kink_id={self.kink_id}, level={self.level})>"


class UserLimit(Base):
    """User's hard and soft limits."""
    __tablename__ = "user_limits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("profiles.user_id"),
        nullable=False,
        index=True
    )
    limit_type: Mapped[LimitType] = mapped_column(
        SQLEnum(LimitType),
        nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="limits")

    def __repr__(self) -> str:
        return f"<UserLimit(id={self.id}, type={self.limit_type})>"


class UserSettings(Base):
    """User privacy and notification settings."""
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        primary_key=True
    )
    privacy_level: Mapped[PrivacyLevel] = mapped_column(
        SQLEnum(PrivacyLevel),
        default=PrivacyLevel.MEMBERS,
        nullable=False
    )
    notify_transfers: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_mentions: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_bdsm: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettings(user_id={self.user_id}, privacy={self.privacy_level})>"
