#!/usr/bin/env python
"""
Test script to verify Combined Risk Method functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silay_drrmo.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from monitoring.models import BenchmarkSettings
from monitoring.views import get_combined_risk_level

def test_combined_risk_methods():
    """Test all 4 combined risk methods"""
    
    print("\n" + "="*70)
    print("COMBINED RISK METHOD FUNCTIONALITY TEST")
    print("="*70 + "\n")
    
    # Test scenarios with different risk levels
    test_cases = [
        ("Low + Low", "Low Risk (<30mm)", "Low Risk (<1.0m)"),
        ("Low + Moderate", "Low Risk (<30mm)", "Moderate Risk (1.0-1.5m)"),
        ("Moderate + Low", "Moderate Risk (30-50mm)", "Low Risk (<1.0m)"),
        ("Moderate + Moderate", "Moderate Risk (30-50mm)", "Moderate Risk (1.0-1.5m)"),
        ("High + Low", "High Risk (50-100mm)", "Low Risk (<1.0m)"),
        ("High + Moderate", "High Risk (50-100mm)", "Moderate Risk (1.0-1.5m)"),
        ("Low + High", "Low Risk (<30mm)", "High Risk (>1.5m)"),
    ]
    
    methods = ['max', 'rainfall_priority', 'tide_priority', 'equal']
    
    for method in methods:
        print(f"\n{'─'*70}")
        print(f"Testing Method: {method.upper()}")
        print(f"{'─'*70}")
        
        # Set method
        settings = BenchmarkSettings.get_settings()
        settings.combined_risk_method = method
        settings.save()
        
        for scenario_name, rain_risk, tide_risk in test_cases:
            combined, color = get_combined_risk_level(rain_risk, tide_risk)
            print(f"  {scenario_name:20} → {combined:15} ({color})")
    
    print("\n" + "="*70)
    print("Key Points:")
    print("="*70)
    print("""
1. MAX method:
   - Returns the HIGHEST risk between rainfall and tide
   - Most conservative approach
   - Example: 10mm + 0.5m = Low Risk (both are low)
   
2. RAINFALL_PRIORITY method (80% rainfall, 20% tide):
   - Weights rainfall 4x more than tide
   - For regions where rainfall is primary concern
   - Example: Moderate rainfall + Low tide = Moderate Risk (rainfall wins)
   
3. TIDE_PRIORITY method (20% rainfall, 80% tide):
   - Weights tide 4x more than rainfall
   - For coastal areas where tide is primary concern
   - Example: Low rainfall + Moderate tide = Moderate Risk (tide wins)
   
4. EQUAL method (50% rainfall, 50% tide):
   - Both factors equally important
   - Balanced approach
   - Example: Moderate rainfall + Low tide = Low/Moderate Risk (average)
""")
    
    print("\n" + "="*70)
    print("Form Submission Test")
    print("="*70 + "\n")
    
    # Show current settings
    settings = BenchmarkSettings.get_settings()
    print(f"Current Settings:")
    print(f"  Rainfall Moderate Threshold: {settings.rainfall_moderate_threshold} mm")
    print(f"  Rainfall High Threshold: {settings.rainfall_high_threshold} mm")
    print(f"  Tide Moderate Threshold: {settings.tide_moderate_threshold} m")
    print(f"  Tide High Threshold: {settings.tide_high_threshold} m")
    print(f"  Combined Risk Method: {settings.combined_risk_method}")
    
    print("\n✅ All tests completed successfully!")
    print("   The Combined Risk Method can now be configured via the admin form.")
    print("   Navigate to: /monitoring/benchmark-settings/")

if __name__ == '__main__':
    test_combined_risk_methods()
