"""
Clean up old PAGASA tide data and verify system is ready for WorldTides
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silay_drrmo.settings')
django.setup()

from monitoring.models import TideLevelData
from django.utils import timezone

print("=" * 80)
print("TIDE DATA CLEANUP & VERIFICATION")
print("=" * 80)

# Show current tide data
print("\nCURRENT TIDE DATA IN DATABASE:")
print("-" * 80)
recent_tides = TideLevelData.objects.all().order_by('-timestamp')[:10]

for i, tide in enumerate(recent_tides, 1):
    print(f"{i}. Height: {tide.height_m}m | Station: {tide.station_name} | Time: {tide.timestamp}")

# Check for old PAGASA data
pagasa_tides = TideLevelData.objects.filter(station_name__contains='PAGASA')
print(f"\nFound {pagasa_tides.count()} PAGASA tide records")

worldtides_tides = TideLevelData.objects.filter(station_name__contains='WorldTides')
print(f"Found {worldtides_tides.count()} WorldTides records")

default_tides = TideLevelData.objects.filter(station_name='Default')
print(f"Found {default_tides.count()} Default records")

# Ask user what to do
print("\n" + "=" * 80)
print("OPTIONS:")
print("=" * 80)
print("1. Keep all data (recommended for historical analysis)")
print("2. Delete only PAGASA tide records")
print("3. Delete ALL tide records (fresh start)")
print("\nℹ️  Note: New data will be fetched when you visit the dashboard")

choice = input("\nEnter your choice (1/2/3) or 'cancel': ").strip()

if choice == '2':
    count = pagasa_tides.count()
    pagasa_tides.delete()
    print(f"\n✅ Deleted {count} PAGASA tide records")
    print("   Next dashboard visit will fetch WorldTides data")
    
elif choice == '3':
    count = TideLevelData.objects.all().count()
    confirm = input(f"\n⚠️  This will delete ALL {count} tide records. Type 'yes' to confirm: ")
    if confirm.lower() == 'yes':
        TideLevelData.objects.all().delete()
        print(f"\n✅ Deleted all {count} tide records")
        print("   Next dashboard visit will fetch fresh WorldTides data")
    else:
        print("\n❌ Cancelled")
        
elif choice == '1':
    print("\n✅ Keeping all data")
    print("   Old PAGASA records will remain for historical reference")
    print("   New WorldTides data will be added on next fetch (if >3 hours old)")
    
else:
    print("\n❌ Cancelled")

print("\n" + "=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print("1. Start your Django development server")
print("2. Visit the monitoring dashboard")
print("3. System will automatically fetch WorldTides data for Cebu City")
print("4. Run verify_data_sources.py again to confirm")
print("=" * 80)
