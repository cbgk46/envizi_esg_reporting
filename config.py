import json
from typing import Dict

# Langflow API configuration
LANGFLOW_API_URL = "http://localhost:7860/api/v1/run/dd764172-0f56-49d4-a634-bbc2a27a818e"

# Simple user database (in production, use a proper database)
USERS = {
    "faiz": {
        "password": "envizi",
        "name": "Faiz",
        "company": "Apex Manufacturing",
        "industry": "Chemical Manufacturing",
        "revenue": "$75M-$100M",
        "location": "Kuala Lumpur, Malaysia"
    }
}

def load_questions() -> Dict:
    """Load questions from questions.json file"""
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback questions if file not found
        return {
            "questionnaireReference": [
                {"questionId": "Q01", "dimension": "Sustainability Leadership", "element": "Leadership", "question": "Sustainability is a priority for my Leadership committee"}
            ],
            "responses": {
                "1": "Resist - Minimal or no sustainability practices, reactive approach",
                "2": "Comply - Basic regulatory compliance, limited proactive measures",
                "3": "Optimize - Proactive sustainability improvements, some integration into business",
                "4": "Reinvent - Sustainability as core business driver, comprehensive approach",
                "5": "Lead - Industry leadership in sustainability, market shaping activities"
            }
        }

# Load questions at startup
QUESTIONS_DATA = load_questions() 