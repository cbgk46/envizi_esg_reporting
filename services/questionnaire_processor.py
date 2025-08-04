from typing import Dict, List, Tuple
import plotly.graph_objects as go
import plotly.io as pio
import base64
from models import SpiderChartModel
from config import QUESTIONS_DATA, RECOMMENDATIONS_DATA, SURVEY_DATA, DIMENSION_MAPPING, USERS
from services.openai_service import generate_executive_summary, get_company_sustainability_insights

def calculate_dimension_averages(responses: Dict[str, int]) -> Dict[str, float]:
    """Calculate average scores for each dimension based on user responses"""
    dimension_scores = {}
    dimension_counts = {}
    
    # Group responses by dimension
    for question in QUESTIONS_DATA["questionnaireReference"]:
        question_id = question["questionId"]
        dimension = question["dimension"]
        
        if question_id in responses:
            score = responses[question_id]
            
            if dimension not in dimension_scores:
                dimension_scores[dimension] = 0
                dimension_counts[dimension] = 0
            
            dimension_scores[dimension] += score
            dimension_counts[dimension] += 1
    
    # Calculate averages
    dimension_averages = {}
    for dimension in dimension_scores:
        if dimension_counts[dimension] > 0:
            dimension_averages[dimension] = round(dimension_scores[dimension] / dimension_counts[dimension], 2)
    
    return dimension_averages

def determine_maturity_level(score: float) -> str:
    """Determine maturity level based on score"""
    if score < 2.0:
        return "resist"
    elif score < 3.0:
        return "comply"
    elif score < 4.0:
        return "optimize"
    elif score < 5.0:
        return "reinvent"
    else:
        return "lead"

def get_dimension_recommendation(dimension_name: str, maturity_level: str) -> str:
    """Get recommendation for a specific dimension and maturity level"""
    for report in RECOMMENDATIONS_DATA["mini_reports"]:
        if report["name"] == dimension_name:
            return report["recommendations"].get(maturity_level, "No recommendation available")
    return "No recommendation available"

def get_industry_averages() -> Dict[str, float]:
    """Get industry averages mapped to our dimension names"""
    industry_avgs = {}
    
    for avg_data in SURVEY_DATA["industry_averages"]:
        dimension_name = avg_data["name"]
        industry_avg = avg_data["industry_average"]
        
        # Map dimension names to our standard format
        for our_dim, mapping in DIMENSION_MAPPING.items():
            if (dimension_name == our_dim or 
                dimension_name.replace(" & ", " ").replace("Mgmt", "Management") == our_dim or
                dimension_name.replace("Costs", "Competency").replace("Design & Customers", "Product Management") == our_dim):
                industry_avgs[our_dim] = industry_avg
                break
    
    return industry_avgs

def create_comparison_spider_chart(user_scores: Dict[str, float], company_name: str) -> str:
    """Create a spider chart comparing user scores vs industry averages"""
    
    # Get industry averages
    industry_avgs = get_industry_averages()
    
    # Define the dimensions in order
    dimensions = [
        'Sustainability Leadership',
        'Organization', 
        'Sustainability Risk Management',
        'Data & Systems',
        'People & Competency',
        'Asset Management',
        'Product Management',
        'Vendor Management',
        'Metrics & Reporting',
        'Managing Change'
    ]
    
    # Prepare data for chart
    user_values = []
    industry_values = []
    categories = []
    
    for dim in dimensions:
        if dim in user_scores:
            user_values.append(user_scores[dim])
            industry_values.append(industry_avgs.get(dim, 0))
            categories.append(dim)
    
    # Create the spider chart
    fig = go.Figure()
    
    # Add user scores trace
    fig.add_trace(go.Scatterpolar(
        r=user_values,
        theta=categories,
        fill='toself',
        name=f'{company_name} (Your Scores)',
        line=dict(color='#4CAF50', width=3),
        fillcolor='rgba(76, 175, 80, 0.3)',
        marker=dict(size=8, color='#4CAF50')
    ))
    
    # Add industry average trace
    fig.add_trace(go.Scatterpolar(
        r=industry_values,
        theta=categories,
        fill='toself',
        name='Industry Average',
        line=dict(color='#FF6B6B', width=2, dash='dash'),
        fillcolor='rgba(255, 107, 107, 0.1)',
        marker=dict(size=6, color='#FF6B6B')
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
                tickfont=dict(size=9),
                rotation=90,
                direction='clockwise'
            ),
            bgcolor='white'
        ),
        showlegend=True,
        title=dict(
            text=f"Sustainability Maturity Assessment - {company_name} vs Industry",
            x=0.5,
            font=dict(size=16, color='#4CAF50')
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        width=700,
        height=600,
        margin=dict(l=80, r=80, t=80, b=100),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    # Convert to base64 image
    img_bytes = pio.to_image(fig, format="png", width=700, height=600, scale=2)
    img_base64 = base64.b64encode(img_bytes).decode()
    
    return img_base64

def create_spider_chart_model(user_scores: Dict[str, float]) -> SpiderChartModel:
    """Create SpiderChartModel from user dimension scores"""
    # Initialize with default values
    chart_data = {
        'sustainability_leadership': 1,
        'organization': 1,
        'sustainability_risk_management': 1,
        'data_systems': 1,
        'people_competency': 1,
        'direct_asset_management': 1,
        'product_management': 1,
        'vendor_management': 1,
        'metrics_reporting': 1,
        'managing_change': 1
    }
    
    # Update with actual user scores
    for dimension, score in user_scores.items():
        if dimension in DIMENSION_MAPPING:
            chart_key = DIMENSION_MAPPING[dimension]["chart_key"]
            chart_data[chart_key] = int(round(score))
    
    return SpiderChartModel(**chart_data)

def generate_sustainability_report(user_scores: Dict[str, float], company_name: str, industry: str = None) -> str:
    """Generate a comprehensive sustainability report in markdown format"""
    
    report_sections = []
    
    # Header
    report_sections.append(f"# 🌱 Sustainability Maturity Assessment Report")
    report_sections.append(f"**Company:** {company_name}")
    report_sections.append(f"**Assessment Date:** {__import__('datetime').datetime.now().strftime('%B %d, %Y')}")
    report_sections.append("")
    
    # AI-Generated Executive Summary
    report_sections.append("## 📊 Executive Summary")
    industry_avgs = get_industry_averages()
    ai_summary = generate_executive_summary(user_scores, industry_avgs, company_name)
    report_sections.append(ai_summary)
    report_sections.append("")
    
    # Overall Score Information
    overall_score = round(sum(user_scores.values()) / len(user_scores), 2)
    overall_maturity = determine_maturity_level(overall_score)
    report_sections.append(f"**Overall Sustainability Maturity Score:** {overall_score}/5.0")
    report_sections.append(f"**Overall Maturity Level:** {overall_maturity.title()}")
    report_sections.append("")
    
    # AI-Powered Company Sustainability Insights
    report_sections.append("## 🔍 Company-Specific Sustainability Insights")
    try:
        sustainability_insights = get_company_sustainability_insights(company_name, industry)
        report_sections.append(sustainability_insights)
    except Exception as e:
        print(f"Error generating sustainability insights: {e}")
        report_sections.append("*Sustainability insights are currently unavailable. Please ensure API keys are configured.*")
    report_sections.append("")
    
    # Dimension Analysis
    report_sections.append("## 📈 Dimension Analysis & Recommendations")
    report_sections.append("")
    
    for dimension, score in user_scores.items():
        maturity_level = determine_maturity_level(score)
        recommendation = get_dimension_recommendation(dimension, maturity_level)
        
        report_sections.append(f"### {dimension}")
        report_sections.append(f"- **Score** - {score}/5.0")
        report_sections.append(f"- **Maturity Level** - {maturity_level.title()}")
        report_sections.append(f"- **Next Steps** - {recommendation}")
        report_sections.append("")
    
    # Industry Comparison
    report_sections.append("## 🏭 Industry Comparison")
    report_sections.append("| Dimension | Your Score | Industry Average | Gap |")
    report_sections.append("|-----------|------------|------------------|-----|")
    
    for dimension, score in user_scores.items():
        industry_avg = industry_avgs.get(dimension, 0)
        gap = round(score - industry_avg, 2)
        gap_indicator = "📈" if gap > 0 else "📉" if gap < 0 else "➡️"
        report_sections.append(f"| {dimension} | {score} | {industry_avg} | {gap_indicator} {gap:+.2f} |")
    
    report_sections.append("")
    
    # Key Insights
    strong_areas = [dim for dim, score in user_scores.items() if score >= 3.5]
    improvement_areas = [dim for dim, score in user_scores.items() if score < 2.5]
    
    report_sections.append("## 💡 Key Insights")
    
    if strong_areas:
        report_sections.append("### 🚀 Strengths")
        for area in strong_areas:
            report_sections.append(f"- **{area}:** Performing well with score of {user_scores[area]}")
        report_sections.append("")
    
    if improvement_areas:
        report_sections.append("### ⚠️ Areas for Improvement")
        for area in improvement_areas:
            report_sections.append(f"- **{area}:** Needs attention with score of {user_scores[area]}")
        report_sections.append("")
    
    # Recommendations Summary
    report_sections.append("## 🎯 Priority Actions")
    priority_dimensions = sorted(user_scores.items(), key=lambda x: x[1])[:3]
    
    for i, (dimension, score) in enumerate(priority_dimensions, 1):
        maturity_level = determine_maturity_level(score)
        recommendation = get_dimension_recommendation(dimension, maturity_level)
        report_sections.append(f"**{i}. {dimension}**")
        report_sections.append(f"   {recommendation}")
        report_sections.append("")
    
    return "\n".join(report_sections)

def process_questionnaire_responses(current_user: str, responses: Dict[str, int], company_name: str) -> Dict:
    """Main function to process questionnaire responses and generate complete analysis"""
    
    # Step 1: Calculate dimension averages
    dimension_averages = calculate_dimension_averages(responses)
    
    # Step 2: Create spider chart comparing user vs industry
    spider_chart_base64 = create_comparison_spider_chart(dimension_averages, company_name)
    
    # Step 3: Create spider chart model for compatibility with existing system
    spider_chart_model = create_spider_chart_model(dimension_averages)
    
    # Step 4: Generate comprehensive report
    user_industry = USERS.get(current_user, {}).get('industry', None)
    sustainability_report = generate_sustainability_report(dimension_averages, company_name, user_industry)
    
    # Step 5: Prepare result structure similar to langflow result
    result = {
        "success": True,
        "extracted_text": sustainability_report,
        "dimension_scores": dimension_averages,
        "spider_chart_base64": spider_chart_base64,
        "spider_chart_model": spider_chart_model,
        "overall_score": round(sum(dimension_averages.values()) / len(dimension_averages), 2),
        "maturity_level": determine_maturity_level(round(sum(dimension_averages.values()) / len(dimension_averages), 2))
    }
    
    return result 