"""
API routes for the Telecom News Multi-Agent System
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from agents.workflow import telecom_workflow
from services.database import get_final_report, get_tips_alerts, get_agent_output
from services.config import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/pipeline/run")
async def run_pipeline(telecom_data: Dict[str, Any], domains: List[str] = ["prawo", "polityka", "financial"]):
    """
    Run the complete pipeline using telecom news scraper data
    
    Args:
        telecom_data: JSON data from telecom_news_scraper.py
        domains: List of domains to process
        
    Returns:
        Final comprehensive report
    """
    try:
        logger.info(f"Starting pipeline with telecom data for domains: {domains}")
        
        # Process each domain through the pipeline
        domain_reports = {}
        
        for domain in domains:
            logger.info(f"Processing domain: {domain}")
            
            # Step 1: Verify articles using Serper Verification Agent
            from agents.serper_verification_agent import serper_verification_agent
            verified_urls = await serper_verification_agent.verify_results(telecom_data, domain)
            
            if not verified_urls:
                logger.warning(f"No verified URLs for domain: {domain} - using Perplexity-only report")
                
                # Step 5: Get Perplexity context (skip scraping and processing)
                from services.perplexity_service import perplexity_service
                perplexity_context = await perplexity_service.get_domain_context(domain)
                
                if not perplexity_context or perplexity_context.get("status") != "success":
                    logger.warning(f"Perplexity context failed for domain: {domain}")
                    domain_reports[domain] = {
                        "status": "no_data",
                        "message": f"No relevant articles found for {domain} domain and Perplexity failed"
                    }
                    continue
                
                # Step 6: Create Perplexity-only final report
                from agents.final_summarizer_agent import final_summarizer_agent
                final_report = await final_summarizer_agent.synthesize_domain_report(
                    None, perplexity_context, domain  # No writer report, only Perplexity
                )
                
                domain_reports[domain] = final_report
                continue
            
            # Step 2: Scrape content from verified URLs
            from services.http_client import scraper_client
            scraped_content = await telecom_workflow._scrape_urls(verified_urls)
            
            if not scraped_content:
                logger.warning(f"No scraped content for domain: {domain}")
                domain_reports[domain] = {
                    "status": "scraping_failed",
                    "message": f"Failed to scrape content for {domain} domain"
                }
                continue
            
            # Step 3: Process content with Keeper Agent
            from agents.keeper_agent import keeper_agent
            keeper_outputs = await telecom_workflow._process_content_with_keeper(scraped_content, domain)
            
            if not keeper_outputs:
                logger.warning(f"No keeper outputs for domain: {domain}")
                domain_reports[domain] = {
                    "status": "processing_failed",
                    "message": f"Failed to process content for {domain} domain"
                }
                continue
            
            # Step 4: Aggregate with Writer Agent
            from agents.writer_agent import writer_agent
            writer_report = await writer_agent.aggregate_domain(keeper_outputs, domain)
            
            if not writer_report or writer_report.get("status") != "success":
                logger.warning(f"Writer aggregation failed for domain: {domain}")
                domain_reports[domain] = {
                    "status": "aggregation_failed",
                    "message": f"Failed to aggregate content for {domain} domain"
                }
                continue
            
            # Step 5: Get Perplexity context
            from services.perplexity_service import perplexity_service
            perplexity_context = await perplexity_service.get_domain_context(domain)
            
            if not perplexity_context or perplexity_context.get("status") != "success":
                logger.warning(f"Perplexity context failed for domain: {domain}")
                domain_reports[domain] = {
                    "status": "context_failed",
                    "message": f"Failed to get context for {domain} domain"
                }
                continue
            
            # Step 6: Final synthesis
            from agents.final_summarizer_agent import final_summarizer_agent
            final_report = await final_summarizer_agent.synthesize_domain_report(
                writer_report, perplexity_context, domain
            )
            
            domain_reports[domain] = final_report
        
        # Step 7: Generate final tips and alerts
        from agents.tips_alerts_generator import tips_alerts_generator
        final_tips_alerts = await tips_alerts_generator.generate_tips_alerts(domain_reports)
        
        return {
            "status": "success",
            "message": "Pipeline completed successfully",
            "domain_reports": domain_reports,
            "final_tips_alerts": final_tips_alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@router.get("/reports")
async def get_all_reports():
    """Get all available domain reports"""
    try:
        reports = {}
        
        for domain in settings.domains:
            report = await get_final_report(domain)
            if report:
                reports[domain] = report
        
        return {
            "message": "All reports retrieved",
            "reports": reports,
            "total_domains": len(reports),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get all reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reports: {str(e)}")


@router.get("/tips-alerts")
async def get_tips_alerts():
    """Get final tips and alerts"""
    try:
        tips_alerts = await get_tips_alerts()
        
        if not tips_alerts:
            return {
                "message": "No tips and alerts available",
                "status": "not_found",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "message": "Tips and alerts retrieved",
            "tips_alerts": tips_alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get tips and alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tips and alerts: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }