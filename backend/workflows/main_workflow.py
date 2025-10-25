"""
Main Workflow for Smart Tracker
Integrates all agents and handles object storage
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import json
import os

from agents.workflow import TelecomWorkflow
from agents.final_summarizer_agent import final_summarizer_agent
from agents.tips_alerts_generator import tips_alerts_generator
from services.database_simple import create_report, get_user
from services.objest_storage import upload_file, download_file
from services.http_client import PerplexityClient

logger = logging.getLogger(__name__)

class MainWorkflow:
    """Main workflow orchestrating all agents and object storage"""
    
    def __init__(self):
        self.telecom_workflow = TelecomWorkflow()
        self.perplexity_client = PerplexityClient()
        self.domains = ["prawo", "polityka", "financial"]
    
    async def run_complete_workflow(self, user_email: str, days_back: int = 7) -> Dict[str, Any]:
        """
        Run the complete workflow for a user
        
        Args:
            user_email: User email
            days_back: Number of days to look back
            
        Returns:
            Workflow result with file paths
        """
        try:
            logger.info(f"Starting complete workflow for user: {user_email}")
            
            # Check if user exists
            user = get_user(user_email)
            if not user:
                return {"status": "error", "message": "User not found"}
            
            # Create storage directory for this user
            user_storage_dir = f"{user_email}/reports/{date.today().strftime('%Y-%m-%d')}"
            
            # Step 1: Run telecom workflow for each domain
            domain_reports = {}
            writer_reports = {}
            perplexity_reports = {}
            
            for domain in self.domains:
                logger.info(f"Processing domain: {domain}")
                
                # Try telecom workflow first
                try:
                    workflow_result = await self.telecom_workflow.run_domain_workflow(domain)
                    
                    if workflow_result.get("status") == "success":
                        # Store the raw workflow result
                        domain_reports[domain] = workflow_result
                        
                        # Try to get writer report
                        writer_outputs = workflow_result.get("writer_outputs", [])
                        if writer_outputs:
                            # Use writer agent
                            from agents.writer_agent import writer_agent
                            writer_report = await writer_agent.aggregate_domain(writer_outputs, domain)
                            writer_reports[domain] = writer_report
                        else:
                            logger.warning(f"No writer outputs for domain: {domain}")
                            writer_reports[domain] = None
                    else:
                        logger.warning(f"Workflow failed for domain: {domain}")
                        domain_reports[domain] = None
                        writer_reports[domain] = None
                        
                except Exception as e:
                    logger.error(f"Workflow error for domain {domain}: {e}")
                    domain_reports[domain] = None
                    writer_reports[domain] = None
                
                # Always get Perplexity report as fallback/enhancement
                try:
                    perplexity_query = self._get_perplexity_query(domain)
                    perplexity_result = await self.perplexity_client.summarize(perplexity_query, domain)
                    perplexity_reports[domain] = self._format_perplexity_result(perplexity_result, domain)
                except Exception as e:
                    logger.error(f"Perplexity error for domain {domain}: {e}")
                    perplexity_reports[domain] = None
            
            # Step 2: Run final summarizer for each domain
            final_reports = {}
            for domain in self.domains:
                try:
                    writer_report = writer_reports.get(domain)
                    perplexity_report = perplexity_reports.get(domain)
                    
                    final_report = await final_summarizer_agent.synthesize_domain_report(
                        writer_report, perplexity_report, domain
                    )
                    final_reports[domain] = final_report
                    
                except Exception as e:
                    logger.error(f"Final summarizer error for domain {domain}: {e}")
                    final_reports[domain] = None
            
            # Step 3: Generate tips and alerts
            try:
                tips_alerts = await tips_alerts_generator.generate_tips_alerts(final_reports)
            except Exception as e:
                logger.error(f"Tips and alerts generation failed: {e}")
                tips_alerts = {"tips": [], "alerts": []}
            
            # Step 4: Store files in object storage
            storage_paths = await self._store_files_in_object_storage(
                user_storage_dir, final_reports, tips_alerts
            )
            
            # Step 5: Create database report
            report_result = await self._create_database_report(
                user_email, final_reports, tips_alerts, storage_paths
            )
            
            logger.info(f"Complete workflow finished for user: {user_email}")
            return {
                "status": "success",
                "user_email": user_email,
                "report_id": report_result.get("report_id"),
                "storage_paths": storage_paths,
                "domains_processed": list(final_reports.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Complete workflow failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_perplexity_query(self, domain: str) -> str:
        """Get Perplexity query for domain"""
        queries = {
            "prawo": [
                "Poland telecommunications law regulation UKE UOKiK last week",
                "Polish telecom legal changes UKE decisions recent",
                "Poland telecom regulatory updates UOKiK competition last week",
                "UKE spectrum allocation decisions Polish telecom recent",
                "Poland telecom law changes EU directives last week"
            ],
            "polityka": [
                "Poland telecom policy government announcements last week",
                "Polish telecom ministry digital policy recent changes",
                "Poland 5G strategy government telecom recent updates",
                "Polish telecom infrastructure policy EU funding last week",
                "Poland telecom competition policy government recent"
            ],
            "financial": [
                "Poland telecom market financial results last week",
                "Polish telecom operators earnings revenue recent",
                "Poland telecom market stock prices recent changes",
                "telecom investment Poland infrastructure funding last week",
                "Polish telecom market financial outlook recent"
            ]
        }
        
        domain_queries = queries.get(domain, [])
        return " ".join(domain_queries[:3])  # Use first 3 queries
    
    def _format_perplexity_result(self, result: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Format Perplexity result"""
        try:
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "domain": domain,
                "content": content,
                "key_points": self._extract_key_points(content),
                "entities": self._extract_entities(content),
                "impact_assessment": {
                    "impact_level": "medium",
                    "affected_parties": ["All telecom stakeholders"],
                    "time_horizon": "short-term"
                },
                "confidence": "medium",
                "generated_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error formatting Perplexity result: {e}")
            return {
                "domain": domain,
                "content": f"No Perplexity data available for {domain}",
                "key_points": [],
                "entities": {},
                "impact_assessment": {"impact_level": "low"},
                "confidence": "low",
                "generated_at": datetime.utcnow().isoformat(),
                "status": "error"
            }
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content"""
        # Simple extraction - in production, use more sophisticated NLP
        lines = content.split('\n')
        key_points = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                key_points.append(line)
        return key_points[:5]  # Limit to 5 key points
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract entities from content"""
        # Simple extraction - in production, use NER
        entities = {
            "organizations": [],
            "people": [],
            "locations": []
        }
        
        # Look for common telecom entities
        telecom_orgs = ["UKE", "UOKiK", "Play", "Orange", "T-Mobile", "Plus", "KRRiT"]
        for org in telecom_orgs:
            if org in content:
                entities["organizations"].append(org)
        
        return entities
    
    async def _store_files_in_object_storage(self, user_storage_dir: str, 
                                           final_reports: Dict[str, Any], 
                                           tips_alerts: Dict[str, Any]) -> Dict[str, str]:
        """Store files in object storage and return paths"""
        storage_paths = {}
        
        try:
            # Store tips and alerts JSON
            tips_alerts_path = f"{user_storage_dir}/tips_alerts.json"
            tips_alerts_file = f"temp_tips_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(tips_alerts_file, 'w', encoding='utf-8') as f:
                json.dump(tips_alerts, f, ensure_ascii=False, indent=2)
            
            if upload_file(tips_alerts_file, tips_alerts_path):
                storage_paths["tips_alerts"] = tips_alerts_path
                os.remove(tips_alerts_file)  # Clean up temp file
            
            # Store final report as TXT
            final_report_path = f"{user_storage_dir}/final_report.txt"
            final_report_file = f"temp_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(final_report_file, 'w', encoding='utf-8') as f:
                f.write("# Smart Tracker Final Report\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for domain, report in final_reports.items():
                    if report and report.get("status") == "success":
                        f.write(f"## {domain.title()} Domain\n\n")
                        f.write(report.get("synthesis", "No synthesis available"))
                        f.write("\n\n---\n\n")
            
            if upload_file(final_report_file, final_report_path):
                storage_paths["final_report"] = final_report_path
                os.remove(final_report_file)  # Clean up temp file
            
            # Store individual domain reports
            for domain, report in final_reports.items():
                if report and report.get("status") == "success":
                    domain_path = f"{user_storage_dir}/domains/{domain}_report.txt"
                    domain_file = f"temp_{domain}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    
                    with open(domain_file, 'w', encoding='utf-8') as f:
                        f.write(f"# {domain.title()} Domain Report\n\n")
                        f.write(report.get("synthesis", "No synthesis available"))
                    
                    if upload_file(domain_file, domain_path):
                        storage_paths[f"{domain}_report"] = domain_path
                        os.remove(domain_file)  # Clean up temp file
            
            logger.info(f"Files stored in object storage: {storage_paths}")
            return storage_paths
            
        except Exception as e:
            logger.error(f"Error storing files in object storage: {e}")
            return {}
    
    async def _create_database_report(self, user_email: str, final_reports: Dict[str, Any], 
                                     tips_alerts: Dict[str, Any], storage_paths: Dict[str, str]) -> Dict[str, Any]:
        """Create database report with storage paths"""
        try:
            # Count tips and alerts
            tips_count = len(tips_alerts.get("tips", []))
            alerts_count = len(tips_alerts.get("alerts", []))
            
            # Create report files JSON
            report_files = {
                "tips_alerts_json": storage_paths.get("tips_alerts", ""),
                "final_report_txt": storage_paths.get("final_report", ""),
                "domain_reports": {
                    domain: storage_paths.get(f"{domain}_report", "")
                    for domain in self.domains
                }
            }
            
            # Create report in database
            report_result = create_report(
                user_email=user_email,
                report_date=date.today(),
                report_domains=self.domains,
                report_alerts=alerts_count,
                report_tips=tips_count,
                report_alerts_tips_json_path=storage_paths.get("tips_alerts", ""),
                path_to_report=storage_paths.get("final_report", ""),
                path_to_report_vector="",  # Skip RAG for now
                report_status="published"
            )
            
            return report_result
            
        except Exception as e:
            logger.error(f"Error creating database report: {e}")
            return {"status": "error", "message": str(e)}

# Global workflow instance
main_workflow = MainWorkflow()
