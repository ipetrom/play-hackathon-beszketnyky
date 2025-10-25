"""
Test script for database path storage
Tests if storage paths are properly saved to database
"""

import sys
import os
from datetime import date

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_simple import create_user, get_user, init_db, create_report, get_user_reports

def test_database_paths():
    """Test if storage paths are properly saved to database"""
    print("Testing Database Path Storage...")
    
    try:
        # Initialize database
        print("Initializing database...")
        init_db()
        print("Database initialized")
        
        # Create a test user
        user_email = "test@paths.com"
        user_name = "Paths Test User"
        
        print(f"Creating test user: {user_email}")
        user_result = create_user(user_email, user_name)
        print(f"User creation: {user_result}")
        
        if user_result.get("status") != "success":
            print("Failed to create test user")
            return False
        
        # Create a test report with storage paths
        print("\nCreating test report with storage paths...")
        test_tips_alerts_path = "test@paths.com/reports/20251025_052500/tips_alerts.json"
        test_final_report_path = "test@paths.com/reports/20251025_052500/final_report.txt"
        
        report_result = create_report(
            user_email=user_email,
            report_date=date.today(),
            report_domains=["prawo", "polityka", "financial"],
            report_alerts=3,
            report_tips=5,
            report_alerts_tips_json_path=test_tips_alerts_path,
            path_to_report=test_final_report_path,
            path_to_report_vector="",
            report_status="published"
        )
        
        print(f"Report creation result: {report_result}")
        
        if report_result.get("status") == "success":
            print("Report created successfully!")
            
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
                if (report.get('report_alerts_tips_json_path') == test_tips_alerts_path and 
                    report.get('path_to_report') == test_final_report_path):
                    print("SUCCESS: Storage paths are properly set in database!")
                    return True
                else:
                    print("ERROR: Storage paths are not set correctly in database")
                    print(f"Expected tips_alerts_path: {test_tips_alerts_path}")
                    print(f"Got tips_alerts_path: {report.get('report_alerts_tips_json_path')}")
                    print(f"Expected final_report_path: {test_final_report_path}")
                    print(f"Got final_report_path: {report.get('path_to_report')}")
                    return False
            else:
                print("ERROR: No reports found in database")
                return False
        else:
            print(f"Report creation failed: {report_result.get('message')}")
            return False
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    test_database_paths()
