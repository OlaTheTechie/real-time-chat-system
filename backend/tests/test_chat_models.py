import pytest
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user import User
from app.models.chat import ChatRoom, Message, RoomType, MemberRole, room_memberships
from app.core.security import get_password_hash


class TestChatRoomModel:
    """Test ChatRoom model functionality"""
    
    def test_chatroom_creation(self, db_session: Session):
        """Test creating a new chat room"""
        # Create a user first
        user = User(
            email="creator@example.com",
            username="creator",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create a chat room
        room = ChatRoom(
            name="Test Room",
            room_type=RoomType.group,
            created_by=user.id
        )
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        assert room.id is not None
        assert room.name == "Test Room"
        assert room.room_type == RoomType.group
        assert room.created_by == user.id
        assert room.created_at is not None
    
    def test_one_to_one_chatroom(self, db_session: Session):
        """Test creating a one-to-one chat room"""
        user = User(
            email="user1@example.com",
            username="user1",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        room = ChatRoom(
            name=None,  # One-to-one rooms may not have names
            room_type=RoomType.one_to_one,
            created_by=user.id
        )
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        assert room.id is not None
        assert room.name is None
        assert room.room_type == RoomType.one_to_one
    
    def test_chatroom_creator_relationship(self, db_session: Session):
        """Test relationship between chat room and creator"""
        user = User(
            email="creator2@example.com",
            username="creator2",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        room = ChatRoom(
            name="Creator Test Room",
            room_type=RoomType.group,
            created_by=user.id
        )
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        # Test relationship
        assert room.creator.id == user.id
        assert room.creator.username == "creator2"
        assert len(user.created_rooms) == 1
        assert user.created_rooms[0].id == room.id
    
    def test_chatroom_members_relationship(self, db_session: Session):
        """Test many-to-many relationship between chat rooms and users"""
        # Create users
        user1 = User(
            email="member1@example.com",
            username="member1",
            hashed_password=get_password_hash("password")
        )
        user2 = User(
            email="member2@example.com",
            username="member2",
            hashed_password=get_password_hash("password")
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)
        
        # Create room
        room = ChatRoom(
            name="Members Test Room",
            room_type=RoomType.group,
            created_by=user1.id
        )
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        # Add members
        room.members.append(user1)
        room.members.append(user2)
        db_session.commit()
        
        # Test relationships
        assert len(room.members) == 2
        assert user1 in room.members
        assert user2 in room.members
        assert room in user1.rooms
        assert room in user2.rooms


class TestMessageModel:
    """Test Message model functionality"""
    
    def test_message_creation(self, db_session: Session):
        """Test creating a new message"""
        # Create user and room
        user = User(
            email="sender@example.com",
            username="sender",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        room = ChatRoom(
            name="Message Test Room",
            room_type=RoomType.group,
            created_by=user.id
        )
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        # Create message
        message = Message(
            room_id=room.id,
            sender_id=user.id,
            content="Hello, World!"
        )
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        assert message.id is not None
        assert message.room_id == room.id
        assert message.sender_id == user.id
        assert message.content == "Hello, World!"
        assert message.timestamp is not None
        assert message.message_type == "text"
        assert message.is_edited is False
    
    def test_message_sender_relationship(self, db_session: Session):
        """Test relationship between message and sender"""
        user = User(
            email="sender2@example.com",
            username="sender2",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        room = ChatRoom(
            name="Sender Test Room",
            room_type=RoomType.group,
            created_by=user.id
        )
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        message = Message(
            room_id=room.id,
            sender_id=user.id,
            content="Test message"
        )
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        # Test relationship
        assert message.sender.id == user.id
        assert message.sender.username == "sender2"
        assert len(user.sent_messages) == 1
        assert user.sent_messages[0].id == message.id
    
    def test_message_room_relationship(self, db_session: Session):
        """Test relationship between message and room"""
        user = User(
            email="sender3@example.com",
            username="sender3",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        room = ChatRoom(
            name="Room Test",
            room_type=RoomType.group,
            created_by=user.id
        )
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        # Create multiple messages
        message1 = Message(
            room_id=room.id,
            sender_id=user.id,
            content="First message"
        )
        message2 = Message(
            room_id=room.id,
            sender_id=user.id,
            content="Second message"
        )
        db_session.add_all([message1, message2])
        db_session.commit()
        
        # Test relationship
        assert len(room.messages) == 2
        assert message1 in room.messages
        assert message2 in room.messages
        assert message1.room.id == room.id
        assert message2.room.id == room.id
    
    def test_message_timestamp_ordering(self, db_session: Session):
        """Test that messages maintain timestamp ordering"""
        user = User(
            email="sender4@example.com",
            username="sender4",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        room = ChatRoom(
            name="Timestamp Test Room",
            room_type=RoomType.group,
            created_by=user.id
        )
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        # Create messages
        message1 = Message(
            room_id=room.id,
            sender_id=user.id,
            content="First"
        )
        db_session.add(message1)
        db_session.commit()
        
        message2 = Message(
            room_id=room.id,
            sender_id=user.id,
            content="Second"
        )
        db_session.add(message2)
        db_session.commit()
        
        # Query messages ordered by timestamp
        messages = db_session.query(Message).filter(
            Message.room_id == room.id
        ).order_by(Message.timestamp).all()
        
        assert len(messages) == 2
        assert messages[0].content == "First"
        assert messages[1].content == "Second"
        assert messages[0].timestamp <= messages[1].timestamp
    
    def test_message_edit_flag(self, db_session: Session):
        """Test message edit flag functionality"""
        user = User(
            email="editor@example.com",
            username="editor",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        room = ChatRoom(
            name="Edit Test Room",
            room_type=RoomType.group,
            created_by=user.id
        )
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        message = Message(
            room_id=room.id,
            sender_id=user.id,
            content="Original content"
        )
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        assert message.is_edited is False
        
        # Edit message
        message.content = "Edited content"
        message.is_edited = True
        db_session.commit()
        db_session.refresh(message)
        
        assert message.content == "Edited content"
        assert message.is_edited is True


class TestRoomMembership:
    """Test RoomMembership association table functionality"""
    
    def test_room_membership_creation(self, db_session: Session):
        """Test creating room memberships"""
        # Create users
        user1 = User(
            email="member3@example.com",
            username="member3",
            hashed_password=get_password_hash("password")
        )
        user2 = User(
            email="member4@example.com",
            username="member4",
            hashed_password=get_password_hash("password")
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create room
        room = ChatRoom(
            name="Membership Test Room",
            room_type=RoomType.group,
            created_by=user1.id
        )
        db_session.add(room)
        db_session.commit()
        
        # Add members
        room.members.append(user1)
        room.members.append(user2)
        db_session.commit()
        
        # Query memberships
        memberships = db_session.query(room_memberships).filter(
            room_memberships.c.room_id == room.id
        ).all()
        
        assert len(memberships) == 2
        assert any(m.user_id == user1.id for m in memberships)
        assert any(m.user_id == user2.id for m in memberships)
    
    def test_room_membership_constraints(self, db_session: Session):
        """Test that room membership enforces constraints"""
        from sqlalchemy.exc import IntegrityError
        
        user = User(
            email="constraint@example.com",
            username="constraint",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        room = ChatRoom(
            name="Constraint Test Room",
            room_type=RoomType.group,
            created_by=user.id
        )
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        # Add user as member
        room.members.append(user)
        db_session.commit()
        
        # Verify user is in room
        assert user in room.members
        assert len(room.members) == 1
        
        # Try to add same user again (should raise IntegrityError due to unique constraint)
        with pytest.raises(IntegrityError):
            room.members.append(user)
            db_session.commit()
    
    def test_multiple_rooms_per_user(self, db_session: Session):
        """Test that a user can be member of multiple rooms"""
        user = User(
            email="multiroom@example.com",
            username="multiroom",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create multiple rooms
        room1 = ChatRoom(
            name="Room 1",
            room_type=RoomType.group,
            created_by=user.id
        )
        room2 = ChatRoom(
            name="Room 2",
            room_type=RoomType.group,
            created_by=user.id
        )
        db_session.add_all([room1, room2])
        db_session.commit()
        
        # Add user to both rooms
        room1.members.append(user)
        room2.members.append(user)
        db_session.commit()
        
        # Verify user is in both rooms
        assert len(user.rooms) == 2
        assert room1 in user.rooms
        assert room2 in user.rooms
