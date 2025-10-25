"""
Simple test for the main workflow components
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_simple import init_db, create_user, get_user

def test_database_connection():
    """Test database connection and basic operations"""
    print("Testing database connection...")
    
    try:
        # Initialize database
        print("Initializing database...")
        init_db()
        print("Database initialized successfully")
        
        # Test user creation
        print("Testing user creation...")
        user_result = create_user("test@simple.com", "Simple Test User")
        print(f"User creation result: {user_result}")
        
        if user_result.get("status") == "success":
            print("User creation successful")
            
            # Test user retrieval
            user = get_user("test@simple.com")
            print(f"Retrieved user: {user}")
            
            if user:
                print("User retrieval successful")
                return True
            else:
                print("User retrieval failed")
                return False
        else:
            print(f"User creation failed: {user_result.get('message')}")
            return False
        
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()
