#!/usr/bin/env python3
"""Test Scaleway PostgreSQL connection"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.utils.config import settings

print(f"Testing connection to: {settings.DB_HOST}")
print(f"Database: {settings.DB_NAME}")

try:
    engine = create_engine(settings.DB_URL, echo=True)
    
    # Test connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(f"✅ Connection successful! Result: {result.fetchone()}")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)
