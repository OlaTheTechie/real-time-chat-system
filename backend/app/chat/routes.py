"""
Chat routes using class-based views
"""
from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.chat.schemas import (
    ChatRoomCreate, ChatRoomResponse, ChatRoomDetail,
    MessageCreate, MessageResponse, MessageListResponse
)
from app.chat.views import ChatRoomViews, MessageViews

router = APIRouter()


# list user's chat rooms
@router.get("/rooms", response_model=List[ChatRoomResponse])
def list_user_chat_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all chat rooms for the current user"""
    return ChatRoomViews.list_user_chat_rooms(current_user, db)


# create a new chat room
@router.post("/rooms", response_model=ChatRoomResponse, status_code=status.HTTP_201_CREATED)
def create_chat_room(
    room_data: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat room"""
    return ChatRoomViews.create_chat_room(room_data, current_user, db)


# get chat room details
@router.get("/rooms/{room_id}", response_model=ChatRoomDetail)
def get_chat_room_details(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific chat room including recent messages"""
    return ChatRoomViews.get_chat_room_details(room_id, current_user, db)


# get room messages with pagination
@router.get("/rooms/{room_id}/messages", response_model=MessageListResponse)
def get_room_messages(
    room_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated message history for a chat room"""
    return MessageViews.get_room_messages(room_id, page, page_size, current_user, db)


# send a message to a room
@router.post("/rooms/{room_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    room_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to a chat room via REST API"""
    return MessageViews.send_message(room_id, message_data, current_user, db)
