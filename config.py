import json
import os
from typing import Dict

# Debug mode configuration (set to False for production)
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
DEBUG_DEFAULT_SCORE = int(os.getenv("DEBUG_DEFAULT_SCORE", "3"))  # Default to "3" (Neither agree nor disagree)

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
        # Try to load the complete questions file first
        with open("questions (1).json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        try:
            # Fallback to original questions.json
            with open("questions.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback questions if no file found
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

def load_recommendations() -> Dict:
    """Load recommendations from recommendations.json file"""
    try:
        with open("recommendations.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"maturity_framework": {"levels": {}}, "mini_reports": []}

def load_survey_data() -> Dict:
    """Load survey data from survey_data.json file"""
    try:
        with open("survey_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"industry_averages": [], "companies": {}}

# Load data at startup
RECOMMENDATIONS_DATA = load_recommendations()
SURVEY_DATA = load_survey_data()

# Dimension mapping to handle naming inconsistencies between files
DIMENSION_MAPPING = {
    "Sustainability Leadership": {
        "survey_key": "sustainability_leadership",
        "chart_key": "sustainability_leadership"
    },
    "Organization": {
        "survey_key": "organization", 
        "chart_key": "organization"
    },
    "Sustainability Risk Management": {
        "survey_key": "sustainability_risk_mgmt",
        "chart_key": "sustainability_risk_management"
    },
    "Data & Systems": {
        "survey_key": "data_systems",
        "chart_key": "data_systems"
    },
    "People & Competency": {
        "survey_key": "people_costs",
        "chart_key": "people_competency"
    },
    "Asset Management": {
        "survey_key": "asset_management",
        "chart_key": "direct_asset_management"
    },
    "Product Management": {
        "survey_key": "design_customers",
        "chart_key": "product_management"
    },
    "Vendor Management": {
        "survey_key": "vendor_management",
        "chart_key": "vendor_management"
    },
    "Metrics & Reporting": {
        "survey_key": "metrics_reporting",
        "chart_key": "metrics_reporting"
    },
    "Managing Change": {
        "survey_key": "managing_change",
        "chart_key": "managing_change"
    }
} 