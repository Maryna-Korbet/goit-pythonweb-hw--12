from fastapi import (
    Depends,
    HTTPException
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth_services import AuthService, oauth2_scheme
from src.services.user_services import UserService
from src.entity.models import User, UserRole
from src.services.cache import get_cache_service
from src.config import messages
from src.database.db import get_db


def get_auth_service(
        db: AsyncSession = Depends(get_db),
        cache_service: get_cache_service = Depends(get_cache_service)):
    """Get auth service."""
    return AuthService(db, cache_service)


def get_user_service(
        db: AsyncSession = Depends(get_db),
        cache_service: get_cache_service = Depends(get_cache_service)):
    """Get user service."""
    return UserService(db, cache_service)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get current user."""
    return await auth_service.get_current_user(token)


# Get current Moderator
def get_current_moderator_user(current_user: User = Depends(get_current_user)):
    """Get current moderator user."""
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403, 
            detail=messages.role_access_info.get("en")
            )
    return current_user


# Get current Admin
def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """Get current admin user."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, 
            detail=messages.role_access_info.get("en")
            )
    return current_user