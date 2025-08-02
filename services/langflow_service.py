import requests
from typing import Dict
from datetime import datetime
from config import USERS, QUESTIONS_DATA, LANGFLOW_API_URL

def format_questionnaire_for_langflow(user: str, responses: Dict) -> str:
    """Format questionnaire responses for Langflow API"""
    user_info = USERS[user]
    
    # Create the formatted string
    formatted_text = f"""APEX MANUFACTURING - SUSTAINABILITY QUESTIONNAIRE
Company: {user_info['company']}
Industry: {user_info['industry']}
Revenue: {user_info['revenue']}
Location: {user_info['location']}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

QUESTIONNAIRE RESPONSES
========================

"""
    
    # Add each question and response
    for question_data in QUESTIONS_DATA["questionnaireReference"]:
        question_id = question_data["questionId"]
        question_text = question_data["question"]
        dimension = question_data["dimension"]
        element = question_data["element"]
        
        if question_id in responses:
            response_level = responses[question_id]
            response_text = QUESTIONS_DATA["responses"][str(response_level)]
            formatted_text += f"Q{question_id[1:]}: {question_text}\n"
            formatted_text += f"Dimension: {dimension} | Element: {element}\n"
            formatted_text += f"A{question_id[1:]}: Level {response_level} - {response_text}\n\n"
        else:
            formatted_text += f"Q{question_id[1:]}: {question_text}\n"
            formatted_text += f"Dimension: {dimension} | Element: {element}\n"
            formatted_text += f"A{question_id[1:]}: Not answered\n\n"
    
    return formatted_text

def call_langflow_api(formatted_data: str) -> Dict:
    """Call Langflow API with formatted questionnaire data"""
    payload = {
        "input_value": formatted_data,
        "output_type": "chat",
        "input_type": "chat"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(LANGFLOW_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        # Parse the JSON response
        response_data = response.json()
        
        # Extract the nested text content
        try:
            extracted_text = response_data["outputs"][0]["outputs"][0]["results"]["message"]["data"]["text"]
            return {
                "success": True,
                "response_data": response_data,
                "extracted_text": extracted_text,
                "status_code": response.status_code
            }
        except (KeyError, IndexError, TypeError) as e:
            return {
                "success": False,
                "error": f"Error extracting text from response structure: {e}",
                "response_data": response_data,
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error making API request: {e}",
            "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        }
    except ValueError as e:
        return {
            "success": False,
            "error": f"Error parsing JSON response: {e}",
            "status_code": None
        } 