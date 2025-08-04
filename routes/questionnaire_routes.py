from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from datetime import datetime
import markdown
from playwright.async_api import async_playwright

from auth import require_login
from config import USERS, QUESTIONS_DATA, DEBUG_MODE, DEBUG_DEFAULT_SCORE
from services.questionnaire_processor import process_questionnaire_responses
from services.openai_service import extract_sustainability_scores
from services.chart_service import create_spider_chart

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Global variable to store langflow results (in production, use a proper database)
langflow_results = {}

@router.get("/questionnaire", response_class=HTMLResponse)
async def questionnaire_page(request: Request, current_user: str = Depends(require_login)):
    """Questionnaire page (requires login)"""
    
    context = {
        "request": request,
        "user_name": USERS[current_user]['name'],
        "total_questions": len(QUESTIONS_DATA['questionnaireReference']),
        "questions": QUESTIONS_DATA['questionnaireReference'],
        "responses": QUESTIONS_DATA['responses'],
        "debug_mode": DEBUG_MODE,
        "debug_default_score": DEBUG_DEFAULT_SCORE
    }
    
    return templates.TemplateResponse("questionnaire.html", context)

@router.post("/submit-questionnaire")
async def submit_questionnaire(
    request: Request,
    current_user: str = Depends(require_login)
):
    """Handle questionnaire submission"""
    
    # Get form data
    form_data = await request.form()
    
    # Extract general information fields
    general_info = {
        "company": form_data.get("company", "").strip(),
        "name": form_data.get("name", "").strip(),
        "email": form_data.get("email", "").strip(),
        "industry": form_data.get("industry", "").strip(),
        "employees": form_data.get("employees", "").strip(),
        "headquarters": form_data.get("headquarters", "").strip(),
        "products": form_data.get("products", "").strip(),
        "manufacturing_location": form_data.get("manufacturing_location", "").strip(),
        "profile": form_data.get("profile", "").strip()
    }
    
    # Validate required general information fields
    required_fields = ["company", "name", "email", "industry", "employees", "headquarters"]
    missing_fields = [field for field in required_fields if not general_info[field]]
    
    if missing_fields:
        # In a real application, you'd handle this error more gracefully
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    # Process sustainability questionnaire responses
    responses = {}
    for question_id in QUESTIONS_DATA["questionnaireReference"]:
        q_id = question_id["questionId"]
        if q_id in form_data:
            responses[q_id] = int(form_data[q_id])
    
    # Update user information with general info (for this session)
    # In a real application, you'd save this to a database
    if current_user in USERS:
        USERS[current_user].update({
            "general_info": general_info,
            "last_updated": str(datetime.now())
        })
    
    # Process questionnaire using new logic with updated company name
    company_name = general_info["company"]  # Use the form company name instead of config
    processed_result = process_questionnaire_responses(current_user, responses, company_name)
    
    # Add general information to the processed result
    processed_result["general_information"] = general_info
    
    # Store the result in session for display on success page
    session_id = request.cookies.get("session_id")
    if session_id:
        langflow_results[session_id] = processed_result
    
    # In a real application, you would save this to a database
    response_data = {
        "user": current_user,
        "timestamp": str(request.headers.get("date", "")),
        "general_information": general_info,
        "total_questions": len(QUESTIONS_DATA["questionnaireReference"]),
        "answered_questions": len(responses),
        "responses": responses,
        "processed_result": processed_result
    }
    
    # Redirect to report page to display the Langflow analysis
    return RedirectResponse(url="/report", status_code=status.HTTP_302_FOUND)

@router.get("/report", response_class=HTMLResponse)
async def report_page(request: Request, current_user: str = Depends(require_login)):
    """Report page displaying Langflow analysis results"""
    
    # Get Langflow result if available
    langflow_result = None
    markdown_content = None
    html_content = None
    spider_chart_base64 = None
    sustainability_scores = None
    general_information = None
    session_id = request.cookies.get("session_id")
    
    if session_id and session_id in langflow_results:
        langflow_result = langflow_results[session_id]
        
        # Extract general information if available in langflow result
        if langflow_result and "general_information" in langflow_result:
            general_information = langflow_result["general_information"]
        
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
                
                # Use spider chart from processed result if available
                if "spider_chart_base64" in langflow_result:
                    spider_chart_base64 = langflow_result["spider_chart_base64"]
                
                # Use spider chart model from processed result if available
                if "spider_chart_model" in langflow_result:
                    sustainability_scores = langflow_result["spider_chart_model"]
                else:
                    # Fallback to OpenAI extraction if needed
                    sustainability_scores = extract_sustainability_scores(processed_content)
                    if not spider_chart_base64:
                        # Use company name from general info if available, otherwise fallback to user config
                        company_name = general_information.get("company") if general_information else USERS[current_user]['company']
                        spider_chart_base64 = create_spider_chart(sustainability_scores, company_name)
                
            except Exception as e:
                print(f"Error converting markdown to HTML: {e}")
                html_content = f"<pre>{markdown_content}</pre>"
    
    # Fallback to user's general info if not in langflow result
    if not general_information and current_user in USERS and "general_info" in USERS[current_user]:
        general_information = USERS[current_user]["general_info"]
    
    context = {
        "request": request,
        "user_name": USERS[current_user]['name'],
        "total_questions": len(QUESTIONS_DATA['questionnaireReference']),
        "langflow_result": langflow_result,
        "markdown_content": markdown_content,
        "html_content": html_content,
        "spider_chart_base64": spider_chart_base64,
        "sustainability_scores": sustainability_scores,
        "general_information": general_information
    }
    
    return templates.TemplateResponse("report.html", context)

@router.get("/download-pdf")
async def download_pdf(request: Request, current_user: str = Depends(require_login)):
    """Generate and download PDF version of the sustainability report"""
    
    # Get Langflow result if available
    langflow_result = None
    markdown_content = None
    html_content = None
    spider_chart_base64 = None
    sustainability_scores = None
    session_id = request.cookies.get("session_id")
    
    if session_id and session_id in langflow_results:
        langflow_result = langflow_results[session_id]
        
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
                
                # Use spider chart from processed result if available
                if "spider_chart_base64" in langflow_result:
                    spider_chart_base64 = langflow_result["spider_chart_base64"]
                
                # Use spider chart model from processed result if available
                if "spider_chart_model" in langflow_result:
                    sustainability_scores = langflow_result["spider_chart_model"]
                else:
                    # Fallback to OpenAI extraction if needed
                    sustainability_scores = extract_sustainability_scores(processed_content)
                    if not spider_chart_base64:
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

@router.get("/success", response_class=HTMLResponse)
async def success_page(request: Request, current_user: str = Depends(require_login)):
    """Success page after questionnaire submission"""
    
    # Get Langflow result if available
    langflow_result = None
    session_id = request.cookies.get("session_id")
    if session_id and session_id in langflow_results:
        langflow_result = langflow_results[session_id]
    
    context = {
        "request": request,
        "user_name": USERS[current_user]['name'],
        "total_questions": len(QUESTIONS_DATA['questionnaireReference']),
        "langflow_result": langflow_result
    }
    
    return templates.TemplateResponse("success.html", context) 