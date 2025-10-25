"""
S3 Loader service for loading telecom data from object storage
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os

from services.objest_storage import download_file, list_files

logger = logging.getLogger(__name__)

def load_report_from_s3() -> Dict[str, Any]:
    """
    Load the latest telecom report from S3 object storage
    
    Returns:
        Telecom report data or empty structure if not found
    """
    try:
        # Look for the latest telecom report file
        # Assuming files are named like: telecom_report_YYYYMMDD_HHMMSS.json
        files = list_files()
        
        if not files:
            logger.warning("No files found in S3 bucket")
            return _create_empty_telecom_data()
        
        # Find the latest telecom report
        telecom_files = [f for f in files if f.startswith('telecom_report_') and f.endswith('.json')]
        
        if not telecom_files:
            logger.warning("No telecom report files found in S3")
            return _create_empty_telecom_data()
        
        # Sort by filename (which includes timestamp) to get the latest
        latest_file = sorted(telecom_files)[-1]
        
        # Download the file
        local_file = f"temp_telecom_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if download_file(latest_file, local_file):
            # Load the JSON data
            with open(local_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clean up temp file
            os.remove(local_file)
            
            logger.info(f"Loaded telecom report from S3: {latest_file}")
            return data
        else:
            logger.error(f"Failed to download telecom report: {latest_file}")
            return _create_empty_telecom_data()
            
    except Exception as e:
        logger.error(f"Error loading telecom report from S3: {e}")
        return _create_empty_telecom_data()

def _create_empty_telecom_data() -> Dict[str, Any]:
    """Create empty telecom data structure"""
    return {
        "report_period": "No data available",
        "summary": {
            "total_articles": 0,
            "legal_articles": 0,
            "political_articles": 0,
            "financial_articles": 0
        },
        "key_insights": [],
        "risk_areas": [],
        "action_items": [],
        "categories": {
            "prawo": [],
            "polityka": [],
            "financial": []
        },
        "scraped_at": datetime.now().isoformat(),
        "total_articles": 0
    }