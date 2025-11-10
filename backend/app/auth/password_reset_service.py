import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.database.redis_client import get_redis
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.core.security import get_password_hash
from app.core.email import email_service


class PasswordResetService:
    def __init__(self, db: Session, redis_client=None):
        self.db = db
        try:
            self.redis_client = redis_client or get_redis()
            # Test Redis connection
            self.redis_client.ping()
            self.redis_available = True
        except Exception as e:
            print(f"Redis not available, using database only: {e}")
            self.redis_client = None
            self.redis_available = False
        self.token_expiry_minutes = 30
    
    def generate_reset_token(self) -> str:
        """Generate a secure random token for password reset"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def create_reset_token(self, email: str, send_email: bool = True) -> Optional[str]:
        """Create a password reset token for the given email"""
        # find user by email
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        # generate token
        token = self.generate_reset_token()
        
        # store in database
        reset_token = PasswordResetToken.create_token(
            user_id=user.id,
            token=token,
            expires_in_minutes=self.token_expiry_minutes
        )
        self.db.add(reset_token)
        
        # also store in redis for faster lookup (optional but recommended)
        if self.redis_available:
            try:
                redis_key = f"password_reset:{token}"
                redis_value = f"{user.id}:{user.email}"
                self.redis_client.setex(
                    redis_key, 
                    timedelta(minutes=self.token_expiry_minutes), 
                    redis_value
                )
            except Exception as e:
                print(f"Redis error (non-critical): {e}")
        
        self.db.commit()
        
        # send email with reset link
        if send_email:
            try:
                email_service.send_password_reset_email(email, token)
            except Exception as e:
                print(f"Email sending error (non-critical): {e}")
        
        return token
    
    def verify_reset_token(self, token: str) -> Optional[User]:
        """Verify a password reset token and return the associated user"""
        # first check redis for faster lookup (if available)
        if self.redis_available:
            try:
                redis_key = f"password_reset:{token}"
                redis_value = self.redis_client.get(redis_key)
                
                if redis_value:
                    # handle both bytes and string responses from redis
                    if isinstance(redis_value, bytes):
                        redis_value = redis_value.decode()
                    user_id = int(redis_value.split(':')[0])
                    user = self.db.query(User).filter(User.id == user_id).first()
                    
                    # also verify in database
                    db_token = self.db.query(PasswordResetToken).filter(
                        PasswordResetToken.token == token,
                        PasswordResetToken.user_id == user_id
                    ).first()
                    
                    if db_token and not db_token.is_expired() and not db_token.is_used():
                        return user
            except Exception as e:
                print(f"Redis error (non-critical), falling back to database: {e}")
        
        # fallback to database-only lookup
        db_token = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()
        
        if db_token and not db_token.is_expired() and not db_token.is_used():
            return db_token.user
        
        return None
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password using the provided token"""
        user = self.verify_reset_token(token)
        if not user:
            return False
        
        # update user password
        user.hashed_password = get_password_hash(new_password)
        
        # mark token as used in database
        db_token = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.user_id == user.id
        ).first()
        
        if db_token:
            db_token.mark_as_used()
        
        # remove from redis (if available)
        if self.redis_available:
            try:
                redis_key = f"password_reset:{token}"
                self.redis_client.delete(redis_key)
            except Exception as e:
                print(f"Redis error (non-critical): {e}")
        
        self.db.commit()
        return True
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens from database (can be run as a background task)"""
        expired_tokens = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.expires_at < datetime.utcnow()
        ).all()
        
        for token in expired_tokens:
            # remove from redis if exists and available
            if self.redis_available:
                try:
                    redis_key = f"password_reset:{token.token}"
                    self.redis_client.delete(redis_key)
                except Exception as e:
                    print(f"Redis error (non-critical): {e}")
            
            # remove from database
            self.db.delete(token)
        
        self.db.commit()
        return len(expired_tokens)