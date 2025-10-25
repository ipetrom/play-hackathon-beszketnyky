"""
Test script for object storage
"""

import os
import sys
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.objest_storage import upload_file, list_files

def test_object_storage():
    """Test object storage functionality"""
    print("Testing Object Storage...")
    
    try:
        # Test data
        test_data = {
            "test": "data",
            "timestamp": datetime.now().isoformat(),
            "message": "Hello from object storage test"
        }
        
        # Create test file
        test_file = "test_object_storage.json"
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"Created test file: {test_file}")
        
        # Upload to object storage
        s3_key = f"test/{test_file}"
        print(f"Uploading to: {s3_key}")
        
        success = upload_file(test_file, s3_key)
        
        if success:
            print("Upload successful!")
            
            # List files to verify
            print("Listing files in bucket:")
            list_files()
        else:
            print("Upload failed!")
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"Cleaned up {test_file}")
        
        return success
        
    except Exception as e:
        print(f"Object storage test failed: {e}")
        return False

if __name__ == "__main__":
    test_object_storage()
