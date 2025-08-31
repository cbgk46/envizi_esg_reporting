"""
Configuration for spider chart generation methods.
This allows easy switching between different chart generation approaches.
"""

import os
from enum import Enum


class ChartMethod(Enum):
    """Available chart generation methods"""
    KALEIDO = "kaleido"           # Original Plotly + Kaleido (requires Kaleido)
    MATPLOTLIB = "matplotlib"     # Matplotlib polar plots (reliable, static)
    SVG = "svg"                  # Pure SVG generation (lightweight, fast)
    HTML = "html"                # Interactive Plotly HTML (for web embedding)
    PLAYWRIGHT = "playwright"     # Browser-based rendering (high quality)


class ChartConfig:
    """Configuration class for chart generation"""
    
    # Default chart method - can be overridden by environment variable
    DEFAULT_METHOD = ChartMethod.MATPLOTLIB
    
    # Chart method preferences in order of fallback
    FALLBACK_ORDER = [
        ChartMethod.MATPLOTLIB,
        ChartMethod.SVG,
        ChartMethod.KALEIDO,
        ChartMethod.HTML
    ]
    
    @classmethod
    def get_chart_method(cls) -> ChartMethod:
        """Get the configured chart method"""
        method_str = os.getenv('CHART_METHOD', cls.DEFAULT_METHOD.value).lower()
        
        try:
            return ChartMethod(method_str)
        except ValueError:
            print(f"Warning: Unknown chart method '{method_str}', using default: {cls.DEFAULT_METHOD.value}")
            return cls.DEFAULT_METHOD
    
    @classmethod
    def is_method_available(cls, method: ChartMethod) -> bool:
        """Check if a chart method is available based on dependencies"""
        if method == ChartMethod.KALEIDO:
            try:
                import kaleido
                import plotly.io as pio
                # Test if kaleido works
                pio.to_image({"data": [], "layout": {}}, format="png", width=100, height=100)
                return True
            except:
                return False
        
        elif method == ChartMethod.MATPLOTLIB:
            try:
                import matplotlib.pyplot as plt
                import numpy as np
                return True
            except ImportError:
                return False
        
        elif method == ChartMethod.SVG:
            # SVG generation only requires basic Python
            return True
        
        elif method == ChartMethod.HTML:
            try:
                import plotly.graph_objects as go
                import plotly.offline as pyo
                return True
            except ImportError:
                return False
        
        elif method == ChartMethod.PLAYWRIGHT:
            try:
                import playwright
                return True
            except ImportError:
                return False
        
        return False
    
    @classmethod
    def get_available_method(cls) -> ChartMethod:
        """Get the first available chart method from preferences"""
        preferred_method = cls.get_chart_method()
        
        # Check if preferred method is available
        if cls.is_method_available(preferred_method):
            return preferred_method
        
        # Fallback to first available method
        for method in cls.FALLBACK_ORDER:
            if cls.is_method_available(method):
                print(f"Preferred method {preferred_method.value} unavailable, using {method.value}")
                return method
        
        # If nothing else works, return SVG (should always work)
        print("Warning: No chart methods available, falling back to SVG")
        return ChartMethod.SVG
    
    @classmethod
    def get_method_info(cls) -> dict:
        """Get information about all chart methods"""
        return {
            method.value: {
                "available": cls.is_method_available(method),
                "description": cls._get_method_description(method)
            }
            for method in ChartMethod
        }
    
    @classmethod
    def _get_method_description(cls, method: ChartMethod) -> str:
        """Get description for a chart method"""
        descriptions = {
            ChartMethod.KALEIDO: "Plotly with Kaleido - High quality static images (requires Kaleido)",
            ChartMethod.MATPLOTLIB: "Matplotlib polar plots - Reliable and widely supported",
            ChartMethod.SVG: "Pure SVG generation - Lightweight and fast",
            ChartMethod.HTML: "Interactive Plotly HTML - Great for web embedding",
            ChartMethod.PLAYWRIGHT: "Browser-based rendering - Highest quality output"
        }
        return descriptions.get(method, "Unknown method")


# Convenience functions
def get_current_chart_method() -> ChartMethod:
    """Get the currently configured chart method"""
    return ChartConfig.get_available_method()


def set_chart_method(method: str):
    """Set the chart method via environment variable"""
    os.environ['CHART_METHOD'] = method


def list_available_methods() -> list:
    """List all available chart methods"""
    return [
        method.value for method in ChartMethod 
        if ChartConfig.is_method_available(method)
    ]


def print_chart_status():
    """Print status of all chart methods"""
    print("Chart Generation Methods Status:")
    print("=" * 40)
    
    for method, info in ChartConfig.get_method_info().items():
        status = "✓ Available" if info["available"] else "✗ Unavailable"
        print(f"{method:12} | {status:12} | {info['description']}")
    
    current = get_current_chart_method()
    print(f"\nCurrent method: {current.value}")


if __name__ == "__main__":
    print_chart_status()
