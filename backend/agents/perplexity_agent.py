"""
Perplexity Service
Provides additional context for each domain using Perplexity API
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from services.http_client import perplexity_client
from services.config import settings

logger = logging.getLogger(__name__)

class PerplexityService:
    """Service: Domain context enrichment using Perplexity API"""
    
    def __init__(self):
        self.name = "PerplexityService"
        self.domains = settings.domains
        
        # Domain-specific search queries
        self.domain_queries = {
            "prawo": [
                "Poland telecommunications law regulation UKE UOKiK 2025",
                "Polish telecom operators legal requirements spectrum allocation",
                "Poland telecom regulatory changes 2025 EU directives",
                "UKE decisions Polish telecom market 2025",
                "telecom law Poland spectrum auction 5G"
            ],
            "polityka": [
                "Poland telecom policy government strategy 2025",
                "Polish telecom ministry digital transformation policy",
                "Poland 5G strategy government telecom investment",
                "Polish telecom infrastructure policy EU funding",
                "Poland telecom competition policy market regulation"
            ],
            "financial": [
                "Poland telecom market financial results 2025",
                "Polish telecom operators revenue profit investment",
                "Poland telecom market capitalization stock prices",
                "telecom investment Poland infrastructure funding",
                "Polish telecom market growth financial outlook"
            ]
        }
    
    async def get_domain_context(self, domain: str) -> Dict[str, Any]:
        """
        Get additional context for domain using Perplexity
        
        Args:
            domain: Target domain (prawo/polityka/financial)
            
        Returns:
            Domain context from Perplexity
        """
        try:
            logger.info(f"Getting Perplexity context for domain: {domain}")
            
            if domain not in self.domain_queries:
                logger.warning(f"Unknown domain: {domain}")
                return self._create_empty_context(domain)
            
            # Get the most relevant query for the domain
            query = self.domain_queries[domain][0]  # Use the first query
            
            # Get context from Perplexity
            response = await perplexity_client.summarize(query, domain)
            
            if not response or "choices" not in response:
                logger.warning(f"No response from Perplexity for domain: {domain}")
                return self._create_empty_context(domain)
            
            # Extract content from response
            content = response["choices"][0]["message"]["content"]
            
            # Process the context
            context = self._process_perplexity_response(content, domain)
            
            logger.info(f"Successfully got Perplexity context for domain: {domain}")
            return context
            
        except Exception as e:
            logger.error(f"Perplexity context failed for domain {domain}: {e}")
            return self._create_empty_context(domain)
    
    def _process_perplexity_response(self, content: str, domain: str) -> Dict[str, Any]:
        """Process Perplexity response into structured format"""
        try:
            # Extract key information from the response
            context = {
                "domain": domain,
                "source": "Perplexity",
                "generated_at": datetime.utcnow().isoformat(),
                "content": content,
                "key_points": self._extract_key_points(content),
                "entities": self._extract_entities(content),
                "impact_assessment": self._assess_perplexity_impact(content, domain),
                "confidence": self._assess_confidence(content),
                "status": "success"
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to process Perplexity response: {e}")
            return self._create_empty_context(domain)
    
    def _extract_key_points(self, content: str) -> list:
        """Extract key points from Perplexity response"""
        try:
            # Simple extraction of bullet points or numbered items
            import re
            
            # Look for bullet points
            bullet_points = re.findall(r'[•\-\*]\s*([^\n]+)', content)
            
            # Look for numbered items
            numbered_points = re.findall(r'\d+\.\s*([^\n]+)', content)
            
            # Look for key phrases
            key_phrases = re.findall(r'([A-Z][^.!?]*telecom[^.!?]*[.!?])', content, re.IGNORECASE)
            
            all_points = bullet_points + numbered_points + key_phrases
            
            # Clean and deduplicate
            cleaned_points = []
            seen = set()
            
            for point in all_points:
                point = point.strip()
                if point and point not in seen and len(point) > 10:
                    cleaned_points.append(point)
                    seen.add(point)
            
            return cleaned_points[:10]  # Limit to 10 key points
            
        except Exception as e:
            logger.error(f"Failed to extract key points: {e}")
            return []
    
    def _extract_entities(self, content: str) -> Dict[str, list]:
        """Extract entities from Perplexity response"""
        try:
            entities = {
                "organizations": [],
                "people": [],
                "dates": [],
                "numbers": [],
                "locations": []
            }
            
            import re
            
            # Extract organizations
            org_patterns = [
                r'\b(Play|Orange|T-Mobile|Plus)\b',
                r'\b(UKE|UOKiK|KRRiT)\b',
                r'\b(Ministerstwo|Urząd)\s+[A-Z][a-z]+',
                r'\b(Sejm|Senat|Rząd)\b'
            ]
            
            for pattern in org_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                entities["organizations"].extend(matches)
            
            # Extract dates
            date_patterns = [
                r'\d{4}',
                r'\d{1,2}\s*(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)',
                r'\d{1,2}\.\d{1,2}\.\d{4}'
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                entities["dates"].extend(matches)
            
            # Extract numbers
            number_patterns = [
                r'\d+[\s,]*\d*\s*(milion|miliard|mln|mld)',
                r'\d+[\s,]*\d*\s*(MHz|GHz|MB|GB)',
                r'\d+[\s,]*\d*\s*(zł|euro|USD)',
                r'\d+[\s,]*\d*\s*%'
            ]
            
            for pattern in number_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                entities["numbers"].extend(matches)
            
            # Extract locations
            location_patterns = [
                r'\b(Warszawa|Kraków|Gdańsk|Wrocław|Poznań)\b',
                r'\b(Polska|Poland)\b'
            ]
            
            for pattern in location_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                entities["locations"].extend(matches)
            
            # Deduplicate
            for category in entities:
                entities[category] = list(set(entities[category]))
            
            return entities
            
        except Exception as e:
            logger.error(f"Failed to extract entities: {e}")
            return {"organizations": [], "people": [], "dates": [], "numbers": [], "locations": []}
    
    def _assess_perplexity_impact(self, content: str, domain: str) -> Dict[str, Any]:
        """Assess impact based on Perplexity response"""
        try:
            content_lower = content.lower()
            
            # Determine impact level
            high_impact_keywords = ["ustawa", "rozporządzenie", "decyzja", "kara", "grzywna", "zakaz", "nowa", "zmiana"]
            medium_impact_keywords = ["taryfa", "cena", "opłata", "plan", "strategia", "program"]
            
            if any(keyword in content_lower for keyword in high_impact_keywords):
                impact_level = "high"
            elif any(keyword in content_lower for keyword in medium_impact_keywords):
                impact_level = "medium"
            else:
                impact_level = "low"
            
            # Determine time horizon
            if any(keyword in content_lower for keyword in ["natychmiast", "pilne", "urgent", "immediate"]):
                time_horizon = "immediate"
            elif any(keyword in content_lower for keyword in ["wkrótce", "soon", "near", "bliski"]):
                time_horizon = "near"
            else:
                time_horizon = "medium"
            
            # Determine affected parties
            affected_parties = []
            for operator in settings.telecom_operators:
                if operator.lower() in content_lower:
                    affected_parties.append(operator)
            
            if not affected_parties:
                affected_parties = ["All"]
            
            return {
                "impact_level": impact_level,
                "time_horizon": time_horizon,
                "affected_parties": affected_parties,
                "reasoning": f"Based on Perplexity analysis: {impact_level} impact level"
            }
            
        except Exception as e:
            logger.error(f"Failed to assess impact: {e}")
            return {
                "impact_level": "low",
                "time_horizon": "medium",
                "affected_parties": ["All"],
                "reasoning": "Unable to assess impact"
            }
    
    def _assess_confidence(self, content: str) -> str:
        """Assess confidence in Perplexity response"""
        try:
            content_lower = content.lower()
            
            # High confidence indicators
            high_confidence_keywords = ["zgodnie z", "według", "potwierdza", "oficjalnie", "decyzja", "ustawa"]
            
            # Medium confidence indicators
            medium_confidence_keywords = ["prawdopodobnie", "możliwe", "może", "prawdopodobny"]
            
            # Low confidence indicators
            low_confidence_keywords = ["spekulacja", "możliwe", "niepewne", "niejasne"]
            
            if any(keyword in content_lower for keyword in high_confidence_keywords):
                return "high"
            elif any(keyword in content_lower for keyword in low_confidence_keywords):
                return "low"
            elif any(keyword in content_lower for keyword in medium_confidence_keywords):
                return "medium"
            else:
                return "medium"  # Default to medium confidence
                
        except Exception as e:
            logger.error(f"Failed to assess confidence: {e}")
            return "medium"
    
    def _create_empty_context(self, domain: str) -> Dict[str, Any]:
        """Create empty context for failed processing"""
        return {
            "domain": domain,
            "source": "Perplexity",
            "generated_at": datetime.utcnow().isoformat(),
            "content": f"No context available for {domain} domain",
            "key_points": [],
            "entities": {"organizations": [], "people": [], "dates": [], "numbers": [], "locations": []},
            "impact_assessment": {
                "impact_level": "low",
                "time_horizon": "medium",
                "affected_parties": ["All"],
                "reasoning": "No data available"
            },
            "confidence": "low",
            "status": "error"
        }

# Global service instance
perplexity_service = PerplexityService()
