"""
Admin routes using class-based views for managing users, chat rooms, and messages
These routes are intended for development and testing purposes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.database import get_db
from app.api.v1.admin_views import AdminViews, UserAdmin, ChatRoomAdmin, MessageAdmin

router = APIRouter()


# user management routes
@router.get("/users", response_model=List[UserAdmin])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all users with pagination"""
    return AdminViews.list_users(skip, limit, db)


@router.get("/users/{user_id}", response_model=UserAdmin)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    return AdminViews.get_user(user_id, db)


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user by ID"""
    return AdminViews.delete_user(user_id, db)


# chatroom management routes
@router.get("/chat-rooms", response_model=List[ChatRoomAdmin])
async def list_chat_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all chat rooms with pagination"""
    return AdminViews.list_chat_rooms(skip, limit, db)


@router.get("/chat-rooms/{room_id}", response_model=ChatRoomAdmin)
async def get_chat_room(room_id: int, db: Session = Depends(get_db)):
    """Get a specific chat room by ID"""
    return AdminViews.get_chat_room(room_id, db)


@router.delete("/chat-rooms/{room_id}")
async def delete_chat_room(room_id: int, db: Session = Depends(get_db)):
    """Delete a chat room by ID"""
    return AdminViews.delete_chat_room(room_id, db)


# message management routes
@router.get("/messages", response_model=List[MessageAdmin])
async def list_messages(
    room_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all messages with optional room filter and pagination"""
    return AdminViews.list_messages(room_id, skip, limit, db)


@router.get("/messages/{message_id}", response_model=MessageAdmin)
async def get_message(message_id: int, db: Session = Depends(get_db)):
    """Get a specific message by ID"""
    return AdminViews.get_message(message_id, db)


@router.delete("/messages/{message_id}")
async def delete_message(message_id: int, db: Session = Depends(get_db)):
    """Delete a message by ID"""
    return AdminViews.delete_message(message_id, db)


# database statistics route
@router.get("/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """Get database statistics"""
    return AdminViews.get_database_stats(db)
