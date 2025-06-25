from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import secrets
from typing import Optional, Dict, List
import json
import os
import requests
from datetime import datetime
import markdown
from playwright.async_api import async_playwright
import tempfile
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from pydantic import BaseModel
import plotly.graph_objects as go
import plotly.io as pio
import base64

class SpiderChartModel(BaseModel):
    sustainability_leadership: int
    organization: int
    sustainability_risk_management: int
    data_systems: int
    people_competency: int
    direct_asset_management: int
    product_management: int
    vendor_management: int
    metrics_reporting: int
    managing_change: int

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

def create_spider_chart(scores: SpiderChartModel, company_name: str) -> str:
    """Create a spider chart from sustainability scores and return as base64 image"""
    
    # Define the dimensions and their display names
    dimensions = [
        ('sustainability_leadership', 'Sustainability Leadership'),
        ('organization', 'Organization Structure'),
        ('sustainability_risk_management', 'Risk Management'),
        ('data_systems', 'Data Systems'),
        ('people_competency', 'People & Competency'),
        ('direct_asset_management', 'Asset Management'),
        ('product_management', 'Product Management'),
        ('vendor_management', 'Vendor Management'),
        ('metrics_reporting', 'Metrics & Reporting'),
        ('managing_change', 'Managing Change')
    ]
    
    # Extract values and labels
    categories = [dim[1] for dim in dimensions]
    values = [getattr(scores, dim[0]) for dim in dimensions]
    
    # Create the spider chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=company_name,
        line=dict(color='#4CAF50', width=3),
        fillcolor='rgba(76, 175, 80, 0.3)',
        marker=dict(size=8, color='#4CAF50')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['Resist', 'Comply', 'Optimize', 'Reinvent', 'Lead'],
                tickfont=dict(size=10),
                gridcolor='rgba(0,0,0,0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(size=11),
                rotation=90,
                direction='clockwise'
            ),
            bgcolor='white'
        ),
        showlegend=True,
        title=dict(
            text=f"Sustainability Maturity Assessment - {company_name}",
            x=0.5,
            font=dict(size=16, color='#4CAF50')
        ),
        width=600,
        height=600,
        margin=dict(l=80, r=80, t=80, b=80),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    # Convert to base64 image
    img_bytes = pio.to_image(fig, format="png", width=600, height=600, scale=2)
    img_base64 = base64.b64encode(img_bytes).decode()
    
    return img_base64

app = FastAPI(
    title="FastAPI Login & Questionnaire",
    description="A FastAPI application with login and questionnaire functionality",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Security
security = HTTPBasic()

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

# Session management (in production, use proper session management)
active_sessions = {}

# Langflow API configuration
LANGFLOW_API_URL = "http://localhost:7860/api/v1/run/dd764172-0f56-49d4-a634-bbc2a27a818e"

# Load questions from JSON file
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

def get_current_user(request: Request) -> Optional[str]:
    """Get current user from session"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in active_sessions:
        return active_sessions[session_id]
    return None

def create_session(username: str) -> str:
    """Create a new session for user"""
    session_id = secrets.token_urlsafe(32)
    active_sessions[session_id] = username
    return session_id

def require_login(request: Request) -> str:
    """Dependency to require login"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Redirect to login",
            headers={"Location": "/login"}
        )
    return user

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

@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect root to login page"""
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Handle login form submission"""
    if username in USERS and USERS[username]["password"] == password:
        session_id = create_session(username)
        response = RedirectResponse(url="/questionnaire", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=3600)
        return response
    else:
        return RedirectResponse(url="/login?error=Invalid username or password", status_code=status.HTTP_302_FOUND)

@app.get("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("session_id")
    return response

@app.get("/questionnaire", response_class=HTMLResponse)
async def questionnaire_page(request: Request, current_user: str = Depends(require_login)):
    """Questionnaire page (requires login)"""
    
    context = {
        "request": request,
        "user_name": USERS[current_user]['name'],
        "total_questions": len(QUESTIONS_DATA['questionnaireReference']),
        "questions": QUESTIONS_DATA['questionnaireReference']
    }
    
    return templates.TemplateResponse("questionnaire.html", context)

@app.post("/submit-questionnaire")
async def submit_questionnaire(
    request: Request,
    current_user: str = Depends(require_login)
):
    """Handle questionnaire submission"""
    
    # Get form data
    form_data = await request.form()
    
    # Process responses
    responses = {}
    for question_id in QUESTIONS_DATA["questionnaireReference"]:
        q_id = question_id["questionId"]
        if q_id in form_data:
            responses[q_id] = int(form_data[q_id])
    
    # Format data for Langflow
    formatted_data = format_questionnaire_for_langflow(current_user, responses)
    
    # Call Langflow API
    langflow_result = call_langflow_api(formatted_data)
    
    # Store the result in session for display on success page
    session_id = request.cookies.get("session_id")
    if session_id and session_id in active_sessions:
        # In a real application, you would store this in a database
        # For now, we'll store it in a simple dict (not persistent)
        if not hasattr(app.state, 'langflow_results'):
            app.state.langflow_results = {}
        app.state.langflow_results[session_id] = langflow_result
    
    # In a real application, you would save this to a database
    response_data = {
        "user": current_user,
        "timestamp": str(request.headers.get("date", "")),
        "total_questions": len(QUESTIONS_DATA["questionnaireReference"]),
        "answered_questions": len(responses),
        "responses": responses,
        "langflow_result": langflow_result
    }
    
    # Redirect to report page to display the Langflow analysis
    return RedirectResponse(url="/report", status_code=status.HTTP_302_FOUND)

@app.get("/report", response_class=HTMLResponse)
async def report_page(request: Request, current_user: str = Depends(require_login)):
    """Report page displaying Langflow analysis results"""
    
    # Get Langflow result if available
    langflow_result = None
    markdown_content = None
    html_content = None
    spider_chart_base64 = None
    sustainability_scores = None
    session_id = request.cookies.get("session_id")
    
    if session_id and hasattr(app.state, 'langflow_results') and session_id in app.state.langflow_results:
        langflow_result = app.state.langflow_results[session_id]
        
        # Extract markdown content if available
        if langflow_result and langflow_result.get("success") and "extracted_text" in langflow_result:
            markdown_content = langflow_result["extracted_text"]
            
            # Convert markdown to HTML on the server side
            try:
                # Strip markdown code fence if present
                processed_content = markdown_content.strip()
                if processed_content.startswith('```markdown'):
                    # Remove opening ```markdown
                    processed_content = processed_content[11:].strip()
                    # Remove closing ```
                    if processed_content.endswith('```'):
                        processed_content = processed_content[:-3].strip()
                
                html_content = markdown.markdown(
                    processed_content,
                    extensions=['markdown.extensions.tables', 'markdown.extensions.fenced_code', 'markdown.extensions.toc']
                )
                
                # Extract sustainability scores using OpenAI
                sustainability_scores = extract_sustainability_scores(processed_content)
                
                # Generate spider chart
                spider_chart_base64 = create_spider_chart(sustainability_scores, USERS[current_user]['company'])
                
            except Exception as e:
                print(f"Error converting markdown to HTML: {e}")
                html_content = f"<pre>{markdown_content}</pre>"
    
    context = {
        "request": request,
        "user_name": USERS[current_user]['name'],
        "total_questions": len(QUESTIONS_DATA['questionnaireReference']),
        "langflow_result": langflow_result,
        "markdown_content": markdown_content,
        "html_content": html_content,
        "spider_chart_base64": spider_chart_base64,
        "sustainability_scores": sustainability_scores
    }
    
    return templates.TemplateResponse("report.html", context)

@app.get("/download-pdf")
async def download_pdf(request: Request, current_user: str = Depends(require_login)):
    """Generate and download PDF version of the sustainability report"""
    
    # Get Langflow result if available
    langflow_result = None
    markdown_content = None
    html_content = None
    spider_chart_base64 = None
    sustainability_scores = None
    session_id = request.cookies.get("session_id")
    
    if session_id and hasattr(app.state, 'langflow_results') and session_id in app.state.langflow_results:
        langflow_result = app.state.langflow_results[session_id]
        
        # Extract markdown content if available
        if langflow_result and langflow_result.get("success") and "extracted_text" in langflow_result:
            markdown_content = langflow_result["extracted_text"]
            
            # Convert markdown to HTML on the server side
            try:
                # Strip markdown code fence if present
                processed_content = markdown_content.strip()
                if processed_content.startswith('```markdown'):
                    # Remove opening ```markdown
                    processed_content = processed_content[11:].strip()
                    # Remove closing ```
                    if processed_content.endswith('```'):
                        processed_content = processed_content[:-3].strip()
                
                html_content = markdown.markdown(
                    processed_content,
                    extensions=['markdown.extensions.tables', 'markdown.extensions.fenced_code', 'markdown.extensions.toc']
                )
                
                # Extract sustainability scores using OpenAI
                sustainability_scores = extract_sustainability_scores(processed_content)
                
                # Generate spider chart for PDF
                spider_chart_base64 = create_spider_chart(sustainability_scores, USERS[current_user]['company'])
                
            except Exception as e:
                print(f"Error converting markdown to HTML: {e}")
                html_content = f"<pre>{markdown_content}</pre>"
    
    if not html_content:
        raise HTTPException(status_code=404, detail="No report data available")
    
    # Create PDF-friendly HTML
    pdf_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Sustainability Report - {USERS[current_user]['company']}</title>
                 <style>
             @page {{
                 size: A4;
                 margin: 0;
             }}
            
                         body {{
                 font-family: 'Arial', sans-serif;
                 line-height: 1.6;
                 color: #333;
                 margin: 2cm;
                 padding: 0;
             }}
            
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #4CAF50;
            }}
            
            .header h1 {{
                color: #4CAF50;
                font-size: 24pt;
                margin: 0;
            }}
            
            .header .company-info {{
                margin-top: 10px;
                font-size: 12pt;
                color: #666;
            }}
            
            h1 {{
                color: #4CAF50;
                font-size: 18pt;
                margin: 20px 0 10px 0;
                border-bottom: 2px solid #4CAF50;
                padding-bottom: 5px;
            }}
            
            h2 {{
                color: #4CAF50;
                font-size: 16pt;
                margin: 15px 0 8px 0;
                border-bottom: 1px solid #4CAF50;
                padding-bottom: 3px;
            }}
            
            h3 {{
                color: #4CAF50;
                font-size: 14pt;
                margin: 12px 0 6px 0;
            }}
            
            p {{
                margin: 8px 0;
                text-align: justify;
            }}
            
            ul, ol {{
                margin: 8px 0;
                padding-left: 20px;
            }}
            
            li {{
                margin: 4px 0;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
                font-size: 10pt;
            }}
            
            th, td {{
                padding: 8px;
                border: 1px solid #ddd;
                text-align: left;
            }}
            
            th {{
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }}
            
            blockquote {{
                border-left: 4px solid #4CAF50;
                margin: 10px 0;
                padding: 10px 15px;
                background-color: #f9f9f9;
                font-style: italic;
            }}
            
            code {{
                background-color: #f5f5f5;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }}
            
            pre {{
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                line-height: 1.4;
            }}
            
            .page-break {{
                page-break-before: always;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌱 Sustainability Maturity Assessment Report</h1>
            <div class="company-info">
                <strong>{USERS[current_user]['company']}</strong><br>
                {USERS[current_user]['industry']} | {USERS[current_user]['location']}<br>
                Revenue: {USERS[current_user]['revenue']}<br>
                Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </div>
        </div>
        
                 <div class="content">
             <!-- Spider Chart Section -->
             {f'''
             <div class="spider-chart-section" style="text-align: center; margin-bottom: 30px; page-break-inside: avoid;">
                 <h2 style="color: #4CAF50; margin-bottom: 15px;">📊 Sustainability Maturity Assessment Radar</h2>
                 <img src="data:image/png;base64,{spider_chart_base64}" 
                      alt="Sustainability Spider Chart" 
                      style="max-width: 100%; height: auto; margin-bottom: 15px;">
                 
                 <div class="scores-summary" style="margin-top: 15px;">
                     <h3 style="color: #4CAF50; margin-bottom: 10px;">Dimension Scores (1-5 Scale)</h3>
                     <table style="width: 100%; margin: 0 auto; font-size: 10pt;">
                         <tr>
                             <td>📈 Sustainability Leadership</td><td><strong>{sustainability_scores.sustainability_leadership}</strong></td>
                             <td>🏢 Organization Structure</td><td><strong>{sustainability_scores.organization}</strong></td>
                         </tr>
                         <tr>
                             <td>⚠️ Risk Management</td><td><strong>{sustainability_scores.sustainability_risk_management}</strong></td>
                             <td>💾 Data Systems</td><td><strong>{sustainability_scores.data_systems}</strong></td>
                         </tr>
                         <tr>
                             <td>👥 People & Competency</td><td><strong>{sustainability_scores.people_competency}</strong></td>
                             <td>🏭 Asset Management</td><td><strong>{sustainability_scores.direct_asset_management}</strong></td>
                         </tr>
                         <tr>
                             <td>📦 Product Management</td><td><strong>{sustainability_scores.product_management}</strong></td>
                             <td>🤝 Vendor Management</td><td><strong>{sustainability_scores.vendor_management}</strong></td>
                         </tr>
                         <tr>
                             <td>📊 Metrics & Reporting</td><td><strong>{sustainability_scores.metrics_reporting}</strong></td>
                             <td>🔄 Managing Change</td><td><strong>{sustainability_scores.managing_change}</strong></td>
                         </tr>
                     </table>
                 </div>
             </div>
             <div style="page-break-before: always;"></div>
             ''' if spider_chart_base64 and sustainability_scores else ''}
             
             <!-- Main Report Content -->
             {html_content}
         </div>
    </body>
    </html>
    """
    
    try:
        # Create filename
        company_name = USERS[current_user]['company'].replace(' ', '_').replace(',', '')
        filename = f"Sustainability_Report_{company_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Generate PDF using playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set content and generate PDF
            await page.set_content(pdf_html)
            pdf_bytes = await page.pdf(
                format='A4',
                margin={
                    'top': '2cm',
                    'right': '2cm',
                    'bottom': '2cm',
                    'left': '2cm'
                },
                print_background=True,
                display_header_footer=True,
                header_template='<div style="font-size:10px; text-align:center; width:100%;">Sustainability Maturity Assessment Report</div>',
                footer_template='<div style="font-size:10px; text-align:center; width:100%;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>'
            )
            
            await browser.close()
        
        # Return PDF as download
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

@app.get("/success", response_class=HTMLResponse)
async def success_page(request: Request, current_user: str = Depends(require_login)):
    """Success page after questionnaire submission"""
    
    # Get Langflow result if available
    langflow_result = None
    session_id = request.cookies.get("session_id")
    if session_id and hasattr(app.state, 'langflow_results') and session_id in app.state.langflow_results:
        langflow_result = app.state.langflow_results[session_id]
    
    context = {
        "request": request,
        "user_name": USERS[current_user]['name'],
        "total_questions": len(QUESTIONS_DATA['questionnaireReference']),
        "langflow_result": langflow_result
    }
    
    return templates.TemplateResponse("success.html", context)

@app.get("/hello")
async def hello():
    """Simple hello endpoint that returns JSON"""
    return {"message": "Hello, World!", "status": "success"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "FastAPI Sustainability Questionnaire App"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 