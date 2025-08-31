"""
Alternative questionnaire processor without Kaleido dependency.
This version uses matplotlib or other alternatives for spider chart generation.
"""

from typing import Dict, List, Tuple
import base64
from models import SpiderChartModel
from config import QUESTIONS_DATA, RECOMMENDATIONS_DATA, SURVEY_DATA, DIMENSION_MAPPING, USERS
from services.openai_service import generate_executive_summary, get_company_sustainability_insights
from services.spider_chart_alternatives import (
    create_matplotlib_spider_chart,
    create_html_spider_chart,
    create_svg_spider_chart
)


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


def create_comparison_spider_chart(user_scores: Dict[str, float], company_name: str, 
                                 chart_type: str = "matplotlib") -> str:
    """
    Create a spider chart comparing user scores vs industry averages
    
    Args:
        user_scores: Dictionary of dimension scores
        company_name: Company name for chart title
        chart_type: Type of chart to generate ("matplotlib", "svg", "html")
    
    Returns:
        Base64 encoded image string or HTML string (depending on chart_type)
    """
    
    # Get industry averages
    industry_avgs = get_industry_averages()
    
    # Filter to ensure we only include dimensions that exist in user_scores
    filtered_industry_avgs = {dim: industry_avgs.get(dim, 0) for dim in user_scores.keys()}
    
    try:
        if chart_type == "matplotlib":
            return create_matplotlib_spider_chart(user_scores, company_name, filtered_industry_avgs)
        elif chart_type == "svg":
            return create_svg_spider_chart(user_scores, company_name, filtered_industry_avgs)
        elif chart_type == "html":
            return create_html_spider_chart(user_scores, company_name, filtered_industry_avgs)
        else:
            # Default to matplotlib
            return create_matplotlib_spider_chart(user_scores, company_name, filtered_industry_avgs)
    
    except Exception as e:
        print(f"Error creating spider chart with {chart_type}: {e}")
        # Fallback to SVG if other methods fail
        try:
            return create_svg_spider_chart(user_scores, company_name, filtered_industry_avgs)
        except Exception as svg_error:
            print(f"SVG fallback also failed: {svg_error}")
            # Return a placeholder base64 image
            return create_placeholder_chart_image(company_name)


def create_placeholder_chart_image(company_name: str) -> str:
    """Create a simple placeholder image when chart generation fails"""
    placeholder_svg = f'''
    <svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="white" stroke="#ddd"/>
        <text x="300" y="180" text-anchor="middle" font-size="18" font-family="Arial" fill="#666">
            Chart for {company_name}
        </text>
        <text x="300" y="220" text-anchor="middle" font-size="14" font-family="Arial" fill="#999">
            Chart generation temporarily unavailable
        </text>
    </svg>
    '''
    return base64.b64encode(placeholder_svg.encode()).decode()


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
    try:
        ai_summary = generate_executive_summary(user_scores, industry_avgs, company_name)
        report_sections.append(ai_summary)
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        report_sections.append("*Executive summary generation temporarily unavailable.*")
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


def process_questionnaire_responses(current_user: str, responses: Dict[str, int], 
                                  company_name: str, chart_type: str = "matplotlib") -> Dict:
    """
    Main function to process questionnaire responses and generate complete analysis
    
    Args:
        current_user: Current user identifier
        responses: Dictionary of question responses
        company_name: Company name
        chart_type: Type of chart to generate ("matplotlib", "svg", "html")
    
    Returns:
        Dictionary containing analysis results
    """
    
    # Step 1: Calculate dimension averages
    dimension_averages = calculate_dimension_averages(responses)
    
    # Step 2: Create spider chart comparing user vs industry
    spider_chart_base64 = create_comparison_spider_chart(dimension_averages, company_name, chart_type)
    
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
        "maturity_level": determine_maturity_level(round(sum(dimension_averages.values()) / len(dimension_averages), 2)),
        "chart_type": chart_type
    }
    
    return result
