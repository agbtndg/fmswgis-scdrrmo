"""
Script to clear all rainfall and tide level trend data from the database
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silay_drrmo.settings')
django.setup()

from monitoring.models import RainfallData, TideLevelData

def clear_trend_data():
    """Delete all rainfall and tide level data"""
    
    # Count existing records
    rainfall_count = RainfallData.objects.count()
    tide_count = TideLevelData.objects.count()
    
    print("=" * 60)
    print("CLEARING TREND DATA")
    print("=" * 60)
    print(f"\nCurrent Records:")
    print(f"  - Rainfall Data: {rainfall_count} records")
    print(f"  - Tide Level Data: {tide_count} records")
    
    if rainfall_count == 0 and tide_count == 0:
        print("\n✓ Database is already empty. No data to delete.")
        return
    
    # Confirm deletion
    print("\n" + "!" * 60)
    print("WARNING: This will permanently delete all trend data!")
    print("!" * 60)
    confirm = input("\nType 'YES' to confirm deletion: ")
    
    if confirm != 'YES':
        print("\n✗ Deletion cancelled.")
        return
    
    # Delete all records
    print("\nDeleting records...")
    RainfallData.objects.all().delete()
    TideLevelData.objects.all().delete()
    
    print("\n✓ All trend data has been deleted successfully!")
    print("\nNext steps:")
    print("  1. Update data collection to use synchronized 3-hour intervals")
    print("  2. Ensure both rainfall and tide data use the same timestamps")
    print("  3. Start collecting new synchronized data")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    clear_trend_data()
