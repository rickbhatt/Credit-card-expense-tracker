#!/usr/bin/env python3
"""
Database setup script for Credit Card Tracker

Usage:
    python setup_db.py

This script creates all necessary database tables based on SQLAlchemy models.
Run this script whenever you need to initialize or update your database schema.
"""

import sys
import os

# Add src directory to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db.setup import setup_database_tables


def main():
    """Main entry point for database setup"""
    print("Credit Card Tracker - Database Setup")
    print("=" * 40)
    
    success = setup_database_tables()
    
    if success:
        print("\n✅ Database setup completed successfully!")
        print("You can now run your application.")
        sys.exit(0)
    else:
        print("\n❌ Database setup failed!")
        print("Please check your environment variables and database connection.")
        sys.exit(1)


if __name__ == "__main__":
    main()