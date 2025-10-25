"""
Email service for sending reports to users
"""

import aiosmtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from datetime import datetime
import json

from .config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name
    
    async def send_report_email(
        self, 
        user_email: str, 
        user_name: str,
        domain_reports: Dict[str, Any],
        tips_alerts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send pipeline report to user's email
        
        Args:
            user_email: User's email address
            user_name: User's name
            domain_reports: Domain reports data
            tips_alerts: Tips and alerts data
            
        Returns:
            Dict with status and message
        """
        try:
            logger.info(f"Sending report email to {user_email}")

            html_content = self._create_html_report(
                user_name, domain_reports, tips_alerts
            )

            message = MIMEMultipart("alternative")
            message["Subject"] = f"Telecom News Report - {datetime.now().strftime('%Y-%m-%d')}"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = user_email

            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            
            logger.info(f"Report email sent successfully to {user_email}")
            return {
                "status": "success",
                "message": f"Report sent to {user_email}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {user_email}: {e}")
            return {
                "status": "error",
                "message": f"Failed to send email: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _create_html_report(
        self, 
        user_name: str,
        domain_reports: Dict[str, Any],
        tips_alerts: Dict[str, Any]
    ) -> str:
        """Create HTML email content"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .domain-title {{ color: #4CAF50; font-size: 18px; font-weight: bold; margin-top: 20px; }}
                .alert {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }}
                .tip {{ background-color: #d1ecf1; padding: 10px; border-left: 4px solid #17a2b8; margin: 10px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Telecom News Report</h1>
                    <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                
                <div class="section">
                    <h2>Hello, {user_name}!</h2>
                    <p>Here is your latest telecom news report covering legal, political, and financial developments.</p>
                </div>
        """

        for domain, report in domain_reports.items():
            if report.get("status") == "success":
                html += f"""
                <div class="section">
                    <div class="domain-title">{domain.upper()} Domain</div>
                    <p>{report.get('summary', 'No summary available')}</p>
                </div>
                """

        if tips_alerts and tips_alerts.get("status") == "success":
            html += """
            <div class="section">
                <h2>Tips & Alerts</h2>
            """
            
            alerts = tips_alerts.get("alerts", [])
            for alert in alerts:
                html += f"""
                <div class="alert">
                    <strong>{alert.get('title', 'Alert')}</strong><br>
                    {alert.get('description', '')}
                </div>
                """
            
            tips = tips_alerts.get("tips", [])
            for tip in tips:
                html += f"""
                <div class="tip">
                    <strong>{tip.get('title', 'Tip')}</strong><br>
                    {tip.get('description', '')}
                </div>
                """
            
            html += "</div>"

        html += """
                <div class="footer">
                    <p>This is an automated report from Telecom News Multi-Agent System</p>
                    <p>To update your preferences, please visit your account settings</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

email_service = EmailService()