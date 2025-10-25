"""
Example usage of the Telecom News Multi-Agent System
"""

import asyncio
import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing Telecom News Multi-Agent System API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/../health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: Get available domains
    print("\n2. Available Domains")
    try:
        response = requests.get(f"{BASE_URL}/domains")
        print(f"✅ Domains: {response.status_code}")
        print(f"   Domains: {response.json()}")
    except Exception as e:
        print(f"❌ Domains request failed: {e}")
    
    # Test 3: Get system status
    print("\n3. System Status")
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"✅ System status: {response.status_code}")
        print(f"   Status: {response.json()}")
    except Exception as e:
        print(f"❌ Status request failed: {e}")
    
    # Test 4: Get domain status
    print("\n4. Domain Status")
    for domain in ["prawo", "polityka", "financial"]:
        try:
            response = requests.get(f"{BASE_URL}/domains/{domain}/status")
            print(f"✅ {domain} status: {response.status_code}")
            print(f"   {domain}: {response.json()}")
        except Exception as e:
            print(f"❌ {domain} status failed: {e}")
    
    # Test 5: Search domain
    print("\n5. Search Domain")
    try:
        response = requests.get(f"{BASE_URL}/search/prawo", params={"query": "Poland telecom law 2025"})
        print(f"✅ Search: {response.status_code}")
        print(f"   Search result: {response.json()}")
    except Exception as e:
        print(f"❌ Search failed: {e}")
    
    # Test 6: Get analytics
    print("\n6. Analytics")
    try:
        response = requests.get(f"{BASE_URL}/analytics")
        print(f"✅ Analytics: {response.status_code}")
        print(f"   Analytics: {response.json()}")
    except Exception as e:
        print(f"❌ Analytics failed: {e}")

def run_workflow_example():
    """Example of running the complete workflow"""
    print("\n🚀 Running Complete Workflow Example")
    print("=" * 50)
    
    # Run full workflow
    print("\n1. Running Full Workflow")
    try:
        response = requests.post(f"{BASE_URL}/workflow/run")
        print(f"✅ Full workflow: {response.status_code}")
        result = response.json()
        print(f"   Workflow ID: {result.get('workflow_id')}")
        print(f"   Execution time: {result.get('execution_time')} seconds")
        print(f"   Domains processed: {result.get('domains_processed')}")
        print(f"   Status: {result.get('status')}")
    except Exception as e:
        print(f"❌ Full workflow failed: {e}")
    
    # Run single domain workflow
    print("\n2. Running Single Domain Workflow (Prawo)")
    try:
        response = requests.post(f"{BASE_URL}/workflow/domain/prawo")
        print(f"✅ Single domain workflow: {response.status_code}")
        result = response.json()
        print(f"   Domain: {result.get('domain')}")
        print(f"   Status: {result.get('result', {}).get('status')}")
    except Exception as e:
        print(f"❌ Single domain workflow failed: {e}")

def get_reports_example():
    """Example of getting reports and tips/alerts"""
    print("\n📊 Getting Reports and Tips/Alerts")
    print("=" * 50)
    
    # Get all reports
    print("\n1. All Domain Reports")
    try:
        response = requests.get(f"{BASE_URL}/reports")
        print(f"✅ All reports: {response.status_code}")
        result = response.json()
        print(f"   Total domains: {result.get('total_domains')}")
        print(f"   Available reports: {list(result.get('reports', {}).keys())}")
    except Exception as e:
        print(f"❌ All reports failed: {e}")
    
    # Get specific domain report
    print("\n2. Specific Domain Report (Prawo)")
    try:
        response = requests.get(f"{BASE_URL}/reports/prawo")
        print(f"✅ Prawo report: {response.status_code}")
        result = response.json()
        if result.get('report'):
            report = result['report']
            print(f"   Domain: {report.get('domain')}")
            print(f"   Confidence: {report.get('confidence')}")
            print(f"   Status: {report.get('status')}")
            print(f"   Executive Summary: {report.get('executive_summary', '')[:100]}...")
    except Exception as e:
        print(f"❌ Prawo report failed: {e}")
    
    # Get tips and alerts
    print("\n3. Tips and Alerts")
    try:
        response = requests.get(f"{BASE_URL}/tips-alerts")
        print(f"✅ Tips and alerts: {response.status_code}")
        result = response.json()
        if result.get('tips_alerts'):
            tips_alerts = result['tips_alerts']
            print(f"   Summary: {tips_alerts.get('summary', {})}")
            print(f"   Priority alerts: {len(tips_alerts.get('priority_alerts', []))}")
            print(f"   Actionable tips: {len(tips_alerts.get('actionable_tips', []))}")
    except Exception as e:
        print(f"❌ Tips and alerts failed: {e}")

def agent_output_example():
    """Example of getting agent outputs"""
    print("\n🤖 Getting Agent Outputs")
    print("=" * 50)
    
    agents = ["keeper", "writer", "perplexity", "final_summarizer"]
    domains = ["prawo", "polityka", "financial"]
    
    for agent in agents:
        for domain in domains:
            try:
                response = requests.get(f"{BASE_URL}/agents/{agent}/output/{domain}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {agent} - {domain}: {result.get('status', 'unknown')}")
                else:
                    print(f"⚠️  {agent} - {domain}: No output available")
            except Exception as e:
                print(f"❌ {agent} - {domain}: {e}")

def main():
    """Main example function"""
    print("🎯 Telecom News Multi-Agent System - Example Usage")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Run workflow example
    run_workflow_example()
    
    # Get reports example
    get_reports_example()
    
    # Agent outputs example
    agent_output_example()
    
    print("\n" + "=" * 60)
    print("✅ Example usage completed!")
    print("📚 For more information, check the API documentation at:")
    print("   http://localhost:8000/docs")
    print("=" * 60)

if __name__ == "__main__":
    main()
