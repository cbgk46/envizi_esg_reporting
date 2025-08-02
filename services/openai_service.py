import json
from openai import OpenAI
from models import SpiderChartModel
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

# Initialize OpenAI client
client = OpenAI()

def extract_sustainability_scores(markdown_content: str) -> SpiderChartModel:
    """Extract sustainability dimension scores from Langflow markdown using OpenAI"""
    
    prompt = f"""
    Please analyze the following sustainability assessment report and extract the numerical scores for each dimension. 
    The scores should be on a scale of 1-5, where:
    - 1 = Resist - Minimal or no sustainability practices
    - 2 = Comply - Basic regulatory compliance
    - 3 = Optimize - Proactive sustainability improvements
    - 4 = Reinvent - Sustainability as core business driver
    - 5 = Lead - Industry leadership in sustainability
    
    Extract scores for these exact dimensions:
    - sustainability_leadership
    - organization
    - sustainability_risk_management
    - data_systems
    - people_competency
    - direct_asset_management
    - product_management
    - vendor_management
    - metrics_reporting
    - managing_change
    
    If a specific dimension is not mentioned, estimate based on related content and context.
    
    Return your response in JSON format matching this structure:
    {{
        "sustainability_leadership": 5,
        "organization": 4,
        "sustainability_risk_management": 3,
        "data_systems": 2,
        "people_competency": 4,
        "direct_asset_management": 3,
        "product_management": 2,
        "vendor_management": 3,
        "metrics_reporting": 4,
        "managing_change": 3
    }}
    
    Assessment Report:
    {markdown_content}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert sustainability analyst. Extract precise numerical scores from sustainability assessment reports."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        scores_json = response.choices[0].message.content
        scores_data = json.loads(scores_json)
        return SpiderChartModel(**scores_data)
        
    except Exception as e:
        print(f"Error extracting scores with OpenAI: {e}")
        # Fallback default scores if API fails
        return SpiderChartModel(
            sustainability_leadership=3,
            organization=3,
            sustainability_risk_management=3,
            data_systems=3,
            people_competency=3,
            direct_asset_management=3,
            product_management=3,
            vendor_management=3,
            metrics_reporting=3,
            managing_change=3
        )

def generate_executive_summary(user_scores: Dict[str, float], industry_averages: Dict[str, float], company_name: str) -> str:
    """Generate an executive summary using OpenAI based on survey data and industry averages"""
    
    overall_score = round(sum(user_scores.values()) / len(user_scores), 2)
    
    # Create comparison data for prompt
    comparison_data = []
    for dimension, user_score in user_scores.items():
        industry_avg = industry_averages.get(dimension, 0)
        gap = round(user_score - industry_avg, 2)
        comparison_data.append(f"- {dimension}: User {user_score}/5.0 vs Industry {industry_avg}/5.0 (Gap: {gap:+.2f})")
    
    prompt = f"""
    Generate a concise executive summary for {company_name}'s sustainability maturity assessment. 
    
    Key Data:
    - Overall Score: {overall_score}/5.0
    - Company: {company_name}
    
    Dimension Comparison (User vs Industry Average):
    {chr(10).join(comparison_data)}
    
    Requirements:
    - Maximum 5 lines
    - Professional, actionable tone
    - Focus on key insights, strengths, and priority areas
    - Mention overall maturity level and key recommendations
    - Be specific about the company's position relative to industry
    
    Return only the executive summary text, no additional formatting or headers.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert sustainability consultant creating executive summaries for corporate sustainability assessments. Be concise, insightful, and actionable."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating executive summary with OpenAI: {e}")
        # Fallback summary if API fails
        return f"{company_name} achieved an overall sustainability maturity score of {overall_score}/5.0. The assessment reveals opportunities for improvement across key dimensions while highlighting areas of strength relative to industry benchmarks. Immediate focus should be placed on the lowest-scoring dimensions to accelerate sustainability maturity. Strategic investments in foundational capabilities will drive long-term competitive advantage. The company is positioned to advance its sustainability journey through targeted action plans." 