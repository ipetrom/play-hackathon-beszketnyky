"""
Final Summarizer Agent (Agent 4: "Prawna kategoria / Finalizer")
LLM-based fusion of Writer's domain summary with Perplexity's summary
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from services.llm_service import llm_service
from services.config import settings
from services.report_logger import report_logger

logger = logging.getLogger(__name__)

class FinalSummarizerAgent:
    """Agent 4: LLM-based final domain report synthesizer"""
    
    def __init__(self):
        self.name = "FinalSummarizerAgent"
    
    async def synthesize_domain_report(self, writer_report: Dict[str, Any], 
                                     perplexity_summary: Dict[str, Any], 
                                     domain: str) -> Dict[str, Any]:
        """
        LLM-based synthesis of final domain report from Writer and Perplexity outputs
        
        Args:
            writer_report: Domain report from Writer Agent
            perplexity_summary: Independent summary from Perplexity Agent
            domain: Target domain (prawo/polityka/financial)
            
        Returns:
            Final synthesized domain report
        """
        try:
            logger.info(f"LLM-based synthesizing final report for domain: {domain}")
            
            # Check if we have valid inputs
            has_writer = writer_report and writer_report.get("status") == "success"
            has_perplexity = perplexity_summary and perplexity_summary.get("status") == "success"
            
            if not has_writer and not has_perplexity:
                logger.warning(f"No valid inputs for domain: {domain}")
                report = self._create_fallback_report(domain, None)
                # Log the report
                try:
                    log_file = report_logger.log_final_summarizer_output(domain, report)
                    if log_file:
                        logger.info(f"No-inputs fallback report logged to: {log_file}")
                except Exception as e:
                    logger.error(f"Error logging no-inputs fallback report: {e}")
                return report
            
            if not has_writer:
                logger.info(f"Using Perplexity-only report for domain: {domain}")
                report = self._create_perplexity_only_report(domain, perplexity_summary)
                # Log the report
                try:
                    log_file = report_logger.log_final_summarizer_output(domain, report)
                    if log_file:
                        logger.info(f"Perplexity-only report logged to: {log_file}")
                except Exception as e:
                    logger.error(f"Error logging Perplexity-only report: {e}")
                return report
            
            if not has_perplexity:
                logger.warning(f"No valid perplexity summary for domain: {domain}")
                report = self._create_fallback_report(domain, writer_report)
                # Log the report
                try:
                    log_file = report_logger.log_final_summarizer_output(domain, report)
                    if log_file:
                        logger.info(f"Fallback report logged to: {log_file}")
                except Exception as e:
                    logger.error(f"Error logging fallback report: {e}")
                return report
            
            # Use LLM to synthesize both sources
            llm_synthesis = await self._llm_synthesize_sources(writer_report, perplexity_summary, domain)
            
            # Create final report with plain text synthesis
            final_report = {
                "domain": domain,
                "generated_at": datetime.utcnow().isoformat(),
                "synthesis": llm_synthesis.get("synthesis", ""),
                "evidence": self._create_evidence_list(writer_report, perplexity_summary),
                "sources": {
                    "writer_sources": writer_report.get("sources_count", 0) if writer_report.get("sources_count") else 0,
                    "perplexity_confidence": perplexity_summary.get("confidence", "medium")
                },
                "status": "success"
            }
            
            logger.info(f"Successfully synthesized final report with LLM for domain: {domain}")
            
            # Log the final report to text file
            try:
                log_file = report_logger.log_final_summarizer_output(domain, final_report)
                if log_file:
                    logger.info(f"Final summarizer report logged to: {log_file}")
                else:
                    logger.warning(f"Failed to log final summarizer report for domain: {domain}")
            except Exception as e:
                logger.error(f"Error logging final summarizer report: {e}")
            
            return final_report
            
        except Exception as e:
            logger.error(f"LLM final synthesis failed for domain {domain}: {e}")
            report = self._create_fallback_report(domain, writer_report or perplexity_summary)
            # Log the report
            try:
                log_file = report_logger.log_final_summarizer_output(domain, report)
                if log_file:
                    logger.info(f"Exception fallback report logged to: {log_file}")
            except Exception as log_e:
                logger.error(f"Error logging exception fallback report: {log_e}")
            return report
    
    async def _llm_synthesize_sources(self, writer_report: Dict[str, Any], 
                                    perplexity_summary: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Use LLM to synthesize Writer and Perplexity sources"""
        try:
            system_prompt = f"""You are a telecommunications expert specializing in Poland's telecom market.
            Your task is to synthesize information from multiple sources for the {domain} domain.
            
            You must:
            1. Merge insights from both sources
            2. Resolve conflicts and inconsistencies
            3. Prioritize official sources and recent information
            4. Assess confidence levels
            5. Identify gaps and unknowns
            6. Generate actionable recommendations
            
            Focus on:
            - Polish telecom operators: Play, Orange, T-Mobile, Plus
            - Regulators: UKE, UOKiK, KRRiT
            - Government: Ministry of Digitalization, Ministry of Development
            - EU regulations affecting Poland
            - Market developments and policy changes
            
            Provide a comprehensive synthesis with clear confidence levels."""
            
            prompt = f"""
            Domain: {domain}
            
            Writer Report:
            {writer_report.get('report', 'No writer report available')}
            
            Perplexity Summary:
            Content: {perplexity_summary.get('content', '')}
            Key Points: {json.dumps(perplexity_summary.get('key_points', []), ensure_ascii=False)}
            Entities: {json.dumps(perplexity_summary.get('entities', {}), ensure_ascii=False)}
            Impact: {json.dumps(perplexity_summary.get('impact_assessment', {}), ensure_ascii=False)}
            Confidence: {perplexity_summary.get('confidence', 'medium')}
            
            Synthesize these sources and return a comprehensive plain text report with:
            - Executive Summary
            - Merged Analysis
            - Confidence Assessment
            - Gaps and Unknowns
            - Recommendations
            - Impact Assessment
            
            Use clear headings, bullet points, and well-organized sections.
            """
            
            response = await llm_service.generate_response(prompt, system_prompt)
            
            if not response or isinstance(response, dict) and "raw_response" in response:
                return self._create_fallback_synthesis(domain)
            
            # Return plain text response wrapped in a simple structure
            return {
                "synthesis": response,
                "domain": domain,
                "generated_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"LLM synthesis failed: {e}")
            return self._create_fallback_synthesis(domain)
    
    def _create_fallback_synthesis(self, domain: str) -> Dict[str, Any]:
        """Create fallback synthesis when LLM fails"""
        return {
            "synthesis": f"""# {domain.title()} Domain Synthesis

## Executive Summary
Synthesis of {domain} domain based on available sources. Limited data available for comprehensive analysis.

## Merged Analysis
Analysis of {domain} domain developments and their implications for the telecommunications industry.

## Confidence Assessment
- Confidence Level: Medium
- Data Quality: Limited
- Source Reliability: Mixed

## Gaps and Unknowns
- Monitor {domain} domain for new developments
- Additional data sources needed
- Regular updates required

## Recommendations
- Monitor {domain} domain developments
- Review regulatory impact
- Assess operational implications

## Impact Assessment
- Impact Level: Low to Medium
- Affected Parties: All telecom stakeholders
- Time Horizon: Short to medium term
- Consensus: Limited data available
""",
            "domain": domain,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "fallback"
        }
    
    
    def _create_evidence_list(self, writer_report: Dict[str, Any], 
                            perplexity_summary: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create evidence list from both sources"""
        evidence = []
        
        # Add writer sources
        writer_sources = writer_report.get("sources", [])
        for source in writer_sources:
            evidence.append({
                "title": source.get("title", ""),
                "url": source.get("url", ""),
                "date": source.get("processed_at", ""),
                "source": "Writer Agent",
                "impact": source.get("impact_level", "low")
            })
        
        # Add perplexity source
        evidence.append({
            "title": f"Perplexity Analysis - {perplexity_summary.get('domain', '')}",
            "url": "Perplexity API",
            "date": perplexity_summary.get("generated_at", ""),
            "source": "Perplexity Agent",
            "impact": perplexity_summary.get("impact_assessment", {}).get("impact_level", "low")
        })
        
        return evidence
    
    def _merge_impact_assessments(self, writer_report: Dict[str, Any], 
                                perplexity_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Merge impact assessments from both sources"""
        try:
            writer_impact = writer_report.get("impact_summary", {})
            perplexity_impact = perplexity_summary.get("impact_assessment", {})
            
            # Determine dominant impact level
            writer_level = writer_impact.get("dominant_impact_level", "low")
            perplexity_level = perplexity_impact.get("impact_level", "low")
            
            # Use the higher impact level
            impact_levels = ["low", "medium", "high"]
            writer_index = impact_levels.index(writer_level)
            perplexity_index = impact_levels.index(perplexity_level)
            dominant_level = impact_levels[max(writer_index, perplexity_index)]
            
            # Merge affected parties
            writer_parties = writer_impact.get("affected_parties", {})
            perplexity_parties = perplexity_impact.get("affected_parties", [])
            
            all_parties = set()
            if isinstance(writer_parties, dict):
                all_parties.update(writer_parties.keys())
            if isinstance(perplexity_parties, list):
                all_parties.update(perplexity_parties)
            
            return {
                "dominant_impact_level": dominant_level,
                "affected_parties": list(all_parties),
                "writer_impact": writer_level,
                "perplexity_impact": perplexity_level,
                "consensus": writer_level == perplexity_level
            }
            
        except Exception as e:
            logger.error(f"Impact assessment merge failed: {e}")
            return {
                "dominant_impact_level": "low",
                "affected_parties": ["All"],
                "writer_impact": "low",
                "perplexity_impact": "low",
                "consensus": True
            }
    
    async def _generate_final_recommendations(self, writer_report: Dict[str, Any], 
                                            perplexity_summary: Dict[str, Any], 
                                            merged_analysis: str, domain: str) -> List[str]:
        """Generate final recommendations"""
        try:
            system_prompt = f"""Generate final actionable recommendations for telecom stakeholders.
            Combine insights from both sources for the {domain} domain.
            Prioritize high-impact, actionable recommendations."""
            
            prompt = f"""
            Domain: {domain}
            
            Writer Recommendations:
            {writer_report.get('now_what', [])}
            
            Merged Analysis:
            {merged_analysis[:500]}...
            
            Generate 3-5 final recommendations that:
            1. Address the most critical developments
            2. Are specific and actionable
            3. Consider both sources' insights
            """
            
            response = await llm_service.generate_response(prompt, system_prompt)
            
            # Extract recommendations
            recommendations = []
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('1.') or line.startswith('2.')):
                    recommendations.append(line)
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            logger.error(f"Final recommendations generation failed: {e}")
            return [f"Monitor {domain} domain developments", "Assess regulatory impact", "Review operational implications"]
    
    def _create_perplexity_only_report(self, domain: str, perplexity_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Create report using only Perplexity data"""
        try:
            return {
                "domain": domain,
                "generated_at": datetime.utcnow().isoformat(),
                "synthesis": f"""# {domain.title()} Domain Report

## Executive Summary
{perplexity_summary.get("content", f"Analysis based on Perplexity data for {domain} domain")}

## Analysis
Perplexity-based analysis for {domain} domain. This report is based solely on Perplexity data without additional verification.

## Confidence Assessment
- Confidence Level: {perplexity_summary.get("confidence", "medium")}
- Data Quality: Perplexity-based
- Source Reliability: Perplexity API

## Key Points
{chr(10).join([f"- {point}" for point in perplexity_summary.get("key_points", [f"Monitor {domain} domain developments"])])}

## Gaps and Unknowns
- Monitor {domain} domain for new developments
- Additional verification sources needed
- Regular updates required

## Recommendations
{chr(10).join([f"- {rec}" for rec in perplexity_summary.get("key_points", [f"Monitor {domain} domain developments"])[:5]])}

## Impact Assessment
- Impact Level: {perplexity_summary.get("impact_assessment", {}).get("impact_level", "low")}
- Affected Parties: All telecom stakeholders
- Time Horizon: Short to medium term
- Consensus: Perplexity-based assessment
""",
                "evidence": [{
                    "title": f"Perplexity Analysis - {domain}",
                    "url": "Perplexity API",
                    "date": perplexity_summary.get("generated_at", ""),
                    "source": "Perplexity Service",
                    "impact": perplexity_summary.get("impact_assessment", {}).get("impact_level", "low")
                }],
                "sources": {
                    "writer_sources": 0,
                    "perplexity_confidence": perplexity_summary.get("confidence", "medium")
                },
                "status": "perplexity_only"
            }
        except Exception as e:
            logger.error(f"Failed to create Perplexity-only report: {e}")
            return self._create_fallback_report(domain, perplexity_summary)
    
    def _create_fallback_report(self, domain: str, available_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback report when synthesis fails"""
        return {
            "domain": domain,
            "generated_at": datetime.utcnow().isoformat(),
            "synthesis": f"""# {domain.title()} Domain Fallback Report

## Executive Summary
Limited analysis available for {domain} domain. Unable to synthesize comprehensive report due to insufficient data.

## Analysis
Analysis based on available sources for {domain} domain. Data quality is limited and may not reflect current developments.

## Confidence Assessment
- Confidence Level: Low
- Data Quality: Limited
- Source Reliability: Unknown

## Gaps and Unknowns
- Monitor {domain} domain for new developments
- Additional data sources needed
- Regular updates required

## Recommendations
- Monitor {domain} domain developments
- Review regulatory impact
- Assess operational implications

## Impact Assessment
- Impact Level: Low
- Affected Parties: All telecom stakeholders
- Time Horizon: Unknown
- Consensus: Limited data available
""",
            "evidence": [],
            "sources": {
                "writer_sources": 0,
                "perplexity_confidence": "low"
            },
            "status": "partial"
        }

# Global agent instance
final_summarizer_agent = FinalSummarizerAgent()
