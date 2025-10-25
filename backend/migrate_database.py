"""
Database migration script to add missing columns and fix schema
"""

import asyncio
import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_new import init_db, engine

async def migrate_database():
    """Add missing columns to the database"""
    try:
        print("Starting database migration...")
        
        # Initialize database connection
        await init_db()
        
        async with engine.begin() as conn:
            # Add missing columns to users table
            print("Adding report_time and report_delay_days columns to users table...")
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS report_time TIME DEFAULT '09:00:00'
            """))
            
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS report_delay_days INTEGER DEFAULT 1
            """))
            
            print("Migration completed successfully!")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(migrate_database())
