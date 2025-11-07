"""
Database initialization script
Creates all tables and optionally seeds initial data
"""
from sqlalchemy.orm import Session
from app.database.database import engine, SessionLocal, Base
from app.models import User, ChatRoom, Message, PasswordResetToken
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialize database by creating all tables
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_db() -> None:
    """
    Drop all database tables (use with caution!)
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def seed_test_data(db: Session) -> None:
    """
    Seed database with test data for development
    """
    try:
        # Check if data already exists
        existing_user = db.query(User).first()
        if existing_user:
            logger.info("Database already contains data, skipping seed")
            return
        
        # Create test users
        user1 = User(
            email="alice@example.com",
            username="alice",
            hashed_password=get_password_hash("password123"),
            is_online=False
        )
        user2 = User(
            email="bob@example.com",
            username="bob",
            hashed_password=get_password_hash("password123"),
            is_online=False
        )
        
        db.add(user1)
        db.add(user2)
        db.commit()
        db.refresh(user1)
        db.refresh(user2)
        
        logger.info("Test users created successfully")
        
    except Exception as e:
        logger.error(f"Error seeding test data: {e}")
        db.rollback()
        raise


if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    
    # Optionally seed test data
    db = SessionLocal()
    try:
        seed_test_data(db)
    finally:
        db.close()
    
    logger.info("Database initialization complete")
