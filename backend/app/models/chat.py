from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database.database import Base


class RoomType(enum.Enum):
    one_to_one = "one_to_one"
    group = "group"


class MemberRole(enum.Enum):
    member = "member"
    admin = "admin"


# association table for many-to-many relationship between users and chat rooms
room_memberships = Table(
    'room_memberships',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('room_id', Integer, ForeignKey('chat_rooms.id'), primary_key=True),
    Column('joined_at', DateTime, default=datetime.utcnow),
    Column('role', Enum(MemberRole), default=MemberRole.member)
)


class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    room_type = Column(Enum(RoomType), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # relationships
    creator = relationship("User", back_populates="created_rooms")
    members = relationship("User", secondary=room_memberships, back_populates="rooms")
    messages = relationship("Message", back_populates="room")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    message_type = Column(String, default="text")
    is_edited = Column(Boolean, default=False)
    
    # relationships
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")


# roommembership is defined as a table above for the many-to-many relationship