from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    status,
    BackgroundTasks,
    UploadFile,
    File,
)
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.services.auth_services import AuthService, oauth2_scheme
from src.schemas.user_schema import UserResponse,
from src.schemas.password_schema import ResetPasswordRequestSchema, ResetPasswordSchema
from src.entity.models import User
from src.config import messages
from src.core.depend_service import (
    get_auth_service,
    get_current_admin_user,
    get_current_moderator_user,
    get_user_service,
    get_current_user,
)
from src.services.user_services import UserService
from src.schemas.email_schema import RequestEmail
from src.services.email_services import send_email
from src.core.email_token import get_email_from_token
from src.services.upload_file_services import UploadFileService
from src.config.config import settings



router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=UserResponse)
@limiter.limit("10/minute")
async def me(
    request: Request,
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get current user."""
    return await auth_service.get_current_user(token)


@router.get("/confirmed_email/{token}")
async def confirmed_email(
    token: str, user_service: UserService = Depends(get_user_service)
):
    """Confirmed email."""
    email = get_email_from_token(token)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Verification error"
        )
    if user.confirmed:
        return {"message": messages.email_already_confirmed.get("en")}
    await user_service.confirmed_email(email)
    return {"message": messages.email_confirmed.get("en")}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    """Request email."""
    user = await user_service.get_user_by_email(str(body.email))

    if user.confirmed:
        return {"message": messages.email_already_confirmed.get("en")}
    if user:
        background_tasks.add_task(
            send_email, 
            user.email, 
            user.username, 
            str(request.base_url)
        )
    return {"message": messages.email_confirm_request.get("en")}


@router.get("/moderator")
def read_moderator(
    current_user: User = Depends(get_current_moderator_user),
):
    """Read moderator."""
    return {
        "message": messages.welcome_messages["moderator"]
        .get("en")
        .format(username=current_user.username)
    }

@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Update avatar user."""
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME, 
        settings.CLOUDINARY_API_KEY, 
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.username)
    user = await user_service.update_avatar_url(user.email, avatar_url)
    return user


@router.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin_user)):
    """Read admin."""
    return {
        "message": messages.welcome_messages["admin"]
        .get("en")
        .format(username=current_user.username)
    }


@router.post("/request_password_reset")
async def request_password_reset(
    body: ResetPasswordRequestSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    """Request password reset."""
    user = await user_service.request_password_reset(str(body.email))
    if user:
        background_tasks.add_task(
            send_email,
            user.email,
            user.username,
            str(request.base_url),
            "reset_password"
        )
    return {"message": messages.password_reset_email_sent.get("en")}


@router.post("/reset_password/{token}")
async def reset_password(
    token: str,
    body: ResetPasswordSchema,
    user_service: UserService = Depends(get_user_service),
):
    """Reset password."""
    await user_service.reset_password(token, body.new_password)
    return {"message": messages.password_reset_success.get("en")}