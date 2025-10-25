"""
Example: How to use the complete pipeline with telecom news scraper data
"""

import asyncio
import json
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_telecom_data():
    """Load telecom news scraper data"""
    # This would be your telecom_report_20251024_214933.json file
    sample_data = {
        "report_period": "Last 7 days (scraped on 2025-10-24 21:49:33)",
        "summary": {
            "total_articles": 9,
            "legal_articles": 1,
            "political_articles": 8,
            "financial_articles": 0
        },
        "categories": {
            "prawo": [
                {
                    "title": "Małopolski Urząd Wojewódzki w Krakowie",
                    "link": "https://www.malopolska.uw.gov.pl/",
                    "snippet": "Małopolski Urząd Wojewódzki w Krakowie zaprasza na oficjalną stronę internetową...",
                    "date": "7 kwi 2011",
                    "source": "Małopolski Urząd Wojewódzki w Krakowie",
                    "category": "prawo",
                    "scraped_at": "2025-10-24T21:49:32.170752"
                }
            ],
            "polityka": [
                {
                    "title": "Wifi mattresses? Internet-connected litter boxes?",
                    "link": "https://www.theguardian.com/commentisfree/picture/2025/oct/24/wifi-mattresses-internet-connected-litter-boxes-stop-it-youre-making-fools-of-us-all",
                    "snippet": "I have to nominate my son's Bluetooth connected light globe...",
                    "date": "4 godziny temu",
                    "source": "The Guardian",
                    "category": "polityka",
                    "scraped_at": "2025-10-24T21:49:33.327723"
                }
            ],
            "financial": []
        }
    }
    return sample_data

def test_pipeline_api():
    """Test the pipeline using the API endpoint"""
    try:
        logger.info("Testing pipeline via API...")
        
        # Load telecom data
        telecom_data = load_telecom_data()
        
        # API endpoint
        url = "http://localhost:8000/api/v1/pipeline/run"
        
        # Request payload
        payload = {
            "telecom_data": telecom_data,
            "domains": ["prawo", "polityka", "financial"]
        }
        
        # Make request
        response = requests.post(url, json=payload, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✓ Pipeline API call successful!")
            logger.info(f"Status: {result.get('status')}")
            logger.info(f"Message: {result.get('message')}")
            
            # Print domain reports
            domain_reports = result.get('domain_reports', {})
            for domain, report in domain_reports.items():
                logger.info(f"Domain {domain}: {report.get('status', 'unknown')}")
            
            # Print final tips and alerts
            tips_alerts = result.get('final_tips_alerts', {})
            if tips_alerts:
                logger.info("Final tips and alerts generated!")
            
            return True
        else:
            logger.error(f"API call failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Pipeline API test failed: {e}")
        return False

def test_health_check():
    """Test if the API is running"""
    try:
        logger.info("Testing API health...")
        
        response = requests.get("http://localhost:8000/health", timeout=10)
        
        if response.status_code == 200:
            logger.info("✓ API is running and healthy")
            return True
        else:
            logger.error(f"API health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

def test_system_status():
    """Test system status endpoint"""
    try:
        logger.info("Testing system status...")
        
        response = requests.get("http://localhost:8000/api/v1/status", timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            logger.info("✓ System status retrieved")
            logger.info(f"System status: {status.get('system_status')}")
            logger.info(f"Domains: {status.get('domains')}")
            return True
        else:
            logger.error(f"Status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return False

def main():
    """Main function to test the pipeline"""
    logger.info("=" * 60)
    logger.info("Telecom News Pipeline Usage Example")
    logger.info("=" * 60)
    
    # Test sequence
    tests = [
        ("Health Check", test_health_check),
        ("System Status", test_system_status),
        ("Pipeline API", test_pipeline_api)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"{test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Pipeline is working correctly.")
    else:
        logger.warning("⚠ Some tests failed. Make sure the API is running.")
    
    return passed == total

if __name__ == "__main__":
    main()
