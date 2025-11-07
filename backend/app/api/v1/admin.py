"""
Admin routes for managing users, chat rooms, and messages
These routes are intended for development and testing purposes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.database import get_db
from app.models.user import User
from app.models.chat import ChatRoom, Message, RoomType
from app.auth.dependencies import get_current_user
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter()


# Pydantic schemas for admin operations
class UserAdmin(BaseModel):
    id: int
    email: str
    username: str
    is_online: bool
    last_seen: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRoomAdmin(BaseModel):
    id: int
    name: Optional[str]
    room_type: str
    created_by: int
    created_at: datetime
    member_count: int
    message_count: int
    
    class Config:
        from_attributes = True


class MessageAdmin(BaseModel):
    id: int
    room_id: int
    sender_id: int
    content: str
    timestamp: datetime
    message_type: str
    is_edited: bool
    
    class Config:
        from_attributes = True


# User management routes
@router.get("/users", response_model=List[UserAdmin])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List all users with pagination
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserAdmin)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a user by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}


# ChatRoom management routes
@router.get("/chat-rooms", response_model=List[ChatRoomAdmin])
async def list_chat_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List all chat rooms with pagination
    """
    rooms = db.query(ChatRoom).offset(skip).limit(limit).all()
    
    result = []
    for room in rooms:
        result.append(ChatRoomAdmin(
            id=room.id,
            name=room.name,
            room_type=room.room_type.value,
            created_by=room.created_by,
            created_at=room.created_at,
            member_count=len(room.members),
            message_count=len(room.messages)
        ))
    
    return result


@router.get("/chat-rooms/{room_id}", response_model=ChatRoomAdmin)
async def get_chat_room(
    room_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific chat room by ID
    """
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    return ChatRoomAdmin(
        id=room.id,
        name=room.name,
        room_type=room.room_type.value,
        created_by=room.created_by,
        created_at=room.created_at,
        member_count=len(room.members),
        message_count=len(room.messages)
    )


@router.delete("/chat-rooms/{room_id}")
async def delete_chat_room(
    room_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a chat room by ID
    """
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    db.delete(room)
    db.commit()
    return {"message": f"Chat room {room_id} deleted successfully"}


# Message management routes
@router.get("/messages", response_model=List[MessageAdmin])
async def list_messages(
    room_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List all messages with optional room filter and pagination
    """
    query = db.query(Message)
    
    if room_id:
        query = query.filter(Message.room_id == room_id)
    
    messages = query.order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()
    return messages


@router.get("/messages/{message_id}", response_model=MessageAdmin)
async def get_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific message by ID
    """
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a message by ID
    """
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    return {"message": f"Message {message_id} deleted successfully"}


# Database statistics route
@router.get("/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """
    Get database statistics
    """
    user_count = db.query(User).count()
    room_count = db.query(ChatRoom).count()
    message_count = db.query(Message).count()
    
    return {
        "users": user_count,
        "chat_rooms": room_count,
        "messages": message_count
    }
