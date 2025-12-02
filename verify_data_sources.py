"""
Verification Script: Check if data is from APIs or default values
This script verifies that rainfall, weather, and tide data are coming from
Open-Meteo and WorldTides APIs, not default fallback values.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silay_drrmo.settings')
django.setup()

from monitoring.models import RainfallData, WeatherData, TideLevelData
from django.utils import timezone
import requests

print("=" * 80)
print("DATA SOURCE VERIFICATION")
print("=" * 80)

# 1. Check Open-Meteo API for Silay City
print("\n1. CHECKING OPEN-METEO API (Silay City)")
print("-" * 80)
try:
    response = requests.get(
        'https://api.open-meteo.com/v1/forecast',
        params={
            'latitude': 10.7959,
            'longitude': 122.9749,
            'current': 'temperature_2m,precipitation,relative_humidity_2m,wind_speed_10m',
            'timezone': 'Asia/Manila'
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        current = data.get('current', {})
        
        print("✅ API Response: SUCCESS")
        print(f"   Location: {data['latitude']}°N, {data['longitude']}°E")
        print(f"   Time: {current['time']}")
        print(f"   Temperature: {current['temperature_2m']}°C")
        print(f"   Precipitation: {current['precipitation']}mm")
        print(f"   Humidity: {current['relative_humidity_2m']}%")
        print(f"   Wind Speed: {current['wind_speed_10m']}km/h")
        
        api_temp = current['temperature_2m']
        api_rain = current['precipitation']
        api_humidity = current['relative_humidity_2m']
        api_wind = current['wind_speed_10m']
    else:
        print(f"❌ API Response: FAILED (Status {response.status_code})")
        api_temp = api_rain = api_humidity = api_wind = None
        
except Exception as e:
    print(f"❌ API Error: {e}")
    api_temp = api_rain = api_humidity = api_wind = None

# 2. Check WorldTides API for Cebu City
print("\n2. CHECKING WORLDTIDES API (Cebu City)")
print("-" * 80)

from django.conf import settings

try:
    api_key = settings.WORLDTIDES_API_KEY
    
    response = requests.get(
        'https://www.worldtides.info/api/v3',
        params={
            'heights': '',
            'lat': 10.3157,
            'lon': 123.8854,
            'key': api_key,
            'date': timezone.now().strftime('%Y-%m-%d'),
            'days': 1
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        heights = data.get('heights', [])
        
        if heights:
            now_timestamp = timezone.now().timestamp()
            closest = min(heights, key=lambda x: abs(x['dt'] - now_timestamp))
            
            print("✅ API Response: SUCCESS")
            print(f"   Location: Cebu City (10.3157°N, 123.8854°E)")
            print(f"   Tide Height: {closest['height']}m")
            print(f"   Timestamp: {closest['dt']}")
            print(f"   Total Heights Available: {len(heights)}")
            
            api_tide = closest['height']
        else:
            print("⚠️  API Response: SUCCESS but no heights data")
            api_tide = None
    elif response.status_code == 402:
        print("❌ API Response: QUOTA EXCEEDED (402)")
        api_tide = None
    elif response.status_code == 401:
        print("❌ API Response: AUTH FAILED (401) - Check API key")
        api_tide = None
    else:
        print(f"❌ API Response: FAILED (Status {response.status_code})")
        print(f"   Response: {response.text[:200]}")
        api_tide = None
        
except AttributeError:
    print("❌ WorldTides API Key not configured in settings")
    api_tide = None
except Exception as e:
    print(f"❌ API Error: {e}")
    api_tide = None

# 3. Check Database Records
print("\n3. CHECKING DATABASE RECORDS")
print("-" * 80)

# Rainfall Data
rainfall = RainfallData.objects.last()
if rainfall:
    print(f"\n📊 RAINFALL DATA:")
    print(f"   Value: {rainfall.value_mm}mm")
    print(f"   Station: {rainfall.station_name}")
    print(f"   Timestamp: {rainfall.timestamp}")
    
    if api_rain is not None:
        if abs(rainfall.value_mm - api_rain) < 0.1:
            print(f"   ✅ MATCHES API: {api_rain}mm")
        else:
            print(f"   ⚠️  DIFFERENT FROM API: {api_rain}mm (may be from earlier hour)")
    
    # Check if default value
    if rainfall.value_mm == 0 and rainfall.station_name == 'Open-Meteo (Silay City)':
        print(f"   ℹ️  Zero rainfall (likely real data, not default)")
    elif rainfall.station_name != 'Open-Meteo (Silay City)':
        print(f"   ❌ USING DEFAULT/FALLBACK SOURCE!")
else:
    print("❌ No rainfall data in database")

# Weather Data
weather = WeatherData.objects.last()
if weather:
    print(f"\n🌡️  WEATHER DATA:")
    print(f"   Temperature: {weather.temperature_c}°C")
    print(f"   Humidity: {weather.humidity_percent}%")
    print(f"   Wind Speed: {weather.wind_speed_kph}km/h")
    print(f"   Station: {weather.station_name}")
    print(f"   Timestamp: {weather.timestamp}")
    
    if api_temp is not None:
        if abs(weather.temperature_c - api_temp) < 0.5:
            print(f"   ✅ MATCHES API: {api_temp}°C")
        else:
            print(f"   ⚠️  DIFFERENT FROM API: {api_temp}°C (may be from earlier hour)")
    
    # Check for default values
    if weather.temperature_c == 28.5 and weather.humidity_percent == 75 and weather.wind_speed_kph == 10:
        print(f"   ⚠️  POSSIBLE DEFAULT VALUES (28.5°C, 75%, 10km/h)")
    
    if weather.station_name != 'Open-Meteo (Silay City)':
        print(f"   ❌ USING DEFAULT/FALLBACK SOURCE!")
else:
    print("❌ No weather data in database")

# Tide Data
tide = TideLevelData.objects.last()
if tide:
    print(f"\n🌊 TIDE DATA:")
    print(f"   Height: {tide.height_m}m")
    print(f"   Station: {tide.station_name}")
    print(f"   Timestamp: {tide.timestamp}")
    
    if api_tide is not None:
        if abs(tide.height_m - api_tide) < 0.1:
            print(f"   ✅ MATCHES API: {api_tide}m")
        else:
            print(f"   ⚠️  DIFFERENT FROM API: {api_tide}m (may be from earlier period)")
    
    # Check for default values
    if tide.height_m == 0.8 and tide.station_name == 'Default':
        print(f"   ❌ USING DEFAULT VALUE! API failed or not configured")
    elif tide.station_name == 'WorldTides - Cebu City':
        print(f"   ✅ FROM WORLDTIDES API")
    elif 'WorldTides' in tide.station_name:
        print(f"   ✅ FROM WORLDTIDES API (Cebu City)")
    else:
        print(f"   ⚠️  Unknown source: {tide.station_name}")
else:
    print("❌ No tide data in database")

# 4. Summary
print("\n" + "=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)

issues = []

# Check rainfall
if rainfall:
    if rainfall.station_name == 'Open-Meteo (Silay City)':
        print("✅ RAINFALL: Using Open-Meteo API (Silay City)")
    else:
        print("❌ RAINFALL: NOT using Open-Meteo!")
        issues.append("Rainfall not from Open-Meteo")
else:
    print("❌ RAINFALL: No data in database")
    issues.append("No rainfall data")

# Check weather
if weather:
    if weather.station_name == 'Open-Meteo (Silay City)':
        # Check if looks like default values
        if weather.temperature_c == 28.5 and weather.humidity_percent == 75 and weather.wind_speed_kph == 10:
            print("⚠️  WEATHER: Using Open-Meteo but may be default values")
            issues.append("Weather may be default (28.5°C, 75%, 10km/h)")
        else:
            print("✅ WEATHER: Using Open-Meteo API (Silay City)")
    else:
        print("❌ WEATHER: NOT using Open-Meteo!")
        issues.append("Weather not from Open-Meteo")
else:
    print("❌ WEATHER: No data in database")
    issues.append("No weather data")

# Check tide
if tide:
    if tide.station_name == 'Default' and tide.height_m == 0.8:
        print("❌ TIDE: Using default value (0.8m)!")
        issues.append("Tide is default value - WorldTides API failed")
    elif 'WorldTides' in tide.station_name:
        print("✅ TIDE: Using WorldTides API (Cebu City)")
    else:
        print(f"⚠️  TIDE: Unknown source ({tide.station_name})")
        issues.append(f"Tide source unclear: {tide.station_name}")
else:
    print("❌ TIDE: No data in database")
    issues.append("No tide data")

print("\n" + "=" * 80)

if not issues:
    print("🎉 ALL DATA VERIFIED: Coming from APIs, not defaults!")
    print("\n✓ Open-Meteo (Silay City) - Rainfall & Weather")
    print("✓ WorldTides (Cebu City) - Tides")
else:
    print("⚠️  ISSUES FOUND:")
    for issue in issues:
        print(f"   • {issue}")
    print("\n💡 RECOMMENDATIONS:")
    print("   1. Run your Django server to trigger data updates")
    print("   2. Wait 1 hour for Open-Meteo data to refresh")
    print("   3. Check WorldTides API key in settings.py")
    print("   4. Visit the monitoring dashboard to trigger API calls")

print("=" * 80)
