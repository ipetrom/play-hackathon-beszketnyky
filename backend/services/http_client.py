"""
HTTP client service for external API calls
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from .config import settings

logger = logging.getLogger(__name__)

class HTTPClient:
    """HTTP client for external API calls"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(settings.request_timeout)
        self.max_retries = settings.max_retries
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

class SerperClient(HTTPClient):
    """Client for Serper API (Google search)"""
    
    async def search(self, query: str, domain: str) -> Dict[str, Any]:
        """Search using Serper API"""
        try:
            headers = {
                "X-API-KEY": settings.serper_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": settings.max_search_results,
                "gl": "pl",  # Poland
                "hl": "pl"   # Polish language
            }
            
            async with self:
                response = await self.client.post(
                    f"{settings.serper_base_url}/search",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Serper search completed for domain: {domain}")
                return data
                
        except Exception as e:
            logger.error(f"Serper search failed: {e}")
            raise

class PerplexityClient(HTTPClient):
    """Client for Perplexity API"""
    
    async def summarize(self, query: str, domain: str) -> Dict[str, Any]:
        """Get summary from Perplexity"""
        try:
            headers = {
                "Authorization": f"Bearer {settings.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            payload = {
                "model": settings.perplexity_model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"""Monitor and summarize recent {domain} changes in Poland for last week only as for {current_date} that could impact the telecommunication industry.
Focus on:
- New or updated laws, regulations, or government communications
- Activities by UKE (Office of Electronic Communications), UOKiK (Competition and Consumer Protection), and other relevant bodies
- Emerging risks or compliance requirements
For each relevant update:
- Summarize the change (max 100 words)
- Highlight affected telecom areas (e.g. infrastructure, spectrum, consumer rights, competition)
- Suggest if business action or legal review is required
Use trustworthy Polish sources:
- Major legal or telecom-focused news portals
Return results in a plain-text structured format suitable for daily tracking and quick business decisions."""
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1
            }
            
            async with self:
                response = await self.client.post(
                    f"{settings.perplexity_base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Perplexity summary completed for domain: {domain}")
                return data
                
        except Exception as e:
            logger.error(f"Perplexity summary failed: {e}")
            raise

class WebScraperClient(HTTPClient):
    """Client for web scraping"""
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from URL"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            async with self:
                response = await self.client.get(url, headers=headers)
                response.raise_for_status()
                
                # Extract main content (simplified - in production, use trafilatura or similar)
                content = response.text
                
                # Basic content extraction
                title = self._extract_title(content)
                main_text = self._extract_main_text(content)
                
                result = {
                    "url": url,
                    "title": title,
                    "content": main_text,
                    "scraped_at": datetime.utcnow().isoformat(),
                    "status": "success"
                }
                
                logger.info(f"Successfully scraped URL: {url}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to scrape URL {url}: {e}")
            return {
                "url": url,
                "title": "",
                "content": "",
                "scraped_at": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    def _extract_title(self, html: str) -> str:
        """Extract title from HTML"""
        import re
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match:
            return title_match.group(1).strip()
        return ""
    
    def _extract_main_text(self, html: str) -> str:
        """Extract main text content from HTML"""
        import re
        
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.IGNORECASE | re.DOTALL)
        
        # Extract text from common content containers
        content_patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<main[^>]*>(.*?)</main>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*article[^"]*"[^>]*>(.*?)</div>'
        ]
        
        for pattern in content_patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1)
                # Remove HTML tags
                content = re.sub(r'<[^>]+>', ' ', content)
                # Clean up whitespace
                content = re.sub(r'\s+', ' ', content).strip()
                if len(content) > settings.min_content_length:
                    return content[:settings.max_content_length]
        
        # Fallback: extract all text
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:settings.max_content_length]

# Global client instances
serper_client = SerperClient()
perplexity_client = PerplexityClient()
scraper_client = WebScraperClient()
