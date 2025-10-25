"""
Financial News Scraper for Telecommunications
Specialized scraper for monitoring financial and market developments
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

class FinancialTelecomScraper:
    def __init__(self, serper_api_key: str):
        self.serper_api_key = serper_api_key
        self.base_url = "https://google.serper.dev/news"
        self.headers = {
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json"
        }
        
        # Financial news sources
        self.financial_sources = [
            "reuters.com/markets",
            "bloomberg.com/markets",
            "wsj.com/markets",
            "ft.com/markets",
            "cnbc.com",
            "marketwatch.com",
            "investing.com",
            "biznes.pap.pl",
            "rp.pl",
            "money.pl",
            "bankier.pl",
            "stooq.pl",
            "pulshr.pl",
            "nbp.pl",
            "ecb.europa.eu",
            "fred.stlouisfed.org",
            "imf.org",
            "bis.org",
            "oanda.com"
        ]
        
        # Financial keywords
        self.financial_keywords = [
            "akcje", "stocks", "giełda", "stock exchange", "kurs", "price", "cena",
            "cena", "price", "koszt", "cost", "przychód", "revenue", "dochód", "income",
            "zysk", "profit", "strata", "loss", "inwestycja", "investment", "kapitał", "capital",
            "finansowanie", "financing", "kredyt", "credit", "pożyczka", "loan",
            "fuzja", "merger", "przejęcie", "acquisition", "sprzedaż", "sale",
            "wyniki", "results", "raport", "report", "kwartał", "quarter",
            "roczny", "annual", "budżet", "budget", "wydatki", "expenses"
        ]

    async def search_financial_news(self, query: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Search for financial news using Serper API"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            search_query = f"{query} after:{start_date.strftime('%Y-%m-%d')} before:{end_date.strftime('%Y-%m-%d')}"
            
            # Add site restrictions for financial sources
            site_queries = " OR ".join([f"site:{source}" for source in self.financial_sources])
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
            logger.error(f"Error searching financial news: {e}")
            return []

    def is_financial_relevant(self, title: str, snippet: str) -> bool:
        """Check if article is financially relevant"""
        text = f"{title} {snippet}".lower()
        return any(keyword.lower() in text for keyword in self.financial_keywords)

    def extract_financial_entities(self, text: str) -> List[str]:
        """Extract financial entities mentioned in text"""
        entities = []
        text_lower = text.lower()
        
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
        if "cyfrowy polsat" in text_lower:
            entities.append("Cyfrowy Polsat")
        
        # Financial institutions
        if "nbp" in text_lower or "narodowy bank polski" in text_lower:
            entities.append("NBP")
        if "ecb" in text_lower or "european central bank" in text_lower:
            entities.append("ECB")
        if "imf" in text_lower or "international monetary fund" in text_lower:
            entities.append("IMF")
        if "bis" in text_lower or "bank for international settlements" in text_lower:
            entities.append("BIS")
        
        # Stock exchanges
        if "gpw" in text_lower or "giełda papierów wartościowych" in text_lower:
            entities.append("GPW")
        if "warsaw stock exchange" in text_lower:
            entities.append("Warsaw Stock Exchange")
        
        return entities

    def extract_financial_metrics(self, text: str) -> Dict[str, Any]:
        """Extract financial metrics from text"""
        metrics = {}
        text_lower = text.lower()
        
        # Revenue patterns
        revenue_patterns = [
            r"przychód[^0-9]*(\d+(?:[.,]\d+)?)\s*(?:mln|milion|mld|miliard|mln zł|milion zł|mld zł|miliard zł)",
            r"revenue[^0-9]*(\d+(?:[.,]\d+)?)\s*(?:mln|million|billion|mln zł|million zł|billion zł)"
        ]
        
        # Profit patterns
        profit_patterns = [
            r"zysk[^0-9]*(\d+(?:[.,]\d+)?)\s*(?:mln|milion|mld|miliard|mln zł|milion zł|mld zł|miliard zł)",
            r"profit[^0-9]*(\d+(?:[.,]\d+)?)\s*(?:mln|million|billion|mln zł|million zł|billion zł)"
        ]
        
        # Stock price patterns
        price_patterns = [
            r"kurs[^0-9]*(\d+(?:[.,]\d+)?)\s*zł",
            r"price[^0-9]*(\d+(?:[.,]\d+)?)\s*zł"
        ]
        
        import re
        
        for pattern in revenue_patterns:
            match = re.search(pattern, text_lower)
            if match:
                metrics["revenue"] = match.group(1)
                break
        
        for pattern in profit_patterns:
            match = re.search(pattern, text_lower)
            if match:
                metrics["profit"] = match.group(1)
                break
        
        for pattern in price_patterns:
            match = re.search(pattern, text_lower)
            if match:
                metrics["stock_price"] = match.group(1)
                break
        
        return metrics

    def categorize_financial_impact(self, article: Dict[str, Any]) -> str:
        """Categorize the financial impact level"""
        title = article.get("title", "").lower()
        snippet = article.get("snippet", "").lower()
        text = f"{title} {snippet}"
        
        # High impact indicators
        high_impact_keywords = [
            "bankructwo", "bankruptcy", "upadłość", "liquidation", "likwidacja",
            "fuzja", "merger", "przejęcie", "acquisition", "sprzedaż", "sale",
            "wyniki finansowe", "financial results", "raport roczny", "annual report",
            "dywidenda", "dividend", "wypłata", "payout"
        ]
        
        # Medium impact indicators
        medium_impact_keywords = [
            "inwestycja", "investment", "wydatki", "expenses", "koszty", "costs",
            "przychód", "revenue", "dochód", "income", "zysk", "profit",
            "akcje", "stocks", "giełda", "stock exchange"
        ]
        
        if any(keyword in text for keyword in high_impact_keywords):
            return "high"
        elif any(keyword in text for keyword in medium_impact_keywords):
            return "medium"
        else:
            return "low"

    async def scrape_telecom_earnings(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape telecom earnings and financial results"""
        queries = [
            "telecom earnings Poland",
            "telekomunikacja wyniki finansowe",
            "Orange wyniki",
            "Play wyniki",
            "Plus wyniki",
            "telecom revenue Poland",
            "telecom profit Poland",
            "telecom quarterly results"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_financial_news(query, days_back)
            all_articles.extend(articles)
        
        processed_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article.get("link") not in seen_urls:
                article["category"] = "earnings"
                article["impact_level"] = self.categorize_financial_impact(article)
                article["entities"] = self.extract_financial_entities(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["financial_metrics"] = self.extract_financial_metrics(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["scraped_at"] = datetime.now().isoformat()
                processed_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return processed_articles

    async def scrape_telecom_investments(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape telecom investment news"""
        queries = [
            "telecom investment Poland",
            "telekomunikacja inwestycja",
            "telecom infrastructure investment",
            "5G investment Poland",
            "telecom network investment",
            "telecom capital expenditure",
            "telecom funding Poland"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_financial_news(query, days_back)
            all_articles.extend(articles)
        
        processed_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article.get("link") not in seen_urls:
                article["category"] = "investments"
                article["impact_level"] = self.categorize_financial_impact(article)
                article["entities"] = self.extract_financial_entities(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["financial_metrics"] = self.extract_financial_metrics(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["scraped_at"] = datetime.now().isoformat()
                processed_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return processed_articles

    async def scrape_telecom_market_movements(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape telecom market movements and stock news"""
        queries = [
            "telecom stocks Poland",
            "telekomunikacja giełda",
            "telecom market Poland",
            "telecom stock price",
            "telecom trading Poland",
            "telecom shares Poland",
            "telecom equity Poland"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_financial_news(query, days_back)
            all_articles.extend(articles)
        
        processed_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article.get("link") not in seen_urls:
                article["category"] = "market_movements"
                article["impact_level"] = self.categorize_financial_impact(article)
                article["entities"] = self.extract_financial_entities(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["financial_metrics"] = self.extract_financial_metrics(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["scraped_at"] = datetime.now().isoformat()
                processed_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return processed_articles

    async def scrape_currency_rates(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape currency and economic indicators"""
        queries = [
            "PLN USD exchange rate",
            "kurs złoty dolar",
            "PLN EUR exchange rate", 
            "kurs złoty euro",
            "Polish zloty exchange rate",
            "NBP interest rate",
            "Polish central bank rate"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_financial_news(query, days_back)
            all_articles.extend(articles)
        
        processed_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article.get("link") not in seen_urls:
                article["category"] = "currency_rates"
                article["impact_level"] = self.categorize_financial_impact(article)
                article["entities"] = self.extract_financial_entities(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["financial_metrics"] = self.extract_financial_metrics(f"{article.get('title', '')} {article.get('snippet', '')}")
                article["scraped_at"] = datetime.now().isoformat()
                processed_articles.append(article)
                seen_urls.add(article.get("link"))
        
        return processed_articles

    async def scrape_all_financial_news(self, days_back: int = 7) -> Dict[str, Any]:
        """Scrape all financial news categories"""
        logger.info("Starting financial news scraping...")
        
        # Run all financial scrapers concurrently
        earnings_task = self.scrape_telecom_earnings(days_back)
        investments_task = self.scrape_telecom_investments(days_back)
        market_task = self.scrape_telecom_market_movements(days_back)
        currency_task = self.scrape_currency_rates(days_back)
        
        earnings_news, investments_news, market_news, currency_news = await asyncio.gather(
            earnings_task, investments_task, market_task, currency_task
        )
        
        all_financial_news = earnings_news + investments_news + market_news + currency_news
        
        return {
            "earnings": earnings_news,
            "investments": investments_news,
            "market_movements": market_news,
            "currency_rates": currency_news,
            "all_financial_news": all_financial_news,
            "scraped_at": datetime.now().isoformat(),
            "total_articles": len(all_financial_news),
            "high_impact_count": len([a for a in all_financial_news if a.get("impact_level") == "high"]),
            "medium_impact_count": len([a for a in all_financial_news if a.get("impact_level") == "medium"]),
            "low_impact_count": len([a for a in all_financial_news if a.get("impact_level") == "low"])
        }

async def main():
    """Main function to run the financial scraper"""
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        logger.error("SERPER_API_KEY environment variable not set")
        return
    
    scraper = FinancialTelecomScraper(serper_api_key)
    financial_data = await scraper.scrape_all_financial_news(days_back=7)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"financial_telecom_news_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(financial_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Financial scraping completed. Found {financial_data['total_articles']} articles")
    logger.info(f"High impact: {financial_data['high_impact_count']}, Medium: {financial_data['medium_impact_count']}, Low: {financial_data['low_impact_count']}")
    
    return financial_data

if __name__ == "__main__":
    asyncio.run(main())
