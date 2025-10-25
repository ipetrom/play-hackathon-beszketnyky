"""
Test script for Smart Tracker database
Run this to verify database connection and operations
"""

import asyncio
import sys
import os
from datetime import date

# Set environment variable before importing
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://smart_tracker_user:smart_tracker_password@localhost:5432/smart_tracker'

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_new import (
    init_db, create_user, get_user, create_report, 
    get_user_reports, get_report, update_report_status
)

async def test_database():
    """Test database operations"""
    print("Testing Smart Tracker Database...")
    
    try:
        # Initialize database
        print("Initializing database connection...")
        await init_db()
        print("Database connected successfully!")
        
        # Test user operations
        print("\nTesting user operations...")
        
        # Create test user
        user_result = await create_user("test@play.pl", "Test User")
        print(f"User creation: {user_result}")
        
        # Get user
        user = await get_user("test@play.pl")
        print(f"Retrieved user: {user}")
        
        # Test report operations
        print("\nTesting report operations...")
        
        # Create test report
        report_result = await create_report(
            user_email="test@play.pl",
            report_date=date.today(),
            report_domains=["prawo", "polityka", "financial"],
            report_alerts=3,
            report_tips=5,
            report_alerts_tips_json_path="test@play.pl/reports/2025-01-25/tips_alerts.json",
            path_to_report="test@play.pl/reports/2025-01-25/report.txt",
            path_to_report_vector="test@play.pl/reports/2025-01-25/vectors/",
            report_status="published"
        )
        print(f"Report creation: {report_result}")
        
        # Get user reports
        reports = await get_user_reports("test@play.pl")
        print(f"User reports: {len(reports)} found")
        for report in reports:
            print(f"  - Report {report['report_id']}: {report['report_date']} ({report['report_status']})")
        
        # Get specific report
        if reports:
            report_id = reports[0]['report_id']
            report = await get_report(report_id)
            print(f"Specific report: {report}")
            
            # Update report status
            update_result = await update_report_status(report_id, "archived")
            print(f"Status update: {update_result}")
        
        print("\nAll database tests passed!")
        
    except Exception as e:
        print(f"Database test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_database())
    sys.exit(0 if success else 1)
