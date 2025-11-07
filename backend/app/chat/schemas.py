from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.chat import RoomType, MemberRole


class MessageResponse(BaseModel):
    id: int
    room_id: int
    sender_id: int
    content: str
    timestamp: datetime
    message_type: str
    is_edited: bool
    sender_username: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChatRoomMember(BaseModel):
    id: int
    username: str
    email: str
    is_online: bool
    
    class Config:
        from_attributes = True


class ChatRoomResponse(BaseModel):
    id: int
    name: Optional[str] = None
    room_type: RoomType
    created_by: int
    created_at: datetime
    members: List[ChatRoomMember] = []
    last_message: Optional[MessageResponse] = None
    
    class Config:
        from_attributes = True


class ChatRoomCreate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    room_type: RoomType
    member_ids: List[int] = Field(..., min_length=1)


class ChatRoomDetail(BaseModel):
    id: int
    name: Optional[str] = None
    room_type: RoomType
    created_by: int
    created_at: datetime
    members: List[ChatRoomMember] = []
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: str = Field(default="text")


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
