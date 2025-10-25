"""
Main Telecommunications Intelligence Scraper
Orchestrates all scrapers and generates comprehensive reports.
"""

import asyncio
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from telecom_news_scraper import TelecomNewsScraper
from legal_scraper import LegalTelecomScraper
from political_scraper import PoliticalTelecomScraper
from financial_scraper import FinancialTelecomScraper
from report_generator import TelecomReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelecomIntelligenceOrchestrator:
    def __init__(self, serper_api_key: str):
        self.serper_api_key = serper_api_key
        self.scrapers = {
            "general": TelecomNewsScraper(serper_api_key),
            "legal": LegalTelecomScraper(serper_api_key),
            "political": PoliticalTelecomScraper(serper_api_key),
            "financial": FinancialTelecomScraper(serper_api_key)
        }
        self.report_generator = TelecomReportGenerator()

    async def run_comprehensive_scraping(self, days_back: int = 7) -> Dict[str, Any]:
        """Run all scrapers and generate comprehensive report"""
        logger.info("Starting comprehensive telecommunications intelligence scraping...")
        
        # Run all scrapers concurrently
        tasks = {
            "general": self.scrapers["general"].scrape_all_news(days_back),
            "legal": self.scrapers["legal"].scrape_all_legal_news(days_back),
            "political": self.scrapers["political"].scrape_all_political_news(days_back),
            "financial": self.scrapers["financial"].scrape_all_financial_news(days_back)
        }
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks.values())
        
        # Organize results
        scraping_results = {
            "general": results[0],
            "legal": results[1],
            "political": results[2],
            "financial": results[3],
            "scraped_at": datetime.now().isoformat(),
            "days_back": days_back
        }
        
        # Calculate totals
        total_articles = (
            scraping_results["general"]["total_articles"] +
            scraping_results["legal"]["total_articles"] +
            scraping_results["political"]["total_articles"] +
            scraping_results["financial"]["total_articles"]
        )
        
        scraping_results["total_articles"] = total_articles
        
        logger.info(f"Scraping completed. Total articles found: {total_articles}")
        logger.info(f"General: {scraping_results['general']['total_articles']}")
        logger.info(f"Legal: {scraping_results['legal']['total_articles']}")
        logger.info(f"Political: {scraping_results['political']['total_articles']}")
        logger.info(f"Financial: {scraping_results['financial']['total_articles']}")
        
        return scraping_results

    async def generate_intelligence_report(self, scraping_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive intelligence report"""
        logger.info("Generating intelligence report...")
        
        # Prepare data for report generation
        report_data = {
            "total_articles": scraping_data["total_articles"],
            "legal": scraping_data["legal"],
            "polityka": scraping_data["political"],
            "financial": scraping_data["financial"]
        }
        
        # Generate weekly report
        report = self.report_generator.generate_weekly_report(report_data)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_generator.save_report(report, f"telecom_intelligence_{timestamp}.json")
        
        # Generate and save summary
        summary_text = self.report_generator.generate_summary_text(report)
        summary_file = report_file.replace('.json', '_summary.md')
        
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_text)
        
        logger.info(f"Report saved: {report_file}")
        logger.info(f"Summary saved: {summary_file}")
        
        return report

    async def run_daily_brief(self, days_back: int = 1) -> Dict[str, Any]:
        """Run daily brief scraping"""
        logger.info("Starting daily brief scraping...")
        
        # Run scrapers for daily brief
        tasks = {
            "legal": self.scrapers["legal"].scrape_all_legal_news(days_back),
            "political": self.scrapers["political"].scrape_all_political_news(days_back),
            "financial": self.scrapers["financial"].scrape_all_financial_news(days_back)
        }
        
        results = await asyncio.gather(*tasks.values())
        
        daily_data = {
            "legal": results[0],
            "political": results[1],
            "financial": results[2],
            "scraped_at": datetime.now().isoformat(),
            "days_back": days_back
        }
        
        total_articles = (
            daily_data["legal"]["total_articles"] +
            daily_data["political"]["total_articles"] +
            daily_data["financial"]["total_articles"]
        )
        
        daily_data["total_articles"] = total_articles
        
        # Save daily data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        daily_file = f"reports/daily_brief_{timestamp}.json"
        
        os.makedirs("reports", exist_ok=True)
        with open(daily_file, "w", encoding="utf-8") as f:
            json.dump(daily_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Daily brief saved: {daily_file}")
        logger.info(f"Daily articles found: {total_articles}")
        
        return daily_data

    async def run_weekly_report(self, days_back: int = 7) -> Dict[str, Any]:
        """Run full weekly report"""
        logger.info("Starting weekly report generation...")
        
        # Run comprehensive scraping
        scraping_data = await self.run_comprehensive_scraping(days_back)
        
        # Generate intelligence report
        report = await self.generate_intelligence_report(scraping_data)
        
        return report

    def save_raw_data(self, data: Dict[str, Any], filename: str = None) -> str:
        """Save raw scraping data"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"raw_telecom_data_{timestamp}.json"
        
        os.makedirs("reports", exist_ok=True)
        filepath = os.path.join("reports", filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Raw data saved: {filepath}")
        return filepath

async def main():
    """Main function to run the orchestrator"""
    # Get API key from environment
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        logger.error("SERPER_API_KEY environment variable not set")
        logger.error("Please set your Serper API key: export SERPER_API_KEY='your_key_here'")
        return
    
    # Initialize orchestrator
    orchestrator = TelecomIntelligenceOrchestrator(serper_api_key)
    
    try:
        # Run weekly report
        logger.info("Running weekly telecommunications intelligence report...")
        report = await orchestrator.run_weekly_report(days_back=7)
        
        logger.info("Weekly report generation completed successfully!")
        
        # Print summary
        print("\n" + "="*60)
        print("TELECOMMUNICATIONS INTELLIGENCE REPORT SUMMARY")
        print("="*60)
        print(f"Total Articles Scraped: {report['report_metadata']['total_articles']}")
        print(f"Report Generated: {report['report_metadata']['generated_at']}")
        print(f"Period Covered: {report['report_metadata']['period']}")
        print(f"Overall Risk Level: {report['risk_assessment']['overall_risk_level'].upper()}")
        print(f"Action Items: {len(report['action_items'])}")
        print("="*60)
        
        return report
        
    except Exception as e:
        logger.error(f"Error running orchestrator: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
