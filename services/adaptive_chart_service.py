"""
Adaptive chart service that automatically selects the best available chart generation method.
This service provides a unified interface while handling different chart generation backends.
"""

import asyncio
from typing import Dict, Optional, Union
from models import SpiderChartModel
from chart_config import ChartMethod, ChartConfig
from services.spider_chart_alternatives import (
    create_matplotlib_spider_chart,
    create_html_spider_chart,
    create_svg_spider_chart,
    create_browser_spider_chart
)


class AdaptiveChartService:
    """Service that adapts chart generation based on available dependencies"""
    
    def __init__(self):
        self.current_method = ChartConfig.get_available_method()
        print(f"AdaptiveChartService initialized with method: {self.current_method.value}")
    
    def create_spider_chart(self, scores: SpiderChartModel, company_name: str) -> str:
        """
        Create a spider chart from sustainability scores using the best available method
        
        Args:
            scores: SpiderChartModel containing dimension scores
            company_name: Company name for chart title
            
        Returns:
            Base64 encoded image string
        """
        # Convert SpiderChartModel to dictionary
        user_scores = self._spider_model_to_dict(scores)
        
        return self.create_comparison_spider_chart(user_scores, company_name)
    
    def create_comparison_spider_chart(self, user_scores: Dict[str, float], 
                                     company_name: str,
                                     industry_scores: Optional[Dict[str, float]] = None) -> str:
        """
        Create a comparison spider chart using the best available method
        
        Args:
            user_scores: Dictionary of dimension scores
            company_name: Company name for chart title
            industry_scores: Optional industry average scores for comparison
            
        Returns:
            Base64 encoded image string or HTML string (depending on method)
        """
        try:
            if self.current_method == ChartMethod.KALEIDO:
                return self._create_kaleido_chart(user_scores, company_name, industry_scores)
            elif self.current_method == ChartMethod.MATPLOTLIB:
                return create_matplotlib_spider_chart(user_scores, company_name, industry_scores)
            elif self.current_method == ChartMethod.SVG:
                return create_svg_spider_chart(user_scores, company_name, industry_scores)
            elif self.current_method == ChartMethod.HTML:
                return create_html_spider_chart(user_scores, company_name, industry_scores)
            elif self.current_method == ChartMethod.PLAYWRIGHT:
                # Playwright method is async, so we need to handle it specially
                return asyncio.run(create_browser_spider_chart(user_scores, company_name, industry_scores))
            else:
                # Fallback to matplotlib
                return create_matplotlib_spider_chart(user_scores, company_name, industry_scores)
                
        except Exception as e:
            print(f"Error creating chart with {self.current_method.value}: {e}")
            return self._fallback_chart_creation(user_scores, company_name, industry_scores)
    
    async def create_comparison_spider_chart_async(self, user_scores: Dict[str, float], 
                                                 company_name: str,
                                                 industry_scores: Optional[Dict[str, float]] = None) -> str:
        """
        Async version of create_comparison_spider_chart for use in async contexts
        """
        try:
            if self.current_method == ChartMethod.PLAYWRIGHT:
                return await create_browser_spider_chart(user_scores, company_name, industry_scores)
            else:
                # For non-async methods, run in thread pool
                return await asyncio.get_event_loop().run_in_executor(
                    None, self.create_comparison_spider_chart, user_scores, company_name, industry_scores
                )
        except Exception as e:
            print(f"Error creating async chart with {self.current_method.value}: {e}")
            return await asyncio.get_event_loop().run_in_executor(
                None, self._fallback_chart_creation, user_scores, company_name, industry_scores
            )
    
    def _create_kaleido_chart(self, user_scores: Dict[str, float], company_name: str,
                            industry_scores: Optional[Dict[str, float]] = None) -> str:
        """Create chart using original Kaleido method"""
        try:
            import plotly.graph_objects as go
            import plotly.io as pio
            import base64
            
            # Ensure Kaleido is initialized
            self._ensure_kaleido_initialized()
            
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
            
            # Convert to base64 image
            img_bytes = pio.to_image(fig, format="png", width=700, height=600, scale=2)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return img_base64
            
        except Exception as e:
            print(f"Kaleido chart creation failed: {e}")
            raise
    
    def _ensure_kaleido_initialized(self):
        """Initialize Kaleido Chrome if not already done"""
        try:
            import kaleido
            import plotly.io as pio
            import plotly.graph_objects as go
            
            # Check if kaleido is already initialized by trying a simple operation
            try:
                pio.to_image(go.Figure(), format="png", width=100, height=100)
            except Exception:
                # If it fails, initialize kaleido
                print("Initializing Kaleido Chrome for chart generation...")
                kaleido.get_chrome_sync()
                print("Kaleido Chrome initialized successfully")
                
        except Exception as e:
            print(f"Warning: Kaleido initialization failed: {e}")
            raise RuntimeError("Chart generation is currently unavailable. Kaleido initialization failed.")
    
    def _fallback_chart_creation(self, user_scores: Dict[str, float], company_name: str,
                               industry_scores: Optional[Dict[str, float]] = None) -> str:
        """Fallback chart creation when primary method fails"""
        fallback_methods = [
            (ChartMethod.MATPLOTLIB, create_matplotlib_spider_chart),
            (ChartMethod.SVG, create_svg_spider_chart),
        ]
        
        for method, create_func in fallback_methods:
            if ChartConfig.is_method_available(method):
                try:
                    print(f"Attempting fallback to {method.value}")
                    return create_func(user_scores, company_name, industry_scores)
                except Exception as e:
                    print(f"Fallback method {method.value} also failed: {e}")
                    continue
        
        # Ultimate fallback - create a placeholder
        return self._create_placeholder_chart(company_name)
    
    def _create_placeholder_chart(self, company_name: str) -> str:
        """Create a placeholder chart when all methods fail"""
        import base64
        
        placeholder_svg = f'''
        <svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="white" stroke="#ddd" stroke-width="2"/>
            <text x="300" y="180" text-anchor="middle" font-size="18" font-family="Arial" fill="#666">
                Sustainability Assessment Chart
            </text>
            <text x="300" y="200" text-anchor="middle" font-size="16" font-family="Arial" fill="#4CAF50">
                {company_name}
            </text>
            <text x="300" y="240" text-anchor="middle" font-size="12" font-family="Arial" fill="#999">
                Chart generation temporarily unavailable
            </text>
        </svg>
        '''
        return base64.b64encode(placeholder_svg.encode()).decode()
    
    def _spider_model_to_dict(self, scores: SpiderChartModel) -> Dict[str, float]:
        """Convert SpiderChartModel to dictionary format"""
        # Define mapping from model attributes to dimension names
        dimension_mapping = {
            'sustainability_leadership': 'Sustainability Leadership',
            'organization': 'Organization',
            'sustainability_risk_management': 'Sustainability Risk Management',
            'data_systems': 'Data & Systems',
            'people_competency': 'People & Competency',
            'direct_asset_management': 'Asset Management',
            'product_management': 'Product Management',
            'vendor_management': 'Vendor Management',
            'metrics_reporting': 'Metrics & Reporting',
            'managing_change': 'Managing Change'
        }
        
        result = {}
        for attr, display_name in dimension_mapping.items():
            if hasattr(scores, attr):
                result[display_name] = float(getattr(scores, attr))
        
        return result
    
    def get_method_info(self) -> dict:
        """Get information about current chart method"""
        return {
            "current_method": self.current_method.value,
            "available_methods": ChartConfig.get_method_info(),
            "fallback_order": [method.value for method in ChartConfig.FALLBACK_ORDER]
        }
    
    def switch_method(self, method: Union[str, ChartMethod]) -> bool:
        """
        Switch to a different chart generation method
        
        Args:
            method: Method to switch to (string or ChartMethod enum)
            
        Returns:
            True if switch was successful, False otherwise
        """
        if isinstance(method, str):
            try:
                method = ChartMethod(method.lower())
            except ValueError:
                print(f"Unknown chart method: {method}")
                return False
        
        if ChartConfig.is_method_available(method):
            self.current_method = method
            print(f"Switched to chart method: {method.value}")
            return True
        else:
            print(f"Chart method {method.value} is not available")
            return False


# Create a global instance for easy access
adaptive_chart_service = AdaptiveChartService()


# Convenience functions that use the global instance
def create_spider_chart(scores: SpiderChartModel, company_name: str) -> str:
    """Create spider chart using adaptive service"""
    return adaptive_chart_service.create_spider_chart(scores, company_name)


def create_comparison_spider_chart(user_scores: Dict[str, float], company_name: str,
                                 industry_scores: Optional[Dict[str, float]] = None) -> str:
    """Create comparison spider chart using adaptive service"""
    return adaptive_chart_service.create_comparison_spider_chart(user_scores, company_name, industry_scores)


async def create_comparison_spider_chart_async(user_scores: Dict[str, float], company_name: str,
                                             industry_scores: Optional[Dict[str, float]] = None) -> str:
    """Create comparison spider chart asynchronously using adaptive service"""
    return await adaptive_chart_service.create_comparison_spider_chart_async(user_scores, company_name, industry_scores)


def get_chart_service_info() -> dict:
    """Get information about the chart service"""
    return adaptive_chart_service.get_method_info()


def switch_chart_method(method: Union[str, ChartMethod]) -> bool:
    """Switch chart generation method"""
    return adaptive_chart_service.switch_method(method)
