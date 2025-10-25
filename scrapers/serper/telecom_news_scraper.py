"""
Telecommunications News Scraper
Comprehensive web scraper for monitoring telecommunications domain news
across legal, political, and financial categories using Serper API.
"""

import asyncio
import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelecomNewsScraper:
    def __init__(self, serper_api_key: str):
        self.serper_api_key = serper_api_key
        self.base_url = "https://google.serper.dev/news"
        self.headers = {
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json"
        }
        
        # Telecommunications keywords for relevance filtering
        self.telecom_keywords = [
            "telekomunikacja", "telecom", "telecommunications", "telefonia", "telephony",
            "internet", "broadband", "5G", "4G", "LTE", "mobile", "mobilny", "sieć", "network",
            "operator", "dostawca", "provider", "abonament", "subscription", "roaming",
            "infrastruktura", "infrastructure", "fibra", "fiber", "kabel", "cable",
            "satelita", "satellite", "IoT", "cyfryzacja", "digitalization",
            "regulacja", "regulation", "UKE", "regulator", "spectrum", "widmo",
            "frequency", "częstotliwość", "base station", "stacja bazowa"
        ]
        
        # Legal sources (Prawo)
        self.legal_sources = [
            "legislacja.rcl.gov.pl",
            "isap.sejm.gov.pl", 
            "gov.pl",
            "prezydent.pl",
            "sejm.gov.pl",
            "senat.gov.pl",
            "uke.gov.pl",
            "uokik.gov.pl",
            "berec.europa.eu",
            "digital-strategy.ec.europa.eu",
            "consilium.europa.eu",
            "europarl.europa.eu",
            "enisa.europa.eu",
            "oecd.org"
        ]
        
        # Political sources (Polityka)
        self.political_sources = [
            "reuters.com",
            "bloomberg.com", 
            "wsj.com",
            "cnn.com",
            "nbcnews.com",
            "foxnews.com",
            "nytimes.com",
            "washingtonpost.com",
            "apnews.com",
            "theguardian.com",
            "thetimes.co.uk",
            "bbc.com",
            "lemonde.fr",
            "afp.com",
            "onet.pl",
            "biznes.pap.pl",
            "rp.pl",
            "ec.europa.eu",
            "politico.eu",
            "news.cn",
            "caixinglobal.com",
            "japantimes.co.jp",
            "nhk.or.jp",
            "ft.com"
        ]
        
        # Financial sources (Market)
        self.financial_sources = [
            "nbp.pl",
            "ecb.europa.eu",
            "fred.stlouisfed.org",
            "imf.org",
            "bis.org",
            "reuters.com/markets",
            "oanda.com",
            "bloomberg.com/markets",
            "wsj.com/markets",
            "ft.com/markets"
        ]

    async def search_news(self, query: str, sources: List[str] = None, days_back: int = 7) -> List[Dict[str, Any]]:
        """Search for news using Serper API"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Build query with date range and sources
            search_query = f"{query} after:{start_date.strftime('%Y-%m-%d')} before:{end_date.strftime('%Y-%m-%d')}"
            
            if sources:
                site_queries = " OR ".join([f"site:{source}" for source in sources])
                search_query = f"({search_query}) AND ({site_queries})"
            
            payload = {
                "q": search_query,
                "num": 20,  # Number of results
                "gl": "pl",  # Country: Poland
                "hl": "pl"   # Language: Polish
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("news", [])
                    else:
                        logger.error(f"Serper API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return []

    def is_telecom_relevant(self, title: str, snippet: str) -> bool:
        """Check if article is relevant to telecommunications"""
        text = f"{title} {snippet}".lower()
        
        # Enhanced telecom keywords for better filtering
        enhanced_telecom_keywords = [
            "telekomunikacja", "telecom", "telecommunications", "telefonia", "telephony",
            "internet", "broadband", "5g", "4g", "lte", "mobile", "mobilny", "sieć", "network",
            "operator", "dostawca", "provider", "abonament", "subscription", "roaming",
            "infrastruktura", "infrastructure", "fibra", "fiber", "kabel", "cable",
            "satelita", "satellite", "iot", "cyfryzacja", "digitalization",
            "regulacja", "regulation", "uke", "regulator", "spectrum", "widmo",
            "frequency", "częstotliwość", "antenna", "antena", "base station", "stacja bazowa",
            "orange", "play", "plus", "t-mobile", "vodafone", "cyfrowy polsat",
            "abonament", "subscription", "roaming", "internet rzeczy", "smart city",
            "cybersecurity", "cyberbezpieczeństwo", "data protection", "ochrona danych"
        ]
        
        return any(keyword.lower() in text for keyword in enhanced_telecom_keywords)

    def categorize_article(self, article: Dict[str, Any]) -> str:
        """Categorize article based on source"""
        source = article.get("source", "").lower()
        
        if any(legal_source in source for legal_source in self.legal_sources):
            return "prawo"
        elif any(political_source in source for political_source in self.political_sources):
            return "polityka"
        elif any(financial_source in source for financial_source in self.financial_sources):
            return "financial"
        else:
            return "other"

    async def scrape_legal_news(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape legal/regulatory news"""
        queries = [
            "telekomunikacja regulacja prawo",
            "UKE decyzja",
            "telecom regulation Poland",
            "telefonia prawo",
            "internet regulacja",
            "5G spectrum allocation",
            "telecom law Poland"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_news(query, self.legal_sources, days_back)
            all_articles.extend(articles)
        
        # Filter and deduplicate
        filtered_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if (self.is_telecom_relevant(article.get("title", ""), article.get("snippet", "")) and
                article.get("link") not in seen_urls):
                article["category"] = "prawo"
                article["scraped_at"] = datetime.now().isoformat()
                filtered_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return filtered_articles

    async def scrape_political_news(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape political news affecting telecom"""
        queries = [
            "telecom policy Poland",
            "telekomunikacja polityka",
            "digital policy Poland",
            "cyfryzacja Polska",
            "telecom investment Poland",
            "5G Poland policy",
            "internet policy Poland"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_news(query, self.political_sources, days_back)
            all_articles.extend(articles)
        
        # Filter and deduplicate
        filtered_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if (self.is_telecom_relevant(article.get("title", ""), article.get("snippet", "")) and
                article.get("link") not in seen_urls):
                article["category"] = "polityka"
                article["scraped_at"] = datetime.now().isoformat()
                filtered_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return filtered_articles

    async def scrape_financial_news(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape financial/market news"""
        queries = [
            "telecom stocks Poland",
            "telekomunikacja giełda",
            "telecom market Poland",
            "telecom investment Poland",
            "telecom earnings Poland",
            "telecom financial results",
            "telecom merger Poland"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_news(query, self.financial_sources, days_back)
            all_articles.extend(articles)
        
        # Filter and deduplicate
        filtered_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if (self.is_telecom_relevant(article.get("title", ""), article.get("snippet", "")) and
                article.get("link") not in seen_urls):
                article["category"] = "financial"
                article["scraped_at"] = datetime.now().isoformat()
                filtered_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return filtered_articles

    async def scrape_all_news(self, days_back: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape all categories of news"""
        logger.info("Starting comprehensive telecom news scraping...")
        
        # Run all scrapers concurrently
        legal_task = self.scrape_legal_news(days_back)
        political_task = self.scrape_political_news(days_back)
        financial_task = self.scrape_financial_news(days_back)
        
        legal_news, political_news, financial_news = await asyncio.gather(
            legal_task, political_task, financial_task
        )
        
        return {
            "prawo": legal_news,
            "polityka": political_news,
            "financial": financial_news,
            "scraped_at": datetime.now().isoformat(),
            "total_articles": len(legal_news) + len(political_news) + len(financial_news)
        }

    def generate_weekly_report(self, news_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate weekly report summary"""
        report = {
            "report_period": f"Last 7 days (scraped on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
            "summary": {
                "total_articles": news_data["total_articles"],
                "legal_articles": len(news_data["prawo"]),
                "political_articles": len(news_data["polityka"]),
                "financial_articles": len(news_data["financial"])
            },
            "key_insights": [],
            "risk_areas": [],
            "action_items": [],
            "categories": news_data
        }
        
        # Generate insights based on article content
        all_articles = news_data["prawo"] + news_data["polityka"] + news_data["financial"]
        
        # Look for regulatory changes
        regulatory_keywords = ["decyzja", "decision", "regulacja", "regulation", "prawo", "law"]
        regulatory_articles = [a for a in all_articles if any(kw in a.get("title", "").lower() for kw in regulatory_keywords)]
        
        if regulatory_articles:
            report["key_insights"].append(f"Found {len(regulatory_articles)} regulatory/legal developments")
            report["action_items"].append("Review regulatory changes for compliance impact")
        
        # Look for market movements
        market_keywords = ["cena", "price", "koszt", "cost", "inwestycja", "investment", "wyniki", "results"]
        market_articles = [a for a in all_articles if any(kw in a.get("title", "").lower() for kw in market_keywords)]
        
        if market_articles:
            report["key_insights"].append(f"Found {len(market_articles)} market-related developments")
            report["action_items"].append("Monitor market trends for competitive positioning")
        
        # Look for technology trends
        tech_keywords = ["5G", "6G", "IoT", "AI", "artificial intelligence", "sztuczna inteligencja"]
        tech_articles = [a for a in all_articles if any(kw in a.get("title", "").lower() for kw in tech_keywords)]
        
        if tech_articles:
            report["key_insights"].append(f"Found {len(tech_articles)} technology-related developments")
            report["action_items"].append("Assess technology trends for strategic planning")
        
        return report

async def main():
    """Main function to run the scraper"""
    # Get API key from environment
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        logger.error("SERPER_API_KEY environment variable not set")
        return
    
    scraper = TelecomNewsScraper(serper_api_key)
    
    # Scrape all news
    news_data = await scraper.scrape_all_news(days_back=7)
    
    # Generate report
    report = scraper.generate_weekly_report(news_data)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save raw data
    with open(f"telecom_news_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    # Save report
    with open(f"telecom_report_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Scraping completed. Found {news_data['total_articles']} articles")
    logger.info(f"Legal: {len(news_data['prawo'])}, Political: {len(news_data['polityka'])}, Financial: {len(news_data['financial'])}")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())
