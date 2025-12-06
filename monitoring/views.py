from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
import requests
from .models import RainfallData, WeatherData, TideLevelData, FloodRecord, BenchmarkSettings
from django.utils import timezone
from datetime import timedelta
import json
from .forms import FloodRecordForm, BARANGAYS
from django.conf import settings
import logging
from django.contrib.auth.decorators import login_required

# Set up logging
logger = logging.getLogger(__name__)


def should_update_trend_data(last_timestamp):
    """
    Check if we should update trend data based on 3-hour intervals.
    Data should be collected at: 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00
    """
    if not last_timestamp:
        return True
    
    now = timezone.now()
    time_diff = (now - last_timestamp).total_seconds()
    
    # Update if more than 3 hours (10800 seconds) have passed
    if time_diff >= 10800:
        return True
    
    return False


def get_synchronized_timestamp():
    """
    Get a timestamp rounded to the nearest 3-hour interval.
    This ensures both rainfall and tide data use the same timestamps.
    Returns timezone-aware datetime.
    """
    now = timezone.now()
    hour = (now.hour // 3) * 3  # Round down to nearest 3-hour mark
    return now.replace(hour=hour, minute=0, second=0, microsecond=0)


def get_flood_risk_level(rainfall_mm):
    """Determine flood risk level based on rainfall."""
    settings = BenchmarkSettings.get_settings()
    if rainfall_mm >= settings.rainfall_high_threshold:
        return "High Risk (>={:.0f}mm)".format(settings.rainfall_high_threshold), "red"
    elif rainfall_mm >= settings.rainfall_moderate_threshold:
        return "Moderate Risk ({:.0f}-{:.0f}mm)".format(settings.rainfall_moderate_threshold, settings.rainfall_high_threshold), "orange"
    else:
        return "Low Risk (<{:.0f}mm)".format(settings.rainfall_moderate_threshold), "yellow"
    

def get_tide_risk_level(tide_m):
    """Determine tide risk level based on height."""
    settings = BenchmarkSettings.get_settings()
    if tide_m >= settings.tide_high_threshold:
        return "High Risk (>={:.1f}m)".format(settings.tide_high_threshold), "red"
    elif tide_m >= settings.tide_moderate_threshold:
        return "Moderate Risk ({:.1f}-{:.1f}m)".format(settings.tide_moderate_threshold, settings.tide_high_threshold), "orange"
    else:
        return "Low Risk (<{:.1f}m)".format(settings.tide_moderate_threshold), "yellow"
    

def get_combined_risk_level(rainfall_mm, tide_m):
    """
    Determine combined risk level based on threshold-based logic.
    Both rainfall AND tide must meet thresholds to trigger that risk level.
    
    Example with defaults:
    - Rainfall 32mm + Tide 0.3m = Low (rainfall met moderate threshold but tide didn't)
    - Rainfall 32mm + Tide 1.0m = Moderate (both met moderate thresholds)
    - Rainfall 50mm + Tide 1.5m = High (both met high thresholds)
    """
    settings = BenchmarkSettings.get_settings()
    
    # Check HIGH RISK: Both rainfall AND tide must meet high thresholds
    if rainfall_mm >= settings.rainfall_high_threshold and tide_m >= settings.tide_high_threshold:
        return "High Risk", "red"
    
    # Check MODERATE RISK: Both rainfall AND tide must meet moderate thresholds
    if rainfall_mm >= settings.rainfall_moderate_threshold and tide_m >= settings.tide_moderate_threshold:
        return "Moderate Risk", "orange"
    
    # Otherwise: LOW RISK
    return "Low Risk", "yellow"



def generate_flood_insights(weather_forecast, rainfall_data, tide_data, flood_records):
    """Generate intelligent flood prediction insights based on forecast data and historical patterns."""
    settings = BenchmarkSettings.get_settings()
    
    insights = {
        'risk_alerts': [],
        'forecast_analysis': [],
        'recommendations': [],
        'trends': [],
        'severity': 'low'
    }

    if not weather_forecast:
        return insights

    # Analyze forecast for high-risk periods based on rainfall benchmarks
    high_risk_days = []
    total_precipitation = 0
    max_precipitation = 0
    high_rainfall_days = 0

    for i, day in enumerate(weather_forecast):
        precip = day.get('precipitation', 0)
        total_precipitation += precip
        max_precipitation = max(max_precipitation, precip)

        # Check if precipitation exceeds high risk threshold
        if precip >= settings.rainfall_high_threshold:
            high_rainfall_days += 1
            high_risk_days.append({
                'day': i + 1,
                'date': day.get('formatted_date', f'Day {i+1}'),
                'precipitation': precip,
                'risk_level': 'high'
            })

    # Generate risk alerts based on rainfall thresholds
    if high_rainfall_days > 0:
        insights['risk_alerts'].append({
            'type': 'warning',
            'title': f'High Rainfall Alert',
            'message': f'{high_rainfall_days} day(s) with rainfall ≥ {settings.rainfall_high_threshold}mm predicted in the next 7 days',
            'severity': 'high'
        })
        insights['severity'] = 'high'

    if total_precipitation >= settings.rainfall_high_threshold * 2:
        insights['risk_alerts'].append({
            'type': 'warning',
            'title': 'High Total Precipitation',
            'message': f'Total precipitation of {total_precipitation:.1f}mm expected over 7 days',
            'severity': 'medium'
        })

    # Forecast analysis
    avg_temp = sum(day.get('temp_max', 28) for day in weather_forecast) / len(weather_forecast)
    max_humidity = max(day.get('humidity', 75) for day in weather_forecast)

    insights['forecast_analysis'].append({
        'title': 'Temperature Trend',
        'analysis': f'Average maximum temperature: {avg_temp:.1f}Â°C. {"High temperatures may intensify rainfall events." if avg_temp > 32 else "Temperatures within normal range."}',
        'impact': 'moderate' if avg_temp > 32 else 'low'
    })

    insights['forecast_analysis'].append({
        'title': 'Humidity Analysis',
        'analysis': f'Maximum humidity: {max_humidity}%. {"High humidity indicates moisture saturation, increasing flood risk." if max_humidity > 85 else "Humidity levels within normal range."}',
        'impact': 'high' if max_humidity > 85 else 'low'
    })

    # Historical context
    if flood_records:
        recent_floods = [record for record in flood_records if record.get('date')]
        if recent_floods:
            insights['trends'].append({
                'title': 'Historical Flood Patterns',
                'analysis': f'{len(recent_floods)} flood events recorded. Current conditions {"similar to past flood events" if total_precipitation > 30 else "different from typical flood patterns"}.',
                'recommendation': 'Monitor closely if patterns match historical flood events.'
            })

    # Generate recommendations based on analysis
    if insights['severity'] == 'high':
        insights['recommendations'].extend([
            {
                'priority': 'high',
                'action': 'Activate Emergency Response Teams',
                'reason': 'Heavy rainfall predicted in forecast'
            },
            {
                'priority': 'high',
                'action': 'Pre-position Emergency Supplies',
                'reason': 'High flood risk identified'
            },
            {
                'priority': 'medium',
                'action': 'Monitor Low-lying Areas',
                'reason': 'Vulnerable barangays at risk'
            }
        ])
    elif total_precipitation > 20:
        insights['recommendations'].extend([
            {
                'priority': 'medium',
                'action': 'Increase Monitoring Frequency',
                'reason': 'Moderate precipitation expected'
            },
            {
                'priority': 'low',
                'action': 'Prepare Drainage Systems',
                'reason': 'Preventive maintenance recommended'
            }
        ])
    else:
        insights['recommendations'].append({
            'priority': 'low',
            'action': 'Maintain Regular Monitoring',
            'reason': 'Current conditions stable'
        })

    # Add time-based insights
    # Get current hour in Philippines timezone (Asia/Manila)
    from django.utils import timezone as tz
    import pytz
    manila_tz = pytz.timezone('Asia/Manila')
    current_time = tz.now().astimezone(manila_tz)
    current_hour = current_time.hour
    
    if 6 <= current_hour <= 18:  # Daytime
        insights['forecast_analysis'].append({
            'title': 'Daytime Monitoring',
            'analysis': 'Currently daytime hours. Visual inspection of vulnerable areas recommended.',
            'impact': 'low'
        })
    else:  # Nighttime
        insights['forecast_analysis'].append({
            'title': 'Nighttime Monitoring',
            'analysis': 'Currently nighttime hours. Focus on automated monitoring systems and emergency response readiness.',
            'impact': 'medium'
        })

    return insights
    
@login_required
def monitoring_view(request):
    # Get time range parameter, default to 24h
    time_range = request.GET.get('time_range', '24h')
    
    # Calculate time filter based on selected range
    now = timezone.now()
    if time_range == '24h':
        time_filter = now - timedelta(hours=24)
        range_label = 'Last 24 Hours'
    elif time_range == '7d':
        time_filter = now - timedelta(days=7)
        range_label = 'Last 7 Days'
    elif time_range == '30d':
        time_filter = now - timedelta(days=30)
        range_label = 'Last 30 Days'
    elif time_range == '90d':
        time_filter = now - timedelta(days=90)
        range_label = 'Last 90 Days'
    elif time_range == 'all':
        time_filter = now - timedelta(days=365)  # Limit to 1 year for performance
        range_label = 'Last Year'
    else:
        time_filter = now - timedelta(hours=24)  # Default fallback
        range_label = 'Last 24 Hours'
    
    # Fetch or create initial data
    rainfall_data = RainfallData.objects.last()
    weather_data = WeatherData.objects.last()
    tide_data = TideLevelData.objects.last()

    # Initialize forecast data
    weather_forecast = []
    pagasa_data = None
    # Fetch current conditions from Open-Meteo API (hourly updates)
    # Location: Silay City, Negros Occidental
    try:
        api_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': 10.7959,  # Silay City, Negros Occidental
            'longitude': 122.9749,
            'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,rain',
            'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m,rain',
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean,wind_speed_10m_max',
            'timezone': 'Asia/Manila',
            'forecast_days': 7
        }
        
        logger.info(f"Requesting Open-Meteo API for current conditions: {api_url}")
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Use current weather data for real-time values
        current = data.get('current', {})
        rainfall_value = current.get('rain', 0)  # Current rain in mm
        temperature = current.get('temperature_2m', 28.5)
        humidity = current.get('relative_humidity_2m', 75)
        wind_speed = current.get('wind_speed_10m', 10)
        
        logger.info(f"Open-Meteo (Current) - Rain: {rainfall_value}mm, Temp: {temperature}°C, Humidity: {humidity}%, Wind: {wind_speed}km/h")

        # Only create new records on 3-hour intervals (synchronized with tide data)
        # Updates at: 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00
        if should_update_trend_data(rainfall_data.timestamp if rainfall_data else None):
            sync_timestamp = get_synchronized_timestamp()
            rainfall_data = RainfallData.objects.create(value_mm=rainfall_value, station_name='Open-Meteo (Silay City)')
            # Update the timestamp to synchronized time
            rainfall_data.timestamp = sync_timestamp
            rainfall_data.save()
            logger.info(f"Created new rainfall record: {rainfall_value}mm at {sync_timestamp}")

        if not weather_data or (timezone.now() - weather_data.timestamp).total_seconds() > 3600:
            weather_data = WeatherData.objects.create(
                temperature_c=temperature,
                humidity_percent=humidity,
                wind_speed_kph=wind_speed,
                station_name='Open-Meteo (Silay City)'
            )
            logger.info(f"Created new weather record")

        # Process 7-day forecast data from Open-Meteo (Silay City)
        logger.info("Using Open-Meteo for Silay City forecast")
        daily_data = data.get('daily', {})
        if daily_data:
            dates = daily_data.get('time', [])
            temp_max = daily_data.get('temperature_2m_max', [])
            temp_min = daily_data.get('temperature_2m_min', [])
            precipitation = daily_data.get('precipitation_sum', [])
            humidity_avg = daily_data.get('relative_humidity_2m_mean', [])
            wind_max = daily_data.get('wind_speed_10m_max', [])
            
            weather_forecast = []
            for i in range(min(len(dates), 7)):
                from datetime import datetime
                date_obj = datetime.strptime(dates[i], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%b %d')
                
                forecast_day = {
                    'date': dates[i],
                    'formatted_date': formatted_date,
                    'temp_max': temp_max[i] if i < len(temp_max) else 28.5,
                    'temp_min': temp_min[i] if i < len(temp_min) else 25.0,
                    'precipitation': precipitation[i] if i < len(precipitation) else 0.0,
                    'humidity': humidity_avg[i] if i < len(humidity_avg) else 75,
                    'wind_speed': wind_max[i] if i < len(wind_max) else 10.0,
                }
                weather_forecast.append(forecast_day)
            
            logger.info(f"Processed {len(weather_forecast)} days of Open-Meteo forecast for Silay City")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Open-Meteo API Error: {e}")
        if not rainfall_data:
            rainfall_data = RainfallData.objects.create(value_mm=0, station_name='Open-Meteo (Silay City)')
            logger.warning("Created default rainfall record due to API error")
        if not weather_data:
            weather_data = WeatherData.objects.create(
                temperature_c=28.5,
                humidity_percent=75,
                wind_speed_kph=10,
                station_name='Open-Meteo (Silay City)'
            )
            logger.warning("Created default weather record due to API error")
    except Exception as e:
        logger.error(f"Unexpected error fetching weather data: {e}")

    # Fetch tide data from WorldTides (Cebu City) on 3-hour intervals (synchronized with rainfall)
    if should_update_trend_data(tide_data.timestamp if tide_data else None):
        try:
            tide_api_url = "https://www.worldtides.info/api/v3"
            params = {
                'heights': '',
                'lat': 10.3157,  # Cebu City, Cebu
                'lon': 123.8854,
                'key': settings.WORLDTIDES_API_KEY,
                'date': timezone.now().strftime('%Y-%m-%d'),
                'days': 1
            }
            
            logger.info(f"Fetching WorldTides API for Cebu City: {tide_api_url}")
            tide_response = requests.get(tide_api_url, params=params, timeout=10)
            
            if tide_response.status_code == 200:
                tide_data_json = tide_response.json()
                heights = tide_data_json.get('heights', [])
                
                if heights:
                    now_timestamp = timezone.now().timestamp()
                    closest_height = min(heights, key=lambda x: abs(x['dt'] - now_timestamp))
                    tide_value = closest_height.get('height', 0.8)
                    
                    sync_timestamp = get_synchronized_timestamp()
                    tide_data = TideLevelData.objects.create(
                        height_m=tide_value,
                        station_name='WorldTides - Cebu City'
                    )
                    # Update the timestamp to synchronized time
                    tide_data.timestamp = sync_timestamp
                    tide_data.save()
                    logger.info(f"Created tide record from WorldTides (Cebu City): {tide_value}m at {sync_timestamp}")
                else:
                    logger.warning("No tide heights in WorldTides API response")
                    
            elif tide_response.status_code == 402:
                logger.error("WorldTides API quota exceeded (402) - Using PAGASA only")
            elif tide_response.status_code == 401:
                logger.error("WorldTides API authentication failed (401) - Check API key")
            else:
                logger.error(f"WorldTides API error: {tide_response.status_code} - {tide_response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"WorldTides API Error (backup): {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching WorldTides backup data: {e}")

    # Create default tide data if WorldTides failed
    if not tide_data:
        sync_timestamp = get_synchronized_timestamp()
        tide_data = TideLevelData.objects.create(height_m=0.8, station_name='Default')
        tide_data.timestamp = sync_timestamp
        tide_data.save()
        logger.warning(f"Created default tide record at {sync_timestamp} (WorldTides API unavailable)")

    # Convert QuerySets to lists of dictionaries for JSON serialization
    rainfall_history = list(RainfallData.objects.filter(
        timestamp__gte=time_filter
    ).order_by('timestamp').values('timestamp', 'value_mm'))
    
    tide_history = list(TideLevelData.objects.filter(
        timestamp__gte=time_filter
    ).order_by('timestamp').values('timestamp', 'height_m'))
    
    # Order by date descending (most recent first) for proper table display, and include ID for edit/delete
    flood_records = list(FloodRecord.objects.all().order_by('-date')[:20].values(
        'id', 'event', 'date', 'affected_barangays', 'casualties_dead', 'casualties_injured', 'casualties_missing',
        'affected_persons', 'affected_families', 'houses_damaged_partially', 'houses_damaged_totally',
        'damage_infrastructure_php', 'damage_agriculture_php', 'damage_institutions_php',
        'damage_private_commercial_php', 'damage_total_php'
    ))
    
    # Format numbers with thousands separator for display
    for record in flood_records:
        record['casualties_dead_fmt'] = "{:,.0f}".format(record['casualties_dead'])
        record['casualties_injured_fmt'] = "{:,.0f}".format(record['casualties_injured'])
        record['casualties_missing_fmt'] = "{:,.0f}".format(record['casualties_missing'])
        record['affected_persons_fmt'] = "{:,.0f}".format(record['affected_persons'])
        record['affected_families_fmt'] = "{:,.0f}".format(record['affected_families'])
        record['houses_damaged_partially_fmt'] = "{:,.0f}".format(record['houses_damaged_partially'])
        record['houses_damaged_totally_fmt'] = "{:,.0f}".format(record['houses_damaged_totally'])
        record['damage_infrastructure_php_fmt'] = "{:,.2f}".format(record['damage_infrastructure_php'])
        record['damage_agriculture_php_fmt'] = "{:,.2f}".format(record['damage_agriculture_php'])
        record['damage_institutions_php_fmt'] = "{:,.2f}".format(record['damage_institutions_php'])
        record['damage_private_commercial_php_fmt'] = "{:,.2f}".format(record['damage_private_commercial_php'])
        record['damage_total_php_fmt'] = "{:,.2f}".format(record['damage_total_php'])

    # Aggregate data for graphs
    dates = [record['date'].strftime('%Y-%m-%d') for record in flood_records]
    casualties_data = {
        'dead': [record['casualties_dead'] for record in flood_records],
        'injured': [record['casualties_injured'] for record in flood_records],
        'missing': [record['casualties_missing'] for record in flood_records],
    }
    affected_data = {
        'persons': [record['affected_persons'] for record in flood_records],
        'families': [record['affected_families'] for record in flood_records],
    }
    houses_data = {
        'partially': [record['houses_damaged_partially'] for record in flood_records],
        'totally': [record['houses_damaged_totally'] for record in flood_records],
    }
    damage_data = {
        'infrastructure': [float(record['damage_infrastructure_php']) for record in flood_records],
        'agriculture': [float(record['damage_agriculture_php']) for record in flood_records],
        'institutions': [float(record['damage_institutions_php']) for record in flood_records],
        'private_commercial': [float(record['damage_private_commercial_php']) for record in flood_records],
        'total': [float(record['damage_total_php']) for record in flood_records],
    }

    # Prepare rainfall and tide trend data
    rainfall_timestamps = [r['timestamp'].strftime('%Y-%m-%d %H:%M') for r in rainfall_history]
    rainfall_values = [r['value_mm'] for r in rainfall_history]
    tide_timestamps = [t['timestamp'].strftime('%Y-%m-%d %H:%M') for t in tide_history]
    tide_values = [t['height_m'] for t in tide_history]

    # Prepare forecast data for charts
    forecast_dates = [day['formatted_date'] for day in weather_forecast]
    forecast_temp_max = [day['temp_max'] for day in weather_forecast]
    forecast_temp_min = [day['temp_min'] for day in weather_forecast]
    forecast_precipitation = [day['precipitation'] for day in weather_forecast]
    forecast_humidity = [day['humidity'] for day in weather_forecast]
    forecast_wind_speed = [day['wind_speed'] for day in weather_forecast]

    # Generate flood prediction insights
    insights = generate_flood_insights(weather_forecast, rainfall_data, tide_data, flood_records)

    # Determine flood risk levels
    rain_risk_level, rain_risk_color = get_flood_risk_level(rainfall_data.value_mm if rainfall_data else 0)
    tide_risk_level, tide_risk_color = get_tide_risk_level(tide_data.height_m if tide_data else 0)
    
    # Get current rainfall and tide values for combined risk calculation
    current_rainfall_mm = rainfall_data.value_mm if rainfall_data else 0
    current_tide_m = tide_data.height_m if tide_data else 0
    combined_risk_level, combined_risk_color = get_combined_risk_level(current_rainfall_mm, current_tide_m)

    # Get earliest and latest data dates for date picker constraints
    earliest_rainfall = RainfallData.objects.order_by('timestamp').first()
    earliest_tide = TideLevelData.objects.order_by('timestamp').first()
    earliest_flood = FloodRecord.objects.order_by('date').first()
    
    # Find the earliest date among all data sources
    earliest_dates = []
    if earliest_rainfall:
        earliest_dates.append(earliest_rainfall.timestamp.date())
    if earliest_tide:
        earliest_dates.append(earliest_tide.timestamp.date())
    if earliest_flood:
        earliest_dates.append(earliest_flood.date)
    
    min_date = min(earliest_dates).isoformat() if earliest_dates else None
    max_date = timezone.now().date().isoformat()  # Today's date

    # Get available years from flood records for filter dropdown
    available_years = FloodRecord.objects.dates('date', 'year', order='DESC')
    years_list = [date.year for date in available_years]

    # Get "On This Day" flood records (same month and day from previous years)
    today = timezone.now().date()
    on_this_day_records = FloodRecord.objects.filter(
        date__month=today.month,
        date__day=today.day
    ).exclude(
        date__year=today.year  # Exclude current year
    ).order_by('-date').values(
        'id', 'event', 'date', 'affected_barangays', 'casualties_dead', 'casualties_injured', 'casualties_missing',
        'affected_persons', 'affected_families', 'houses_damaged_partially', 'houses_damaged_totally',
        'damage_infrastructure_php', 'damage_agriculture_php', 'damage_institutions_php',
        'damage_private_commercial_php', 'damage_total_php'
    )
    
    # Format "On This Day" records and calculate years ago
    on_this_day_list = []
    for record in on_this_day_records:
        years_ago = today.year - record['date'].year
        record['years_ago'] = years_ago
        record['casualties_dead_fmt'] = "{:,.0f}".format(record['casualties_dead'])
        record['casualties_injured_fmt'] = "{:,.0f}".format(record['casualties_injured'])
        record['casualties_missing_fmt'] = "{:,.0f}".format(record['casualties_missing'])
        record['affected_persons_fmt'] = "{:,.0f}".format(record['affected_persons'])
        record['affected_families_fmt'] = "{:,.0f}".format(record['affected_families'])
        record['houses_damaged_partially_fmt'] = "{:,.0f}".format(record['houses_damaged_partially'])
        record['houses_damaged_totally_fmt'] = "{:,.0f}".format(record['houses_damaged_totally'])
        record['damage_infrastructure_php_fmt'] = "{:,.2f}".format(record['damage_infrastructure_php'])
        record['damage_agriculture_php_fmt'] = "{:,.2f}".format(record['damage_agriculture_php'])
        record['damage_institutions_php_fmt'] = "{:,.2f}".format(record['damage_institutions_php'])
        record['damage_private_commercial_php_fmt'] = "{:,.2f}".format(record['damage_private_commercial_php'])
        record['damage_total_php_fmt'] = "{:,.2f}".format(record['damage_total_php'])
        on_this_day_list.append(record)

    context = {
        'rainfall_data': rainfall_data,
        'weather_data': weather_data,
        'tide_data': tide_data,
        'weather_forecast': weather_forecast,
        'forecast_dates': forecast_dates,
        'forecast_temp_max': forecast_temp_max,
        'forecast_temp_min': forecast_temp_min,
        'forecast_precipitation': forecast_precipitation,
        'forecast_humidity': forecast_humidity,
        'forecast_wind_speed': forecast_wind_speed,
        'insights': insights,
        'rainfall_history': rainfall_history,
        'tide_history': tide_history,
        'rain_risk_level': rain_risk_level,
        'rain_risk_color': rain_risk_color,
        'tide_risk_level': tide_risk_level,
        'tide_risk_color': tide_risk_color,
        'combined_risk_level': combined_risk_level,
        'combined_risk_color': combined_risk_color,
        'flood_records': flood_records,
        'graph_dates': dates,
        'casualties_data': casualties_data,
        'affected_data': affected_data,
        'houses_data': houses_data,
        'damage_data': damage_data,
        'rainfall_timestamps': rainfall_timestamps,
        'rainfall_values': rainfall_values,
        'tide_timestamps': tide_timestamps,
        'tide_values': tide_values,
        'time_range': time_range,
        'range_label': range_label,
        'min_date': min_date,
        'max_date': max_date,
        'available_years': years_list,
        'on_this_day_records': on_this_day_list,
        'today': today,
    }
    return render(request, 'monitoring/monitoring.html', context)

@login_required
def trends_comparison_api(request):
    """API endpoint for yearly trends comparison on the same date."""
    month = request.GET.get('month')
    day = request.GET.get('day')
    
    if not month or not day:
        return JsonResponse({'error': 'Month and day parameters required'}, status=400)
    
    try:
        month = int(month)
        day = int(day)
    except ValueError:
        return JsonResponse({'error': 'Invalid month or day'}, status=400)
    
    # Get all years that have data for this date
    rainfall_by_year = {}
    tide_by_year = {}
    
    # Query rainfall data for this date across all years
    rainfall_records = RainfallData.objects.filter(
        timestamp__month=month,
        timestamp__day=day
    ).values('timestamp', 'value_mm').order_by('timestamp')
    
    for record in rainfall_records:
        year = record['timestamp'].year
        if year not in rainfall_by_year:
            rainfall_by_year[year] = []
        rainfall_by_year[year].append(record['value_mm'])
    
    # Query tide data for this date across all years
    tide_records = TideLevelData.objects.filter(
        timestamp__month=month,
        timestamp__day=day
    ).values('timestamp', 'height_m').order_by('timestamp')
    
    for record in tide_records:
        year = record['timestamp'].year
        if year not in tide_by_year:
            tide_by_year[year] = []
        tide_by_year[year].append(record['height_m'])
    
    # Get common years and calculate averages
    all_years = sorted(set(list(rainfall_by_year.keys()) + list(tide_by_year.keys())))
    
    years = []
    rainfall_values = []
    tide_values = []
    
    for year in all_years:
        years.append(year)
        
        # Calculate average rainfall for this year
        if year in rainfall_by_year and rainfall_by_year[year]:
            avg_rainfall = sum(rainfall_by_year[year]) / len(rainfall_by_year[year])
            rainfall_values.append(avg_rainfall)
        else:
            rainfall_values.append(0)
        
        # Calculate average tide for this year
        if year in tide_by_year and tide_by_year[year]:
            avg_tide = sum(tide_by_year[year]) / len(tide_by_year[year])
            tide_values.append(avg_tide)
        else:
            tide_values.append(0)
    
    return JsonResponse({
        'years': years,
        'rainfall_values': rainfall_values,
        'tide_values': tide_values
    })

@login_required
def fetch_data_api(request):
    """API endpoint for AJAX updates with error handling."""
    try:
        data = {
            'rainfall': RainfallData.objects.last().value_mm if RainfallData.objects.exists() else 0,
            'temperature': WeatherData.objects.last().temperature_c if WeatherData.objects.exists() else 0,
            'tide': TideLevelData.objects.last().height_m if TideLevelData.objects.exists() else 0,
        }
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error in fetch_data_api: {e}")
        return JsonResponse({'error': 'Unable to fetch data'}, status=500)

@login_required
@login_required
def fetch_trends_api(request):
    """API endpoint for fetching trend data with time range filtering."""
    try:
        from datetime import datetime, date
        
        # Check for custom date range parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        now = timezone.now()
        time_filter = None
        range_label = ""
        
        if start_date_str and end_date_str:
            # Custom date range provided
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                
                # Validation: end date should be after start date
                if end_date < start_date:
                    return JsonResponse({'error': 'End date must be after start date'}, status=400)
                
                # Validation: no future dates
                if start_date > now.date() or end_date > now.date():
                    return JsonResponse({'error': 'Cannot select future dates'}, status=400)
                
                # Validation: reasonable range (max 2 years)
                date_diff = (end_date - start_date).days
                if date_diff > 730:  # 2 years
                    return JsonResponse({'error': 'Date range cannot exceed 2 years'}, status=400)
                
                # Create datetime objects for filtering (start of start_date to end of end_date)
                start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
                end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
                
                time_filter = start_datetime
                range_label = f'Custom Range: {start_date.strftime("%b %d, %Y")} - {end_date.strftime("%b %d, %Y")}'
                
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        else:
            # Use predefined time range
            time_range = request.GET.get('time_range', '24h')
            
            if time_range == '24h':
                time_filter = now - timedelta(hours=24)
                range_label = 'Last 24 Hours'
            elif time_range == '7d':
                time_filter = now - timedelta(days=7)
                range_label = 'Last 7 Days'
            elif time_range == '30d':
                time_filter = now - timedelta(days=30)
                range_label = 'Last 30 Days'
            elif time_range == '90d':
                time_filter = now - timedelta(days=90)
                range_label = 'Last 90 Days'
            elif time_range == 'all':
                time_filter = now - timedelta(days=365)  # Limit to 1 year for performance
                range_label = 'Last Year'
            else:
                time_filter = now - timedelta(hours=24)  # Default fallback
                range_label = 'Last 24 Hours'
        
        # Fetch filtered data
        if start_date_str and end_date_str:
            # Custom date range filtering (timezone-aware, inclusive)
            rainfall_history = list(RainfallData.objects.filter(
                timestamp__gte=start_datetime,
                timestamp__lte=end_datetime
            ).order_by('timestamp').values('timestamp', 'value_mm'))

            tide_history = list(TideLevelData.objects.filter(
                timestamp__gte=start_datetime,
                timestamp__lte=end_datetime
            ).order_by('timestamp').values('timestamp', 'height_m'))
        else:
            # Time-based filtering
            rainfall_history = list(RainfallData.objects.filter(
                timestamp__gte=time_filter
            ).order_by('timestamp').values('timestamp', 'value_mm'))
            
            tide_history = list(TideLevelData.objects.filter(
                timestamp__gte=time_filter
            ).order_by('timestamp').values('timestamp', 'height_m'))
        
        # Prepare trend data
        rainfall_timestamps = [r['timestamp'].strftime('%Y-%m-%d %H:%M') for r in rainfall_history]
        rainfall_values = [r['value_mm'] for r in rainfall_history]
        tide_timestamps = [t['timestamp'].strftime('%Y-%m-%d %H:%M') for t in tide_history]
        tide_values = [t['height_m'] for t in tide_history]
        
        data = {
            'time_range': request.GET.get('time_range', 'custom'),
            'range_label': range_label,
            'rainfall_timestamps': rainfall_timestamps,
            'rainfall_values': rainfall_values,
            'tide_timestamps': tide_timestamps,
            'tide_values': tide_values,
        }
        
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error in fetch_trends_api: {e}")
        return JsonResponse({'error': 'Unable to fetch trend data'}, status=500)

@login_required
def flood_record_form(request):
    """Handle flood record form submission with comprehensive error handling."""
    if request.method == 'POST':
        form = FloodRecordForm(request.POST)
        
        try:
            if form.is_valid():
                flood_record = form.save()
                
                # Log the activity (import at top of file)
                from maps.models import FloodRecordActivity
                FloodRecordActivity.objects.create(
                    user=request.user,
                    action='CREATE',
                    flood_record_id=flood_record.id,
                    event_type=flood_record.event,
                    event_date=flood_record.date,
                    affected_barangays=flood_record.affected_barangays,
                    casualties_dead=flood_record.casualties_dead,
                    casualties_injured=flood_record.casualties_injured,
                    casualties_missing=flood_record.casualties_missing,
                    affected_persons=flood_record.affected_persons,
                    affected_families=flood_record.affected_families,
                    damage_total_php=flood_record.damage_total_php
                )
                
                success_message = f'✅ Flood record for {flood_record.event} on {flood_record.date.strftime("%Y-%m-%d")} has been successfully added!'
                logger.info(f"Flood record created: {flood_record.id} - {flood_record.event}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': success_message,
                        'redirect_url': reverse('monitoring_view')
                    })
                
                messages.success(request, success_message)
                return redirect('monitoring_view')
            else:
                error_message = '❌ Please correct the errors below and try again.'
                logger.warning(f"Form validation errors: {form.errors}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message,
                        'errors': form.errors
                    })
                    
                messages.error(request, error_message)
        except Exception as e:
            error_message = f'❌ An unexpected error occurred while saving the record: {str(e)}'
            logger.error(f"Error saving flood record: {e}", exc_info=True)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
                
            messages.error(request, error_message)
    else:
        form = FloodRecordForm()
    
    return render(request, 'monitoring/flood_record_form.html', {
        'form': form, 
        'BARANGAYS': BARANGAYS
    })

@login_required
def flood_record_edit(request, record_id):
    """Handle editing of existing flood record."""
    flood_record = get_object_or_404(FloodRecord, id=record_id)
    
    if request.method == 'POST':
        form = FloodRecordForm(request.POST, instance=flood_record)
        
        try:
            if form.is_valid():
                flood_record = form.save()
                success_message = f'✅ Flood record for {flood_record.event} on {flood_record.date.strftime("%Y-%m-%d")} has been successfully updated!'
                logger.info(f"Flood record updated: {flood_record.id} - {flood_record.event}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': success_message,
                        'redirect_url': reverse('monitoring_view') + '#flood-records'
                    })
                
                messages.success(request, success_message)
                return redirect(reverse('monitoring_view') + '#flood-records')
            else:
                error_message = '❌ Please correct the errors below and try again.'
                logger.warning(f"Form validation errors: {form.errors}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message,
                        'errors': form.errors
                    })
                    
                messages.error(request, error_message)
        except Exception as e:
            error_message = f'❌ An unexpected error occurred while updating the record: {str(e)}'
            logger.error(f"Error updating flood record: {e}", exc_info=True)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
                
            messages.error(request, error_message)
    else:
        form = FloodRecordForm(instance=flood_record)
    
    return render(request, 'monitoring/flood_record_edit.html', {
        'form': form,
        'BARANGAYS': BARANGAYS,
        'record': flood_record
    })

@login_required
def flood_record_delete(request, record_id):
    """Handle deletion of flood record."""
    flood_record = get_object_or_404(FloodRecord, id=record_id)
    
    if request.method == 'POST':
        try:
            event_name = flood_record.event
            event_date = flood_record.date.strftime("%Y-%m-%d")
            # Log the activity before deleting
            from maps.models import FloodRecordActivity
            FloodRecordActivity.objects.create(
                user=request.user,
                action='DELETE',
                flood_record_id=flood_record.id,
                event_type=flood_record.event,
                event_date=flood_record.date,
                affected_barangays=flood_record.affected_barangays,
                casualties_dead=flood_record.casualties_dead,
                casualties_injured=flood_record.casualties_injured,
                casualties_missing=flood_record.casualties_missing,
                affected_persons=flood_record.affected_persons,
                affected_families=flood_record.affected_families,
                damage_total_php=flood_record.damage_total_php
            )
            flood_record.delete()
            
            success_message = f'✅ Flood record for {event_name} on {event_date} has been successfully deleted!'
            logger.info(f"Flood record deleted: {record_id} - {event_name}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'redirect_url': reverse('monitoring_view') + '#flood-records'
                })
            
            messages.success(request, success_message)
            return redirect(reverse('monitoring_view') + '#flood-records')
        except Exception as e:
            error_message = f'❌ An error occurred while deleting the record: {str(e)}'
            logger.error(f"Error deleting flood record: {e}", exc_info=True)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
            
            messages.error(request, error_message)
            return redirect(reverse('monitoring_view') + '#flood-records')
    
    return render(request, 'monitoring/flood_record_delete.html', {
        'record': flood_record
    })


def is_staff_user(user):
    """Check if user is a staff member"""
    return user.is_staff


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["GET", "POST"])
def benchmark_settings_view(request):
    """View for managing benchmark settings (admin only)"""
    settings = BenchmarkSettings.get_settings()
    
    if request.method == 'POST':
        try:
            # Get form data
            rainfall_moderate = float(request.POST.get('rainfall_moderate_threshold', 30))
            rainfall_high = float(request.POST.get('rainfall_high_threshold', 50))
            tide_moderate = float(request.POST.get('tide_moderate_threshold', 1.0))
            tide_high = float(request.POST.get('tide_high_threshold', 1.5))
            
            # Validation
            errors = []
            if rainfall_moderate >= rainfall_high:
                errors.append("Rainfall moderate threshold must be less than high threshold")
            if tide_moderate >= tide_high:
                errors.append("Tide moderate threshold must be less than high threshold")
            if rainfall_moderate <= 0 or rainfall_high <= 0:
                errors.append("Rainfall thresholds must be positive")
            if tide_moderate <= 0 or tide_high <= 0:
                errors.append("Tide thresholds must be positive")
            
            if errors:
                for error in errors:
                    messages.error(request, f"❌ {error}")
                return render(request, 'monitoring/benchmark_settings.html', {
                    'settings': settings,
                    'errors': errors
                })
            
            # Update settings
            settings.rainfall_moderate_threshold = rainfall_moderate
            settings.rainfall_high_threshold = rainfall_high
            settings.tide_moderate_threshold = tide_moderate
            settings.tide_high_threshold = tide_high
            settings.updated_by = request.user.get_full_name() or request.user.username
            settings.save()
            
            messages.success(request, "✅ Benchmark settings updated successfully!")
            return redirect('benchmark_settings')
        
        except ValueError as e:
            messages.error(request, f"❌ Invalid input: Please enter valid numbers")
            return render(request, 'monitoring/benchmark_settings.html', {
                'settings': settings
            })
        except Exception as e:
            messages.error(request, f"❌ An error occurred: {str(e)}")
            return render(request, 'monitoring/benchmark_settings.html', {
                'settings': settings
            })
    
    return render(request, 'monitoring/benchmark_settings.html', {
        'settings': settings
    })


@login_required
def export_trends(request):
    """Export rainfall and tide trends data to CSV or PDF"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    
    export_type = request.GET.get('type', 'csv')
    time_range = request.GET.get('time_range', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    
    # Determine filtering method
    now = timezone.now()
    
    if start_date_str and end_date_str:
        # Custom date range
        try:
            from datetime import date as date_module
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
            
            time_filter = start_datetime
            end_filter = end_datetime
            range_label = f'Custom Range: {start_date.strftime("%b %d, %Y")} - {end_date.strftime("%b %d, %Y")}'
            use_range = True
        except ValueError:
            # Fallback to default
            time_filter = now - timedelta(hours=24)
            end_filter = now
            range_label = 'Last 24 Hours'
            use_range = True
    else:
        # Predefined time range
        use_range = False
        if time_range == '24h':
            time_filter = now - timedelta(hours=24)
            range_label = 'Last 24 Hours'
        elif time_range == '7d':
            time_filter = now - timedelta(days=7)
            range_label = 'Last 7 Days'
        elif time_range == '30d':
            time_filter = now - timedelta(days=30)
            range_label = 'Last 30 Days'
        elif time_range == '90d':
            time_filter = now - timedelta(days=90)
            range_label = 'Last 90 Days'
        elif time_range == 'all':
            time_filter = now - timedelta(days=365)
            range_label = 'Last Year'
        else:
            time_filter = now - timedelta(hours=24)
            range_label = 'Last 24 Hours'
    
    # Fetch data based on filter type
    if use_range and 'end_filter' in locals():
        rainfall_data = RainfallData.objects.filter(timestamp__gte=time_filter, timestamp__lte=end_filter).order_by('timestamp')
        tide_data = TideLevelData.objects.filter(timestamp__gte=time_filter, timestamp__lte=end_filter).order_by('timestamp')
    else:
        rainfall_data = RainfallData.objects.filter(timestamp__gte=time_filter).order_by('timestamp')
        tide_data = TideLevelData.objects.filter(timestamp__gte=time_filter).order_by('timestamp')
    
    # Create combined dataset
    combined_data = []
    rainfall_dict = {r.timestamp: r for r in rainfall_data}
    tide_dict = {t.timestamp: t for t in tide_data}
    all_timestamps = sorted(set(list(rainfall_dict.keys()) + list(tide_dict.keys())))
    
    for ts in all_timestamps:
        combined_data.append({
            'timestamp': ts,
            'rainfall': rainfall_dict.get(ts),
            'tide': tide_dict.get(ts)
        })
    
    if export_type == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        filename = f'rainfall_tide_trends_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['# Rainfall & Tide Trends Export'])
        writer.writerow([f'# Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}'])
        writer.writerow([f'# Time Range: {range_label}'])
        writer.writerow([f'# Total Records: {len(combined_data)}'])
        writer.writerow([])
        
        writer.writerow(['#', 'Timestamp', 'Rainfall (mm)', 'Tide Level (m)'])
        
        for idx, data in enumerate(combined_data, 1):
            rainfall_value = data['rainfall'].value_mm if data['rainfall'] else '-'
            tide_value = data['tide'].height_m if data['tide'] else '-'
            writer.writerow([
                idx,
                data['timestamp'].strftime('%Y-%m-%d %H:%M'),
                rainfall_value,
                tide_value
            ])
        
        return response
    
    elif export_type == 'pdf':
        from reportlab.lib.utils import ImageReader
        from reportlab.platypus import Image as RLImage
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        import os
        
        response = HttpResponse(content_type='application/pdf')
        filename = f'rainfall_tide_trends_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Custom page template with header and footer (PORTRAIT)
        def add_header_footer(canvas, doc):
            canvas.saveState()
            
            # Header - DRRMO logo/header
            header_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR / 'static', 'images', 'drrmo_header.png')
            if os.path.exists(header_path):
                try:
                    page_width = letter[0]
                    canvas.drawImage(header_path, 0, doc.height + doc.topMargin, 
                                   width=page_width, height=0.9*inch, 
                                   preserveAspectRatio=True, mask='auto')
                except:
                    pass
            
            # Footer line
            page_width = letter[0]
            canvas.setStrokeColor(colors.HexColor('#1e3a5f'))
            canvas.setLineWidth(2)
            canvas.line(0.5*inch, 0.45*inch, page_width - 0.5*inch, 0.45*inch)
            
            # Footer text
            canvas.setFont('Helvetica-Bold', 8)
            canvas.setFillColor(colors.HexColor('#1e3a5f'))
            footer_text = "SILAY CITY DISASTER RISK REDUCTION & MANAGEMENT COUNCIL"
            text_width = canvas.stringWidth(footer_text, 'Helvetica-Bold', 8)
            canvas.drawString((page_width - text_width) / 2, 0.28*inch, footer_text)
            
            # Page number
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.HexColor('#6b7280'))
            page_text = f"Page {doc.page}"
            canvas.drawRightString(page_width - 0.5*inch, 0.28*inch, page_text)
            
            canvas.restoreState()
        
        # Use PORTRAIT orientation
        doc = SimpleDocTemplate(response, pagesize=letter, 
                                rightMargin=0.5*inch, leftMargin=0.5*inch,
                                topMargin=1*inch, bottomMargin=0.7*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1e3a5f'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Title
        title = Paragraph('RAINFALL & TIDE TRENDS REPORT', title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.08*inch))
        
        # Metadata with professional styling
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#4a5568'),
            leading=11,
            alignment=TA_CENTER
        )
        
        metadata_text = f'''
        <b>Report Generated:</b> {datetime.now().strftime("%B %d, %Y at %I:%M %p")} | 
        <b>Time Range:</b> {range_label} | 
        <b>Total Data Points:</b> {len(combined_data):,} records | 
        <b>Document Type:</b> Environmental Monitoring Data | 
        <b>Prepared By:</b> Silay City DRRMO
        '''
        
        metadata_para = Paragraph(metadata_text, metadata_style)
        metadata_table = Table([[metadata_para]], colWidths=[7*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#3b82f6')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(metadata_table)
        elements.append(Spacer(1, 0.12*inch))
        
        # Table text styles
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor=colors.white
        )
        
        cell_style_center = ParagraphStyle(
            'CellStyleCenter',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_CENTER
        )
        
        cell_style_right = ParagraphStyle(
            'CellStyleRight',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_RIGHT
        )
        
        # Table headers
        table_data = [[
            Paragraph('#', header_style),
            Paragraph('Date & Time', header_style),
            Paragraph('Rainfall (mm)', header_style),
            Paragraph('Tide Level (m)', header_style)
        ]]
        
        # Add all records
        for idx, data in enumerate(combined_data, 1):
            rainfall_value = f"{data['rainfall'].value_mm:.2f}" if data['rainfall'] else '0.00'
            tide_value = f"{data['tide'].height_m:.2f}" if data['tide'] else '0.00'
            
            table_data.append([
                Paragraph(str(idx), cell_style_center),
                Paragraph(data['timestamp'].strftime('%Y-%m-%d  %H:%M'), cell_style_center),
                Paragraph(rainfall_value, cell_style_right),
                Paragraph(tide_value, cell_style_right)
            ])
        
        # Column widths for portrait
        col_widths = [
            0.5*inch,   # #
            2.5*inch,   # Date & Time
            2*inch,     # Rainfall
            2*inch      # Tide Level
        ]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.75, colors.HexColor('#cbd5e0')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Border styling
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e3a5f')),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#cbd5e0')),
        ]))
        
        elements.append(table)
        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        
        return response


@login_required
def export_flood_records(request):
    """Export flood records to CSV or PDF"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT
    
    export_type = request.GET.get('type', 'csv')
    start_year = request.GET.get('start_year')
    end_year = request.GET.get('end_year')
    
    # Fetch flood records with optional year filtering
    flood_records = FloodRecord.objects.all().order_by('-date')
    
    # Apply year filters if provided
    if start_year:
        try:
            flood_records = flood_records.filter(date__year__gte=int(start_year))
        except ValueError:
            pass
    
    if end_year:
        try:
            flood_records = flood_records.filter(date__year__lte=int(end_year))
        except ValueError:
            pass
    
    if export_type == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        filename = f'flood_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['# Flood Records Export'])
        writer.writerow([f'# Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}'])
        writer.writerow([f'# Total Records: {flood_records.count()}'])
        writer.writerow([])
        
        writer.writerow([
            '#', 'Date', 'Event', 'Barangays', 'Dead', 'Injured', 'Missing',
            'Affected Persons', 'Affected Families', 'Houses Damaged (Partial)',
            'Houses Damaged (Total)', 'Infrastructure Damage (PHP)', 'Agriculture Damage (PHP)',
            'Institutions Damage (PHP)', 'Private/Commercial Damage (PHP)', 'Total Damage (PHP)'
        ])
        
        for idx, record in enumerate(flood_records, 1):
            writer.writerow([
                idx,
                record.date.strftime('%Y-%m-%d'),
                record.event,
                record.affected_barangays,
                record.casualties_dead,
                record.casualties_injured,
                record.casualties_missing,
                record.affected_persons,
                record.affected_families,
                record.houses_damaged_partially,
                record.houses_damaged_totally,
                f'₱{record.damage_infrastructure_php:,.2f}',
                f'₱{record.damage_agriculture_php:,.2f}',
                f'₱{record.damage_institutions_php:,.2f}',
                f'₱{record.damage_private_commercial_php:,.2f}',
                f'₱{record.damage_total_php:,.2f}'
            ])
        
        return response
    
    elif export_type == 'pdf':
        from reportlab.lib.utils import ImageReader
        from reportlab.platypus import Image as RLImage
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os
        
        response = HttpResponse(content_type='application/pdf')
        filename = f'flood_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Custom page template with header and footer (LANDSCAPE)
        def add_header_footer(canvas, doc):
            canvas.saveState()
            
            # Header - DRRMO logo/header
            header_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR / 'static', 'images', 'drrmo_header.png')
            if os.path.exists(header_path):
                try:
                    page_width = landscape(letter)[0]
                    canvas.drawImage(header_path, 0, doc.height + doc.topMargin, 
                                   width=page_width, height=0.9*inch, 
                                   preserveAspectRatio=True, mask='auto')
                except:
                    pass
            
            # Footer line
            page_width = landscape(letter)[0]
            canvas.setStrokeColor(colors.HexColor('#1e3a5f'))
            canvas.setLineWidth(2)
            canvas.line(0.4*inch, 0.45*inch, page_width - 0.4*inch, 0.45*inch)
            
            # Footer text
            canvas.setFont('Helvetica-Bold', 8)
            canvas.setFillColor(colors.HexColor('#1e3a5f'))
            footer_text = "SILAY CITY DISASTER RISK REDUCTION & MANAGEMENT COUNCIL"
            text_width = canvas.stringWidth(footer_text, 'Helvetica-Bold', 8)
            canvas.drawString((page_width - text_width) / 2, 0.28*inch, footer_text)
            
            # Page number
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.HexColor('#6b7280'))
            page_text = f"Page {doc.page}"
            canvas.drawRightString(page_width - 0.4*inch, 0.28*inch, page_text)
            
            canvas.restoreState()
        
        # Use LANDSCAPE orientation
        doc = SimpleDocTemplate(response, pagesize=landscape(letter), 
                                rightMargin=0.4*inch, leftMargin=0.4*inch,
                                topMargin=1*inch, bottomMargin=0.7*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1e3a5f'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Title
        title = Paragraph('FLOOD RECORDS & DAMAGE ASSESSMENT REPORT', title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.08*inch))
        
        # Metadata with professional styling
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#4a5568'),
            leading=11,
            alignment=TA_CENTER
        )
        
        # Build metadata text with optional filter info
        filter_info = ""
        if start_year or end_year:
            if start_year and end_year:
                filter_info = f" | <b>Filtered:</b> Years {start_year} - {end_year}"
            elif start_year:
                filter_info = f" | <b>Filtered:</b> From year {start_year}"
            elif end_year:
                filter_info = f" | <b>Filtered:</b> Up to year {end_year}"
        
        metadata_text = f'''
        <b>Report Generated:</b> {datetime.now().strftime("%B %d, %Y at %I:%M %p")} | 
        <b>Total Flood Events:</b> {flood_records.count():,} records{filter_info} | 
        <b>Document Type:</b> Historical Flood Event Documentation | 
        <b>Prepared By:</b> Silay City DRRMO
        '''
        
        metadata_para = Paragraph(metadata_text, metadata_style)
        metadata_table = Table([[metadata_para]], colWidths=[9.5*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#3b82f6')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(metadata_table)
        elements.append(Spacer(1, 0.12*inch))
        
        # Table text styles
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=7,
            leading=9,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor=colors.white
        )
        
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontSize=7,
            leading=9,
            alignment=TA_LEFT,
            wordWrap='CJK'
        )
        
        cell_style_center = ParagraphStyle(
            'CellStyleCenter',
            parent=styles['Normal'],
            fontSize=7,
            leading=9,
            alignment=TA_CENTER
        )
        
        cell_style_right = ParagraphStyle(
            'CellStyleRight',
            parent=styles['Normal'],
            fontSize=7,
            leading=9,
            alignment=TA_RIGHT
        )
        
        # Table headers
        table_data = [[
            Paragraph('#', header_style),
            Paragraph('Date', header_style),
            Paragraph('Event', header_style),
            Paragraph('Barangays', header_style),
            Paragraph('Casualties<br/>(D/I/M)', header_style),
            Paragraph('Affected<br/>Persons', header_style),
            Paragraph('Affected<br/>Families', header_style),
            Paragraph('Houses<br/>(P/T)', header_style),
            Paragraph('Infrastructure<br/>Damage (PHP)', header_style),
            Paragraph('Agriculture<br/>Damage (PHP)', header_style),
            Paragraph('Total<br/>Damage (PHP)', header_style)
        ]]
        
        # Add all records without truncating
        for idx, record in enumerate(flood_records, 1):
            # Format casualties as D/I/M
            casualties = f"{record.casualties_dead}/{record.casualties_injured}/{record.casualties_missing}"
            
            # Format houses as P/T
            houses = f"{record.houses_damaged_partially}/{record.houses_damaged_totally}"
            
            # Format currency values (use PHP instead of peso symbol)
            infra_dmg = f"PHP {record.damage_infrastructure_php:,.0f}"
            agri_dmg = f"PHP {record.damage_agriculture_php:,.0f}"
            total_dmg = f"PHP {record.damage_total_php:,.0f}"
            
            table_data.append([
                Paragraph(str(idx), cell_style_center),
                Paragraph(record.date.strftime('%Y-%m-%d'), cell_style_center),
                Paragraph(str(record.event), cell_style),  # No truncation
                Paragraph(str(record.affected_barangays), cell_style),  # No truncation
                Paragraph(casualties, cell_style_center),
                Paragraph(f"{record.affected_persons:,}", cell_style_right),
                Paragraph(f"{record.affected_families:,}", cell_style_right),
                Paragraph(houses, cell_style_center),
                Paragraph(infra_dmg, cell_style_right),
                Paragraph(agri_dmg, cell_style_right),
                Paragraph(total_dmg, cell_style_right)
            ])
        
        # Optimized column widths for landscape
        col_widths = [
            0.3*inch,   # #
            0.75*inch,  # Date
            1.5*inch,   # Event (wider)
            1.4*inch,   # Barangays (wider to prevent cutoff)
            0.65*inch,  # Casualties
            0.75*inch,  # Affected Persons
            0.75*inch,  # Affected Families
            0.6*inch,   # Houses
            1.05*inch,  # Infrastructure
            1.0*inch,   # Agriculture
            1.05*inch   # Total Damage
        ]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            
            # Vertical lines for better separation
            ('LINEAFTER', (0, 0), (0, -1), 1, colors.HexColor('#d1d5db')),
            ('LINEAFTER', (1, 0), (1, -1), 1, colors.HexColor('#d1d5db')),
            ('LINEAFTER', (3, 0), (3, -1), 1, colors.HexColor('#d1d5db')),
            ('LINEAFTER', (7, 0), (7, -1), 1, colors.HexColor('#d1d5db')),
        ]))
        
        elements.append(table)
        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        
        return response