"""
Report Generator for Telecommunications Intelligence
Generates comprehensive weekly and daily reports from scraped news data.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TelecomReportGenerator:
    def __init__(self):
        self.report_templates = {
            "weekly": {
                "title": "Weekly Telecommunications Intelligence Report",
                "sections": ["executive_summary", "legal_developments", "political_developments", 
                           "financial_developments", "key_insights", "risk_assessment", "action_items"]
            },
            "daily": {
                "title": "Daily Telecommunications Intelligence Brief",
                "sections": ["executive_summary", "top_stories", "market_impact", "regulatory_updates"]
            }
        }

    def generate_executive_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary"""
        total_articles = data.get("total_articles", 0)
        high_impact = data.get("high_impact_count", 0)
        medium_impact = data.get("medium_impact_count", 0)
        
        summary = f"""
        This week's telecommunications intelligence report covers {total_articles} relevant articles
        across legal, political, and financial domains. Key findings include {high_impact} high-impact
        developments and {medium_impact} medium-impact items that require attention.
        
        The telecommunications sector continues to evolve rapidly with significant regulatory,
        political, and financial developments affecting market dynamics in Poland and the EU.
        """
        
        return summary.strip()

    def analyze_legal_developments(self, legal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze legal developments"""
        developments = {
            "uke_decisions": len(legal_data.get("uke_decisions", [])),
            "competition_law": len(legal_data.get("competition_law", [])),
            "eu_regulations": len(legal_data.get("eu_regulations", [])),
            "high_impact_items": [],
            "key_entities": [],
            "regulatory_trends": []
        }
        
        # Extract high-impact items
        all_legal = legal_data.get("all_legal_news", [])
        high_impact_items = [item for item in all_legal if item.get("impact_level") == "high"]
        developments["high_impact_items"] = high_impact_items[:5]  # Top 5
        
        # Extract key entities
        entities = set()
        for item in all_legal:
            entities.update(item.get("entities", []))
        developments["key_entities"] = list(entities)[:10]
        
        # Identify regulatory trends
        if developments["uke_decisions"] > 3:
            developments["regulatory_trends"].append("Increased UKE regulatory activity")
        if developments["eu_regulations"] > 2:
            developments["regulatory_trends"].append("EU regulatory developments affecting telecom")
        if developments["competition_law"] > 1:
            developments["regulatory_trends"].append("Competition law enforcement in telecom sector")
        
        return developments

    def analyze_political_developments(self, political_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze political developments"""
        developments = {
            "government_policy": len(political_data.get("government_policy", [])),
            "eu_policy": len(political_data.get("eu_policy", [])),
            "international_relations": len(political_data.get("international_relations", [])),
            "high_impact_items": [],
            "key_entities": [],
            "policy_trends": []
        }
        
        # Extract high-impact items
        all_political = political_data.get("all_political_news", [])
        high_impact_items = [item for item in all_political if item.get("impact_level") == "high"]
        developments["high_impact_items"] = high_impact_items[:5]
        
        # Extract key entities
        entities = set()
        for item in all_political:
            entities.update(item.get("entities", []))
        developments["key_entities"] = list(entities)[:10]
        
        # Identify policy trends
        if developments["government_policy"] > 2:
            developments["policy_trends"].append("Active government policy development")
        if developments["eu_policy"] > 1:
            developments["policy_trends"].append("EU policy developments affecting telecom")
        if developments["international_relations"] > 1:
            developments["policy_trends"].append("International telecom relations activity")
        
        return developments

    def analyze_financial_developments(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial developments"""
        developments = {
            "earnings": len(financial_data.get("earnings", [])),
            "investments": len(financial_data.get("investments", [])),
            "market_movements": len(financial_data.get("market_movements", [])),
            "currency_rates": len(financial_data.get("currency_rates", [])),
            "high_impact_items": [],
            "key_entities": [],
            "market_trends": []
        }
        
        # Extract high-impact items
        all_financial = financial_data.get("all_financial_news", [])
        high_impact_items = [item for item in all_financial if item.get("impact_level") == "high"]
        developments["high_impact_items"] = high_impact_items[:5]
        
        # Extract key entities
        entities = set()
        for item in all_financial:
            entities.update(item.get("entities", []))
        developments["key_entities"] = list(entities)[:10]
        
        # Identify market trends
        if developments["earnings"] > 2:
            developments["market_trends"].append("Active earnings reporting season")
        if developments["investments"] > 1:
            developments["market_trends"].append("Significant investment activity in telecom")
        if developments["market_movements"] > 1:
            developments["market_trends"].append("Telecom stock market activity")
        
        return developments

    def generate_risk_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk assessment"""
        risks = {
            "regulatory_risks": [],
            "market_risks": [],
            "political_risks": [],
            "overall_risk_level": "medium"
        }
        
        # Analyze regulatory risks
        legal_data = data.get("legal", {})
        if legal_data.get("high_impact_count", 0) > 3:
            risks["regulatory_risks"].append("High regulatory activity - increased compliance requirements")
        if legal_data.get("uke_decisions", 0) > 2:
            risks["regulatory_risks"].append("UKE regulatory decisions may impact operations")
        
        # Analyze market risks
        financial_data = data.get("financial", {})
        if financial_data.get("high_impact_count", 0) > 2:
            risks["market_risks"].append("Significant financial developments affecting market stability")
        if financial_data.get("currency_rates", 0) > 1:
            risks["market_risks"].append("Currency fluctuations may impact international operations")
        
        # Analyze political risks
        political_data = data.get("polityka", {})
        if political_data.get("high_impact_count", 0) > 2:
            risks["political_risks"].append("High political activity may affect policy direction")
        
        # Determine overall risk level
        total_high_impact = (legal_data.get("high_impact_count", 0) + 
                           financial_data.get("high_impact_count", 0) + 
                           political_data.get("high_impact_count", 0))
        
        if total_high_impact > 5:
            risks["overall_risk_level"] = "high"
        elif total_high_impact > 2:
            risks["overall_risk_level"] = "medium"
        else:
            risks["overall_risk_level"] = "low"
        
        return risks

    def generate_action_items(self, data: Dict[str, Any]) -> List[str]:
        """Generate actionable items"""
        actions = []
        
        # Legal actions
        legal_data = data.get("legal", {})
        if legal_data.get("high_impact_count", 0) > 0:
            actions.append("Review high-impact legal developments for compliance implications")
        if legal_data.get("uke_decisions", 0) > 0:
            actions.append("Monitor UKE decisions for regulatory impact")
        
        # Political actions
        political_data = data.get("polityka", {})
        if political_data.get("high_impact_count", 0) > 0:
            actions.append("Assess political developments for policy impact")
        if political_data.get("government_policy", 0) > 0:
            actions.append("Monitor government policy developments")
        
        # Financial actions
        financial_data = data.get("financial", {})
        if financial_data.get("high_impact_count", 0) > 0:
            actions.append("Analyze financial developments for market impact")
        if financial_data.get("earnings", 0) > 0:
            actions.append("Review competitor earnings for market positioning")
        
        # General actions
        total_articles = data.get("total_articles", 0)
        if total_articles > 20:
            actions.append("Schedule comprehensive market analysis meeting")
        if total_articles > 10:
            actions.append("Update strategic planning based on intelligence")
        
        return actions[:10]  # Limit to top 10 actions

    def generate_weekly_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive weekly report"""
        report = {
            "report_metadata": {
                "title": "Weekly Telecommunications Intelligence Report",
                "generated_at": datetime.now().isoformat(),
                "period": "Last 7 days",
                "total_articles": data.get("total_articles", 0)
            },
            "executive_summary": self.generate_executive_summary(data),
            "legal_developments": self.analyze_legal_developments(data.get("legal", {})),
            "political_developments": self.analyze_political_developments(data.get("polityka", {})),
            "financial_developments": self.analyze_financial_developments(data.get("financial", {})),
            "risk_assessment": self.generate_risk_assessment(data),
            "action_items": self.generate_action_items(data),
            "key_insights": self.generate_key_insights(data),
            "raw_data": data
        }
        
        return report

    def generate_key_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate key insights"""
        insights = []
        
        # Legal insights
        legal_data = data.get("legal", {})
        if legal_data.get("high_impact_count", 0) > 0:
            insights.append(f"High-impact legal developments detected: {legal_data.get('high_impact_count', 0)} items require immediate attention")
        
        # Political insights
        political_data = data.get("polityka", {})
        if political_data.get("high_impact_count", 0) > 0:
            insights.append(f"Significant political developments: {political_data.get('high_impact_count', 0)} high-impact items affecting telecom policy")
        
        # Financial insights
        financial_data = data.get("financial", {})
        if financial_data.get("high_impact_count", 0) > 0:
            insights.append(f"Major financial developments: {financial_data.get('high_impact_count', 0)} high-impact items affecting market dynamics")
        
        # Cross-domain insights
        total_high_impact = (legal_data.get("high_impact_count", 0) + 
                           political_data.get("high_impact_count", 0) + 
                           financial_data.get("high_impact_count", 0))
        
        if total_high_impact > 5:
            insights.append("Multiple high-impact developments across all domains - comprehensive strategic review recommended")
        elif total_high_impact > 2:
            insights.append("Moderate high-impact activity - targeted monitoring recommended")
        else:
            insights.append("Low high-impact activity - standard monitoring sufficient")
        
        return insights

    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"telecom_intelligence_report_{timestamp}.json"
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        filepath = os.path.join("reports", filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Report saved to {filepath}")
        return filepath

    def generate_summary_text(self, report: Dict[str, Any]) -> str:
        """Generate human-readable summary text"""
        summary = f"""
# {report['report_metadata']['title']}
Generated: {report['report_metadata']['generated_at']}
Period: {report['report_metadata']['period']}
Total Articles: {report['report_metadata']['total_articles']}

## Executive Summary
{report['executive_summary']}

## Key Insights
"""
        
        for insight in report['key_insights']:
            summary += f"- {insight}\n"
        
        summary += f"""
## Risk Assessment
Overall Risk Level: {report['risk_assessment']['overall_risk_level'].upper()}

### Regulatory Risks
"""
        for risk in report['risk_assessment']['regulatory_risks']:
            summary += f"- {risk}\n"
        
        summary += """
### Market Risks
"""
        for risk in report['risk_assessment']['market_risks']:
            summary += f"- {risk}\n"
        
        summary += """
### Political Risks
"""
        for risk in report['risk_assessment']['political_risks']:
            summary += f"- {risk}\n"
        
        summary += """
## Action Items
"""
        for action in report['action_items']:
            summary += f"- {action}\n"
        
        return summary

def main():
    """Main function to test report generation"""
    # This would typically be called with real data from the scrapers
    sample_data = {
        "total_articles": 25,
        "legal": {
            "high_impact_count": 2,
            "medium_impact_count": 3,
            "low_impact_count": 5,
            "uke_decisions": 1,
            "competition_law": 2,
            "eu_regulations": 1
        },
        "polityka": {
            "high_impact_count": 1,
            "medium_impact_count": 4,
            "low_impact_count": 6,
            "government_policy": 3,
            "eu_policy": 2,
            "international_relations": 1
        },
        "financial": {
            "high_impact_count": 1,
            "medium_impact_count": 2,
            "low_impact_count": 4,
            "earnings": 2,
            "investments": 1,
            "market_movements": 1,
            "currency_rates": 1
        }
    }
    
    generator = TelecomReportGenerator()
    report = generator.generate_weekly_report(sample_data)
    
    # Save report
    filepath = generator.save_report(report)
    
    # Generate and save text summary
    summary_text = generator.generate_summary_text(report)
    summary_filepath = filepath.replace('.json', '_summary.md')
    
    with open(summary_filepath, "w", encoding="utf-8") as f:
        f.write(summary_text)
    
    print(f"Report generated: {filepath}")
    print(f"Summary generated: {summary_filepath}")

if __name__ == "__main__":
    main()
