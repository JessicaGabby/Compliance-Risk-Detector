"""
Compliance Risk Detection Tool
Personal project for learning LLM integration and compliance automation
"""

import json
from datetime import datetime
from openai import OpenAI

# ============================================
# GitHub Models configuration
# ============================================
GITHUB_TOKEN = "your-token-here"

client = OpenAI(
    base_url="https://models.inference.ai.azure.com/",
    api_key=GITHUB_TOKEN,
)

MODEL = "gpt-4o-mini"

# ============================================
# ComplianceChecker Class
# Handles risk analysis for multiple industries
# ============================================
class ComplianceChecker:
    def __init__(self, industry="general"):
        self.industry = industry
        self.history = []
    
    def check(self, data):
        """
        Analyzes input data for compliance risks.
        Returns structured JSON with risk score, flags, and recommendations.
        """
        
        prompt = f"""
You are a compliance risk analyst for the {self.industry} industry.

Analyze this data for compliance risks:
{data}

Return ONLY valid JSON with this structure:
{{
    "risk_score": "Low|Medium|High|Critical",
    "flags": [
        {{
            "category": "type of risk",
            "description": "what you found",
            "severity": "Low|Medium|High|Critical",
            "regulation": "relevant rule or law",
            "recommendation": "what to do"
        }}
    ],
    "summary": "one sentence overall assessment"
}}

Only flag things that are clearly problematic.
"""
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content)
        result["timestamp"] = datetime.now().isoformat()
        result["industry"] = self.industry
        result["data_analyzed"] = data[:200]
        
        self.history.append(result)
        return result
    
    def save_report(self, result, filename=None):
        """Exports analysis results to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"compliance_report_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(result, f, indent=2)
        
        return filename


# ============================================
# Command Line Interface
# ============================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("   COMPLIANCE RISK DETECTION TOOL")
    print("="*60)
    
    print("\nSelect industry:")
    print("1. General")
    print("2. Tax / Audit")
    print("3. Banking / Fintech")
    print("4. Healthcare")
    print("5. Corporate / HR")
    
    choice = input("\nEnter 1-5: ")
    industries = {
        "1": "general", 
        "2": "tax_audit", 
        "3": "banking", 
        "4": "healthcare", 
        "5": "corporate"
    }
    industry = industries.get(choice, "general")
    
    checker = ComplianceChecker(industry=industry)
    
    print(f"\nEnter data to check for {industry} compliance risks:")
    print("\nExample formats:")
    print("  Tax: Revenue $500k, Meals $80k, Misc $100k, Contractors $200k")
    print("  Banking: Customer deposits $50k cash weekly, no source of funds")
    
    data = input("\nData: ")
    
    print("\nAnalyzing...")
    result = checker.check(data)
    
    print(f"\nRISK SCORE: {result['risk_score']}")
    print(f"\nSUMMARY: {result['summary']}")
    print(f"\nFLAGS FOUND ({len(result['flags'])}):")
    
    for i, flag in enumerate(result['flags'], 1):
        print(f"\n  {i}. [{flag['severity']}] {flag['category']}")
        print(f"     {flag['description']}")
        print(f"     Regulation: {flag['regulation']}")
        print(f"     Recommendation: {flag['recommendation']}")
    
    report_file = checker.save_report(result)
    print(f"\nReport saved to: {report_file}")
