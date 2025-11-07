import pytest
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.chat import ChatRoom, Message, RoomType
from app.core.security import get_password_hash


def create_test_user(db_session, email, username, password="testpass123"):
    """Helper function to create a test user"""
    user = User(
        email=email,
        username=username,
        hashed_password=get_password_hash(password)
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def get_auth_token(client, email, password="testpass123"):
    """Helper function to get authentication token"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    return response.json()["access_token"]


class TestChatRoomAPI:
    """Test chat room management endpoints"""
    
    def test_create_one_to_one_room(self, client, db_session):
        """Test creating a one-to-one chat room"""
        # Create two users
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        
        # Get auth token for user1
        token = get_auth_token(client, "user1@test.com")
        
        # Create one-to-one room
        response = client.post(
            "/api/v1/chat/rooms",
            json={
                "name": None,
                "room_type": "one_to_one",
                "member_ids": [user2.id]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["room_type"] == "one_to_one"
        assert len(data["members"]) == 2
        assert data["created_by"] == user1.id
    
    def test_create_group_room(self, client, db_session):
        """Test creating a group chat room"""
        # Create three users
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        user3 = create_test_user(db_session, "user3@test.com", "user3")
        
        # Get auth token for user1
        token = get_auth_token(client, "user1@test.com")
        
        # Create group room
        response = client.post(
            "/api/v1/chat/rooms",
            json={
                "name": "Test Group",
                "room_type": "group",
                "member_ids": [user2.id, user3.id]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["room_type"] == "group"
        assert data["name"] == "Test Group"
        assert len(data["members"]) == 3
    
    def test_create_duplicate_one_to_one_room(self, client, db_session):
        """Test that duplicate one-to-one rooms are prevented"""
        # Create two users
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        
        # Get auth token for user1
        token = get_auth_token(client, "user1@test.com")
        
        # Create first room
        client.post(
            "/api/v1/chat/rooms",
            json={
                "name": None,
                "room_type": "one_to_one",
                "member_ids": [user2.id]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Try to create duplicate
        response = client.post(
            "/api/v1/chat/rooms",
            json={
                "name": None,
                "room_type": "one_to_one",
                "member_ids": [user2.id]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_list_user_rooms(self, client, db_session):
        """Test listing user's chat rooms"""
        # Create users
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        
        # Create a room
        room = ChatRoom(
            name="Test Room",
            room_type=RoomType.one_to_one,
            created_by=user1.id
        )
        room.members.extend([user1, user2])
        db_session.add(room)
        db_session.commit()
        
        # Get auth token for user1
        token = get_auth_token(client, "user1@test.com")
        
        # List rooms
        response = client.get(
            "/api/v1/chat/rooms",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == room.id
    
    def test_get_room_details(self, client, db_session):
        """Test getting chat room details"""
        # Create users
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        
        # Create a room with messages
        room = ChatRoom(
            name="Test Room",
            room_type=RoomType.one_to_one,
            created_by=user1.id
        )
        room.members.extend([user1, user2])
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        # Add a message
        message = Message(
            room_id=room.id,
            sender_id=user1.id,
            content="Hello!"
        )
        db_session.add(message)
        db_session.commit()
        
        # Get auth token for user1
        token = get_auth_token(client, "user1@test.com")
        
        # Get room details
        response = client.get(
            f"/api/v1/chat/rooms/{room.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == room.id
        assert len(data["messages"]) == 1
        assert data["messages"][0]["content"] == "Hello!"
    
    def test_get_room_details_unauthorized(self, client, db_session):
        """Test that non-members cannot access room details"""
        # Create users
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        user3 = create_test_user(db_session, "user3@test.com", "user3")
        
        # Create a room between user1 and user2
        room = ChatRoom(
            name="Test Room",
            room_type=RoomType.one_to_one,
            created_by=user1.id
        )
        room.members.extend([user1, user2])
        db_session.add(room)
        db_session.commit()
        
        # Get auth token for user3 (not a member)
        token = get_auth_token(client, "user3@test.com")
        
        # Try to get room details
        response = client.get(
            f"/api/v1/chat/rooms/{room.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403


class TestMessageAPI:
    """Test message endpoints"""
    
    def test_send_message(self, client, db_session):
        """Test sending a message to a chat room"""
        # Create users and room
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        
        room = ChatRoom(
            name="Test Room",
            room_type=RoomType.one_to_one,
            created_by=user1.id
        )
        room.members.extend([user1, user2])
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        # Get auth token for user1
        token = get_auth_token(client, "user1@test.com")
        
        # Send message
        response = client.post(
            f"/api/v1/chat/rooms/{room.id}/messages",
            json={
                "content": "Hello, World!",
                "message_type": "text"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Hello, World!"
        assert data["sender_id"] == user1.id
        assert data["room_id"] == room.id
    
    def test_send_message_unauthorized(self, client, db_session):
        """Test that non-members cannot send messages"""
        # Create users and room
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        user3 = create_test_user(db_session, "user3@test.com", "user3")
        
        room = ChatRoom(
            name="Test Room",
            room_type=RoomType.one_to_one,
            created_by=user1.id
        )
        room.members.extend([user1, user2])
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        # Get auth token for user3 (not a member)
        token = get_auth_token(client, "user3@test.com")
        
        # Try to send message
        response = client.post(
            f"/api/v1/chat/rooms/{room.id}/messages",
            json={
                "content": "Hello!",
                "message_type": "text"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    def test_get_messages_paginated(self, client, db_session):
        """Test getting paginated message history"""
        # Create users and room
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        
        room = ChatRoom(
            name="Test Room",
            room_type=RoomType.one_to_one,
            created_by=user1.id
        )
        room.members.extend([user1, user2])
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
        
        # Add multiple messages
        for i in range(15):
            message = Message(
                room_id=room.id,
                sender_id=user1.id if i % 2 == 0 else user2.id,
                content=f"Message {i}"
            )
            db_session.add(message)
        db_session.commit()
        
        # Get auth token for user1
        token = get_auth_token(client, "user1@test.com")
        
        # Get first page
        response = client.get(
            f"/api/v1/chat/rooms/{room.id}/messages?page=1&page_size=10",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 10
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["has_more"] is True
        
        # Get second page
        response = client.get(
            f"/api/v1/chat/rooms/{room.id}/messages?page=2&page_size=10",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 5
        assert data["has_more"] is False
    
    def test_get_messages_unauthorized(self, client, db_session):
        """Test that non-members cannot access message history"""
        # Create users and room
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        user3 = create_test_user(db_session, "user3@test.com", "user3")
        
        room = ChatRoom(
            name="Test Room",
            room_type=RoomType.one_to_one,
            created_by=user1.id
        )
        room.members.extend([user1, user2])
        db_session.add(room)
        db_session.commit()
        
        # Get auth token for user3 (not a member)
        token = get_auth_token(client, "user3@test.com")
        
        # Try to get messages
        response = client.get(
            f"/api/v1/chat/rooms/{room.id}/messages",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403


class TestAPIAuthentication:
    """Test API authentication requirements"""
    
    def test_chat_endpoints_require_auth(self, client):
        """Test that chat endpoints require authentication"""
        # Try to access endpoints without token
        endpoints = [
            ("/api/v1/chat/rooms", "get"),
            ("/api/v1/chat/rooms", "post"),
            ("/api/v1/chat/rooms/1", "get"),
            ("/api/v1/chat/rooms/1/messages", "get"),
            ("/api/v1/chat/rooms/1/messages", "post"),
        ]
        
        for endpoint, method in endpoints:
            if method == "get":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 403
