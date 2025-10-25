"""
Legal/Regulatory News Scraper for Telecommunications
Specialized scraper for monitoring legal and regulatory developments
affecting the telecommunications industry in Poland and EU.
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

class LegalTelecomScraper:
    def __init__(self, serper_api_key: str):
        self.serper_api_key = serper_api_key
        self.base_url = "https://google.serper.dev/news"
        self.headers = {
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json"
        }
        
        # Legal and regulatory sources
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
            "oecd.org",
            "eur-lex.europa.eu",
            "curia.europa.eu"
        ]
        
        # Legal-specific keywords
        self.legal_keywords = [
            "ustawa", "law", "act", "rozporządzenie", "regulation", "dyrektywa", "directive",
            "decyzja", "decision", "orzeczenie", "judgment", "wyrok", "sentence",
            "regulacja", "regulation", "regulator", "UKE", "UOKiK", "BEREC",
            "spectrum", "widmo", "frequency", "częstotliwość", "licencja", "license",
            "koncesja", "concession", "przetarg", "tender", "aukcja", "auction",
            "konkurencja", "competition", "monopol", "monopoly", "fuzja", "merger",
            "przejęcie", "acquisition", "sankcje", "sanctions", "kara", "penalty",
            "odszkodowanie", "compensation", "odpowiedzialność", "liability"
        ]

    async def search_legal_news(self, query: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Search for legal news using Serper API"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            search_query = f"{query} after:{start_date.strftime('%Y-%m-%d')} before:{end_date.strftime('%Y-%m-%d')}"
            
            # Add site restrictions for legal sources
            site_queries = " OR ".join([f"site:{source}" for source in self.legal_sources])
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
            logger.error(f"Error searching legal news: {e}")
            return []

    def is_legal_relevant(self, title: str, snippet: str) -> bool:
        """Check if article is legally relevant to telecommunications"""
        text = f"{title} {snippet}".lower()
        
        # Must contain both legal AND telecom keywords
        has_legal_keyword = any(keyword.lower() in text for keyword in self.legal_keywords)
        
        # Telecom-specific keywords for better filtering
        telecom_keywords = [
            "telekomunikacja", "telecom", "telefonia", "telephony", "internet", "broadband",
            "5g", "4g", "lte", "mobile", "mobilny", "sieć", "network", "operator", "dostawca",
            "provider", "abonament", "subscription", "roaming", "infrastruktura", "infrastructure",
            "spectrum", "widmo", "frequency", "częstotliwość", "antenna", "antena", "base station",
            "stacja bazowa", "orange", "play", "plus", "t-mobile", "vodafone", "cyfrowy polsat"
        ]
        
        has_telecom_keyword = any(keyword.lower() in text for keyword in telecom_keywords)
        
        return has_legal_keyword and has_telecom_keyword

    def extract_legal_entities(self, text: str) -> List[str]:
        """Extract legal entities mentioned in text"""
        entities = []
        text_lower = text.lower()
        
        # Government entities
        if "uke" in text_lower or "urząd komunikacji elektronicznej" in text_lower:
            entities.append("UKE")
        if "uokik" in text_lower or "urząd ochrony konkurencji" in text_lower:
            entities.append("UOKiK")
        if "berec" in text_lower:
            entities.append("BEREC")
        if "sejm" in text_lower:
            entities.append("Sejm")
        if "senat" in text_lower:
            entities.append("Senat")
        if "prezydent" in text_lower:
            entities.append("Prezydent")
        if "rząd" in text_lower or "government" in text_lower:
            entities.append("Rząd")
        
        # Telecom operators
        if "orange" in text_lower:
            entities.append("Orange")
        if "play" in text_lower:
            entities.append("Play")
        if "plus" in text_lower:
            entities.append("Plus")
        if "t-mobile" in text_lower or "tmobile" in text_lower:
            entities.append("T-Mobile")
        if "vodafone" in text_lower:
            entities.append("Vodafone")
        
        return entities

    def categorize_legal_impact(self, article: Dict[str, Any]) -> str:
        """Categorize the legal impact level"""
        title = article.get("title", "").lower()
        snippet = article.get("snippet", "").lower()
        text = f"{title} {snippet}"
        
        # High impact indicators
        high_impact_keywords = [
            "ustawa", "law", "rozporządzenie", "regulation", "dyrektywa", "directive",
            "decyzja uke", "uke decision", "kara", "penalty", "sankcje", "sanctions"
        ]
        
        # Medium impact indicators  
        medium_impact_keywords = [
            "konsultacje", "consultation", "projekt", "draft", "propozycja", "proposal",
            "przetarg", "tender", "aukcja", "auction", "licencja", "license"
        ]
        
        if any(keyword in text for keyword in high_impact_keywords):
            return "high"
        elif any(keyword in text for keyword in medium_impact_keywords):
            return "medium"
        else:
            return "low"

    async def scrape_uke_decisions(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape UKE (telecom regulator) decisions"""
        queries = [
            "UKE decyzja telekomunikacja",
            "UKE decision telecommunications", 
            "urząd komunikacji elektronicznej decyzja",
            "UKE spectrum allocation",
            "UKE frequency assignment",
            "UKE Orange Play Plus",
            "UKE operator telekomunikacyjny",
            "UKE 5G spectrum",
            "UKE roaming",
            "UKE abonament"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_legal_news(query, days_back)
            all_articles.extend(articles)
        
        # Process and enrich articles
        processed_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article.get("link") not in seen_urls:
                article["category"] = "uke_decision"
                article["impact_level"] = self.categorize_legal_impact(article)
                article["entities"] = self.extract_legal_entities(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["scraped_at"] = datetime.now().isoformat()
                processed_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return processed_articles

    async def scrape_competition_law(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape competition law developments"""
        queries = [
            "UOKiK telekomunikacja",
            "UOKiK telecommunications",
            "konkurencja telekomunikacja",
            "competition telecom",
            "telecom merger Poland",
            "telecom acquisition Poland",
            "telecom monopoly Poland",
            "UOKiK Orange Play Plus",
            "konkurencja operator telekomunikacyjny",
            "telecom antitrust Poland",
            "telecom cartel Poland",
            "telecom market abuse Poland"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_legal_news(query, days_back)
            all_articles.extend(articles)
        
        processed_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article.get("link") not in seen_urls:
                article["category"] = "competition_law"
                article["impact_level"] = self.categorize_legal_impact(article)
                article["entities"] = self.extract_legal_entities(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["scraped_at"] = datetime.now().isoformat()
                processed_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return processed_articles

    async def scrape_eu_regulations(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape EU regulatory developments"""
        queries = [
            "EU telecom regulation",
            "UE regulacja telekomunikacja",
            "BEREC decision",
            "EU digital strategy",
            "EU 5G regulation",
            "EU spectrum policy",
            "digital markets act telecom",
            "EU telecom directive",
            "EU telecom law",
            "EU roaming regulation",
            "EU net neutrality",
            "EU telecom market",
            "EU telecom competition"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_legal_news(query, days_back)
            all_articles.extend(articles)
        
        processed_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article.get("link") not in seen_urls:
                article["category"] = "eu_regulation"
                article["impact_level"] = self.categorize_legal_impact(article)
                article["entities"] = self.extract_legal_entities(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["scraped_at"] = datetime.now().isoformat()
                processed_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return processed_articles

    async def scrape_all_legal_news(self, days_back: int = 7) -> Dict[str, Any]:
        """Scrape all legal news categories"""
        logger.info("Starting legal news scraping...")
        
        # Run all legal scrapers concurrently
        uke_task = self.scrape_uke_decisions(days_back)
        competition_task = self.scrape_competition_law(days_back)
        eu_task = self.scrape_eu_regulations(days_back)
        
        uke_news, competition_news, eu_news = await asyncio.gather(
            uke_task, competition_task, eu_task
        )
        
        all_legal_news = uke_news + competition_news + eu_news
        
        return {
            "uke_decisions": uke_news,
            "competition_law": competition_news,
            "eu_regulations": eu_news,
            "all_legal_news": all_legal_news,
            "scraped_at": datetime.now().isoformat(),
            "total_articles": len(all_legal_news),
            "high_impact_count": len([a for a in all_legal_news if a.get("impact_level") == "high"]),
            "medium_impact_count": len([a for a in all_legal_news if a.get("impact_level") == "medium"]),
            "low_impact_count": len([a for a in all_legal_news if a.get("impact_level") == "low"])
        }

async def main():
    """Main function to run the legal scraper"""
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        logger.error("SERPER_API_KEY environment variable not set")
        return
    
    scraper = LegalTelecomScraper(serper_api_key)
    legal_data = await scraper.scrape_all_legal_news(days_back=7)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"legal_telecom_news_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(legal_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Legal scraping completed. Found {legal_data['total_articles']} articles")
    logger.info(f"High impact: {legal_data['high_impact_count']}, Medium: {legal_data['medium_impact_count']}, Low: {legal_data['low_impact_count']}")
    
    return legal_data

if __name__ == "__main__":
    asyncio.run(main())
