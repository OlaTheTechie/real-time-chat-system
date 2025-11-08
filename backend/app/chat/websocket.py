"""
WebSocket connection manager and handlers for real-time chat
"""
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database.redis_client import get_redis
from app.models.chat import Message, ChatRoom
from app.models.user import User
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting
    """
    def __init__(self):
        # active connections: room_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # websocket to user mapping
        self.websocket_users: Dict[WebSocket, int] = {}
        # redis client for pub/sub
        self.redis = get_redis()
        # pubsub instance
        self.pubsub = None
        # listener task
        self.listener_task = None
    
    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        """
        Accept websocket connection and add to room
        """
        await websocket.accept()
        
        # add to active connections
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
        
        # map websocket to user
        self.websocket_users[websocket] = user_id
        
        # start redis listener if not already running
        if self.listener_task is None:
            self.listener_task = asyncio.create_task(self._redis_listener())
    
    async def disconnect(self, websocket: WebSocket, room_id: int):
        """
        Remove websocket connection from room
        """
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        # remove from user mapping
        if websocket in self.websocket_users:
            del self.websocket_users[websocket]
    
    async def broadcast_to_room(self, room_id: int, message: dict):
        """
        Broadcast message to all connections in a room
        For single-server: direct broadcast to websockets
        For multi-server: use Redis pub/sub
        """
        message_json = json.dumps(message)
        
        # direct broadcast to all websockets in this room (single-server)
        if room_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[room_id]:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    print(f"Error sending to websocket: {e}")
                    disconnected.add(websocket)
            
            # clean up disconnected websockets
            for ws in disconnected:
                await self.disconnect(ws, room_id)
        
        # also publish to redis for multi-server support (optional)
        try:
            channel = f"chat_room_{room_id}"
            self.redis.publish(channel, message_json)
        except Exception as e:
            print(f"Redis publish error (non-critical): {e}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Send message to specific websocket connection
        """
        await websocket.send_text(message)
    
    async def _redis_listener(self):
        """
        Listen to Redis pub/sub channels and broadcast to websockets
        """
        try:
            self.pubsub = self.redis.pubsub()
            
            while True:
                # subscribe to all active room channels
                channels = [f"chat_room_{room_id}" for room_id in self.active_connections.keys()]
                if channels:
                    self.pubsub.subscribe(*channels)
                
                # listen for messages
                message = self.pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    channel = message['channel']
                    data = message['data']
                    
                    # extract room_id from channel name
                    room_id = int(channel.split('_')[-1])
                    
                    # broadcast to all websockets in this room
                    if room_id in self.active_connections:
                        disconnected = set()
                        for websocket in self.active_connections[room_id]:
                            try:
                                await websocket.send_text(data)
                            except Exception:
                                disconnected.add(websocket)
                        
                        # clean up disconnected websockets
                        for ws in disconnected:
                            await self.disconnect(ws, room_id)
                
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Redis listener error: {e}")
        finally:
            if self.pubsub:
                self.pubsub.close()


# global connection manager instance
manager = ConnectionManager()


async def save_message_to_db(
    db: Session,
    room_id: int,
    sender_id: int,
    content: str,
    message_type: str = "text"
) -> Message:
    """
    Save message to database
    """
    message = Message(
        room_id=room_id,
        sender_id=sender_id,
        content=content,
        message_type=message_type,
        timestamp=datetime.utcnow()
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def verify_room_membership(db: Session, user_id: int, room_id: int) -> bool:
    """
    Verify if user is a member of the chat room
    """
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        return False
    
    # check if user is a member
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    return user in room.members
