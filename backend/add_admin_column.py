"""
Migration script to add is_admin column to users table
Run this once after deploying the new code
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def add_admin_column():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
        
        if 'is_admin' not in columns:
            print("Adding is_admin column to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
            conn.commit()
            print("✓ Column added successfully")
        else:
            print("is_admin column already exists")

if __name__ == "__main__":
    add_admin_column()
