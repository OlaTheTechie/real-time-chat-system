"""
Class-based views for admin operations
"""
from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.database import get_db
from app.models.user import User
from app.models.chat import ChatRoom, Message
from pydantic import BaseModel
from datetime import datetime


# pydantic schemas for admin operations
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


class AdminViews:
    """Class-based views for admin operations"""
    
    # user management
    @staticmethod
    def list_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db)
    ) -> List[UserAdmin]:
        """
        List all users with pagination
        
        Time Complexity: O(n) where n is limit
        Space Complexity: O(n)
        """
        users = db.query(User).offset(skip).limit(limit).all()
        return users
    
    @staticmethod
    def get_user(
        user_id: int,
        db: Session = Depends(get_db)
    ) -> UserAdmin:
        """
        Get a specific user by ID
        
        Time Complexity: O(1) with index
        Space Complexity: O(1)
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @staticmethod
    def delete_user(
        user_id: int,
        db: Session = Depends(get_db)
    ) -> dict:
        """
        Delete a user by ID
        
        Time Complexity: O(1) with index
        Space Complexity: O(1)
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
        return {"message": f"User {user_id} deleted successfully"}
    
    # chatroom management
    @staticmethod
    def list_chat_rooms(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db)
    ) -> List[ChatRoomAdmin]:
        """
        List all chat rooms with pagination
        
        Time Complexity: O(n * m) where n is limit, m is avg members per room
        Space Complexity: O(n)
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
    
    @staticmethod
    def get_chat_room(
        room_id: int,
        db: Session = Depends(get_db)
    ) -> ChatRoomAdmin:
        """
        Get a specific chat room by ID
        
        Time Complexity: O(m) where m is number of members
        Space Complexity: O(1)
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
    
    @staticmethod
    def delete_chat_room(
        room_id: int,
        db: Session = Depends(get_db)
    ) -> dict:
        """
        Delete a chat room by ID
        
        Time Complexity: O(1) with index
        Space Complexity: O(1)
        """
        room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Chat room not found")
        
        db.delete(room)
        db.commit()
        return {"message": f"Chat room {room_id} deleted successfully"}
    
    # message management
    @staticmethod
    def list_messages(
        room_id: Optional[int] = None,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db)
    ) -> List[MessageAdmin]:
        """
        List all messages with optional room filter and pagination
        
        Time Complexity: O(n log n) where n is limit (for ordering)
        Space Complexity: O(n)
        """
        query = db.query(Message)
        
        if room_id:
            query = query.filter(Message.room_id == room_id)
        
        messages = query.order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()
        return messages
    
    @staticmethod
    def get_message(
        message_id: int,
        db: Session = Depends(get_db)
    ) -> MessageAdmin:
        """
        Get a specific message by ID
        
        Time Complexity: O(1) with index
        Space Complexity: O(1)
        """
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    
    @staticmethod
    def delete_message(
        message_id: int,
        db: Session = Depends(get_db)
    ) -> dict:
        """
        Delete a message by ID
        
        Time Complexity: O(1) with index
        Space Complexity: O(1)
        """
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        db.delete(message)
        db.commit()
        return {"message": f"Message {message_id} deleted successfully"}
    
    # database statistics
    @staticmethod
    def get_database_stats(db: Session = Depends(get_db)) -> dict:
        """
        Get database statistics
        
        Time Complexity: O(1) - count operations with indexes
        Space Complexity: O(1)
        """
        user_count = db.query(User).count()
        room_count = db.query(ChatRoom).count()
        message_count = db.query(Message).count()
        
        return {
            "users": user_count,
            "chat_rooms": room_count,
            "messages": message_count
        }
