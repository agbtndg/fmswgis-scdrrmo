"""
Quick check: When will the system fetch new tide data?
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silay_drrmo.settings')
django.setup()

from monitoring.models import TideLevelData
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("TIDE DATA UPDATE CHECK")
print("=" * 80)

tide_data = TideLevelData.objects.last()

if tide_data:
    now = timezone.now()
    age_seconds = (now - tide_data.timestamp).total_seconds()
    age_hours = age_seconds / 3600
    age_minutes = (age_seconds % 3600) / 60
    
    print(f"\n📊 CURRENT TIDE DATA:")
    print(f"   Height: {tide_data.height_m}m")
    print(f"   Station: {tide_data.station_name}")
    print(f"   Timestamp: {tide_data.timestamp}")
    print(f"   Age: {int(age_hours)}h {int(age_minutes)}m ({int(age_seconds)}s)")
    
    update_threshold = 10800  # 3 hours
    
    print(f"\n⏰ UPDATE POLICY:")
    print(f"   System fetches new tide data every: {update_threshold/3600} hours")
    print(f"   Current data age: {age_hours:.1f} hours")
    
    if age_seconds > update_threshold:
        print(f"\n   ✅ DATA IS OLD: Will fetch NEW data on next dashboard visit")
        next_update = "Immediately when you visit the dashboard"
    else:
        time_until_update = update_threshold - age_seconds
        hours = int(time_until_update / 3600)
        minutes = int((time_until_update % 3600) / 60)
        next_update = f"In {hours}h {minutes}m"
        print(f"\n   ⏳ DATA IS FRESH: Will fetch new data in {hours}h {minutes}m")
    
    print(f"\n🔄 NEXT UPDATE: {next_update}")
    
    # Check if it's PAGASA data
    if 'PAGASA' in tide_data.station_name:
        print(f"\n⚠️  WARNING: Current data is from OLD PAGASA source")
        print(f"   This should be replaced with WorldTides (Cebu City)")
        print(f"\n💡 TO FIX IMMEDIATELY:")
        print(f"   Run: python cleanup_tide_data.py")
        print(f"   Choose option 2 to delete PAGASA records")
        print(f"   Then visit your dashboard to fetch WorldTides data")
    elif 'WorldTides' in tide_data.station_name:
        print(f"\n✅ Current data is from WorldTides (Cebu City) - CORRECT!")
    elif tide_data.station_name == 'Default':
        print(f"\n❌ Using DEFAULT value (0.8m)")
        print(f"   WorldTides API may have failed")
        print(f"   Check your WORLDTIDES_API_KEY in settings.py")

else:
    print("\n❌ NO TIDE DATA IN DATABASE")
    print("   Visit the dashboard to fetch initial data")

print("\n" + "=" * 80)
