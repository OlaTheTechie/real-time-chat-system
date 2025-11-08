"""
Class-based views for authentication endpoints
"""
from datetime import timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.auth.schemas import (
    UserCreate, UserLogin, UserResponse, Token, TokenRefresh,
    PasswordResetRequest, PasswordResetConfirm
)
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.core.security import (
    create_access_token, create_refresh_token, verify_password, 
    get_password_hash, verify_token
)
from app.core.config import settings
from app.auth.password_reset_service import PasswordResetService
from app.database.redis_client import get_redis


class AuthViews:
    """Class-based views for authentication operations"""
    
    @staticmethod
    def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
        """
        Register a new user
        
        Time Complexity: O(1) - database query with index lookup
        Space Complexity: O(1) - single user object
        """
        # check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def login(user_credentials: UserLogin, db: Session = Depends(get_db)) -> Token:
        """
        Authenticate user and return JWT tokens
        
        Time Complexity: O(1) - database query with index lookup
        Space Complexity: O(1) - token strings
        """
        # find user by email
        user = db.query(User).filter(User.email == user_credentials.email).first()
        
        if not user or not verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # update user online status
        user.is_online = True
        db.commit()
        
        # create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
        """
        Logout user and update online status
        
        Time Complexity: O(1) - single database update
        Space Complexity: O(1)
        """
        current_user.is_online = False
        db.commit()
        
        return {"message": "Successfully logged out"}
    
    @staticmethod
    def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)) -> Token:
        """
        Refresh access token using refresh token
        
        Time Complexity: O(1) - token verification and database lookup
        Space Complexity: O(1) - token strings
        """
        payload = verify_token(token_data.refresh_token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # verify user exists
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def get_current_user_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
        """
        Get current user profile (session check)
        
        Time Complexity: O(1) - user already loaded from token
        Space Complexity: O(1)
        """
        return current_user
    
    @staticmethod
    def request_password_reset(
        reset_request: PasswordResetRequest, 
        db: Session = Depends(get_db),
        redis_client = Depends(get_redis)
    ) -> dict:
        """
        Request a password reset token
        
        Time Complexity: O(1) - database lookup and Redis set
        Space Complexity: O(1) - token string
        """
        reset_service = PasswordResetService(db, redis_client)
        token = reset_service.create_reset_token(reset_request.email)
        
        if token:
            # in a real application, you would send this token via email
            # for now, we'll return it in the response for testing purposes
            return {
                "message": "Password reset token generated successfully",
                "token": token,  # remove this in production - send via email instead
                "note": "In production, this token would be sent via email"
            }
        else:
            # don't reveal whether the email exists or not for security
            return {
                "message": "If the email exists, a password reset token has been sent"
            }
    
    @staticmethod
    def confirm_password_reset(
        reset_confirm: PasswordResetConfirm,
        db: Session = Depends(get_db),
        redis_client = Depends(get_redis)
    ) -> dict:
        """
        Confirm password reset with token and new password
        
        Time Complexity: O(1) - Redis lookup and database update
        Space Complexity: O(1)
        """
        reset_service = PasswordResetService(db, redis_client)
        success = reset_service.reset_password(reset_confirm.token, reset_confirm.new_password)
        
        if success:
            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
