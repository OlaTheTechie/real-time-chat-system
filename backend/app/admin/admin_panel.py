"""
Admin Panel using SQLAdmin for FastAPI
Provides a web-based interface to manage all models
"""
from sqladmin import Admin, ModelView
from app.models.user import User
from app.models.chat import ChatRoom, Message
from app.models.password_reset import PasswordResetToken


class UserAdmin(ModelView, model=User):
    """Admin view for User model"""
    
    column_list = [User.id, User.username, User.email, User.is_online, User.created_at, User.last_seen]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username, User.email, User.created_at]
    column_default_sort = [(User.created_at, True)]
    
    # fields to display in detail view
    column_details_list = [
        User.id, 
        User.username, 
        User.email, 
        User.is_online, 
        User.created_at, 
        User.last_seen
    ]
    
    # fields that can be edited (exclude password)
    form_columns = [User.username, User.email, User.is_online]
    
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class ChatRoomAdmin(ModelView, model=ChatRoom):
    """Admin view for ChatRoom model"""
    
    column_list = [
        ChatRoom.id, 
        ChatRoom.name, 
        ChatRoom.room_type, 
        ChatRoom.created_by, 
        ChatRoom.created_at
    ]
    column_searchable_list = [ChatRoom.name]
    column_sortable_list = [ChatRoom.id, ChatRoom.name, ChatRoom.created_at]
    column_default_sort = [(ChatRoom.created_at, True)]
    
    # fields to display in detail view
    column_details_list = [
        ChatRoom.id,
        ChatRoom.name,
        ChatRoom.room_type,
        ChatRoom.created_by,
        ChatRoom.created_at,
        ChatRoom.members,
        ChatRoom.messages
    ]
    
    # fields that can be edited
    form_columns = [ChatRoom.name, ChatRoom.room_type, ChatRoom.created_by]
    
    name = "Chat Room"
    name_plural = "Chat Rooms"
    icon = "fa-solid fa-comments"


class MessageAdmin(ModelView, model=Message):
    """Admin view for Message model"""
    
    column_list = [
        Message.id,
        Message.room_id,
        Message.sender_id,
        Message.content,
        Message.timestamp,
        Message.message_type,
        Message.is_edited
    ]
    column_searchable_list = [Message.content]
    column_sortable_list = [Message.id, Message.timestamp, Message.room_id, Message.sender_id]
    column_default_sort = [(Message.timestamp, True)]
    
    # fields to display in detail view
    column_details_list = [
        Message.id,
        Message.room_id,
        Message.sender_id,
        Message.content,
        Message.timestamp,
        Message.message_type,
        Message.is_edited,
        Message.sender,
        Message.room
    ]
    
    # fields that can be edited
    form_columns = [
        Message.room_id,
        Message.sender_id,
        Message.content,
        Message.message_type,
        Message.is_edited
    ]
    
    name = "Message"
    name_plural = "Messages"
    icon = "fa-solid fa-message"


class PasswordResetTokenAdmin(ModelView, model=PasswordResetToken):
    """Admin view for PasswordResetToken model"""
    
    column_list = [
        PasswordResetToken.id,
        PasswordResetToken.user_id,
        PasswordResetToken.token,
        PasswordResetToken.created_at,
        PasswordResetToken.expires_at,
        PasswordResetToken.used
    ]
    column_sortable_list = [
        PasswordResetToken.id,
        PasswordResetToken.created_at,
        PasswordResetToken.expires_at
    ]
    column_default_sort = [(PasswordResetToken.created_at, True)]
    
    # fields to display in detail view
    column_details_list = [
        PasswordResetToken.id,
        PasswordResetToken.user_id,
        PasswordResetToken.token,
        PasswordResetToken.created_at,
        PasswordResetToken.expires_at,
        PasswordResetToken.used,
        PasswordResetToken.user
    ]
    
    # read-only view
    can_create = False
    can_edit = False
    can_delete = True
    
    name = "Password Reset Token"
    name_plural = "Password Reset Tokens"
    icon = "fa-solid fa-key"


def setup_admin(app, engine):
    """
    Setup admin panel for the FastAPI application
    
    Args:
        app: FastAPI application instance
        engine: SQLAlchemy engine
    
    Returns:
        Admin instance
    """
    admin = Admin(
        app, 
        engine,
        title="Chat Server Admin",
        base_url="/admin"
    )
    
    # add model views
    admin.add_view(UserAdmin)
    admin.add_view(ChatRoomAdmin)
    admin.add_view(MessageAdmin)
    admin.add_view(PasswordResetTokenAdmin)
    
    return admin
