from app.database.database import Base
from app.models.user import User
from app.models.chat import ChatRoom, Message

# import all models to ensure they are registered with sqlalchemy
__all__ = ["Base", "User", "ChatRoom", "Message"]