"""Authentication routes — sign-in, sign-up, change-password, sign-out, me."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.dependencies import get_current_active_user
from app.core.security import JWTBearer
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePassword,
    GenericMessage,
    Payload,
    SignIn,
    SignInResponse,
    SignUp,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/sign-in", response_model=SignInResponse)
def sign_in(
    payload: SignIn,
    request: Request,
    db: Session = Depends(get_db),
):
    response = AuthService(db).sign_in(payload)
    log_action(
        db,
        user_id=response.user_info.id,
        action="login",
        entity="user",
        entity_id=response.user_info.id,
        ip_address=request.client.host if request.client else None,
    )
    return response


@router.post("/sign-up", response_model=SignInResponse, status_code=201)
def sign_up(
    payload: SignUp,
    request: Request,
    db: Session = Depends(get_db),
):
    response = AuthService(db).sign_up(payload)
    log_action(
        db,
        user_id=response.user_info.id,
        action="sign_up",
        entity="user",
        entity_id=response.user_info.id,
        ip_address=request.client.host if request.client else None,
    )
    return response


@router.get("/me", response_model=Payload)
def me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return AuthService(db).me(current_user)


@router.post("/change-password", response_model=GenericMessage)
def change_password(
    payload: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    AuthService(db).change_password(current_user, payload)
    log_action(
        db,
        user_id=current_user.id,
        action="change_password",
        entity="user",
        entity_id=current_user.id,
    )
    return GenericMessage(message="Password updated successfully")


@router.post("/sign-out", response_model=GenericMessage)
def sign_out(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    token: str = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    AuthService(db).sign_out(current_user, token)
    log_action(
        db,
        user_id=current_user.id,
        action="logout",
        entity="user",
        entity_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
    return GenericMessage(message="Signed out successfully")
