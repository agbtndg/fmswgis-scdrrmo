"""
Test script to verify the AND-based combined risk logic
Usage: python test_and_based_logic.py
"""

import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silay_drrmo.settings')
django.setup()

from monitoring.views import get_combined_risk_level
from monitoring.models import BenchmarkSettings

def test_and_based_logic():
    """Test the AND-based combined risk logic"""
    
    settings = BenchmarkSettings.get_settings()
    
    print("\n" + "="*70)
    print("AND-BASED COMBINED RISK LOGIC TEST")
    print("="*70)
    
    print(f"\nCurrent Thresholds:")
    print(f"  Rainfall Moderate:  {settings.rainfall_moderate_threshold}mm")
    print(f"  Rainfall High:      {settings.rainfall_high_threshold}mm")
    print(f"  Tide Moderate:      {settings.tide_moderate_threshold}m")
    print(f"  Tide High:          {settings.tide_high_threshold}m")
    
    print("\n" + "-"*70)
    print("TEST CASES")
    print("-"*70)
    
    test_cases = [
        # (rainfall_mm, tide_m, expected_risk, description)
        (32, 0.3, "Low Risk", "Rainfall met moderate BUT tide didn't (0.3 < 0.8)"),
        (15, 1.2, "Moderate Risk", "Both met moderate thresholds (15>=10 AND 1.2>=0.8)"),
        (8, 1.2, "Low Risk", "Tide met moderate BUT rainfall didn't (8 < 10)"),
        (55, 1.6, "High Risk", "Both met high thresholds"),
        (100, 0.5, "Low Risk", "Rainfall met high BUT tide didn't (0.5 < 0.8)"),
        (10, 2.0, "Moderate Risk", "Both met moderate (tide exceeded) (10>=10 AND 2.0>=0.8)"),
        (50, 1.5, "High Risk", "Both at/above high thresholds"),
        (30, 0.8, "Moderate Risk", "Both at exact moderate thresholds"),
        (9.9, 0.79, "Low Risk", "Both just below moderate thresholds"),
    ]
    
    passed = 0
    failed = 0
    
    for rainfall, tide, expected, description in test_cases:
        risk_level, color = get_combined_risk_level(rainfall, tide)
        status = "✓ PASS" if risk_level == expected else "✗ FAIL"
        
        if risk_level == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}")
        print(f"  Input:    Rainfall {rainfall}mm, Tide {tide}m")
        print(f"  Expected: {expected}")
        print(f"  Got:      {risk_level} ({color})")
        print(f"  Reason:   {description}")
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*70 + "\n")
    
    if failed == 0:
        print("✓ All tests passed! AND-based logic is working correctly.\n")
        return True
    else:
        print("✗ Some tests failed. Check the logic implementation.\n")
        return False

if __name__ == '__main__':
    success = test_and_based_logic()
    exit(0 if success else 1)
