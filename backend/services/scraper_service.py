"""
Web Scraping Service
Scrapes individual URLs and extracts content
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import trafilatura

from .config import settings

logger = logging.getLogger(__name__)

class ScraperService:
    """Service for scraping individual URLs"""
    
    def __init__(self):
        self.name = "ScraperService"
        self.timeout = 30
        self.max_content_length = settings.max_content_length
        self.min_content_length = settings.min_content_length
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a single URL and extract content
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraped content with metadata
        """
        try:
            logger.info(f"Scraping URL: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status != 200:
                        logger.warning(f"HTTP {response.status} for URL: {url}")
                        return self._create_error_result(url, f"HTTP {response.status}")
                    
                    html_content = await response.text()
                    
                    # Extract content using trafilatura
                    extracted_content = trafilatura.extract(html_content)
                    
                    if not extracted_content:
                        # Fallback to BeautifulSoup
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get text content
                        extracted_content = soup.get_text()
                    
                    # Clean and validate content
                    content = self._clean_content(extracted_content)
                    
                    if len(content) < self.min_content_length:
                        logger.warning(f"Content too short for URL: {url}")
                        return self._create_error_result(url, "Content too short")
                    
                    # Extract title
                    title = self._extract_title(html_content)
                    
                    result = {
                        "url": url,
                        "title": title,
                        "content": content[:self.max_content_length],
                        "content_length": len(content),
                        "scraped_at": datetime.utcnow().isoformat(),
                        "status": "success"
                    }
                    
                    logger.info(f"Successfully scraped URL: {url} ({len(content)} chars)")
                    return result
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout scraping URL: {url}")
            return self._create_error_result(url, "Timeout")
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            return self._create_error_result(url, str(e))
    
    def _clean_content(self, content: str) -> str:
        """Clean extracted content"""
        if not content:
            return ""
        
        # Remove extra whitespace
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Filter out very short lines
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_title(self, html_content: str) -> str:
        """Extract title from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
            
            # Fallback to h1
            h1_tag = soup.find('h1')
            if h1_tag:
                return h1_tag.get_text().strip()
            
            return "No title found"
            
        except Exception as e:
            logger.warning(f"Error extracting title: {e}")
            return "No title found"
    
    def _create_error_result(self, url: str, error: str) -> Dict[str, Any]:
        """Create error result"""
        return {
            "url": url,
            "title": "",
            "content": "",
            "content_length": 0,
            "scraped_at": datetime.utcnow().isoformat(),
            "status": "error",
            "error": error
        }

# Global scraper service instance
scraper_service = ScraperService()


