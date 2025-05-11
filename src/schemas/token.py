from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str