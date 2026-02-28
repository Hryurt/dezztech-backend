from fastapi import APIRouter, BackgroundTasks, Depends, status

from src.auth.dependencies import get_current_active_user
from src.users.dependencies import get_user_service
from src.users.models import User
from src.users.schemas import (
    DeleteAccountRequest,
    EmailChangeRequest,
    EmailChangeVerifyRequest,
    UserChangePasswordRequest,
    UserMeResponse,
    UserMeUpdateRequest,
)
from src.users.service import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=UserMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserMeResponse:
    """Get current authenticated user's profile."""
    return current_user


@router.patch(
    "/me",
    response_model=UserMeResponse,
    summary="Update current user profile",
)
async def update_me(
    data: UserMeUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> UserMeResponse:
    """Update current authenticated user's profile."""
    updated_user = await user_service.update_current_user(current_user, data)
    return updated_user


@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change current user password",
)
async def change_password(
    data: UserChangePasswordRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> None:
    """Change current authenticated user's password."""
    await user_service.change_password(current_user, data)
    background_tasks.add_task(
        user_service.send_password_changed_email,
        current_user,
    )


@router.post(
    "/me/email-change-request",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Request email change",
)
async def email_change_request(
    data: EmailChangeRequest,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> None:
    """Request email change. OTP sent to new email."""
    await user_service.request_email_change(
        current_user, data.new_email, data.current_password
    )


@router.post(
    "/me/email-change-verify",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Verify email change",
)
async def email_change_verify(
    data: EmailChangeVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> None:
    """Verify email change with OTP code."""
    await user_service.confirm_email_change(current_user, data.code)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate current user account",
)
async def delete_me(
    data: DeleteAccountRequest,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> None:
    """Soft delete (deactivate) current authenticated user's account."""
    await user_service.deactivate_account(current_user, data)
