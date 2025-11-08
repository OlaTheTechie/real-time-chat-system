"""
WebSocket routes for real-time chat
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.chat.websocket import manager, save_message_to_db, verify_room_membership
from app.core.security import verify_token
from app.models.user import User
import json
from datetime import datetime


router = APIRouter()


def get_current_user_ws(token: str, db: Session) -> User:
    """
    Get current user from JWT token for WebSocket connections
    """
    payload = verify_token(token)
    if payload is None:
        return None
    
    user_id: int = payload.get("sub")
    if user_id is None:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


@router.websocket("/ws/chat/{room_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str = Query(...),
):
    """
    WebSocket endpoint for real-time chat in a specific room
    
    Query parameters:
    - token: JWT authentication token
    
    Message format (client -> server):
    {
        "type": "message",
        "content": "message text"
    }
    
    Message format (server -> client):
    {
        "type": "message",
        "id": 123,
        "room_id": 1,
        "sender_id": 5,
        "sender_username": "john_doe",
        "content": "message text",
        "timestamp": "2024-01-01T12:00:00"
    }
    """
    # get database session
    db = next(get_db())
    
    try:
        # authenticate user
        user = get_current_user_ws(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # verify room membership
        if not verify_room_membership(db, user.id, room_id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # connect to room
        await manager.connect(websocket, room_id, user.id)
        
        # send connection confirmation
        await manager.send_personal_message(
            json.dumps({
                "type": "connected",
                "room_id": room_id,
                "user_id": user.id
            }),
            websocket
        )
        
        # listen for messages
        while True:
            # receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type", "message")
                content = message_data.get("content", "")
                
                if message_type == "message" and content:
                    # save message to database
                    db_message = await save_message_to_db(
                        db=db,
                        room_id=room_id,
                        sender_id=user.id,
                        content=content
                    )
                    
                    print(f"[WebSocket] Message saved to DB: id={db_message.id}, room={room_id}, sender={user.username}")
                    
                    # prepare broadcast message
                    broadcast_data = {
                        "type": "message",
                        "data": {
                            "id": db_message.id,
                            "room_id": room_id,
                            "sender_id": user.id,
                            "sender_username": user.username,
                            "content": content,
                            "timestamp": db_message.timestamp.isoformat(),
                            "is_edited": False,
                            "message_type": "text"
                        }
                    }
                    
                    print(f"[WebSocket] Broadcasting message to room {room_id}: {broadcast_data}")
                    
                    # broadcast to all room members
                    await manager.broadcast_to_room(room_id, broadcast_data)
                    
                    print(f"[WebSocket] Broadcast complete")
                
            except json.JSONDecodeError:
                # send error message
                await manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "message": "Invalid message format"
                    }),
                    websocket
                )
            except Exception as e:
                # send error message
                await manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "message": str(e)
                    }),
                    websocket
                )
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket, room_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(websocket, room_id)
    finally:
        db.close()


@router.websocket("/ws/notifications")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket endpoint for user notifications (typing indicators, presence updates)
    
    Query parameters:
    - token: JWT authentication token
    
    Message format (client -> server):
    {
        "type": "typing",
        "room_id": 1,
        "is_typing": true
    }
    
    Message format (server -> client):
    {
        "type": "typing",
        "room_id": 1,
        "user_id": 5,
        "username": "john_doe",
        "is_typing": true
    }
    """
    # get database session
    db = next(get_db())
    
    try:
        # authenticate user
        user = get_current_user_ws(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        await websocket.accept()
        
        # send connection confirmation
        await websocket.send_text(
            json.dumps({
                "type": "connected",
                "user_id": user.id
            })
        )
        
        # listen for notification events
        while True:
            data = await websocket.receive_text()
            
            try:
                notification_data = json.loads(data)
                notification_type = notification_data.get("type")
                
                if notification_type == "typing":
                    room_id = notification_data.get("room_id")
                    is_typing = notification_data.get("is_typing", False)
                    
                    # verify room membership
                    if room_id and verify_room_membership(db, user.id, room_id):
                        # broadcast typing indicator
                        broadcast_data = {
                            "type": "typing",
                            "room_id": room_id,
                            "user_id": user.id,
                            "username": user.username,
                            "is_typing": is_typing
                        }
                        await manager.broadcast_to_room(room_id, broadcast_data)
            
            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps({
                        "type": "error",
                        "message": "Invalid notification format"
                    })
                )
            except Exception as e:
                await websocket.send_text(
                    json.dumps({
                        "type": "error",
                        "message": str(e)
                    })
                )
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket notification error: {e}")
    finally:
        db.close()
