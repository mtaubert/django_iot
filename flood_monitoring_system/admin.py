from django.contrib import admin
from flood_monitoring_system.models import environmental_agency_flood_data, MqttWaterLevelData,  User, Subscriptions, StationInformation, StationReadings, FloodArea, FloodAreaPolygon, FloodAlerts

admin.site.register(environmental_agency_flood_data)
admin.site.register(MqttWaterLevelData)
admin.site.register(Subscriptions)
admin.site.register(User)
admin.site.register(StationInformation)
admin.site.register(StationReadings)
admin.site.register(FloodAreaPolygon)
admin.site.register(FloodAlerts)
admin.site.register(FloodArea)