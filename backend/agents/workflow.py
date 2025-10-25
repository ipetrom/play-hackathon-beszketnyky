"""
Telecom Workflow Orchestrator
Coordinates all agents in the multi-agent system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from .serper_verification_agent import serper_verification_agent
from .keeper_agent import keeper_agent
from .writer_agent import writer_agent
from .final_summarizer_agent import final_summarizer_agent
from .tips_alerts_generator import tips_alerts_generator

from services.perplexity_service import perplexity_service

from services.http_client import serper_client, scraper_client
from services.database import store_search_results, store_agent_output, store_final_report, store_tips_alerts
from services.config import settings

logger = logging.getLogger(__name__)

class TelecomWorkflow:
    """Main workflow orchestrator for the telecom multi-agent system"""
    
    def __init__(self):
        self.name = "TelecomWorkflow"
        self.domains = settings.domains
        self.max_concurrent = settings.max_concurrent_agents
    
    async def run_full_workflow(self) -> Dict[str, Any]:
        """
        Run the complete multi-agent workflow for all domains
        
        Returns:
            Final tips and alerts JSON
        """
        try:
            logger.info("Starting full telecom workflow")
            start_time = datetime.utcnow()
            
            # Step 1: Process each domain in parallel
            domain_tasks = []
            for domain in self.domains:
                task = asyncio.create_task(self._process_domain(domain))
                domain_tasks.append(task)
            
            # Wait for all domains to complete
            domain_results = await asyncio.gather(*domain_tasks, return_exceptions=True)
            
            # Step 2: Collect successful domain reports
            successful_reports = {}
            for i, result in enumerate(domain_results):
                domain = self.domains[i]
                if isinstance(result, Exception):
                    logger.error(f"Domain {domain} processing failed: {result}")
                    successful_reports[domain] = self._create_fallback_domain_report(domain)
                else:
                    successful_reports[domain] = result
            
            # Step 3: Generate final tips and alerts
            final_tips_alerts = await tips_alerts_generator.generate_tips_alerts(successful_reports)
            
            # Step 4: Store results
            await store_tips_alerts(final_tips_alerts)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Full workflow completed in {execution_time:.2f} seconds")
            
            return {
                "workflow_id": f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "execution_time": execution_time,
                "domains_processed": len(successful_reports),
                "final_tips_alerts": final_tips_alerts,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Full workflow failed: {e}")
            return {
                "workflow_id": f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "execution_time": 0,
                "domains_processed": 0,
                "final_tips_alerts": {},
                "status": "error",
                "error": str(e)
            }
    
    async def _process_domain(self, domain: str) -> Dict[str, Any]:
        """
        Process a single domain through the complete workflow
        
        Args:
            domain: Target domain (prawo/polityka/financial)
            
        Returns:
            Final domain report
        """
        try:
            logger.info(f"Processing domain: {domain}")
            
            # Step 1: Search using Serper
            search_results = await self._search_domain(domain)
            if not search_results:
                logger.warning(f"No search results for domain: {domain}")
                return self._create_fallback_domain_report(domain)
            
            # Step 2: Verify results
            verified_urls = await serper_verification_agent.verify_results(search_results, domain)
            if not verified_urls:
                logger.warning(f"No verified URLs for domain: {domain}")
                return self._create_fallback_domain_report(domain)
            
            # Step 3: Scrape content
            scraped_content = await self._scrape_urls(verified_urls)
            if not scraped_content:
                logger.warning(f"No scraped content for domain: {domain}")
                return self._create_fallback_domain_report(domain)
            
            # Step 4: Process content with Keeper Agent
            keeper_outputs = await self._process_content_with_keeper(scraped_content, domain)
            if not keeper_outputs:
                logger.warning(f"No keeper outputs for domain: {domain}")
                return self._create_fallback_domain_report(domain)
            
            # Step 5: Aggregate with Writer Agent
            writer_report = await writer_agent.aggregate_domain(keeper_outputs, domain)
            if not writer_report or writer_report.get("status") != "success":
                logger.warning(f"Writer aggregation failed for domain: {domain}")
                return self._create_fallback_domain_report(domain)
            
            # Step 6: Get Perplexity context
            perplexity_context = await perplexity_service.get_domain_context(domain)
            if not perplexity_context or perplexity_context.get("status") != "success":
                logger.warning(f"Perplexity context failed for domain: {domain}")
                return self._create_fallback_domain_report(domain)
            
            # Step 7: Final synthesis
            final_report = await final_summarizer_agent.synthesize_domain_report(
                writer_report, perplexity_context, domain
            )
            
            # Store final report
            await store_final_report(domain, final_report)
            
            logger.info(f"Successfully processed domain: {domain}")
            return final_report
            
        except Exception as e:
            logger.error(f"Domain processing failed for {domain}: {e}")
            return self._create_fallback_domain_report(domain)
    
    async def _search_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """Search for domain-specific content using Serper"""
        try:
            # Create domain-specific search query
            query = self._create_domain_query(domain)
            
            # Perform search
            search_results = await serper_client.search(query, domain)
            
            # Store search results
            await store_search_results(domain, search_results.get("organic", []))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed for domain {domain}: {e}")
            return None
    
    def _create_domain_query(self, domain: str) -> str:
        """Create domain-specific search query"""
        base_queries = {
            "prawo": "Poland telecommunications law regulation UKE UOKiK 2025",
            "polityka": "Poland telecom policy government strategy 2025",
            "financial": "Poland telecom market financial results 2025"
        }
        
        return base_queries.get(domain, f"Poland telecommunications {domain} 2025")
    
    async def _scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape content from verified URLs"""
        try:
            # Limit concurrent scraping
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def scrape_with_semaphore(url):
                async with semaphore:
                    return await scraper_client.scrape_url(url)
            
            # Scrape all URLs concurrently
            tasks = [scrape_with_semaphore(url) for url in urls]
            scraped_content = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            successful_content = []
            for result in scraped_content:
                if isinstance(result, dict) and result.get("status") == "success":
                    successful_content.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Scraping failed: {result}")
            
            return successful_content
            
        except Exception as e:
            logger.error(f"URL scraping failed: {e}")
            return []
    
    async def _process_content_with_keeper(self, scraped_content: List[Dict[str, Any]], domain: str) -> List[Dict[str, Any]]:
        """Process scraped content with Keeper Agent"""
        try:
            keeper_outputs = []
            
            for content in scraped_content:
                if content.get("status") == "success":
                    keeper_output = await keeper_agent.process_content(content, domain)
                    keeper_outputs.append(keeper_output)
                    
                    # Store keeper output
                    await store_agent_output("keeper", domain, keeper_output)
            
            return keeper_outputs
            
        except Exception as e:
            logger.error(f"Keeper processing failed: {e}")
            return []
    
    def _create_fallback_domain_report(self, domain: str) -> Dict[str, Any]:
        """Create fallback domain report when processing fails"""
        return {
            "domain": domain,
            "generated_at": datetime.utcnow().isoformat(),
            "executive_summary": f"No data available for {domain} domain",
            "merged_analysis": f"Analysis unavailable for {domain} domain",
            "confidence": "low",
            "gaps_unknowns": [f"Monitor {domain} domain for new developments"],
            "evidence": [],
            "recommendations": [f"Monitor {domain} domain developments"],
            "sources": {
                "writer_sources": 0,
                "perplexity_confidence": "low"
            },
            "impact_assessment": {
                "dominant_impact_level": "low",
                "affected_parties": ["All"],
                "writer_impact": "low",
                "perplexity_impact": "low",
                "consensus": True
            },
            "status": "error"
        }
    
    async def run_domain_workflow(self, domain: str) -> Dict[str, Any]:
        """
        Run workflow for a single domain
        
        Args:
            domain: Target domain (prawo/polityka/financial)
            
        Returns:
            Domain report
        """
        try:
            logger.info(f"Running single domain workflow for: {domain}")
            
            if domain not in self.domains:
                raise ValueError(f"Unknown domain: {domain}")
            
            result = await self._process_domain(domain)
            return result
            
        except Exception as e:
            logger.error(f"Single domain workflow failed for {domain}: {e}")
            return self._create_fallback_domain_report(domain)
    
    async def get_domain_status(self, domain: str) -> Dict[str, Any]:
        """Get status of a specific domain"""
        try:
            # This would check the database for domain status
            # For now, return a simple status
            return {
                "domain": domain,
                "status": "available",
                "last_processed": datetime.utcnow().isoformat(),
                "next_scheduled": "TBD"
            }
            
        except Exception as e:
            logger.error(f"Failed to get domain status for {domain}: {e}")
            return {
                "domain": domain,
                "status": "error",
                "error": str(e)
            }

# Global workflow instance
telecom_workflow = TelecomWorkflow()
