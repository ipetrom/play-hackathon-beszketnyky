"""
Test script for storage integration
Tests the complete workflow with object storage
"""

import asyncio
import sys
import os
from datetime import date

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflows.main_workflow import main_workflow
from services.database_simple import create_user, get_user, init_db, get_user_reports

async def test_storage_integration():
    """Test the complete workflow with object storage"""
    print("Testing Storage Integration...")
    
    try:
        # Initialize database
        print("Initializing database...")
        init_db()
        print("Database initialized")
        
        # Create a test user
        user_email = "test@storage4.com"
        user_name = "Storage Test User 4"
        
        print(f"Creating test user: {user_email}")
        user_result = create_user(user_email, user_name)
        print(f"User creation: {user_result}")
        
        if user_result.get("status") != "success":
            print("Failed to create test user")
            return False
        
        # Run the main workflow
        print("\nRunning main workflow with storage...")
        workflow_result = await main_workflow.run_complete_workflow(user_email, days_back=7)
        
        print(f"Workflow result: {workflow_result}")
        
        if workflow_result.get("status") == "success":
            print("Main workflow completed successfully!")
            
            # Check database report
            reports = get_user_reports(user_email)
            print(f"Database reports: {reports}")
            
            if reports:
                report = reports[0]
                print(f"Report details:")
                print(f"  - Report ID: {report.get('report_id')}")
                print(f"  - Alerts: {report.get('report_alerts')}")
                print(f"  - Tips: {report.get('report_tips')}")
                print(f"  - Storage paths:")
                print(f"    - Tips/Alerts JSON: {report.get('report_alerts_tips_json_path', 'NOT SET')}")
                print(f"    - Final Report: {report.get('path_to_report', 'NOT SET')}")
                
                # Check if storage paths are set
                if report.get('report_alerts_tips_json_path') and report.get('path_to_report'):
                    print("SUCCESS: Storage paths are properly set in database!")
                    return True
                else:
                    print("WARNING: Storage paths are not set in database")
                    return False
            else:
                print("ERROR: No reports found in database")
                return False
        else:
            print(f"Main workflow failed: {workflow_result.get('message', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_storage_integration())
