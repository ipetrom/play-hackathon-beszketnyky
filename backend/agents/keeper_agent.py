"""
Keeper Agent (Agent 2: "Bramkarz")
LLM-based aggressive noise filtering - extracts only telecom-relevant, decision-useful facts
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from services.llm_service import llm_service
from services.config import settings

logger = logging.getLogger(__name__)

class KeeperAgent:
    """Agent 2: LLM-based filtering and extraction of telecom-relevant facts"""
    
    def __init__(self):
        self.name = "KeeperAgent"
    
    async def process_content(self, scraped_content: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """
        LLM-based processing of scraped content to extract telecom-relevant facts
        
        Args:
            scraped_content: Scraped content from URL
            domain: Target domain (prawo/polityka/financial)
            
        Returns:
            Extracted facts and analysis
        """
        try:
            logger.info(f"LLM-based processing content for domain: {domain}")
            
            if scraped_content.get("status") != "success":
                logger.warning(f"Content scraping failed: {scraped_content.get('error', 'Unknown error')}")
                return self._create_empty_result()
            
            title = scraped_content.get("title", "")
            content = scraped_content.get("content", "")
            url = scraped_content.get("url", "")
            
            if not content or len(content) < settings.min_content_length:
                logger.warning(f"Content too short or empty: {url}")
                return self._create_empty_result()
            
            # Use LLM to process the entire content
            llm_analysis = await self._llm_analyze_content(title, content, domain, url)
            
            result = {
                "url": url,
                "title": title,
                "domain": domain,
                "facts": llm_analysis.get("facts", []),
                "entities": llm_analysis.get("entities", {}),
                "category": llm_analysis.get("category", "regulation"),
                "impact_assessment": llm_analysis.get("impact_assessment", {}),
                "summary": llm_analysis.get("summary", ""),
                "processed_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            logger.info(f"Successfully processed content with LLM: {url}")
            return result
            
        except Exception as e:
            logger.error(f"LLM content processing failed: {e}")
            return self._create_empty_result()
    
    async def _llm_analyze_content(self, title: str, content: str, domain: str, url: str) -> Dict[str, Any]:
        """Use LLM to comprehensively analyze content"""
        try:
            system_prompt = f"""You are a telecommunications expert specializing in Poland's telecom market.
            Your task is to analyze content for the {domain} domain and extract only telecom-relevant, decision-useful information.
            
            Focus on:
            1. Polish telecom operators: Play, Orange, T-Mobile, Plus
            2. Regulators: UKE, UOKiK, KRRiT
            3. Government: Ministry of Digitalization, Ministry of Development
            4. EU regulations affecting Poland
            5. Market developments, regulatory changes, policy decisions
            
            Extract:
            - Key telecom-relevant facts
            - Entities (organizations, people, dates, numbers, locations)
            - Content category (spectrum, pricing, M&A, sanctions, consumer_law, wholesale, infrastructure, regulation, competition, investment)
            - Impact assessment (low/medium/high impact, time horizon, affected parties)
            - Executive summary
            
            Be precise, factual, and focus only on telecom-relevant information."""
            
            prompt = f"""
            Title: {title}
            URL: {url}
            Domain: {domain}
            
            Content: {content[:3000]}...
            
            Analyze this content and return a JSON object with:
            - facts: Array of telecom-relevant facts with fact, relevance, source_evidence, affected_parties
            - entities: Object with organizations, people, dates, numbers, locations arrays
            - category: One of the telecom categories
            - impact_assessment: Object with impact_level, time_horizon, affected_parties, reasoning
            - summary: Executive summary of telecom implications
            """
            
            response = await llm_service.generate_structured_response(
                prompt, system_prompt, {
                    "type": "object",
                    "properties": {
                        "facts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "fact": {"type": "string"},
                                    "relevance": {"type": "string"},
                                    "source_evidence": {"type": "string"},
                                    "affected_parties": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        },
                        "entities": {
                            "type": "object",
                            "properties": {
                                "organizations": {"type": "array", "items": {"type": "string"}},
                                "people": {"type": "array", "items": {"type": "string"}},
                                "dates": {"type": "array", "items": {"type": "string"}},
                                "numbers": {"type": "array", "items": {"type": "string"}},
                                "locations": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "category": {"type": "string"},
                        "impact_assessment": {
                            "type": "object",
                            "properties": {
                                "impact_level": {"type": "string", "enum": ["low", "medium", "high"]},
                                "time_horizon": {"type": "string", "enum": ["immediate", "near", "medium"]},
                                "affected_parties": {"type": "array", "items": {"type": "string"}},
                                "reasoning": {"type": "string"}
                            }
                        },
                        "summary": {"type": "string"}
                    }
                }
            )
            
            if isinstance(response, dict) and "raw_response" in response:
                # Fallback: create basic analysis
                return self._create_fallback_analysis(title, content, domain)
            
            return response if isinstance(response, dict) else self._create_fallback_analysis(title, content, domain)
            
        except Exception as e:
            logger.error(f"LLM content analysis failed: {e}")
            return self._create_fallback_analysis(title, content, domain)
    
    def _create_fallback_analysis(self, title: str, content: str, domain: str) -> Dict[str, Any]:
        """Create fallback analysis when LLM fails"""
        return {
            "facts": [{
                "fact": f"Content from {title}",
                "relevance": f"Relevant to {domain} domain",
                "source_evidence": title,
                "affected_parties": ["All"]
            }],
            "entities": {
                "organizations": [],
                "people": [],
                "dates": [],
                "numbers": [],
                "locations": []
            },
            "category": "regulation",
            "impact_assessment": {
                "impact_level": "low",
                "time_horizon": "medium",
                "affected_parties": ["All"],
                "reasoning": "Fallback analysis due to LLM processing failure"
            },
            "summary": f"Content analysis for {domain} domain: {title}"
        }
    
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create empty result for failed processing"""
        return {
            "url": "",
            "title": "",
            "domain": "",
            "facts": [],
            "entities": {},
            "category": "regulation",
            "impact_assessment": {
                "impact_level": "low",
                "time_horizon": "medium",
                "affected_parties": [],
                "reasoning": "Processing failed"
            },
            "summary": "Content processing failed",
            "processed_at": datetime.utcnow().isoformat(),
            "status": "error"
        }

# Global agent instance
keeper_agent = KeeperAgent()
