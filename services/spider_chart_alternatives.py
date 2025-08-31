"""
Alternative implementations for spider chart generation without Kaleido dependency.

This module provides multiple options for creating spider charts:
1. Matplotlib-based polar plots
2. Plotly HTML charts (interactive)
3. Browser-based rendering using Playwright
4. Pure SVG implementation
5. Chart.js integration
"""

import math
import base64
import json
from typing import Dict, List, Tuple
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import plotly.graph_objects as go
import plotly.offline as pyo
from models import SpiderChartModel


class MatplotlibSpiderChart:
    """Spider chart implementation using Matplotlib polar plots"""
    
    @staticmethod
    def create_spider_chart(user_scores: Dict[str, float], company_name: str, 
                          industry_scores: Dict[str, float] = None) -> str:
        """Create spider chart using Matplotlib and return as base64 image"""
        
        # Prepare data
        dimensions = list(user_scores.keys())
        user_values = list(user_scores.values())
        
        # Number of dimensions
        num_dims = len(dimensions)
        angles = [n / float(num_dims) * 2 * math.pi for n in range(num_dims)]
        angles += angles[:1]  # Complete the circle
        
        # Create figure and polar subplot
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Add user scores
        user_values += user_values[:1]  # Complete the circle
        ax.plot(angles, user_values, 'o-', linewidth=3, label=f'{company_name} (Your Scores)', 
                color='#4CAF50', markersize=8)
        ax.fill(angles, user_values, alpha=0.25, color='#4CAF50')
        
        # Add industry scores if provided
        if industry_scores:
            industry_values = [industry_scores.get(dim, 0) for dim in dimensions]
            industry_values += industry_values[:1]  # Complete the circle
            ax.plot(angles, industry_values, 'o--', linewidth=2, label='Industry Average', 
                    color='#FF6B6B', markersize=6)
            ax.fill(angles, industry_values, alpha=0.1, color='#FF6B6B')
        
        # Customize the chart
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, fontsize=10)
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['Resist', 'Comply', 'Optimize', 'Reinvent', 'Lead'], 
                          fontsize=9, alpha=0.7)
        ax.grid(True, alpha=0.3)
        
        # Add title and legend
        plt.title(f'Sustainability Maturity Assessment - {company_name}', 
                 size=16, color='#4CAF50', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        img_data = buffer.getvalue()
        buffer.close()
        plt.close(fig)
        
        return base64.b64encode(img_data).decode()


class PlotlyHTMLChart:
    """Interactive spider chart using Plotly HTML (no Kaleido required)"""
    
    @staticmethod
    def create_interactive_spider_chart(user_scores: Dict[str, float], company_name: str,
                                      industry_scores: Dict[str, float] = None) -> str:
        """Create interactive Plotly HTML chart"""
        
        dimensions = list(user_scores.keys())
        user_values = list(user_scores.values())
        
        fig = go.Figure()
        
        # Add user scores trace
        fig.add_trace(go.Scatterpolar(
            r=user_values,
            theta=dimensions,
            fill='toself',
            name=f'{company_name} (Your Scores)',
            line=dict(color='#4CAF50', width=3),
            fillcolor='rgba(76, 175, 80, 0.3)',
            marker=dict(size=8, color='#4CAF50')
        ))
        
        # Add industry average trace if provided
        if industry_scores:
            industry_values = [industry_scores.get(dim, 0) for dim in dimensions]
            fig.add_trace(go.Scatterpolar(
                r=industry_values,
                theta=dimensions,
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
                text=f"Sustainability Maturity Assessment - {company_name}",
                x=0.5,
                font=dict(size=16, color='#4CAF50')
            ),
            width=700,
            height=600,
            margin=dict(l=80, r=80, t=80, b=100),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        # Return as HTML div
        return pyo.plot(fig, output_type='div', include_plotlyjs=True)


class PlaywrightSpiderChart:
    """Browser-based rendering using Playwright (already available in your requirements)"""
    
    @staticmethod
    async def create_spider_chart_with_browser(user_scores: Dict[str, float], 
                                             company_name: str,
                                             industry_scores: Dict[str, float] = None) -> str:
        """Create spider chart using browser rendering with Playwright"""
        from playwright.async_api import async_playwright
        
        # Create HTML with Chart.js
        html_content = PlaywrightSpiderChart._generate_chartjs_html(
            user_scores, company_name, industry_scores
        )
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set content and wait for chart to render
            await page.set_content(html_content)
            await page.wait_for_timeout(2000)  # Wait for chart rendering
            
            # Take screenshot of the chart
            chart_element = await page.query_selector('#chartContainer')
            screenshot = await chart_element.screenshot()
            
            await browser.close()
            
            return base64.b64encode(screenshot).decode()
    
    @staticmethod
    def _generate_chartjs_html(user_scores: Dict[str, float], company_name: str,
                             industry_scores: Dict[str, float] = None) -> str:
        """Generate HTML with Chart.js for spider chart"""
        
        dimensions = list(user_scores.keys())
        user_values = list(user_scores.values())
        
        datasets = [{
            'label': f'{company_name} (Your Scores)',
            'data': user_values,
            'borderColor': '#4CAF50',
            'backgroundColor': 'rgba(76, 175, 80, 0.3)',
            'borderWidth': 3,
            'pointBackgroundColor': '#4CAF50',
            'pointBorderColor': '#4CAF50',
            'pointRadius': 6
        }]
        
        if industry_scores:
            industry_values = [industry_scores.get(dim, 0) for dim in dimensions]
            datasets.append({
                'label': 'Industry Average',
                'data': industry_values,
                'borderColor': '#FF6B6B',
                'backgroundColor': 'rgba(255, 107, 107, 0.1)',
                'borderWidth': 2,
                'borderDash': [5, 5],
                'pointBackgroundColor': '#FF6B6B',
                'pointBorderColor': '#FF6B6B',
                'pointRadius': 4
            })
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <div id="chartContainer" style="width: 700px; height: 600px;">
                <canvas id="spiderChart"></canvas>
            </div>
            <script>
                const ctx = document.getElementById('spiderChart').getContext('2d');
                const chart = new Chart(ctx, {{
                    type: 'radar',
                    data: {{
                        labels: {json.dumps(dimensions)},
                        datasets: {json.dumps(datasets)}
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Sustainability Maturity Assessment - {company_name}',
                                font: {{
                                    size: 16,
                                    color: '#4CAF50'
                                }}
                            }},
                            legend: {{
                                position: 'bottom'
                            }}
                        }},
                        scales: {{
                            r: {{
                                min: 0,
                                max: 5,
                                ticks: {{
                                    stepSize: 1,
                                    callback: function(value) {{
                                        const labels = ['', 'Resist', 'Comply', 'Optimize', 'Reinvent', 'Lead'];
                                        return labels[value] || '';
                                    }}
                                }},
                                grid: {{
                                    color: 'rgba(0,0,0,0.1)'
                                }}
                            }}
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """


class SVGSpiderChart:
    """Pure SVG implementation for lightweight spider charts"""
    
    @staticmethod
    def create_svg_spider_chart(user_scores: Dict[str, float], company_name: str,
                               industry_scores: Dict[str, float] = None) -> str:
        """Create spider chart as SVG and return as base64 image"""
        
        dimensions = list(user_scores.keys())
        user_values = list(user_scores.values())
        num_dims = len(dimensions)
        
        # SVG settings
        width, height = 600, 600
        center_x, center_y = width // 2, height // 2
        max_radius = 200
        
        # Calculate angles for each dimension
        angles = [i * 2 * math.pi / num_dims - math.pi / 2 for i in range(num_dims)]
        
        svg_parts = []
        svg_parts.append(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">')
        svg_parts.append('<rect width="100%" height="100%" fill="white"/>')
        
        # Draw grid circles
        for i in range(1, 6):
            radius = (i / 5) * max_radius
            svg_parts.append(f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" '
                           f'fill="none" stroke="rgba(0,0,0,0.1)" stroke-width="1"/>')
        
        # Draw axis lines
        for angle in angles:
            end_x = center_x + max_radius * math.cos(angle)
            end_y = center_y + max_radius * math.sin(angle)
            svg_parts.append(f'<line x1="{center_x}" y1="{center_y}" '
                           f'x2="{end_x}" y2="{end_y}" '
                           f'stroke="rgba(0,0,0,0.1)" stroke-width="1"/>')
        
        # Draw user data polygon
        user_points = []
        for i, value in enumerate(user_values):
            radius = (value / 5) * max_radius
            x = center_x + radius * math.cos(angles[i])
            y = center_y + radius * math.sin(angles[i])
            user_points.append(f"{x},{y}")
        
        points_str = " ".join(user_points)
        svg_parts.append(f'<polygon points="{points_str}" '
                        f'fill="rgba(76, 175, 80, 0.3)" '
                        f'stroke="#4CAF50" stroke-width="3"/>')
        
        # Draw industry data polygon if provided
        if industry_scores:
            industry_values = [industry_scores.get(dim, 0) for dim in dimensions]
            industry_points = []
            for i, value in enumerate(industry_values):
                radius = (value / 5) * max_radius
                x = center_x + radius * math.cos(angles[i])
                y = center_y + radius * math.sin(angles[i])
                industry_points.append(f"{x},{y}")
            
            points_str = " ".join(industry_points)
            svg_parts.append(f'<polygon points="{points_str}" '
                            f'fill="rgba(255, 107, 107, 0.1)" '
                            f'stroke="#FF6B6B" stroke-width="2" stroke-dasharray="5,5"/>')
        
        # Add dimension labels
        for i, dimension in enumerate(dimensions):
            label_radius = max_radius + 30
            x = center_x + label_radius * math.cos(angles[i])
            y = center_y + label_radius * math.sin(angles[i])
            
            svg_parts.append(f'<text x="{x}" y="{y}" text-anchor="middle" '
                           f'dominant-baseline="central" font-size="12" font-family="Arial">'
                           f'{dimension}</text>')
        
        # Add title
        svg_parts.append(f'<text x="{center_x}" y="30" text-anchor="middle" '
                        f'font-size="16" font-family="Arial" fill="#4CAF50">'
                        f'Sustainability Maturity Assessment - {company_name}</text>')
        
        # Add scale labels
        scale_labels = ['Resist', 'Comply', 'Optimize', 'Reinvent', 'Lead']
        for i, label in enumerate(scale_labels, 1):
            radius = (i / 5) * max_radius
            svg_parts.append(f'<text x="{center_x + radius + 5}" y="{center_y}" '
                           f'font-size="10" font-family="Arial" fill="rgba(0,0,0,0.7)">'
                           f'{label}</text>')
        
        svg_parts.append('</svg>')
        svg_content = '\n'.join(svg_parts)
        
        # Convert SVG to base64
        return base64.b64encode(svg_content.encode()).decode()


# Wrapper functions to maintain compatibility with existing code
def create_matplotlib_spider_chart(user_scores: Dict[str, float], company_name: str,
                                  industry_scores: Dict[str, float] = None) -> str:
    """Matplotlib-based alternative to Kaleido"""
    return MatplotlibSpiderChart.create_spider_chart(user_scores, company_name, industry_scores)


def create_html_spider_chart(user_scores: Dict[str, float], company_name: str,
                           industry_scores: Dict[str, float] = None) -> str:
    """HTML-based interactive alternative"""
    return PlotlyHTMLChart.create_interactive_spider_chart(user_scores, company_name, industry_scores)


async def create_browser_spider_chart(user_scores: Dict[str, float], company_name: str,
                                     industry_scores: Dict[str, float] = None) -> str:
    """Browser-rendered alternative using Playwright"""
    return await PlaywrightSpiderChart.create_spider_chart_with_browser(
        user_scores, company_name, industry_scores
    )


def create_svg_spider_chart(user_scores: Dict[str, float], company_name: str,
                          industry_scores: Dict[str, float] = None) -> str:
    """Lightweight SVG alternative"""
    return SVGSpiderChart.create_svg_spider_chart(user_scores, company_name, industry_scores)
