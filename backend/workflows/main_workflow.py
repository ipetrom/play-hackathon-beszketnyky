"""
Main Workflow Orchestrator
Integrates telecom news scraper with agents and object storage
"""

import asyncio
import json
import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_simple import create_report, get_user
from services.objest_storage import upload_file, download_file
from agents.final_summarizer_agent import final_summarizer_agent
from agents.tips_alerts_generator import tips_alerts_generator
from agents.workflow import TelecomWorkflow

# Import the scraper
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'scrappers', 'serper'))
try:
    from telecom_news_scraper import TelecomNewsScraper
except ImportError:
    # Fallback if scraper is not available
    class TelecomNewsScraper:
        def __init__(self, api_key):
            self.api_key = api_key
        
        async def scrape_all_news(self, days_back=7):
            return {
                "prawo": [],
                "polityka": [],
                "financial": [],
                "scraped_at": datetime.now().isoformat(),
                "total_articles": 0
            }

logger = logging.getLogger(__name__)

class MainWorkflowOrchestrator:
    """Main workflow orchestrator for Smart Tracker"""
    
    def __init__(self):
        self.scraper = None
        self.workflow = TelecomWorkflow()
        
    async def run_complete_workflow(self, user_email: str, days_back: int = 7) -> Dict[str, Any]:
        """
        Run the complete workflow:
        1. Scrape telecom news
        2. Process through agents
        3. Generate final reports
        4. Store in object storage
        5. Save paths to database
        """
        try:
            logger.info(f"Starting complete workflow for user: {user_email}")
            
            # Step 1: Scrape telecom news
            logger.info("Step 1: Scraping telecom news...")
            news_data = await self._scrape_telecom_news(days_back)
            
            if not news_data or news_data.get("total_articles", 0) == 0:
                logger.warning("No news articles found")
                return {
                    "status": "warning",
                    "message": "No news articles found for the specified period",
                    "user_email": user_email
                }
            
            # Step 2: Process through agents for each domain
            logger.info("Step 2: Processing through agents...")
            domain_reports = {}
            
            for domain in ["prawo", "polityka", "financial"]:
                domain_articles = news_data.get(domain, [])
                if domain_articles:
                    logger.info(f"Processing {len(domain_articles)} articles for domain: {domain}")
                    domain_report = await self._process_domain_articles(domain, domain_articles)
                    domain_reports[domain] = domain_report
                else:
                    logger.info(f"No articles found for domain: {domain}")
                    domain_reports[domain] = None
            
            # Step 3: Generate tips and alerts
            logger.info("Step 3: Generating tips and alerts...")
            tips_alerts = await self._generate_tips_alerts(domain_reports)
            
            # Step 4: Store files in object storage
            logger.info("Step 4: Storing files in object storage...")
            storage_paths = await self._store_files_in_object_storage(
                user_email, news_data, domain_reports, tips_alerts
            )
            
            # Step 5: Create database report
            logger.info("Step 5: Creating database report...")
            report_result = await self._create_database_report(
                user_email, storage_paths, tips_alerts
            )
            
            logger.info(f"Complete workflow finished for user: {user_email}")
            return {
                "status": "success",
                "user_email": user_email,
                "report_id": report_result.get("report_id"),
                "storage_paths": storage_paths,
                "articles_processed": news_data.get("total_articles", 0),
                "domains_processed": len([d for d in domain_reports.values() if d is not None])
            }
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "user_email": user_email
            }
    
    async def _scrape_telecom_news(self, days_back: int) -> Dict[str, Any]:
        """Scrape telecom news using the scraper"""
        try:
            # Get API key from environment
            serper_api_key = os.getenv("SERPER_API_KEY")
            if not serper_api_key:
                raise ValueError("SERPER_API_KEY environment variable not set")
            
            scraper = TelecomNewsScraper(serper_api_key)
            news_data = await scraper.scrape_all_news(days_back=days_back)
            
            logger.info(f"Scraped {news_data.get('total_articles', 0)} articles")
            return news_data
            
        except Exception as e:
            logger.error(f"News scraping failed: {e}")
            return {}
    
    async def _process_domain_articles(self, domain: str, articles: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Process articles for a specific domain through agents"""
        try:
            # For now, create a simple domain report from articles
            # In the future, this can be enhanced with full agent processing
            domain_report = {
                "domain": domain,
                "generated_at": datetime.utcnow().isoformat(),
                "synthesis": f"# {domain.title()} Domain Report\n\nProcessed {len(articles)} articles for {domain} domain.\n\n## Key Articles\n" + 
                           "\n".join([f"- {article.get('title', 'No title')}" for article in articles[:5]]),
                "sources_count": len(articles),
                "status": "success"
            }
            
            logger.info(f"Created domain report for {domain} with {len(articles)} articles")
            return domain_report
                
        except Exception as e:
            logger.error(f"Domain processing failed for {domain}: {e}")
            return None
    
    async def _generate_tips_alerts(self, domain_reports: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tips and alerts from domain reports"""
        try:
            # Filter out None values
            valid_reports = {k: v for k, v in domain_reports.items() if v is not None}
            
            if not valid_reports:
                logger.warning("No valid domain reports for tips/alerts generation")
                return {
                    "tips": ["Monitor telecom developments", "Review regulatory changes", "Assess market trends"],
                    "alerts": [{"alert": "Limited data available", "alert_level": 2}]
                }
            
            # Generate tips and alerts
            tips_alerts = await tips_alerts_generator.generate_tips_alerts(valid_reports)
            
            return tips_alerts
            
        except Exception as e:
            logger.error(f"Tips/alerts generation failed: {e}")
            return {
                "tips": ["Monitor telecom developments", "Review regulatory changes", "Assess market trends"],
                "alerts": [{"alert": "Tips/alerts generation failed", "alert_level": 3}]
            }
    
    async def _store_files_in_object_storage(self, user_email: str, news_data: Dict[str, Any], 
                                           domain_reports: Dict[str, Any], tips_alerts: Dict[str, Any]) -> Dict[str, str]:
        """Store files in object storage and return paths"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            user_folder = f"{user_email}/reports/{timestamp}"
            
            storage_paths = {}
            
            # 1. Store raw news data as JSON
            news_file = f"{user_folder}/raw_news_data.json"
            with open("temp_news_data.json", "w", encoding="utf-8") as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
            if upload_file("temp_news_data.json", news_file):
                storage_paths["raw_news_data"] = news_file
            if os.path.exists("temp_news_data.json"):
                os.remove("temp_news_data.json")
            
            # 2. Store tips and alerts as JSON
            tips_alerts_file = f"{user_folder}/tips_alerts.json"
            with open("temp_tips_alerts.json", "w", encoding="utf-8") as f:
                json.dump(tips_alerts, f, ensure_ascii=False, indent=2)
            if upload_file("temp_tips_alerts.json", tips_alerts_file):
                storage_paths["tips_alerts"] = tips_alerts_file
            if os.path.exists("temp_tips_alerts.json"):
                os.remove("temp_tips_alerts.json")
            
            # 3. Store final merged report as TXT
            final_report = await self._generate_final_merged_report(domain_reports)
            final_report_file = f"{user_folder}/final_report.txt"
            with open("temp_final_report.txt", "w", encoding="utf-8") as f:
                f.write(final_report)
            if upload_file("temp_final_report.txt", final_report_file):
                storage_paths["final_report"] = final_report_file
            if os.path.exists("temp_final_report.txt"):
                os.remove("temp_final_report.txt")
            
            # 4. Store individual domain reports as TXT files
            domain_reports_paths = {}
            for domain, report in domain_reports.items():
                if report:
                    domain_file = f"{user_folder}/{domain}_report.txt"
                    domain_content = self._format_domain_report(domain, report)
                    with open(f"temp_{domain}_report.txt", "w", encoding="utf-8") as f:
                        f.write(domain_content)
                    if upload_file(f"temp_{domain}_report.txt", domain_file):
                        domain_reports_paths[domain] = domain_file
                    if os.path.exists(f"temp_{domain}_report.txt"):
                        os.remove(f"temp_{domain}_report.txt")
            
            storage_paths["domain_reports"] = domain_reports_paths
            
            logger.info(f"Files stored in object storage for user: {user_email}")
            return storage_paths
            
        except Exception as e:
            logger.error(f"Object storage failed: {e}")
            # Return empty storage paths but don't fail the entire workflow
            return {
                "raw_news_data": "",
                "tips_alerts": "",
                "final_report": "",
                "domain_reports": {}
            }
    
    async def _generate_final_merged_report(self, domain_reports: Dict[str, Any]) -> str:
        """Generate final merged report from all domain reports"""
        try:
            report_sections = []
            report_sections.append("# Smart Tracker - Final Merged Report")
            report_sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_sections.append("")
            
            for domain, report in domain_reports.items():
                if report:
                    report_sections.append(f"## {domain.title()} Domain Report")
                    report_sections.append("")
                    
                    # Extract synthesis from the report
                    synthesis = report.get("synthesis", "")
                    if synthesis:
                        report_sections.append(synthesis)
                    else:
                        report_sections.append(f"Report available for {domain} domain.")
                    
                    report_sections.append("")
                    report_sections.append("---")
                    report_sections.append("")
            
            return "\n".join(report_sections)
            
        except Exception as e:
            logger.error(f"Final report generation failed: {e}")
            return f"# Smart Tracker - Final Report\n\nError generating report: {str(e)}"
    
    def _format_domain_report(self, domain: str, report: Dict[str, Any]) -> str:
        """Format domain report for storage"""
        try:
            content = []
            content.append(f"# {domain.title()} Domain Report")
            content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            content.append("")
            
            synthesis = report.get("synthesis", "")
            if synthesis:
                content.append(synthesis)
            else:
                content.append(f"Report available for {domain} domain.")
            
            return "\n".join(content)
            
        except Exception as e:
            logger.error(f"Domain report formatting failed: {e}")
            return f"# {domain.title()} Domain Report\n\nError formatting report: {str(e)}"
    
    async def _create_database_report(self, user_email: str, storage_paths: Dict[str, str], 
                                     tips_alerts: Dict[str, Any]) -> Dict[str, Any]:
        """Create database report with storage paths"""
        try:
            # Count tips and alerts
            tips_count = len(tips_alerts.get("tips", []))
            alerts_count = len(tips_alerts.get("alerts", []))
            
            # Create report in database
            tips_alerts_path = storage_paths.get("tips_alerts", "")
            final_report_path = storage_paths.get("final_report", "")
            
            logger.info(f"Creating database report with paths:")
            logger.info(f"  - Tips/Alerts JSON: {tips_alerts_path}")
            logger.info(f"  - Final Report: {final_report_path}")
            
            report_result = create_report(
                user_email=user_email,
                report_date=date.today(),
                report_domains=["prawo", "polityka", "financial"],
                report_alerts=alerts_count,
                report_tips=tips_count,
                report_alerts_tips_json_path=tips_alerts_path,
                path_to_report=final_report_path,
                path_to_report_vector="",  # Skip RAG for now
                report_status="published"
            )
            
            return report_result
            
        except Exception as e:
            logger.error(f"Database report creation failed: {e}")
            return {"status": "error", "message": str(e)}

# Global orchestrator instance
main_workflow = MainWorkflowOrchestrator()
