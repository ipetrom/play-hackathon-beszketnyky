"""
Example usage of the Telecommunications Intelligence Scraper
Demonstrates how to use the system for different scenarios.
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from main_scraper import TelecomIntelligenceOrchestrator

async def example_weekly_report():
    """Example: Generate weekly intelligence report"""
    print("Running weekly intelligence report...")
    
    # Initialize orchestrator
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        print("Error: SERPER_API_KEY not set")
        return
    
    orchestrator = TelecomIntelligenceOrchestrator(serper_api_key)
    
    # Run weekly report (last 7 days)
    report = await orchestrator.run_weekly_report(days_back=7)
    
    print(f"Weekly report generated with {report['report_metadata']['total_articles']} articles")
    return report

async def example_daily_brief():
    """Example: Generate daily brief"""
    print("Running daily brief...")
    
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        print("Error: SERPER_API_KEY not set")
        return
    
    orchestrator = TelecomIntelligenceOrchestrator(serper_api_key)
    
    # Run daily brief (last 1 day)
    daily_data = await orchestrator.run_daily_brief(days_back=1)
    
    print(f"Daily brief generated with {daily_data['total_articles']} articles")
    return daily_data

async def example_legal_only():
    """Example: Scrape only legal news"""
    print("Running legal news scraper...")
    
    from legal_scraper import LegalTelecomScraper
    
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        print("Error: SERPER_API_KEY not set")
        return
    
    scraper = LegalTelecomScraper(serper_api_key)
    legal_data = await scraper.scrape_all_legal_news(days_back=7)
    
    print(f"Legal scraping completed: {legal_data['total_articles']} articles")
    print(f"High impact: {legal_data['high_impact_count']}")
    print(f"Medium impact: {legal_data['medium_impact_count']}")
    print(f"Low impact: {legal_data['low_impact_count']}")
    
    return legal_data

async def example_political_only():
    """Example: Scrape only political news"""
    print("Running political news scraper...")
    
    from political_scraper import PoliticalTelecomScraper
    
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        print("Error: SERPER_API_KEY not set")
        return
    
    scraper = PoliticalTelecomScraper(serper_api_key)
    political_data = await scraper.scrape_all_political_news(days_back=7)
    
    print(f"Political scraping completed: {political_data['total_articles']} articles")
    print(f"Government policy: {len(political_data['government_policy'])}")
    print(f"EU policy: {len(political_data['eu_policy'])}")
    print(f"International relations: {len(political_data['international_relations'])}")
    
    return political_data

async def example_financial_only():
    """Example: Scrape only financial news"""
    print("Running financial news scraper...")
    
    from financial_scraper import FinancialTelecomScraper
    
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        print("Error: SERPER_API_KEY not set")
        return
    
    scraper = FinancialTelecomScraper(serper_api_key)
    financial_data = await scraper.scrape_all_financial_news(days_back=7)
    
    print(f"Financial scraping completed: {financial_data['total_articles']} articles")
    print(f"Earnings: {len(financial_data['earnings'])}")
    print(f"Investments: {len(financial_data['investments'])}")
    print(f"Market movements: {len(financial_data['market_movements'])}")
    print(f"Currency rates: {len(financial_data['currency_rates'])}")
    
    return financial_data

async def example_custom_timeframe():
    """Example: Scrape with custom timeframe"""
    print("Running custom timeframe scraping...")
    
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        print("Error: SERPER_API_KEY not set")
        return
    
    orchestrator = TelecomIntelligenceOrchestrator(serper_api_key)
    
    # Scrape last 3 days
    scraping_data = await orchestrator.run_comprehensive_scraping(days_back=3)
    
    print(f"Custom timeframe scraping completed: {scraping_data['total_articles']} articles")
    print(f"General: {scraping_data['general']['total_articles']}")
    print(f"Legal: {scraping_data['legal']['total_articles']}")
    print(f"Political: {scraping_data['political']['total_articles']}")
    print(f"Financial: {scraping_data['financial']['total_articles']}")
    
    return scraping_data

def print_usage_examples():
    """Print usage examples"""
    print("""
Telecommunications Intelligence Scraper - Usage Examples
=====================================================

1. Weekly Intelligence Report (Recommended):
   python main_scraper.py

2. Daily Brief:
   python example_usage.py daily

3. Legal News Only:
   python example_usage.py legal

4. Political News Only:
   python example_usage.py political

5. Financial News Only:
   python example_usage.py financial

6. Custom Timeframe:
   python example_usage.py custom

7. All Examples:
   python example_usage.py all

Environment Setup:
export SERPER_API_KEY="your_serper_api_key_here"
""")

async def main():
    """Main function to run examples"""
    import sys
    
    if len(sys.argv) < 2:
        print_usage_examples()
        return
    
    command = sys.argv[1].lower()
    
    if command == "weekly":
        await example_weekly_report()
    elif command == "daily":
        await example_daily_brief()
    elif command == "legal":
        await example_legal_only()
    elif command == "political":
        await example_political_only()
    elif command == "financial":
        await example_financial_only()
    elif command == "custom":
        await example_custom_timeframe()
    elif command == "all":
        print("Running all examples...")
        await example_weekly_report()
        await example_daily_brief()
        await example_legal_only()
        await example_political_only()
        await example_financial_only()
        await example_custom_timeframe()
    else:
        print_usage_examples()

if __name__ == "__main__":
    asyncio.run(main())
