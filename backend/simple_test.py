"""
Simple test to isolate the database connection issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test direct connection without any imports
from sqlalchemy import create_engine, text

def test_direct_connection():
    """Test direct database connection"""
    print("Testing direct database connection...")
    
    try:
        # Direct connection string
        database_url = "postgresql://root:cXf2dtQlN8m6*{tef,]B@151.115.13.23:12061/rdb"
        
        # Create engine
        engine = create_engine(database_url, echo=True)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            print(f"Database test result: {row}")
        
        print("Direct connection successful!")
        return True
        
    except Exception as e:
        print(f"Direct connection failed: {e}")
        return False

if __name__ == "__main__":
    test_direct_connection()
