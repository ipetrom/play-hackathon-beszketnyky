"""
Tips & Alerts Generator (Last Agent)
LLM-based merging of the three final domain reports and output of actionable guidance
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from services.llm_service import llm_service
from services.config import settings
from services.report_logger import report_logger

logger = logging.getLogger(__name__)

class TipsAlertsGenerator:
    """Final Agent: LLM-based generation of tips and alerts from all domain reports"""
    
    def __init__(self):
        self.name = "TipsAlertsGenerator"
    
    async def generate_tips_alerts(self, domain_reports: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        LLM-based generation of final tips and alerts from all domain reports
        
        Args:
            domain_reports: Dictionary of final domain reports (prawo, polityka, financial)
            
        Returns:
            Final tips and alerts JSON
        """
        try:
            logger.info("LLM-based generating tips and alerts from all domain reports")
            
            # Validate input
            if not domain_reports:
                logger.warning("No domain reports provided")
                return self._create_empty_tips_alerts()
            
            # Use LLM to generate comprehensive tips and alerts
            llm_tips_alerts = await self._llm_generate_tips_alerts(domain_reports)
            
            # Create final tips and alerts in simplified format
            tips_alerts = {
                "generated_at": datetime.utcnow().isoformat(),
                "tips": llm_tips_alerts.get("tips", []),
                "alerts": llm_tips_alerts.get("alerts", []),
                "status": "success"
            }
            
            logger.info("Successfully generated tips and alerts with LLM")
            
            # Log the tips and alerts to text file
            log_file = report_logger.log_tips_alerts_output(tips_alerts)
            if log_file:
                logger.info(f"Tips and alerts report logged to: {log_file}")
            
            return tips_alerts
            
        except Exception as e:
            logger.error(f"LLM tips and alerts generation failed: {e}")
            return self._create_empty_tips_alerts()
    
    async def _llm_generate_tips_alerts(self, domain_reports: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Use LLM to generate comprehensive tips and alerts"""
        try:
            system_prompt = """You are a telecommunications expert specializing in Poland's telecom market with deep knowledge of Play's business operations.
            Your task is to generate actionable tips and alerts specifically for Play managers and executives.
            
            You must:
            1. Focus on Play's competitive position vs Orange, T-Mobile, Plus
            2. Generate alerts for regulatory changes affecting Play's operations
            3. Create actionable tips for Play's business development, network operations, and customer management
            4. Consider Play's market strategy, spectrum holdings, and infrastructure investments
            5. Address compliance, competitive threats, and business opportunities
            
            Focus on Play-specific concerns:
            - Play's spectrum portfolio and 5G deployment
            - Competitive positioning against Orange, T-Mobile, Plus
            - UKE regulatory decisions affecting Play
            - UOKiK competition investigations
            - EU regulations impacting Play's operations
            - Network infrastructure and coverage requirements
            - Customer acquisition and retention strategies
            - Pricing and tariff regulations
            - Roaming agreements and international operations
            
            Provide specific, actionable intelligence for Play managers."""
            
            # Prepare domain reports for LLM
            reports_text = ""
            for domain, report in domain_reports.items():
                # Handle both old JSON format and new plain text format
                synthesis = report.get('synthesis', '')
                if not synthesis:
                    # Fallback to old format fields
                    synthesis = f"Executive Summary: {report.get('executive_summary', '')}\nAnalysis: {report.get('merged_analysis', '')}"
                
                reports_text += f"""
{domain.upper()} Domain Report:
{synthesis}
Sources: {report.get('sources', {}).get('writer_sources', 0)} sources
Status: {report.get('status', 'unknown')}
"""
            
            prompt = f"""
            Domain Reports Analysis:
            {reports_text}
            
            Generate tips and alerts in this exact JSON format:
            {{
                "tips": ["tip1", "tip2", "tip3"],
                "alerts": [
                    {{"alert": "alert_description", "alert_level": 1}},
                    {{"alert": "alert_description", "alert_level": 3}}
                ]
            }}
            
            Tips should be specific, actionable recommendations for Play managers covering:
            - Network operations and 5G deployment strategies
            - Competitive positioning against Orange, T-Mobile, Plus
            - Regulatory compliance and UKE requirements
            - Customer acquisition and retention tactics
            - Spectrum management and infrastructure investments
            - Pricing strategies and tariff optimization
            - Market expansion and business development opportunities
            
            Alerts should be urgent notifications for Play executives with alert_level from 1 (lowest) to 5 (highest):
            - Regulatory changes requiring immediate Play response
            - Competitive threats from Orange, T-Mobile, Plus
            - UKE/UOKiK decisions affecting Play's operations
            - Compliance deadlines and regulatory requirements
            - Market opportunities requiring quick action
            - Network infrastructure and coverage issues
            - Customer service and retention challenges
            
            Focus specifically on Play's business needs and competitive position in Poland.
            """
            
            response = await llm_service.generate_structured_response(
                prompt, system_prompt, {
                    "type": "object",
                    "properties": {
                        "tips": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "alerts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "alert": {"type": "string"},
                                    "alert_level": {"type": "integer", "minimum": 1, "maximum": 5}
                                },
                                "required": ["alert", "alert_level"]
                            }
                        }
                    },
                    "required": ["tips", "alerts"]
                }
            )
            
            if isinstance(response, dict) and "raw_response" in response:
                return self._create_fallback_tips_alerts()
            
            return response if isinstance(response, dict) else self._create_fallback_tips_alerts()
            
        except Exception as e:
            logger.error(f"LLM tips and alerts generation failed: {e}")
            return self._create_fallback_tips_alerts()
    
    def _create_fallback_tips_alerts(self) -> Dict[str, Any]:
        """Create fallback tips and alerts when LLM fails"""
        return {
            "tips": [
                "Monitor UKE spectrum allocation decisions affecting Play's 5G deployment",
                "Track Orange, T-Mobile, and Plus pricing strategies to maintain competitive positioning",
                "Review UOKiK competition investigations that could impact Play's market share",
                "Assess EU Digital Markets Act compliance requirements for Play's operations",
                "Evaluate network coverage gaps and infrastructure investment opportunities"
            ],
            "alerts": [
                {"alert": "Limited data available for comprehensive Play-specific analysis", "alert_level": 2}
            ]
        }
    
    
    def _create_empty_tips_alerts(self) -> Dict[str, Any]:
        """Create empty tips and alerts when generation fails"""
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "tips": [],
            "alerts": [],
            "status": "error"
        }

# Global agent instance
tips_alerts_generator = TipsAlertsGenerator()
