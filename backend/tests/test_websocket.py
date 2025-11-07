"""
Tests for WebSocket functionality
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.chat import ChatRoom, RoomType
from app.core.security import create_access_token
from app.database.database import get_db
import json


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    from app.core.security import get_password_hash
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user2(db_session):
    """Create a second test user"""
    from app.core.security import get_password_hash
    user = User(
        email="testuser2@example.com",
        username="testuser2",
        hashed_password=get_password_hash("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_room(db_session, test_user, test_user2):
    """Create a test chat room with two members"""
    room = ChatRoom(
        name="Test Room",
        room_type=RoomType.group,
        created_by=test_user.id
    )
    room.members.append(test_user)
    room.members.append(test_user2)
    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)
    return room


@pytest.fixture
def auth_token(test_user):
    """Generate JWT token for test user"""
    return create_access_token(data={"sub": test_user.id})


@pytest.fixture
def auth_token2(test_user2):
    """Generate JWT token for second test user"""
    return create_access_token(data={"sub": test_user2.id})


def test_websocket_connection_without_auth(client):
    """Test WebSocket connection fails without authentication"""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/chat/1") as websocket:
            pass


def test_websocket_connection_with_invalid_token(client, test_room):
    """Test WebSocket connection fails with invalid token"""
    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws/chat/{test_room.id}?token=invalid_token") as websocket:
            pass


def test_websocket_connection_success(client, test_room, auth_token):
    """Test successful WebSocket connection with valid authentication"""
    with client.websocket_connect(f"/ws/chat/{test_room.id}?token={auth_token}") as websocket:
        # receive connection confirmation
        data = websocket.receive_text()
        message = json.loads(data)
        
        assert message["type"] == "connected"
        assert message["room_id"] == test_room.id


def test_websocket_send_message(client, test_room, auth_token, test_user):
    """Test sending a message through WebSocket"""
    with client.websocket_connect(f"/ws/chat/{test_room.id}?token={auth_token}") as websocket:
        # receive connection confirmation
        websocket.receive_text()
        
        # send a message
        message_data = {
            "type": "message",
            "content": "Hello, World!"
        }
        websocket.send_text(json.dumps(message_data))
        
        # receive the broadcasted message
        response = websocket.receive_text()
        response_data = json.loads(response)
        
        assert response_data["type"] == "message"
        assert response_data["content"] == "Hello, World!"
        assert response_data["sender_id"] == test_user.id
        assert response_data["sender_username"] == test_user.username
        assert response_data["room_id"] == test_room.id


def test_websocket_invalid_message_format(client, test_room, auth_token):
    """Test WebSocket handles invalid message format"""
    with client.websocket_connect(f"/ws/chat/{test_room.id}?token={auth_token}") as websocket:
        # receive connection confirmation
        websocket.receive_text()
        
        # send invalid JSON
        websocket.send_text("not a json")
        
        # receive error message
        response = websocket.receive_text()
        response_data = json.loads(response)
        
        assert response_data["type"] == "error"
        assert "Invalid message format" in response_data["message"]


def test_websocket_unauthorized_room_access(client, test_room, db_session):
    """Test WebSocket connection fails for non-member user"""
    from app.core.security import get_password_hash
    
    # create a user who is not a member of the room
    unauthorized_user = User(
        email="unauthorized@example.com",
        username="unauthorized",
        hashed_password=get_password_hash("password123")
    )
    db_session.add(unauthorized_user)
    db_session.commit()
    db_session.refresh(unauthorized_user)
    
    # generate token for unauthorized user
    token = create_access_token(data={"sub": unauthorized_user.id})
    
    # attempt to connect should fail
    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws/chat/{test_room.id}?token={token}") as websocket:
            pass


def test_websocket_notifications_connection(client, auth_token, test_user):
    """Test WebSocket notifications endpoint connection"""
    with client.websocket_connect(f"/ws/notifications?token={auth_token}") as websocket:
        # receive connection confirmation
        data = websocket.receive_text()
        message = json.loads(data)
        
        assert message["type"] == "connected"
        assert message["user_id"] == test_user.id


def test_websocket_typing_indicator(client, test_room, auth_token, test_user):
    """Test typing indicator through notifications WebSocket"""
    with client.websocket_connect(f"/ws/notifications?token={auth_token}") as websocket:
        # receive connection confirmation
        websocket.receive_text()
        
        # send typing indicator
        typing_data = {
            "type": "typing",
            "room_id": test_room.id,
            "is_typing": True
        }
        websocket.send_text(json.dumps(typing_data))
        
        # receive the broadcasted typing indicator
        response = websocket.receive_text()
        response_data = json.loads(response)
        
        assert response_data["type"] == "typing"
        assert response_data["room_id"] == test_room.id
        assert response_data["user_id"] == test_user.id
        assert response_data["is_typing"] is True
