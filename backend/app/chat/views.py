"""
Class-based views for chat endpoints
"""
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.chat import ChatRoom, Message, RoomType, room_memberships
from app.chat.schemas import (
    ChatRoomCreate, ChatRoomResponse, ChatRoomDetail, ChatRoomMember,
    MessageCreate, MessageResponse, MessageListResponse
)
from datetime import datetime


class ChatRoomViews:
    """Class-based views for chat room operations"""
    
    @staticmethod
    def list_user_chat_rooms(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> List[ChatRoomResponse]:
        """
        List all chat rooms for the current user
        
        Time Complexity: O(n) where n is the number of rooms user is member of
        Space Complexity: O(n) for storing room list
        """
        # query rooms where user is a member
        rooms = db.query(ChatRoom).join(
            room_memberships
        ).filter(
            room_memberships.c.user_id == current_user.id
        ).options(
            joinedload(ChatRoom.members),
            joinedload(ChatRoom.messages)
        ).all()
        
        # format response with last message
        result = []
        for room in rooms:
            # get last message - o(m log m) where m is messages per room
            last_message = None
            if room.messages:
                last_msg = sorted(room.messages, key=lambda m: m.timestamp, reverse=True)[0]
                last_message = MessageResponse(
                    id=last_msg.id,
                    room_id=last_msg.room_id,
                    sender_id=last_msg.sender_id,
                    content=last_msg.content,
                    timestamp=last_msg.timestamp,
                    message_type=last_msg.message_type,
                    is_edited=last_msg.is_edited,
                    sender_username=last_msg.sender.username if last_msg.sender else None
                )
            
            room_response = ChatRoomResponse(
                id=room.id,
                name=room.name,
                room_type=room.room_type,
                created_by=room.created_by,
                created_at=room.created_at,
                members=[ChatRoomMember(
                    id=member.id,
                    username=member.username,
                    email=member.email,
                    is_online=member.is_online
                ) for member in room.members],
                last_message=last_message
            )
            result.append(room_response)
        
        return result
    
    @staticmethod
    def create_chat_room(
        room_data: ChatRoomCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> ChatRoomResponse:
        """
        Create a new chat room
        
        Time Complexity: O(n) where n is number of members
        Space Complexity: O(n) for storing members
        """
        # validate room type and members
        if room_data.room_type == RoomType.one_to_one:
            if len(room_data.member_ids) != 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One-to-one chat must have exactly one other member"
                )
            
            # check if one-to-one room already exists between these users
            other_user_id = room_data.member_ids[0]
            existing_room = db.query(ChatRoom).join(
                room_memberships, ChatRoom.id == room_memberships.c.room_id
            ).filter(
                ChatRoom.room_type == RoomType.one_to_one
            ).group_by(ChatRoom.id).having(
                func.count(room_memberships.c.user_id) == 2
            ).all()
            
            for room in existing_room:
                member_ids = [m.id for m in room.members]
                if set(member_ids) == {current_user.id, other_user_id}:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="One-to-one chat already exists with this user"
                    )
        
        # verify all member users exist - o(n) database query
        members = db.query(User).filter(User.id.in_(room_data.member_ids)).all()
        if len(members) != len(room_data.member_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more users not found"
            )
        
        # create chat room
        new_room = ChatRoom(
            name=room_data.name,
            room_type=room_data.room_type,
            created_by=current_user.id
        )
        
        # add creator and members - o(n)
        new_room.members.append(current_user)
        for member in members:
            if member.id != current_user.id:
                new_room.members.append(member)
        
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        
        return ChatRoomResponse(
            id=new_room.id,
            name=new_room.name,
            room_type=new_room.room_type,
            created_by=new_room.created_by,
            created_at=new_room.created_at,
            members=[ChatRoomMember(
                id=member.id,
                username=member.username,
                email=member.email,
                is_online=member.is_online
            ) for member in new_room.members],
            last_message=None
        )
    
    @staticmethod
    def get_chat_room_details(
        room_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> ChatRoomDetail:
        """
        Get details of a specific chat room including recent messages
        
        Time Complexity: O(m log m) where m is number of messages (for sorting)
        Space Complexity: O(m) for storing messages
        """
        # get room with members and messages
        room = db.query(ChatRoom).filter(ChatRoom.id == room_id).options(
            joinedload(ChatRoom.members),
            joinedload(ChatRoom.messages).joinedload(Message.sender)
        ).first()
        
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat room not found"
            )
        
        # check if user is a member - o(n) where n is number of members
        if current_user.id not in [member.id for member in room.members]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this chat room"
            )
        
        # sort messages by timestamp - o(m log m)
        sorted_messages = sorted(room.messages, key=lambda m: m.timestamp)
        
        return ChatRoomDetail(
            id=room.id,
            name=room.name,
            room_type=room.room_type,
            created_by=room.created_by,
            created_at=room.created_at,
            members=[ChatRoomMember(
                id=member.id,
                username=member.username,
                email=member.email,
                is_online=member.is_online
            ) for member in room.members],
            messages=[MessageResponse(
                id=msg.id,
                room_id=msg.room_id,
                sender_id=msg.sender_id,
                content=msg.content,
                timestamp=msg.timestamp,
                message_type=msg.message_type,
                is_edited=msg.is_edited,
                sender_username=msg.sender.username if msg.sender else None
            ) for msg in sorted_messages]
        )


class MessageViews:
    """Class-based views for message operations"""
    
    @staticmethod
    def get_room_messages(
        room_id: int,
        page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> MessageListResponse:
        """
        Get paginated message history for a chat room
        
        Time Complexity: O(log n + k) where n is total messages, k is page_size
        Space Complexity: O(k) for storing page of messages
        """
        # verify room exists - o(1) with index
        room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
        
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat room not found"
            )
        
        # check if user is a member - o(1) with index
        is_member = db.query(room_memberships).filter(
            room_memberships.c.room_id == room_id,
            room_memberships.c.user_id == current_user.id
        ).first()
        
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this chat room"
            )
        
        # get total count - o(1) with index
        total = db.query(Message).filter(Message.room_id == room_id).count()
        
        # calculate offset
        offset = (page - 1) * page_size
        
        # get paginated messages - o(log n + k)
        messages = db.query(Message).filter(
            Message.room_id == room_id
        ).options(
            joinedload(Message.sender)
        ).order_by(
            Message.timestamp.desc()
        ).offset(offset).limit(page_size).all()
        
        # reverse to show oldest first in the page - o(k)
        messages = list(reversed(messages))
        
        has_more = offset + page_size < total
        
        return MessageListResponse(
            messages=[MessageResponse(
                id=msg.id,
                room_id=msg.room_id,
                sender_id=msg.sender_id,
                content=msg.content,
                timestamp=msg.timestamp,
                message_type=msg.message_type,
                is_edited=msg.is_edited,
                sender_username=msg.sender.username if msg.sender else None
            ) for msg in messages],
            total=total,
            page=page,
            page_size=page_size,
            has_more=has_more
        )
    
    @staticmethod
    def send_message(
        room_id: int,
        message_data: MessageCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> MessageResponse:
        """
        Send a message to a chat room via REST API
        
        Time Complexity: O(1) - single database insert
        Space Complexity: O(1) - single message object
        """
        # verify room exists - o(1) with index
        room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
        
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat room not found"
            )
        
        # check if user is a member - o(1) with index
        is_member = db.query(room_memberships).filter(
            room_memberships.c.room_id == room_id,
            room_memberships.c.user_id == current_user.id
        ).first()
        
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this chat room"
            )
        
        # create message - o(1)
        new_message = Message(
            room_id=room_id,
            sender_id=current_user.id,
            content=message_data.content,
            message_type=message_data.message_type,
            timestamp=datetime.utcnow()
        )
        
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        return MessageResponse(
            id=new_message.id,
            room_id=new_message.room_id,
            sender_id=new_message.sender_id,
            content=new_message.content,
            timestamp=new_message.timestamp,
            message_type=new_message.message_type,
            is_edited=new_message.is_edited,
            sender_username=current_user.username
        )
