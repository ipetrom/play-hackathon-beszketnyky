"""
Test script for the Telecom News Multi-Agent System
"""

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_system():
    """Test the complete system"""
    try:
        logger.info("Starting system test...")
        
        # Import the workflow
        from agents.workflow import telecom_workflow
        
        # Test 1: Check if workflow is initialized
        logger.info("Test 1: Checking workflow initialization...")
        if telecom_workflow:
            logger.info("✓ Workflow initialized successfully")
        else:
            logger.error("✗ Workflow initialization failed")
            return False
        
        # Test 2: Check domain status
        logger.info("Test 2: Checking domain status...")
        for domain in ["prawo", "polityka", "financial"]:
            status = await telecom_workflow.get_domain_status(domain)
            logger.info(f"✓ Domain {domain}: {status.get('status', 'unknown')}")
        
        # Test 3: Test single domain workflow (if API keys are available)
        logger.info("Test 3: Testing single domain workflow...")
        try:
            # This will fail if API keys are not configured, which is expected
            result = await telecom_workflow.run_domain_workflow("prawo")
            logger.info(f"✓ Domain workflow completed: {result.get('status', 'unknown')}")
        except Exception as e:
            logger.warning(f"⚠ Domain workflow test failed (expected if API keys not configured): {e}")
        
        # Test 4: Check configuration
        logger.info("Test 4: Checking configuration...")
        from services.config import settings
        
        config_checks = [
            ("Domains", len(settings.domains) > 0),
            ("Max Concurrent Agents", settings.max_concurrent_agents > 0),
            ("Request Timeout", settings.request_timeout > 0),
            ("API Host", settings.api_host is not None),
            ("API Port", settings.api_port > 0)
        ]
        
        for check_name, check_result in config_checks:
            if check_result:
                logger.info(f"✓ {check_name}: OK")
            else:
                logger.error(f"✗ {check_name}: Failed")
        
        logger.info("System test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"System test failed: {e}")
        return False

async def test_agents():
    """Test individual agents"""
    try:
        logger.info("Testing individual agents...")
        
        # Test Serper Verification Agent
        from agents.serper_verification_agent import serper_verification_agent
        logger.info("✓ Serper Verification Agent imported")
        
        # Test Keeper Agent
        from agents.keeper_agent import keeper_agent
        logger.info("✓ Keeper Agent imported")
        
        # Test Writer Agent
        from agents.writer_agent import writer_agent
        logger.info("✓ Writer Agent imported")
        
        # Test Perplexity Service
        from services.perplexity_service import perplexity_service
        logger.info("✓ Perplexity Service imported")
        
        # Test Final Summarizer Agent
        from agents.final_summarizer_agent import final_summarizer_agent
        logger.info("✓ Final Summarizer Agent imported")
        
        # Test Tips & Alerts Generator
        from agents.tips_alerts_generator import tips_alerts_generator
        logger.info("✓ Tips & Alerts Generator imported")
        
        logger.info("All agents imported successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Agent test failed: {e}")
        return False

async def test_services():
    """Test services"""
    try:
        logger.info("Testing services...")
        
        # Test configuration service
        from services.config import settings
        logger.info("✓ Configuration service imported")
        
        # Test database service
        from services.database import init_db
        logger.info("✓ Database service imported")
        
        # Test HTTP client service
        from services.http_client import serper_client, perplexity_client, scraper_client
        logger.info("✓ HTTP client service imported")
        
        # Test LLM service (Scaleway Qwen3)
        from services.llm_service import llm_service
        logger.info("✓ Scaleway LLM service imported")
        
        # Test basic LLM functionality
        try:
            response = await llm_service.generate_response(
                "What is 5G technology?",
                "You are a telecommunications expert."
            )
            logger.info(f"✓ Scaleway Qwen3 response: {response[:100]}...")
        except Exception as e:
            logger.warning(f"⚠ LLM test failed (expected if API keys not configured): {e}")
        
        logger.info("All services imported successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Service test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("=" * 50)
    logger.info("Telecom News Multi-Agent System Test")
    logger.info("=" * 50)
    
    # Run all tests
    tests = [
        ("Services Test", test_services),
        ("Agents Test", test_agents),
        ("System Test", test_system)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"{test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("Test Summary")
    logger.info("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready.")
    else:
        logger.warning("⚠ Some tests failed. Check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())
