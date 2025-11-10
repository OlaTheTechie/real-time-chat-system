"""
Authentication routes using class-based views
"""
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.redis_client import get_redis
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.auth.schemas import (
    UserCreate, UserLogin, UserResponse, Token, TokenRefresh,
    PasswordResetRequest, PasswordResetConfirm
)
from app.auth.views import AuthViews

router = APIRouter()

# register endpoint
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    return AuthViews.register(user_data, db)


# login endpoint
@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens"""
    return AuthViews.login(user_credentials, db)


# logout endpoint
@router.post("/logout")
def logout_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout user and update online status"""
    return AuthViews.logout(current_user, db)


# refresh token endpoint
@router.post("/refresh", response_model=Token)
def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    return AuthViews.refresh_token(token_data, db)


# get current user profile (session check)
@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile - session check"""
    return AuthViews.get_current_user_profile(current_user)


# get all users (for chat)
@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users for chat purposes"""
    return AuthViews.get_all_users(current_user, db)


# password reset request
@router.post("/password-reset")
def request_password_reset(
    reset_request: PasswordResetRequest, 
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Request a password reset token"""
    return AuthViews.request_password_reset(reset_request, db, redis_client)


# password reset confirmation
@router.post("/password-reset-confirm")
def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Confirm password reset with token and new password"""
    return AuthViews.confirm_password_reset(reset_confirm, db, redis_client)