"""
Political News Scraper for Telecommunications
Specialized scraper for monitoring political developments
affecting the telecommunications industry in Poland and globally.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class PoliticalTelecomScraper:
    def __init__(self, serper_api_key: str):
        self.serper_api_key = serper_api_key
        self.base_url = "https://google.serper.dev/news"
        self.headers = {
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json"
        }
        
        # Political news sources
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
            "ft.com",
            "dw.com",
            "euronews.com",
            "aljazeera.com"
        ]
        
        # Political keywords
        self.political_keywords = [
            "polityka", "policy", "rząd", "government", "minister", "ministerstwo",
            "ministry", "prezydent", "president", "premier", "prime minister",
            "sejm", "parliament", "senat", "senate", "głosowanie", "voting",
            "wybory", "elections", "kampania", "campaign", "partia", "party",
            "koalicja", "coalition", "opozycja", "opposition", "reforma", "reform",
            "strategia", "strategy", "plan", "program", "budżet", "budget",
            "inwestycja", "investment", "infrastruktura", "infrastructure",
            "cyfryzacja", "digitalization", "transformacja", "transformation"
        ]

    async def search_political_news(self, query: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Search for political news using Serper API"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            search_query = f"{query} after:{start_date.strftime('%Y-%m-%d')} before:{end_date.strftime('%Y-%m-%d')}"
            
            # Add site restrictions for political sources
            site_queries = " OR ".join([f"site:{source}" for source in self.political_sources])
            search_query = f"({search_query}) AND ({site_queries})"
            
            payload = {
                "q": search_query,
                "num": 20,
                "gl": "pl",
                "hl": "pl"
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
            logger.error(f"Error searching political news: {e}")
            return []

    def is_political_relevant(self, title: str, snippet: str) -> bool:
        """Check if article is politically relevant"""
        text = f"{title} {snippet}".lower()
        return any(keyword.lower() in text for keyword in self.political_keywords)

    def extract_political_entities(self, text: str) -> List[str]:
        """Extract political entities mentioned in text"""
        entities = []
        text_lower = text.lower()
        
        # Polish political figures
        if "morawiecki" in text_lower:
            entities.append("Mateusz Morawiecki")
        if "duda" in text_lower:
            entities.append("Andrzej Duda")
        if "kaczyński" in text_lower:
            entities.append("Jarosław Kaczyński")
        if "tusk" in text_lower:
            entities.append("Donald Tusk")
        if "hołownia" in text_lower:
            entities.append("Szymon Hołownia")
        
        # Ministries
        if "ministerstwo cyfryzacji" in text_lower or "ministry of digitalization" in text_lower:
            entities.append("Ministerstwo Cyfryzacji")
        if "ministerstwo infrastruktury" in text_lower:
            entities.append("Ministerstwo Infrastruktury")
        if "ministerstwo finansów" in text_lower:
            entities.append("Ministerstwo Finansów")
        
        # Political parties
        if "pis" in text_lower or "prawo i sprawiedliwość" in text_lower:
            entities.append("PiS")
        if "po" in text_lower or "platforma obywatelska" in text_lower:
            entities.append("PO")
        if "lewica" in text_lower:
            entities.append("Lewica")
        if "konfederacja" in text_lower:
            entities.append("Konfederacja")
        
        # EU entities
        if "von der leyen" in text_lower:
            entities.append("Ursula von der Leyen")
        if "european commission" in text_lower or "komisja europejska" in text_lower:
            entities.append("European Commission")
        if "european parliament" in text_lower or "parlament europejski" in text_lower:
            entities.append("European Parliament")
        
        return entities

    def categorize_political_impact(self, article: Dict[str, Any]) -> str:
        """Categorize the political impact level"""
        title = article.get("title", "").lower()
        snippet = article.get("snippet", "").lower()
        text = f"{title} {snippet}"
        
        # High impact indicators
        high_impact_keywords = [
            "ustawa", "law", "rozporządzenie", "regulation", "decyzja", "decision",
            "budżet", "budget", "reforma", "reform", "strategia", "strategy",
            "wybory", "elections", "głosowanie", "voting", "referendum"
        ]
        
        # Medium impact indicators
        medium_impact_keywords = [
            "projekt", "draft", "propozycja", "proposal", "konsultacje", "consultation",
            "plan", "program", "inwestycja", "investment", "infrastruktura", "infrastructure"
        ]
        
        if any(keyword in text for keyword in high_impact_keywords):
            return "high"
        elif any(keyword in text for keyword in medium_impact_keywords):
            return "medium"
        else:
            return "low"

    def extract_policy_areas(self, text: str) -> List[str]:
        """Extract policy areas mentioned in text"""
        areas = []
        text_lower = text.lower()
        
        if any(term in text_lower for term in ["5g", "5G", "sieć", "network", "infrastruktura"]):
            areas.append("5G Infrastructure")
        if any(term in text_lower for term in ["cyfryzacja", "digitalization", "digital", "cyfrowy"]):
            areas.append("Digitalization")
        if any(term in text_lower for term in ["konkurencja", "competition", "monopol", "monopoly"]):
            areas.append("Competition Policy")
        if any(term in text_lower for term in ["ochrona danych", "data protection", "gdpr", "rodo"]):
            areas.append("Data Protection")
        if any(term in text_lower for term in ["bezpieczeństwo", "security", "cybersecurity"]):
            areas.append("Cybersecurity")
        if any(term in text_lower for term in ["energia", "energy", "zielona", "green"]):
            areas.append("Green Technology")
        
        return areas

    async def scrape_government_policy(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape government policy developments"""
        queries = [
            "telecom policy Poland government",
            "telekomunikacja polityka rząd",
            "digital policy Poland",
            "cyfryzacja Polska rząd",
            "5G policy Poland",
            "telecom investment Poland government",
            "telecom infrastructure Poland policy"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_political_news(query, days_back)
            all_articles.extend(articles)
        
        processed_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article.get("link") not in seen_urls:
                article["category"] = "government_policy"
                article["impact_level"] = self.categorize_political_impact(article)
                article["entities"] = self.extract_political_entities(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["policy_areas"] = self.extract_policy_areas(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["scraped_at"] = datetime.now().isoformat()
                processed_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return processed_articles

    async def scrape_eu_policy(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape EU policy developments"""
        queries = [
            "EU telecom policy",
            "UE polityka telekomunikacja",
            "EU digital strategy",
            "EU 5G policy",
            "EU telecom regulation",
            "EU digital markets act",
            "EU telecom investment"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_political_news(query, days_back)
            all_articles.extend(articles)
        
        processed_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article.get("link") not in seen_urls:
                article["category"] = "eu_policy"
                article["impact_level"] = self.categorize_political_impact(article)
                article["entities"] = self.extract_political_entities(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["policy_areas"] = self.extract_policy_areas(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["scraped_at"] = datetime.now().isoformat()
                processed_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return processed_articles

    async def scrape_international_relations(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape international relations affecting telecom"""
        queries = [
            "telecom international relations Poland",
            "telekomunikacja stosunki międzynarodowe",
            "telecom trade Poland",
            "telecom cooperation Poland",
            "telecom security international",
            "telecom sanctions",
            "telecom export Poland",
            "telecom import Poland"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_political_news(query, days_back)
            all_articles.extend(articles)
        
        processed_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article.get("link") not in seen_urls:
                article["category"] = "international_relations"
                article["impact_level"] = self.categorize_political_impact(article)
                article["entities"] = self.extract_political_entities(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["policy_areas"] = self.extract_policy_areas(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["scraped_at"] = datetime.now().isoformat()
                processed_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return processed_articles

    async def scrape_all_political_news(self, days_back: int = 7) -> Dict[str, Any]:
        """Scrape all political news categories"""
        logger.info("Starting political news scraping...")
        
        # Run all political scrapers concurrently
        government_task = self.scrape_government_policy(days_back)
        eu_task = self.scrape_eu_policy(days_back)
        international_task = self.scrape_international_relations(days_back)
        
        government_news, eu_news, international_news = await asyncio.gather(
            government_task, eu_task, international_task
        )
        
        all_political_news = government_news + eu_news + international_news
        
        return {
            "government_policy": government_news,
            "eu_policy": eu_news,
            "international_relations": international_news,
            "all_political_news": all_political_news,
            "scraped_at": datetime.now().isoformat(),
            "total_articles": len(all_political_news),
            "high_impact_count": len([a for a in all_political_news if a.get("impact_level") == "high"]),
            "medium_impact_count": len([a for a in all_political_news if a.get("impact_level") == "medium"]),
            "low_impact_count": len([a for a in all_political_news if a.get("impact_level") == "low"])
        }

async def main():
    """Main function to run the political scraper"""
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        logger.error("SERPER_API_KEY environment variable not set")
        return
    
    scraper = PoliticalTelecomScraper(serper_api_key)
    political_data = await scraper.scrape_all_political_news(days_back=7)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"political_telecom_news_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(political_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Political scraping completed. Found {political_data['total_articles']} articles")
    logger.info(f"High impact: {political_data['high_impact_count']}, Medium: {political_data['medium_impact_count']}, Low: {political_data['low_impact_count']}")
    
    return political_data

if __name__ == "__main__":
    asyncio.run(main())
