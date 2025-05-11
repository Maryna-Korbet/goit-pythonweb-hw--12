from datetime import datetime, date
from typing import Optional
from enum import Enum

from sqlalchemy import (
    String, 
    DateTime, 
    func, 
    Date,
    Text,
    ForeignKey,
    Boolean,
    Enum as SqlEnum
)
from sqlalchemy.orm import (
    DeclarativeBase, 
    Mapped, 
    mapped_column, 
    relationship
)

from src.config import constants
from src.config import messages


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Contact(Base):
    """Represents a contact in the system."""
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(
        String(
            constants.FIRST_NAME_MIN_LENGTH, 
            constants.FIRST_NAME_MAX_LENGTH
        ), 
        nullable=False,
        comment=messages.contact_schema_first_name.get('en')
    )
    last_name: Mapped[str] = mapped_column(
        String(constants.LAST_NAME_MIN_LENGTH, constants.LAST_NAME_MAX_LENGTH), 
        nullable=False,
        comment=messages.contact_schema_last_name.get('en')
    )
    email: Mapped[str] = mapped_column(
        String(constants.EMAIL_MIN_LENGTH, constants.EMAIL_MAX_LENGTH), 
        nullable=False,
        unique=True,
        index=True,
        comment=messages.contact_schema_email.get('en')
    )
    phone: Mapped[str | None] = mapped_column(
        String(constants.PHONE_MIN_LENGTH, constants.PHONE_MAX_LENGTH),
        nullable=True,
        comment=messages.contact_schema_phone.get('en')
    )
    birthday: Mapped[date | None] = mapped_column(
        Date, 
        nullable=True,
        comment=messages.contact_schema_birthday.get('en')
    )
    additional_info: Mapped[str | None] = mapped_column(
        String(255), 
        nullable=True,
        comment=messages.contact_schema_additional_info.get('en')
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=func.now(),
        comment=messages.contact_schema_created_at.get('en')
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=func.now(), 
        onupdate=func.now(),
        comment=messages.contact_schema_updated_at.get('en')
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")
    

class UserRole(str, Enum):
    """Represents a user role in the system."""
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class User(Base):
    """Represents a user in the system."""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hash_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole), default=UserRole.USER, nullable=False
    )
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user"
    )


class RefreshToken(Base):
    """Represents a refresh token in the system."""
    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    expired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    """ revoked_at: Mapped[datetime] | None = mapped_column(DateTime(timezone=True), nullable=True) """
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")