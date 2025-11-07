#!/usr/bin/env python3
"""
Database management CLI script
Provides commands for initializing, resetting, and seeding the database
"""
import sys
import argparse
from app.database.init_db import init_db, drop_db, seed_test_data
from app.database.database import SessionLocal


def main():
    parser = argparse.ArgumentParser(description="Database management commands")
    parser.add_argument(
        "command",
        choices=["init", "reset", "seed", "drop"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    if args.command == "init":
        print("Initializing database...")
        init_db()
        print("Database initialized successfully!")
        
    elif args.command == "reset":
        print("Resetting database...")
        response = input("This will delete all data. Are you sure? (yes/no): ")
        if response.lower() == "yes":
            drop_db()
            init_db()
            print("Database reset successfully!")
        else:
            print("Reset cancelled")
            
    elif args.command == "seed":
        print("Seeding database with test data...")
        db = SessionLocal()
        try:
            seed_test_data(db)
            print("Database seeded successfully!")
        finally:
            db.close()
            
    elif args.command == "drop":
        print("Dropping all database tables...")
        response = input("This will delete all data. Are you sure? (yes/no): ")
        if response.lower() == "yes":
            drop_db()
            print("Database dropped successfully!")
        else:
            print("Drop cancelled")


if __name__ == "__main__":
    main()
