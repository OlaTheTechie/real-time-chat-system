from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # relationships
    created_rooms = relationship("ChatRoom", back_populates="creator")
    sent_messages = relationship("Message", back_populates="sender")
    rooms = relationship("ChatRoom", secondary="room_memberships", back_populates="members")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")