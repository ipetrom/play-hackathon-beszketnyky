"""
Serper Verification Agent (Agent 1: "Weryfikacja")
LLM-based agent that decides which links merit scraping for the specific domain
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from services.llm_service import llm_service
from services.config import settings

logger = logging.getLogger(__name__)

class SerperVerificationAgent:
    """Agent 1: LLM-based verification and filtering of Serper search results"""
    
    def __init__(self):
        self.name = "SerperVerificationAgent"
    
    async def verify_results(self, search_results: Dict[str, Any], domain: str) -> List[str]:
        """
        LLM-based verification and filtering of search results for a specific domain
        
        Args:
            search_results: Raw Serper API results or telecom news scraper results
            domain: Target domain (prawo/polityka/financial)
            
        Returns:
            List of verified URLs to scrape
        """
        try:
            logger.info(f"Starting LLM-based verification for domain: {domain}")
            
            # Handle telecom news scraper format
            if "categories" in search_results:
                # This is from telecom_news_scraper.py
                articles = search_results.get("categories", {}).get(domain, [])
                if not articles:
                    logger.warning(f"No articles found for domain: {domain}")
                    return []
                
                # Use LLM to verify and filter results
                verified_urls = await self._llm_verify_articles(articles, domain)
                
            else:
                # This is from direct Serper API
                organic_results = search_results.get("organic", [])
                if not organic_results:
                    logger.warning(f"No organic results found for domain: {domain}")
                    return []
                
                # Use LLM to verify and filter results
                verified_urls = await self._llm_verify_results(organic_results, domain)
            
            logger.info(f"LLM verified {len(verified_urls)} URLs for domain: {domain}")
            return verified_urls
            
        except Exception as e:
            logger.error(f"LLM verification failed for domain {domain}: {e}")
            return []
    
    async def _llm_verify_results(self, organic_results: List[Dict[str, Any]], domain: str) -> List[str]:
        """Use LLM to verify and filter search results"""
        try:
            system_prompt = f"""You are a telecommunications expert specializing in Poland's telecom market.
            Your task is to verify and filter search results for the {domain} domain.
            
            You must identify URLs that are:
            1. Relevant to Polish telecommunications (operators: Play, Orange, T-Mobile, Plus; regulators: UKE, UOKiK)
            2. Relevant to the {domain} domain
            3. Poland-specific or EU regulations affecting Poland
            4. Recent and high-quality sources
            5. Decision-useful for telecom stakeholders
            
            Reject URLs that are:
            - Not telecom-related
            - Not Poland-relevant
            - Not domain-relevant
            - Duplicates or low-quality
            - Sports, entertainment, or unrelated content
            
            Return only the URLs that should be scraped for further analysis. If no URLs are relevant, return an empty list."""
            
            # Prepare search results for LLM
            results_text = ""
            for i, result in enumerate(organic_results):
                results_text += f"""
Result {i+1}:
Title: {result.get('title', '')}
Snippet: {result.get('snippet', '')}
URL: {result.get('link', '')}
Date: {result.get('date', '')}
Source: {result.get('source', '')}
"""
            
            prompt = f"""
Search Results for {domain} domain:
{results_text}

Analyze each result and return a JSON array of URLs that should be scraped.
Format: ["url1", "url2", "url3"]
Only include URLs that meet all relevance criteria.
"""
            
            # Get LLM response
            response = await llm_service.generate_structured_response(
                prompt, system_prompt, {
                    "type": "array",
                    "items": {"type": "string"}
                }
            )
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and "raw_response" in response:
                # Fallback: try to extract URLs from raw response
                return self._extract_urls_from_text(response["raw_response"])
            else:
                logger.warning("Unexpected LLM response format")
                return []
                
        except Exception as e:
            logger.error(f"LLM verification failed: {e}")
            return []
    
    def _extract_urls_from_text(self, text: str) -> List[str]:
        """Extract URLs from LLM text response as fallback"""
        import re
        
        # Look for URLs in the text
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # Filter out common non-URL patterns
        filtered_urls = []
        for url in urls:
            if any(domain in url for domain in ['.pl', '.eu', '.com', '.org']):
                filtered_urls.append(url)
        
        return filtered_urls[:10]  # Limit to 10 URLs
    
    async def _llm_verify_articles(self, articles: List[Dict[str, Any]], domain: str) -> List[str]:
        """Use LLM to verify and filter articles from telecom news scraper"""
        try:
            system_prompt = f"""You are a telecommunications expert specializing in Poland's telecom market.
            Your task is to verify and filter articles for the {domain} domain.
            
            You must identify URLs that are:
            1. Relevant to Polish telecommunications (operators: Play, Orange, T-Mobile, Plus; regulators: UKE, UOKiK)
            2. Relevant to the {domain} domain
            3. Poland-specific or EU regulations affecting Poland
            4. Recent and high-quality sources
            5. Decision-useful for telecom stakeholders
            
            Reject URLs that are:
            - Not telecom-related
            - Not Poland-relevant
            - Not domain-relevant
            - Duplicates or low-quality
            - Sports, entertainment, or unrelated content
            
            Return only the URLs that should be scraped for further analysis. If no URLs are relevant, return an empty list."""
            
            # Prepare articles for LLM
            articles_text = ""
            for i, article in enumerate(articles):
                articles_text += f"""
Article {i+1}:
Title: {article.get('title', '')}
Snippet: {article.get('snippet', '')}
URL: {article.get('link', '')}
Date: {article.get('date', '')}
Source: {article.get('source', '')}
Category: {article.get('category', '')}
"""
            
            prompt = f"""
Articles for {domain} domain:
{articles_text}

Analyze each article and return a JSON array of URLs that should be scraped.
Format: ["url1", "url2", "url3"]
Only include URLs that meet all relevance criteria.
"""
            
            # Get LLM response
            response = await llm_service.generate_structured_response(
                prompt, system_prompt, {
                    "type": "array",
                    "items": {"type": "string"}
                }
            )
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and "raw_response" in response:
                # Fallback: try to extract URLs from raw response
                return self._extract_urls_from_text(response["raw_response"])
            else:
                logger.warning("Unexpected LLM response format")
                return []
                
        except Exception as e:
            logger.error(f"LLM article verification failed: {e}")
            return []
    
    async def get_verification_summary(self, original_count: int, verified_count: int, domain: str) -> str:
        """Generate LLM-based verification summary"""
        try:
            system_prompt = """Generate a verification summary for telecom content filtering.
            Focus on the quality and relevance of the filtering process."""
            
            prompt = f"""
Verification Results for {domain} domain:
- Original search results: {original_count}
- URLs selected for scraping: {verified_count}
- Filter rate: {((original_count - verified_count) / original_count * 100):.1f}%

Generate a summary of the verification process and quality assessment.
"""
            
            response = await llm_service.generate_response(prompt, system_prompt)
            return response
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return f"LLM-based verification completed for {domain} domain: {verified_count}/{original_count} URLs selected."

# Global agent instance
serper_verification_agent = SerperVerificationAgent()
