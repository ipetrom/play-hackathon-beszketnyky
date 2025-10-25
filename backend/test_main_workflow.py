"""
Test script for the main workflow
Tests the complete integration from scraper to final output
"""

import asyncio
import sys
import os
from datetime import date

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflows.main_workflow import main_workflow
from services.database_simple import create_user, get_user, init_db

async def test_main_workflow():
    """Test the complete main workflow"""
    print("Testing Main Workflow Integration...")
    
    try:
        # Initialize database first
        print("Initializing database...")
        init_db()
        print("Database initialized")
        
        # Create a test user
        user_email = "test@workflow2.com"
        user_name = "Workflow Test User 2"
        
        print(f"Creating test user: {user_email}")
        user_result = create_user(user_email, user_name)
        print(f"User creation: {user_result}")
        
        if user_result.get("status") != "success":
            print("Failed to create test user")
            return False
        
        # Run the main workflow
        print("\nRunning main workflow...")
        workflow_result = await main_workflow.run_complete_workflow(user_email, days_back=7)
        
        print(f"Workflow result: {workflow_result}")
        
        if workflow_result.get("status") == "success":
            print("Main workflow completed successfully!")
            print(f"   - Report ID: {workflow_result.get('report_id')}")
            print(f"   - Articles processed: {workflow_result.get('articles_processed', 0)}")
            print(f"   - Domains processed: {workflow_result.get('domains_processed', 0)}")
            print(f"   - Storage paths: {workflow_result.get('storage_paths', {})}")
            return True
        else:
            print(f"Main workflow failed: {workflow_result.get('message', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_main_workflow())
