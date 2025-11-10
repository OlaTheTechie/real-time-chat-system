"""
Migration script to add is_admin column to users table
Run this once after deploying the new code
Works with both SQLite and PostgreSQL
"""
from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

def add_admin_column():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if column exists using SQLAlchemy inspector (works for both SQLite and PostgreSQL)
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'is_admin' not in columns:
            print("Adding is_admin column to users table...")
            # Use appropriate syntax based on database type
            if 'postgresql' in settings.DATABASE_URL:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
            else:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
            conn.commit()
            print("✓ Column added successfully")
        else:
            print("✓ is_admin column already exists")

if __name__ == "__main__":
    add_admin_column()
