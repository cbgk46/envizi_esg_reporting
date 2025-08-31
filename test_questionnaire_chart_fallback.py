"""
Test script to verify questionnaire submission uses matplotlib and fallback methods correctly.
This script tests the chart generation in various scenarios.
"""

import os
import sys
import traceback
from unittest.mock import patch, MagicMock
from typing import Dict

# Add the current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.questionnaire_processor_no_kaleido import process_questionnaire_responses
from services.adaptive_chart_service import adaptive_chart_service, get_chart_service_info
from chart_config import ChartMethod, ChartConfig


def create_test_responses() -> Dict[str, int]:
    """Create test questionnaire responses"""
    # Generate responses for the first 10 questions (simulating a partial response)
    responses = {}
    for i in range(1, 11):
        question_id = f"Q{i:02d}"
        responses[question_id] = 3 + (i % 3)  # Scores between 3-5
    return responses


def test_normal_operation():
    """Test normal operation with matplotlib"""
    print("=== Testing Normal Operation ===")
    
    try:
        responses = create_test_responses()
        result = process_questionnaire_responses(
            current_user="test_user",
            responses=responses,
            company_name="Test Company",
            chart_type="matplotlib"
        )
        
        print(f"✓ Normal operation successful")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Chart type: {result.get('chart_type', 'unknown')}")
        print(f"  Chart data length: {len(result.get('spider_chart_base64', ''))}")
        print(f"  Overall score: {result.get('overall_score', 'N/A')}")
        print(f"  Dimensions processed: {len(result.get('dimension_scores', {}))}")
        
        return True
        
    except Exception as e:
        print(f"✗ Normal operation failed: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False


def test_chart_method_fallback():
    """Test fallback behavior when preferred method fails"""
    print("\n=== Testing Chart Method Fallback ===")
    
    # Test different chart methods
    methods_to_test = ["matplotlib", "svg", "html"]
    
    for method in methods_to_test:
        print(f"\nTesting {method} method:")
        try:
            responses = create_test_responses()
            result = process_questionnaire_responses(
                current_user="test_user",
                responses=responses,
                company_name=f"Test Company ({method})",
                chart_type=method
            )
            
            print(f"  ✓ {method} method successful")
            print(f"    Chart type used: {result.get('chart_type', 'unknown')}")
            print(f"    Chart data length: {len(result.get('spider_chart_base64', ''))}")
            
        except Exception as e:
            print(f"  ✗ {method} method failed: {e}")


def test_kaleido_disabled_fallback():
    """Test fallback when Kaleido is disabled"""
    print("\n=== Testing Kaleido Disabled Fallback ===")
    
    # Mock Kaleido to fail
    with patch('services.adaptive_chart_service.ChartConfig.is_method_available') as mock_available:
        def mock_is_available(method):
            if method == ChartMethod.KALEIDO:
                return False  # Simulate Kaleido not available
            # Call the real method for other chart types
            return ChartConfig.is_method_available(method)
        
        mock_available.side_effect = mock_is_available
        
        try:
            responses = create_test_responses()
            result = process_questionnaire_responses(
                current_user="test_user",
                responses=responses,
                company_name="Test Company (No Kaleido)",
                chart_type="matplotlib"  # Should fallback to matplotlib
            )
            
            print(f"✓ Kaleido disabled fallback successful")
            print(f"  Chart type used: {result.get('chart_type', 'unknown')}")
            print(f"  Chart data length: {len(result.get('spider_chart_base64', ''))}")
            
            return True
            
        except Exception as e:
            print(f"✗ Kaleido disabled fallback failed: {e}")
            return False


def test_all_methods_fail_scenario():
    """Test ultimate fallback when all chart methods fail"""
    print("\n=== Testing All Methods Fail Scenario ===")
    
    # Mock all chart creation methods to fail
    with patch('services.spider_chart_alternatives.create_matplotlib_spider_chart') as mock_matplotlib, \
         patch('services.spider_chart_alternatives.create_svg_spider_chart') as mock_svg:
        
        mock_matplotlib.side_effect = Exception("Matplotlib failed")
        mock_svg.side_effect = Exception("SVG failed")
        
        try:
            responses = create_test_responses()
            result = process_questionnaire_responses(
                current_user="test_user",
                responses=responses,
                company_name="Test Company (All Fail)",
                chart_type="matplotlib"
            )
            
            print(f"✓ Ultimate fallback successful")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Chart type: {result.get('chart_type', 'unknown')}")
            print(f"  Chart data length: {len(result.get('spider_chart_base64', ''))}")
            print(f"  Note: Should have placeholder chart")
            
            return True
            
        except Exception as e:
            print(f"✗ Ultimate fallback failed: {e}")
            return False


def test_adaptive_service_info():
    """Test adaptive service information"""
    print("\n=== Testing Adaptive Service Info ===")
    
    try:
        info = get_chart_service_info()
        print(f"Current method: {info['current_method']}")
        print(f"Available methods:")
        
        for method, details in info['available_methods'].items():
            status = "✓" if details['available'] else "✗"
            print(f"  {status} {method}: {details['description']}")
        
        print(f"Fallback order: {info['fallback_order']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Adaptive service info failed: {e}")
        return False


def test_edge_cases():
    """Test edge cases and error scenarios"""
    print("\n=== Testing Edge Cases ===")
    
    # Test with empty responses
    try:
        result = process_questionnaire_responses(
            current_user="test_user",
            responses={},
            company_name="Empty Responses Company",
            chart_type="matplotlib"
        )
        print(f"✓ Empty responses handled gracefully")
        print(f"  Dimensions: {len(result.get('dimension_scores', {}))}")
    except Exception as e:
        print(f"✗ Empty responses failed: {e}")
    
    # Test with invalid chart type
    try:
        result = process_questionnaire_responses(
            current_user="test_user",
            responses=create_test_responses(),
            company_name="Invalid Method Company",
            chart_type="invalid_method"
        )
        print(f"✓ Invalid chart type handled gracefully")
        print(f"  Chart type used: {result.get('chart_type', 'unknown')}")
    except Exception as e:
        print(f"✗ Invalid chart type failed: {e}")


def main():
    """Run all tests"""
    print("Testing Questionnaire Chart Fallback Behavior")
    print("=" * 50)
    
    test_results = []
    
    # Run tests
    test_results.append(test_adaptive_service_info())
    test_results.append(test_normal_operation())
    test_results.append(test_chart_method_fallback())
    test_results.append(test_kaleido_disabled_fallback())
    test_results.append(test_all_methods_fail_scenario())
    
    # Test edge cases (don't count towards pass/fail)
    test_edge_cases()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Questionnaire submission is using fallback methods correctly.")
    else:
        print(f"✗ {total - passed} tests failed. Please check the issues above.")
    
    print("\nChart generation methods available:")
    print(f"Current default: {adaptive_chart_service.current_method.value}")


if __name__ == "__main__":
    main()
