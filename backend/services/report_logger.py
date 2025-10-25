"""
Report Logger Service
Logs final outputs from agents to text files
"""

import logging
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportLogger:
    """Service for logging final agent outputs to text files"""
    
    def __init__(self):
        self.name = "ReportLogger"
        self.logs_dir = "logs"
        self._ensure_logs_directory()
    
    def _ensure_logs_directory(self):
        """Ensure logs directory exists"""
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            logger.info(f"Created logs directory: {self.logs_dir}")
    
    def log_final_summarizer_output(self, domain: str, report: Dict[str, Any]) -> str:
        """
        Log final summarizer agent output to text file
        
        Args:
            domain: Domain name (prawo/polityka/financial)
            report: Final summarizer report
            
        Returns:
            Path to the saved file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"final_summarizer_{domain}_{timestamp}.txt"
            filepath = os.path.join(self.logs_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"FINAL SUMMARIZER REPORT - {domain.upper()}\n")
                f.write(f"Generated at: {report.get('generated_at', 'Unknown')}\n")
                f.write(f"Status: {report.get('status', 'Unknown')}\n")
                f.write("=" * 80 + "\n\n")
                
                # Plain Text Synthesis
                f.write("SYNTHESIS REPORT:\n")
                f.write("-" * 40 + "\n")
                f.write(f"{report.get('synthesis', 'No synthesis available')}\n\n")
                
                # Sources
                f.write("SOURCES:\n")
                f.write("-" * 40 + "\n")
                sources = report.get('sources', {})
                f.write(f"Writer Sources: {sources.get('writer_sources', 0)}\n")
                f.write(f"Perplexity Confidence: {sources.get('perplexity_confidence', 'Unknown')}\n\n")
            
            logger.info(f"Final summarizer output logged to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to log final summarizer output: {e}")
            return ""
    
    def log_tips_alerts_output(self, tips_alerts: Dict[str, Any]) -> Optional[str]:
        """
        Log tips and alerts generator output to JSON file
        
        Args:
            tips_alerts: Tips and alerts report
            
        Returns:
            Path to the saved file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tips_alerts_{timestamp}.json"
            filepath = os.path.join(self.logs_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tips_alerts, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Tips and alerts output logged to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to log tips and alerts output: {e}")
            return None

# Global service instance
report_logger = ReportLogger()
