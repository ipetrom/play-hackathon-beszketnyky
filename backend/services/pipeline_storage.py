"""
Pipeline Storage service for storing pipeline results in object storage
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import os

from services.objest_storage import upload_file
from services.database_simple import create_report

logger = logging.getLogger(__name__)

class PipelineStorage:
    """Handles storage of pipeline results in object storage and database"""
    
    def __init__(self):
        self.base_path = "pipeline_reports"
    
    async def store_pipeline_results(self, user_email: str, domain_reports: Dict[str, Any], 
                                   tips_alerts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store pipeline results in object storage and database
        
        Args:
            user_email: User email
            domain_reports: Reports for each domain
            tips_alerts: Tips and alerts JSON
            
        Returns:
            Storage result with paths
        """
        try:
            # Create storage directory
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            storage_dir = f"{self.base_path}/{user_email}/{timestamp}"
            
            # Store merged summary
            merged_summary_path = await self._store_merged_summary(storage_dir, domain_reports)
            
            # Store tips and alerts
            tips_alerts_path = await self._store_tips_alerts(storage_dir, tips_alerts)
            
            # Store individual domain reports
            domain_paths = await self._store_domain_reports(storage_dir, domain_reports)
            
            # Create database report
            report_result = await self._create_database_report(
                user_email, merged_summary_path, tips_alerts_path, domain_paths, tips_alerts
            )
            
            return {
                "status": "success",
                "storage_paths": {
                    "merged_summary": merged_summary_path,
                    "tips_alerts": tips_alerts_path,
                    "domain_synthesis": domain_paths  # Individual synthesis files
                },
                "report_id": report_result.get("report_id"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error storing pipeline results: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _store_merged_summary(self, storage_dir: str, domain_reports: Dict[str, Any]) -> str:
        """Store merged summary from all domains"""
        try:
            # Create merged summary content
            merged_content = self._create_merged_summary(domain_reports)
            
            # Create temp file
            temp_file = f"temp_merged_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            summary_path = f"{storage_dir}/merged_summary.txt"
            
            # Write content to temp file
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(merged_content)
            
            # Upload to object storage
            if upload_file(temp_file, summary_path):
                os.remove(temp_file)  # Clean up
                logger.info(f"Merged summary stored: {summary_path}")
                return summary_path
            else:
                os.remove(temp_file)  # Clean up
                raise Exception("Failed to upload merged summary")
                
        except Exception as e:
            logger.error(f"Error storing merged summary: {e}")
            raise
    
    async def _store_tips_alerts(self, storage_dir: str, tips_alerts: Dict[str, Any]) -> str:
        """Store tips and alerts JSON"""
        try:
            tips_alerts_path = f"{storage_dir}/tips_alerts.json"
            temp_file = f"temp_tips_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Write JSON to temp file
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(tips_alerts, f, ensure_ascii=False, indent=2)
            
            # Upload to object storage
            if upload_file(temp_file, tips_alerts_path):
                os.remove(temp_file)  # Clean up
                logger.info(f"Tips and alerts stored: {tips_alerts_path}")
                return tips_alerts_path
            else:
                os.remove(temp_file)  # Clean up
                raise Exception("Failed to upload tips and alerts")
                
        except Exception as e:
            logger.error(f"Error storing tips and alerts: {e}")
            raise
    
    async def _store_domain_reports(self, storage_dir: str, domain_reports: Dict[str, Any]) -> Dict[str, str]:
        """Store individual domain synthesis reports as separate .txt files"""
        domain_paths = {}
        
        try:
            for domain, report in domain_reports.items():
                if report and report.get("synthesis"):
                    # Store synthesis content as separate .txt file
                    synthesis_path = f"{storage_dir}/domains/{domain}_synthesis.txt"
                    temp_file = f"temp_{domain}_synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    
                    # Get synthesis content directly
                    synthesis_content = report.get("synthesis", "")
                    
                    # Write synthesis to temp file
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(synthesis_content)
                    
                    # Upload to object storage
                    if upload_file(temp_file, synthesis_path):
                        os.remove(temp_file)  # Clean up
                        domain_paths[domain] = synthesis_path
                        logger.info(f"Domain synthesis stored: {synthesis_path}")
                    else:
                        os.remove(temp_file)  # Clean up
                        logger.warning(f"Failed to store domain synthesis: {domain}")
                else:
                    logger.warning(f"No synthesis content available for domain: {domain}")
            
            return domain_paths
            
        except Exception as e:
            logger.error(f"Error storing domain reports: {e}")
            return domain_paths
    
    def _create_merged_summary(self, domain_reports: Dict[str, Any]) -> str:
        """Create merged summary from all domains"""
        content = []
        content.append("# Smart Tracker - Merged Summary Report")
        content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        content.append("## Executive Summary")
        content.append("This report provides a comprehensive analysis of telecommunications developments across legal, political, and financial domains in Poland.")
        content.append("")
        
        # Add domain summaries
        for domain, report in domain_reports.items():
            if report and report.get("status") == "success":
                content.append(f"## {domain.title()} Domain")
                content.append("")
                
                # Add synthesis if available
                synthesis = report.get("synthesis", "")
                if synthesis:
                    content.append(synthesis)
                else:
                    content.append(f"No detailed analysis available for {domain} domain.")
                
                content.append("")
                content.append("---")
                content.append("")
        
        # Add conclusion
        content.append("## Conclusion")
        content.append("This merged report provides a comprehensive view of telecommunications developments across all monitored domains.")
        content.append("Key insights and actionable recommendations are provided for strategic decision-making.")
        
        return "\n".join(content)
    
    def _create_domain_report_content(self, domain: str, report: Dict[str, Any]) -> str:
        """Create content for individual domain report"""
        content = []
        content.append(f"# {domain.title()} Domain Report")
        content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # Add synthesis
        synthesis = report.get("synthesis", "")
        if synthesis:
            content.append(synthesis)
        else:
            content.append(f"No detailed analysis available for {domain} domain.")
        
        return "\n".join(content)
    
    async def _create_database_report(self, user_email: str, merged_summary_path: str, 
                                    tips_alerts_path: str, domain_paths: Dict[str, str], 
                                    tips_alerts: Dict[str, Any]) -> Dict[str, Any]:
        """Create database report with storage paths"""
        try:
            # Count tips and alerts
            tips_count = len(tips_alerts.get("tips", []))
            alerts_count = len(tips_alerts.get("alerts", []))
            
            # Create report in database
            report_result = create_report(
                user_email=user_email,
                report_date=date.today(),
                report_domains=["prawo", "polityka", "financial"],
                report_alerts=alerts_count,
                report_tips=tips_count,
                report_alerts_tips_json_path=tips_alerts_path,
                path_to_report=merged_summary_path,
                path_to_report_vector="",  # Skip RAG for now
                report_status="published"
            )
            
            # Log domain synthesis paths for reference
            if domain_paths:
                logger.info(f"Domain synthesis files stored:")
                for domain, path in domain_paths.items():
                    logger.info(f"  {domain}: {path}")
            
            return report_result
            
        except Exception as e:
            logger.error(f"Error creating database report: {e}")
            return {"status": "error", "message": str(e)}

# Global instance
pipeline_storage = PipelineStorage()
