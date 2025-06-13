from pydantic import BaseModel, EmailStr, Field

from src.config import constants, messages


class ResetPasswordRequestSchema(BaseModel):
    """Reset password request schema."""
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    """Reset password schema."""
    token: str
    new_password: str = Field(
        min_length=constants.USER_PASSWORD_MIN_LENGTH,
        max_length=constants.USER_PASSWORD_MAX_LENGTH,
        description=messages.password_schema.get("en"),
    )