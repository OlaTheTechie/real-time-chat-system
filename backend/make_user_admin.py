"""
Script to make a user an admin
Usage: python make_user_admin.py <username>
"""
import sys
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user import User

def make_admin(username: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"❌ User '{username}' not found")
            return False
        
        if user.is_admin:
            print(f"ℹ️  User '{username}' is already an admin")
            return True
        
        user.is_admin = True
        db.commit()
        print(f"✓ User '{username}' is now an admin")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_user_admin.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    success = make_admin(username)
    sys.exit(0 if success else 1)
