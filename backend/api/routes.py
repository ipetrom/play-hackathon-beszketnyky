"""
API routes for the Telecom News Multi-Agent System
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from agents.workflow import telecom_workflow
from services.database_simple import create_user, get_user, update_user_settings, get_user_reports, create_report
from services.config import settings
from workflows.main_workflow import main_workflow
from services.s3_loader import load_report_from_s3
from services.pipeline_storage import pipeline_storage

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/pipeline/run")
async def run_pipeline(user_email: str, telecom_data: Dict[str, Any] = None, domains: List[str] = ["prawo", "polityka", "financial"]):
    """
    Run the complete pipeline using telecom news scraper data
    
    Args:
        user_email: User email for storage
        telecom_data: JSON data from telecom_news_scraper.py (optional)
        domains: List of domains to process
        
    Returns:
        Final comprehensive report with storage paths
    """
    try:
        logger.info(f"Starting pipeline with telecom data for domains: {domains}")
        
        # Load telecom data from S3 if not provided
        telecom_data = load_report_from_s3()
        
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
                
                print(f"\n\nPerplexity context for\n\n {domain}: {perplexity_context}")
                
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
        
        # Step 8: Store results in object storage and database
        storage_result = await pipeline_storage.store_pipeline_results(
            user_email, domain_reports, final_tips_alerts
        )
        
        return {
            "status": "success",
            "message": "Pipeline completed successfully",
            "domain_reports": domain_reports,
            "final_tips_alerts": final_tips_alerts,
            "storage_result": storage_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")




@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# ====== MAIN WORKFLOW ENDPOINTS ======

@router.post("/workflow/run")
async def run_main_workflow(user_email: str, days_back: int = 7):
    """Run the complete main workflow for a user"""
    try:
        logger.info(f"Starting main workflow for user: {user_email}")
        
        # Check if user exists
        user = get_user(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Run the complete workflow
        result = await main_workflow.run_complete_workflow(user_email, days_back)
        
        if result.get("status") == "success":
            return {
                "message": "Workflow completed successfully",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Workflow failed"))
        
    except Exception as e:
        logger.error(f"Main workflow failed: {e}")
        raise HTTPException(status_code=500, detail=f"Main workflow failed: {str(e)}")

# ====== USER MANAGEMENT ENDPOINTS ======

@router.post("/users")
async def create_or_login_user(user_data: Dict[str, Any]):
    """Create a new user or login existing user"""
    try:
        user_email = user_data.get("user_email")
        user_name = user_data.get("user_name")
        report_time = user_data.get("report_time", "09:00:00")
        report_delay_days = user_data.get("report_delay_days", 1)
        
        if not user_email or not user_name:
            raise HTTPException(status_code=400, detail="user_email and user_name are required")
        
        # Check if user already exists
        existing_user = get_user(user_email)
        if existing_user:
            # User exists, return user info (login)
            return {
                "message": "User logged in successfully",
                "user": existing_user,
                "user_email": user_email,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # User doesn't exist, create new user
        result = create_user(user_email, user_name, report_time, report_delay_days)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        # Get the newly created user
        new_user = get_user(user_email)
        
        return {
            "message": "User created successfully",
            "user": new_user,
            "user_email": user_email,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to create or login user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create or login user: {str(e)}")

@router.get("/users/{user_email}")
async def get_user_info(user_email: str):
    """Get user information"""
    try:
        user = get_user(user_email)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "message": "User retrieved successfully",
            "user": user,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@router.put("/users/{user_email}/settings")
async def update_user_preferences(user_email: str, settings_data: Dict[str, Any]):
    """Update user settings"""
    try:
        report_time = settings_data.get("report_time")
        report_delay_days = settings_data.get("report_delay_days")
        
        if report_time is None and report_delay_days is None:
            raise HTTPException(status_code=400, detail="At least one setting must be provided")
        
        result = update_user_settings(user_email, report_time, report_delay_days)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return {
            "message": "User settings updated successfully",
            "user_email": user_email,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update user settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update user settings: {str(e)}")

@router.get("/users/{user_email}/reports")
async def get_user_reports_endpoint(user_email: str, status: Optional[str] = None):
    """Get user reports"""
    try:
        reports = get_user_reports(user_email, status)
        
        return {
            "message": f"Reports retrieved for user {user_email}",
            "user_email": user_email,
            "reports": reports,
            "total_reports": len(reports),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get user reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user reports: {str(e)}")

@router.get("/reports")
async def get_all_reports(status: Optional[str] = None, limit: int = 50, offset: int = 0):
    """Get all reports from all users"""
    try:
        from services.database_simple import SessionLocal, Report
        
        session = SessionLocal()
        
        # Build query
        query = session.query(Report)
        if status:
            query = query.filter_by(report_status=status)
        
        # Apply pagination
        total_count = query.count()
        reports = query.order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
        
        session.close()
        
        # Convert to dict format
        reports_data = [
            {
                "report_id": str(report.report_id),
                "user_email": report.user_email,
                "report_date": report.report_date,
                "report_status": report.report_status,
                "report_domains": report.report_domains,
                "report_alerts": report.report_alerts,
                "report_tips": report.report_tips,
                "path_to_report": report.path_to_report,
                "report_alerts_tips_json_path": report.report_alerts_tips_json_path,
                "created_at": report.created_at
            }
            for report in reports
        ]
        
        return {
            "message": "All reports retrieved successfully",
            "reports": reports_data,
            "total_reports": total_count,
            "limit": limit,
            "offset": offset,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get all reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get all reports: {str(e)}")

@router.get("/reports/{report_id}")
def get_report_detail(report_id: str):
    """Get detailed report with domain synthesis files"""
    try:
        from services.database_simple import get_report
        from services.objest_storage import download_file
        
        logger.info(f"Getting report detail for ID: {report_id}")
        
        # Get report from database
        try:
            report = get_report(report_id)
            logger.info(f"Database query result: {report is not None}")
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
            
        if not report:
            logger.error(f"Report {report_id} not found in database")
            raise HTTPException(status_code=404, detail="Report not found")
        
        logger.info(f"Report found: {report['report_id']}, path: {report['path_to_report']}")
        
        # Load domain synthesis files if available
        domain_synthesis = {}
        
        # Try to load synthesis files from storage
        # The domain synthesis files are stored as: pipeline_reports/{user_email}/{timestamp}/domains/{domain}_synthesis.txt
        # We need to reconstruct the path from the report data
        
        if report['path_to_report']:
            # Extract the base path from the main report path
            # path_to_report is like: pipeline_reports/user@email.com/20251025_073929/merged_summary.txt
            # We need: pipeline_reports/user@email.com/20251025_073929/domains/
            base_path = report['path_to_report'].rsplit('/', 1)[0]  # Remove merged_summary.txt
            domains_path = f"{base_path}/domains"
            
        logger.info(f"Looking for domain synthesis files in: {domains_path}")
        
        # Try to load each domain synthesis file
        domains = ['prawo', 'polityka', 'financial']
        for domain in domains:
            synthesis_path = f"{domains_path}/{domain}_synthesis.txt"
            logger.info(f"Trying to load: {synthesis_path}")
            try:
                # Call download_file synchronously
                synthesis_content = download_file(synthesis_path)
                if synthesis_content:
                    domain_synthesis[domain] = synthesis_content
                    logger.info(f"✓ Loaded domain synthesis for {domain} ({len(synthesis_content)} chars)")
                else:
                    logger.warning(f"✗ No content found for domain synthesis: {domain}")
            except Exception as e:
                logger.warning(f"✗ Could not load domain synthesis for {domain} from {synthesis_path}: {e}")
                # Continue with other domains
        else:
            logger.warning("No path_to_report found for this report")
        
        logger.info(f"Final domain synthesis keys: {list(domain_synthesis.keys())}")
        
        # Load tips and alerts JSON if available
        tips_alerts = {}
        if report.get('report_alerts_tips_json_path'):
            tips_alerts_path = report['report_alerts_tips_json_path']
            logger.info(f"Loading tips and alerts from: {tips_alerts_path}")
            try:
                tips_alerts_content = download_file(tips_alerts_path)
                if tips_alerts_content:
                    import json
                    tips_alerts = json.loads(tips_alerts_content)
                    logger.info(f"✓ Loaded tips and alerts: {len(tips_alerts.get('tips', []))} tips, {len(tips_alerts.get('alerts', []))} alerts")
                else:
                    logger.warning("✗ No content found for tips and alerts")
            except Exception as e:
                logger.warning(f"✗ Could not load tips and alerts from {tips_alerts_path}: {e}")
        
        return {
            "message": "Report detail retrieved successfully",
            "report": report,
            "domain_synthesis": domain_synthesis,
            "tips_alerts": tips_alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get report detail: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get report detail: {str(e)}")

@router.get("/test-domain-synthesis/{report_id}")
def test_domain_synthesis(report_id: str):
    """Test endpoint to debug domain synthesis loading"""
    try:
        from services.database_simple import get_report
        from services.objest_storage import download_file
        
        logger.info(f"Testing domain synthesis for ID: {report_id}")
        
        # Get report from database
        report = get_report(report_id)
        if not report:
            return {"error": "Report not found"}
        
        # Load domain synthesis files
        domain_synthesis = {}
        
        if report['path_to_report']:
            base_path = report['path_to_report'].rsplit('/', 1)[0]
            domains_path = f"{base_path}/domains"
            
            domains = ['prawo', 'polityka', 'financial']
            for domain in domains:
                synthesis_path = f"{domains_path}/{domain}_synthesis.txt"
                try:
                    synthesis_content = download_file(synthesis_path)
                    if synthesis_content:
                        domain_synthesis[domain] = synthesis_content
                        logger.info(f"✓ Loaded {domain}: {len(synthesis_content)} chars")
                    else:
                        logger.warning(f"✗ No content for {domain}")
                except Exception as e:
                    logger.warning(f"✗ Error loading {domain}: {e}")
        
        return {
            "report_id": report_id,
            "path_to_report": report['path_to_report'],
            "domain_synthesis": domain_synthesis,
            "domain_count": len(domain_synthesis),
            "debug_info": {
                "base_path": report['path_to_report'].rsplit('/', 1)[0] if report['path_to_report'] else None,
                "domains_path": f"{report['path_to_report'].rsplit('/', 1)[0]}/domains" if report['path_to_report'] else None
            }
        }
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return {"error": str(e)}

@router.post("/reports/{report_id}/chat")
async def chat_with_report(report_id: str, chat_data: Dict[str, Any]):
    """Chat with report using Perplexity AI"""
    try:
        user_question = chat_data.get("question", "").strip()
        if not user_question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        # Get report from database to provide context
        from services.database_simple import get_report
        report = get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Create the prompt with the user's question
        prompt = f"""You are a research assistant specialized in the telecommunications domain.
Your task is to answer the user's question using the most recent, credible news sources available, ideally from the past 3–6 months.

The answer must be:
- Accurate and grounded in current events or industry developments
- Written in a clear, concise, and informative style
- Do NOT include any links, URLs, or source references just an answer.
- Do NOT include citations like [1], [2], etc.

---

User Query:
{user_question}"""
        
        # Use Perplexity service to get the answer
        from services.perplexity_service import perplexity_service
        response = await perplexity_service.get_answer(prompt)
        
        if response.get("status") != "success":
            raise HTTPException(status_code=500, detail="Failed to get AI response")
        
        return {
            "message": "Chat response generated successfully",
            "answer": response.get("answer", "Sorry, I couldn't generate a response."),
            "sources": response.get("sources", []),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to chat with report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to chat with report: {str(e)}")