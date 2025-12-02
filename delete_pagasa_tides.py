"""
Auto-delete PAGASA tide records (non-interactive)
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silay_drrmo.settings')
django.setup()

from monitoring.models import TideLevelData

print("=" * 80)
print("REMOVING OLD PAGASA TIDE RECORDS")
print("=" * 80)

# Delete PAGASA tide records
pagasa_tides = TideLevelData.objects.filter(station_name__contains='PAGASA')
count = pagasa_tides.count()

if count > 0:
    print(f"\nFound {count} PAGASA tide record(s):")
    for tide in pagasa_tides:
        print(f"  - {tide.height_m}m at {tide.timestamp} (Station: {tide.station_name})")
    
    pagasa_tides.delete()
    print(f"\n✅ Deleted {count} PAGASA tide record(s)")
else:
    print("\n✅ No PAGASA tide records found (already clean)")

# Show current tide data
print("\n" + "=" * 80)
print("CURRENT TIDE DATA:")
print("=" * 80)
latest = TideLevelData.objects.last()
if latest:
    from django.utils import timezone
    age_seconds = (timezone.now() - latest.timestamp).total_seconds()
    age_hours = age_seconds / 3600
    
    print(f"\nLatest Record:")
    print(f"  Height: {latest.height_m}m")
    print(f"  Station: {latest.station_name}")
    print(f"  Timestamp: {latest.timestamp}")
    print(f"  Age: {age_hours:.1f} hours")
    
    if age_seconds > 10800:  # 3 hours
        print(f"\n✅ Data is >3 hours old - Will fetch fresh WorldTides data on next visit")
    else:
        remaining = (10800 - age_seconds) / 3600
        print(f"\n⏳ Data is fresh - Will fetch new data in {remaining:.1f} hours")
else:
    print("\n❌ No tide data in database")
    print("✅ Will fetch fresh WorldTides data on next dashboard visit")

print("\n" + "=" * 80)
print("NEXT STEP: Visit your dashboard to fetch WorldTides (Cebu City) data")
print("=" * 80)
