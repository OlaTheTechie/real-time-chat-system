from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.database.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used = Column(String, default=False)  # Changed to String to avoid boolean issues with SQLite
    
    # relationships
    user = relationship("User", back_populates="password_reset_tokens")
    
    @classmethod
    def create_token(cls, user_id: int, token: str, expires_in_minutes: int = 30):
        """Create a new password reset token"""
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        return cls(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
    
    def is_expired(self) -> bool:
        """Check if the token is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_used(self) -> bool:
        """Check if the token has been used"""
        return self.used == "true"
    
    def mark_as_used(self):
        """Mark the token as used"""
        self.used = "true"