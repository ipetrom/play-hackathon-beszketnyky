"""
Test script for Simple Smart Tracker database
"""

import sys
import os
from datetime import date

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_simple import (
    init_db, create_user, get_user, create_report, 
    get_user_reports, get_report, update_report_status
)

def test_simple_database():
    """Test simple database operations"""
    print("Testing Simple Smart Tracker Database...")
    
    try:
        # Initialize database
        print("Initializing database connection...")
        init_db()
        print("Database connected successfully!")
        
        # Test user operations
        print("\nTesting user operations...")
        
        # Create user
        user_result = create_user("viktor.kulyk@hotmail.com", "Viktor", "09:00:00", 1)
        print(f"User creation: {user_result}")
        
        # Get user
        user = get_user("viktor.kulyk@hotmail.com")
        print(f"Retrieved user: {user}")
        
        # Test report operations
        print("\nTesting report operations...")
        
        # Create report
        report_result = create_report(
            user_email="viktor.kulyk@hotmail.com",
            report_date=date.today(),
            report_domains=["prawo", "polityka", "financial"],
            report_alerts=3,
            report_tips=5,
            report_alerts_tips_json_path="viktor.kulyk@hotmail.com/reports/2025-01-25/tips_alerts.json",
            path_to_report="viktor.kulyk@hotmail.com/reports/2025-01-25/report.txt",
            path_to_report_vector="viktor.kulyk@hotmail.com/reports/2025-01-25/vectors/",
            report_status="published"
        )
        print(f"Report creation: {report_result}")
        
        # Get user reports
        user_reports = get_user_reports("viktor.kulyk@hotmail.com")
        print(f"User reports: {len(user_reports)} found")
        for report in user_reports:
            print(f"  - Report {report['report_id']}: {report['report_date']} ({report['report_status']})")
        
        # Get specific report
        if report_result.get("status") == "success":
            report_id = report_result["report_id"]
            specific_report = get_report(report_id)
            print(f"Specific report: {specific_report}")
            
            # Update report status
            status_result = update_report_status(report_id, "archived")
            print(f"Status update: {status_result}")
        
        print("\nAll database tests passed!")
        
    except Exception as e:
        print(f"Database test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_simple_database()
