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

@router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Telecom News Multi-Agent System API",
        "version": "1.0.0",
        "endpoints": {
            "workflow": "/workflow",
            "domains": "/domains",
            "reports": "/reports",
            "tips_alerts": "/tips-alerts",
            "status": "/status"
        }
    }

@router.post("/workflow/run")
async def run_full_workflow(background_tasks: BackgroundTasks):
    """Run the complete multi-agent workflow for all domains"""
    try:
        logger.info("Starting full workflow via API")
        
        # Run workflow in background
        result = await telecom_workflow.run_full_workflow()
        
        return {
            "message": "Full workflow completed",
            "workflow_id": result.get("workflow_id"),
            "execution_time": result.get("execution_time"),
            "domains_processed": result.get("domains_processed"),
            "status": result.get("status"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Full workflow API call failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

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

@router.post("/workflow/domain/{domain}")
async def run_domain_workflow(domain: str):
    """Run workflow for a specific domain"""
    try:
        if domain not in settings.domains:
            raise HTTPException(status_code=400, detail=f"Unknown domain: {domain}")
        
        logger.info(f"Running domain workflow for: {domain}")
        
        result = await telecom_workflow.run_domain_workflow(domain)
        
        return {
            "message": f"Domain workflow completed for {domain}",
            "domain": domain,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Domain workflow API call failed for {domain}: {e}")
        raise HTTPException(status_code=500, detail=f"Domain workflow failed: {str(e)}")

@router.get("/domains")
async def get_domains():
    """Get available domains"""
    return {
        "domains": settings.domains,
        "description": "Available domains for analysis",
        "total": len(settings.domains)
    }

@router.get("/domains/{domain}/status")
async def get_domain_status(domain: str):
    """Get status of a specific domain"""
    try:
        if domain not in settings.domains:
            raise HTTPException(status_code=400, detail=f"Unknown domain: {domain}")
        
        status = await telecom_workflow.get_domain_status(domain)
        return status
        
    except Exception as e:
        logger.error(f"Failed to get domain status for {domain}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get domain status: {str(e)}")

@router.get("/reports/{domain}")
async def get_domain_report(domain: str):
    """Get final report for a specific domain"""
    try:
        if domain not in settings.domains:
            raise HTTPException(status_code=400, detail=f"Unknown domain: {domain}")
        
        report = await get_final_report(domain)
        
        if not report:
            return {
                "message": f"No report available for domain: {domain}",
                "domain": domain,
                "status": "not_found"
            }
        
        return {
            "message": f"Report retrieved for domain: {domain}",
            "domain": domain,
            "report": report,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get domain report for {domain}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get domain report: {str(e)}")

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

@router.get("/agents/{agent_name}/output/{domain}")
async def get_agent_output(agent_name: str, domain: str):
    """Get output from a specific agent for a domain"""
    try:
        if domain not in settings.domains:
            raise HTTPException(status_code=400, detail=f"Unknown domain: {domain}")
        
        output = await get_agent_output(agent_name, domain)
        
        if not output:
            return {
                "message": f"No output available for agent {agent_name} and domain {domain}",
                "agent": agent_name,
                "domain": domain,
                "status": "not_found"
            }
        
        return {
            "message": f"Agent output retrieved for {agent_name} and domain {domain}",
            "agent": agent_name,
            "domain": domain,
            "output": output,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent output for {agent_name} and {domain}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent output: {str(e)}")

@router.get("/status")
async def get_system_status():
    """Get overall system status"""
    try:
        # Check domain statuses
        domain_statuses = {}
        for domain in settings.domains:
            status = await telecom_workflow.get_domain_status(domain)
            domain_statuses[domain] = status.get("status", "unknown")
        
        # Check if tips and alerts are available
        tips_alerts = await get_tips_alerts()
        tips_alerts_available = tips_alerts is not None
        
        return {
            "system_status": "operational",
            "domains": domain_statuses,
            "tips_alerts_available": tips_alerts_available,
            "total_domains": len(settings.domains),
            "active_domains": len([s for s in domain_statuses.values() if s == "available"]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Additional utility endpoints

@router.get("/search/{domain}")
async def search_domain(domain: str, query: Optional[str] = None):
    """Search for content in a specific domain"""
    try:
        if domain not in settings.domains:
            raise HTTPException(status_code=400, detail=f"Unknown domain: {domain}")
        
        # This would trigger a search for the domain
        # For now, return a placeholder
        return {
            "message": f"Search initiated for domain: {domain}",
            "domain": domain,
            "query": query or f"Poland telecommunications {domain} 2025",
            "status": "search_initiated",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Search failed for domain {domain}: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/analytics")
async def get_analytics():
    """Get system analytics and metrics"""
    try:
        # This would provide analytics about the system
        # For now, return basic metrics
        return {
            "message": "Analytics retrieved",
            "metrics": {
                "total_domains": len(settings.domains),
                "system_uptime": "N/A",
                "last_workflow_run": "N/A",
                "total_reports_generated": "N/A"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")
