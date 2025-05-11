from pydantic import BaseModel, Field, ConfigDict, EmailStr

from src.config import constants
from src.config import messages
from src.entity.models import UserRole


class UserBase(BaseModel):
    """User base schema."""
    username: str = Field(
        min_length=constants.USERNAME_MIN_LENGTH,
        max_length=constants.USERNAME_MAX_LENGTH,
        description=messages.username_schema.get("en"),
    )
    email: EmailStr


class UserCreate(UserBase):
    """User create schema."""
    password: str = Field(
        min_length=constants.USER_PASSWORD_MIN_LENGTH,
        max_length=constants.USER_PASSWORD_MAX_LENGTH,
        description=messages.password_schema.get("en"),
    )


class UserResponse(UserBase):
    """User response schema."""
    id: int
    role: UserRole
    avatar: str | None

    model_config = ConfigDict(from_attributes=True)