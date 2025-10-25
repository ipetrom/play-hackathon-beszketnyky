"""
Writer Agent (Agent 3: "Writer")
LLM-based domain aggregation - combines all Keeper outputs for a single domain
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from services.llm_service import llm_service
from services.config import settings

logger = logging.getLogger(__name__)

class WriterAgent:
    """Agent 3: LLM-based aggregation of Keeper outputs into domain reports"""
    
    def __init__(self):
        self.name = "WriterAgent"
    
    async def aggregate_domain(self, keeper_outputs: List[Dict[str, Any]], domain: str) -> Dict[str, Any]:
        """
        LLM-based aggregation of all Keeper outputs for a domain into a comprehensive report
        
        Args:
            keeper_outputs: List of processed content from Keeper Agent
            domain: Target domain (prawo/polityka/financial)
            
        Returns:
            Aggregated domain report
        """
        try:
            logger.info(f"LLM-based aggregating domain report for: {domain}")
            
            if not keeper_outputs:
                logger.warning(f"No keeper outputs for domain: {domain}")
                return self._create_empty_report(domain)
            
            # Filter successful outputs
            successful_outputs = [output for output in keeper_outputs if output.get("status") == "success"]
            
            if not successful_outputs:
                logger.warning(f"No successful outputs for domain: {domain}")
                return self._create_empty_report(domain)
            
            # Use LLM to aggregate all outputs
            llm_report = await self._llm_aggregate_domain(successful_outputs, domain)
            
            # Create final report
            report = {
                "domain": domain,
                "generated_at": datetime.utcnow().isoformat(),
                "sources_count": len(successful_outputs),
                "executive_summary": llm_report.get("executive_summary", ""),
                "what_happened": llm_report.get("what_happened", []),
                "so_what": llm_report.get("so_what", ""),
                "now_what": llm_report.get("now_what", []),
                "key_facts": llm_report.get("key_facts", []),
                "entities": llm_report.get("entities", {}),
                "impact_summary": llm_report.get("impact_summary", {}),
                "sources": self._extract_sources(successful_outputs),
                "status": "success"
            }
            
            logger.info(f"Successfully aggregated domain report with LLM for: {domain}")
            return report
            
        except Exception as e:
            logger.error(f"LLM domain aggregation failed for {domain}: {e}")
            return self._create_empty_report(domain)
    
    async def _llm_aggregate_domain(self, outputs: List[Dict[str, Any]], domain: str) -> Dict[str, Any]:
        """Use LLM to aggregate all domain outputs"""
        try:
            system_prompt = f"""You are a telecommunications expert specializing in Poland's telecom market.
            Your task is to aggregate and synthesize information from multiple sources for the {domain} domain.
            
            Create a comprehensive domain report in plain text format that includes:
            1. Executive summary of key developments
            2. Chronological timeline of events
            3. Strategic analysis of implications
            4. Actionable recommendations
            5. Key facts and entities
            6. Impact assessment
            
            Focus on:
            - Polish telecom operators: Play, Orange, T-Mobile, Plus
            - Regulators: UKE, UOKiK, KRRiT
            - Government: Ministry of Digitalization, Ministry of Development
            - EU regulations affecting Poland
            - Market developments and policy changes
            
            Return the report as plain text, well-structured with clear headings and bullet points.
            Provide actionable insights for telecom stakeholders."""
            
            # Prepare all outputs for LLM
            outputs_text = ""
            for i, output in enumerate(outputs):
                outputs_text += f"""
Source {i+1}:
Title: {output.get('title', '')}
URL: {output.get('url', '')}
Category: {output.get('category', '')}
Facts: {json.dumps(output.get('facts', []), ensure_ascii=False)}
Entities: {json.dumps(output.get('entities', {}), ensure_ascii=False)}
Impact: {json.dumps(output.get('impact_assessment', {}), ensure_ascii=False)}
Summary: {output.get('summary', '')}
"""
            
            prompt = f"""
            Domain: {domain}
            Sources: {len(outputs)} sources analyzed
            
            Source Data:
            {outputs_text}
            
            Generate a comprehensive domain report in plain text format with clear structure:
            - Executive Summary
            - What Happened (chronological events)
            - So What (strategic implications)
            - Now What (actionable recommendations)
            - Key Facts
            - Entities
            - Impact Assessment
            
            Use clear headings, bullet points, and well-organized sections.
            """
            
            response = await llm_service.generate_response(prompt, system_prompt)
            
            if not response or isinstance(response, dict) and "raw_response" in response:
                return self._create_fallback_report(domain)
            
            # Return plain text response wrapped in a simple structure
            return {
                "domain": domain,
                "generated_at": datetime.utcnow().isoformat(),
                "report": response,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"LLM domain aggregation failed: {e}")
            return self._create_fallback_report(domain)
    
    def _create_fallback_report(self, domain: str) -> Dict[str, Any]:
        """Create fallback report when LLM fails"""
        return {
            "domain": domain,
            "generated_at": datetime.utcnow().isoformat(),
            "report": f"""# {domain.title()} Domain Report

## Executive Summary
Domain analysis for {domain} based on available sources. Limited data available for comprehensive analysis.

## What Happened
- Monitor {domain} domain developments for new information

## So What
Analysis of {domain} domain developments and their implications for the telecommunications industry.

## Now What
- Monitor {domain} domain developments
- Review available sources for additional information
- Stay updated on regulatory and market changes

## Key Facts
- Limited data available for {domain} domain
- Further monitoring required

## Entities
- Domain: {domain}
- Status: Limited data

## Impact Assessment
- Impact Level: Low
- Time Horizon: Short-term monitoring required
- Affected Parties: All telecom stakeholders
""",
            "status": "fallback"
        }
    
    def _extract_sources(self, outputs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract source information"""
        sources = []
        
        for output in outputs:
            if output.get("status") == "success":
                sources.append({
                    "title": output.get("title", ""),
                    "url": output.get("url", ""),
                    "category": output.get("category", ""),
                    "impact_level": output.get("impact_assessment", {}).get("impact_level", "low")
                })
        
        return sources
    
    def _create_empty_report(self, domain: str) -> Dict[str, Any]:
        """Create empty report for failed aggregation"""
        return {
            "domain": domain,
            "generated_at": datetime.utcnow().isoformat(),
            "sources_count": 0,
            "executive_summary": f"No data available for {domain} domain",
            "what_happened": [],
            "so_what": f"No analysis available for {domain} domain",
            "now_what": [f"Monitor {domain} domain for new developments"],
            "key_facts": [],
            "entities": {},
            "impact_summary": {
                "dominant_impact_level": "low",
                "dominant_time_horizon": "medium",
                "affected_parties": {},
                "impact_distribution": {},
                "horizon_distribution": {}
            },
            "sources": [],
            "status": "error"
        }

# Global agent instance
writer_agent = WriterAgent()
