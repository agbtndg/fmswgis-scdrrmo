from django.db import models

class RainfallData(models.Model):
    value_mm = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    station_name = models.CharField(max_length=100, default='Silay City')

class WeatherData(models.Model):
    temperature_c = models.FloatField(default=28.5)
    humidity_percent = models.IntegerField(default=75)
    wind_speed_kph = models.FloatField(default=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    station_name = models.CharField(max_length=100, default='Silay City')

class TideLevelData(models.Model):
    height_m = models.FloatField(default=0.8)
    timestamp = models.DateTimeField(auto_now_add=True)
    station_name = models.CharField(max_length=100, default='Silay City')

class FloodRecord(models.Model):
    event = models.CharField(max_length=200)
    date = models.DateField()
    affected_barangays = models.CharField(max_length=500)
    casualties_dead = models.IntegerField(default=0)
    casualties_injured = models.IntegerField(default=0)
    casualties_missing = models.IntegerField(default=0)
    affected_persons = models.IntegerField(default=0)
    affected_families = models.IntegerField(default=0)
    houses_damaged_partially = models.IntegerField(default=0)
    houses_damaged_totally = models.IntegerField(default=0)
    damage_infrastructure_php = models.FloatField(default=0)
    damage_agriculture_php = models.FloatField(default=0)
    damage_institutions_php = models.FloatField(default=0)
    damage_private_commercial_php = models.FloatField(default=0)
    damage_total_php = models.FloatField(default=0)

    def __str__(self):
        return f"{self.event} - {self.date}"

class BenchmarkSettings(models.Model):
    """Store flood risk benchmark thresholds for rainfall and tide level"""
    
    # MODERATE RISK thresholds - Trigger when BOTH conditions are met
    rainfall_moderate_threshold = models.FloatField(
        default=30,
        help_text="Rainfall threshold for Moderate Risk (mm) - Moderate alert when rainfall reaches this level"
    )
    tide_moderate_threshold = models.FloatField(
        default=1.0,
        help_text="Tide level threshold for Moderate Risk (m) - Moderate alert when tide reaches this level"
    )
    
    # HIGH RISK thresholds - Trigger when BOTH conditions are met
    rainfall_high_threshold = models.FloatField(
        default=50,
        help_text="Rainfall threshold for High Risk (mm) - High alert when rainfall reaches this level"
    )
    tide_high_threshold = models.FloatField(
        default=1.5,
        help_text="Tide level threshold for High Risk (m) - High alert when tide reaches this level"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Benchmark Settings"
        verbose_name_plural = "Benchmark Settings"
    
    def __str__(self):
        return "Flood Risk Benchmark Settings"
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton benchmark settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings