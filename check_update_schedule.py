"""
Show current update frequencies and when data will refresh
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silay_drrmo.settings')
django.setup()

from monitoring.models import RainfallData, WeatherData, TideLevelData
from django.utils import timezone
from datetime import timedelta

def format_time(seconds):
    """Convert seconds to human readable format"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        if minutes > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} {minutes} min"
        return f"{hours} hour{'s' if hours != 1 else ''}"

print("=" * 80)
print("CURRENT CONDITIONS UPDATE SCHEDULE")
print("=" * 80)

now = timezone.now()

# Rainfall Data
print("\n📊 RAINFALL DATA (Open-Meteo - Silay City)")
print("-" * 80)
rainfall = RainfallData.objects.last()
if rainfall:
    age = (now - rainfall.timestamp).total_seconds()
    update_interval = 3600  # 1 hour
    
    print(f"Current Value: {rainfall.value_mm}mm")
    print(f"Last Updated: {rainfall.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}")
    print(f"Age: {format_time(age)}")
    print(f"\n⏰ UPDATE SCHEDULE:")
    print(f"   Frequency: Every 1 hour (3600 seconds)")
    
    if age >= update_interval:
        print(f"   Status: ⚠️  DATA IS OLD (>{format_time(update_interval)})")
        print(f"   Next Update: 🔄 IMMEDIATELY when you visit dashboard")
    else:
        remaining = update_interval - age
        print(f"   Status: ✅ DATA IS FRESH")
        print(f"   Next Update: In {format_time(remaining)}")
else:
    print("❌ No data in database")
    print("Next Update: Immediately when you visit dashboard")

# Weather Data
print("\n🌡️  WEATHER DATA (Open-Meteo - Silay City)")
print("-" * 80)
weather = WeatherData.objects.last()
if weather:
    age = (now - weather.timestamp).total_seconds()
    update_interval = 3600  # 1 hour
    
    print(f"Current Values:")
    print(f"   Temperature: {weather.temperature_c}°C")
    print(f"   Humidity: {weather.humidity_percent}%")
    print(f"   Wind Speed: {weather.wind_speed_kph} km/h")
    print(f"Last Updated: {weather.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}")
    print(f"Age: {format_time(age)}")
    print(f"\n⏰ UPDATE SCHEDULE:")
    print(f"   Frequency: Every 1 hour (3600 seconds)")
    
    if age >= update_interval:
        print(f"   Status: ⚠️  DATA IS OLD (>{format_time(update_interval)})")
        print(f"   Next Update: 🔄 IMMEDIATELY when you visit dashboard")
    else:
        remaining = update_interval - age
        print(f"   Status: ✅ DATA IS FRESH")
        print(f"   Next Update: In {format_time(remaining)}")
else:
    print("❌ No data in database")
    print("Next Update: Immediately when you visit dashboard")

# Tide Data
print("\n🌊 TIDE DATA (WorldTides - Cebu City)")
print("-" * 80)
tide = TideLevelData.objects.last()
if tide:
    age = (now - tide.timestamp).total_seconds()
    update_interval = 10800  # 3 hours
    
    print(f"Current Value: {tide.height_m}m")
    print(f"Station: {tide.station_name}")
    print(f"Last Updated: {tide.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}")
    print(f"Age: {format_time(age)}")
    print(f"\n⏰ UPDATE SCHEDULE:")
    print(f"   Frequency: Every 3 hours (10800 seconds)")
    
    if age >= update_interval:
        print(f"   Status: ⚠️  DATA IS OLD (>{format_time(update_interval)})")
        print(f"   Next Update: 🔄 IMMEDIATELY when you visit dashboard")
    else:
        remaining = update_interval - age
        print(f"   Status: ✅ DATA IS FRESH")
        print(f"   Next Update: In {format_time(remaining)}")
else:
    print("❌ No data in database")
    print("Next Update: Immediately when you visit dashboard")

# Summary
print("\n" + "=" * 80)
print("UPDATE FREQUENCY SUMMARY")
print("=" * 80)
print("\n📋 Automatic Updates (When You Visit Dashboard):")
print("   • Rainfall: Every 1 hour")
print("   • Weather (Temp/Humidity/Wind): Every 1 hour")
print("   • Tides: Every 3 hours")
print("\n🔄 How It Works:")
print("   1. You visit the monitoring dashboard")
print("   2. System checks age of each data type")
print("   3. If older than threshold, fetches fresh data from API")
print("   4. New data is saved to database with current timestamp")
print("\n💡 Data Sources:")
print("   • Open-Meteo API (Silay City) - Rainfall & Weather")
print("   • WorldTides API (Cebu City) - Tides")
print("\n⚡ Real-Time Updates:")
print("   Dashboard auto-refreshes every 5 minutes to fetch new data")
print("   You can also manually refresh the page anytime")

# Check if any data needs updating
print("\n" + "=" * 80)
needs_update = []

if rainfall and (now - rainfall.timestamp).total_seconds() >= 3600:
    needs_update.append("Rainfall")
if weather and (now - weather.timestamp).total_seconds() >= 3600:
    needs_update.append("Weather")
if tide and (now - tide.timestamp).total_seconds() >= 10800:
    needs_update.append("Tides")

if needs_update:
    print("⚠️  DATA NEEDS UPDATE:")
    for item in needs_update:
        print(f"   • {item}")
    print("\n💡 Action: Visit your dashboard to fetch fresh data")
else:
    print("✅ ALL DATA IS CURRENT - No updates needed right now")

print("=" * 80)
