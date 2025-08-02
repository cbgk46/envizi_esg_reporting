import json
from openai import OpenAI
from models import SpiderChartModel
from dotenv import load_dotenv

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