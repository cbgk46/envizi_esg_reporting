import plotly.graph_objects as go
import plotly.io as pio
import base64
from models import SpiderChartModel

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