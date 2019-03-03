from email._header_value_parser import Domain
from _datetime import datetime, timedelta
from django.db import models
from math import sin, cos, sqrt, atan2, radians

# Create your models here.
class MqttWaterLevelData(models.Model):
    hardware_serial = models.CharField(max_length=20)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    altitude = models.IntegerField()
    river_height_mm = models.CharField(max_length=6)
    time = models.CharField(max_length=20)

    class Meta:
        unique_together = ("time", "hardware_serial")

    def get_newest(self):
        newest = MqttWaterLevelData.objects.all().order_by('-time')[:1]
        viewdata = {
            "pin_data": [
            ]
        }
        for name in MqttWaterLevelData.objects.all().values("hardware_serial").distinct():
            print(name["hardware_serial"])
            newest = MqttWaterLevelData.objects.all().filter(hardware_serial=name["hardware_serial"]).order_by('-time')[:1]
            viewdata["pin_data"].append({
                    "id": newest[0].hardware_serial,
                    "lat": newest[0].latitude,
                    "long": newest[0].longitude,
                    "alt": newest[0].altitude,
                    "reading": newest[0].river_height_mm,
                    "time": newest[0].time
                })
        #print(viewdata)
        return viewdata

    def get_all(self):
        #results = MqttWaterLevelData.objects.
        viewdata = {
            "results": []
        }
        for name in MqttWaterLevelData.objects.all().values("hardware_serial").distinct():
            newest = MqttWaterLevelData.objects.all().filter(hardware_serial=name["hardware_serial"]).order_by('-time')
            heights_and_times = []
            for item in newest:
                heights_and_times.append((item.time, item.river_height_mm))
            viewdata["results"].append({
                "id": name,
                "time_reading": heights_and_times,
                "lat": newest[0].latitude,
                "long": newest[0].longitude,
            })
        #print(viewdata)
        return viewdata

    def get_between_dates(self, min_time, max_time):
        viewdata = {
            "results": []
        }
        for name in MqttWaterLevelData.objects.all().values("hardware_serial").distinct():
            all_for_station = MqttWaterLevelData.objects.all().filter(hardware_serial=name["hardware_serial"]).order_by('-time')
            heights_and_times = []
            for item in all_for_station:
                cur_time = datetime.fromtimestamp(int(item.time[0:10]))
                if max_time > cur_time > min_time:
                    heights_and_times.append((item.time, item.river_height_mm))
            viewdata["results"].append({
                "id": name,
                "time_reading": heights_and_times,
                "lat": all_for_station[0].latitude,
                "long": all_for_station[0].longitude,
            })

        return viewdata


    def get_presets(self):
        viewdata = {
            "day": [],
            "week": [],
            "month": []
        }
        for name in MqttWaterLevelData.objects.all().values("hardware_serial").distinct():
            all_for_station = MqttWaterLevelData.objects.all().filter(hardware_serial=name["hardware_serial"]).order_by('-time')
            day = []
            week = []
            month = []
            for item in all_for_station:
                cur_time = datetime.fromtimestamp(int(item.time[0:10]))
                if cur_time > datetime.now() - timedelta(days=30):
                    month.append((item.time, item.river_height_mm))
                if cur_time > datetime.now() - timedelta(days=7):
                    week.append((item.time, item.river_height_mm))
                if cur_time > datetime.now() - timedelta(days=1):
                    day.append((item.time, item.river_height_mm))

            viewdata["day"].append({
                "id": name,
                "time_reading": day,
                "lat": all_for_station[0].latitude,
                "long": all_for_station[0].longitude,
            })

            viewdata["week"].append({
                "id": name,
                "time_reading": week,
                "lat": all_for_station[0].latitude,
                "long": all_for_station[0].longitude,
            })

            viewdata["month"].append({
                "id": name,
                "time_reading": month,
                "lat": all_for_station[0].latitude,
                "long": all_for_station[0].longitude,
            })

        return viewdata


class environmental_agency_flood_data(models.Model):
    sensor_id = models.CharField(max_length=80)
    label = models.CharField(max_length=40)
    town = models.CharField(max_length=40)
    river = models.CharField(max_length=40)
    lat = models.DecimalField(max_digits=9, decimal_places=7)
    long = models.DecimalField(max_digits=10, decimal_places=7)
    reading = models.FloatField()
    time = models.CharField(max_length = 20)

    def get_newest(self):
        newest = environmental_agency_flood_data.objects.all().order_by('-time')[:1]

        viewdata = {
            "pin_data": [
                {
                    "id": newest[0].sensor_id,
                    "label": newest[0].label,
                    "river": newest[0].river,
                    "town": newest[0].town,
                    "lat": newest[0].lat,
                    "long": newest[0].long,
                    "reading": newest[0].reading*1000,
                    "time": newest[0].time
                }
            ]
        }
        return viewdata



    def get_all(self):
        newest = environmental_agency_flood_data.objects.all().order_by('-time')
        viewdata = {
            "results": []
        }
        heights_and_times = []
        for item in newest:
            heights_and_times.append((item.time, item.reading*1000))
            viewdata["results"].append({
                "id": newest[0].label,
                "time_reading": heights_and_times,
                "lat": newest[0].lat,
                "long": newest[0].long,
            })
        return viewdata


class test_environmental_agency_flood_data(models.Model):
    sensor_id = models.CharField(max_length = 80)
    label = models.CharField(max_length = 40)
    town = models.CharField(max_length=40)
    river = models.CharField(max_length=40)
    lat = models.DecimalField(max_digits=9, decimal_places=7)
    long = models.DecimalField(max_digits=10, decimal_places=7)
    reading = models.FloatField()
    time = models.DateTimeField(auto_now=False, auto_now_add=False)
    station = models.CharField(null=False, default=False, max_length=10)

    def get_newest(self):
        newest = test_environmental_agency_flood_data.objects.all().order_by('-time')[:1]

        viewdata = {
            "pin_data": [
                {
                    "id": newest[0].sensor_id,
                    "label": newest[0].label,
                    "river": newest[0].sensor_id,
                    "town": newest[0].town,
                    "lat": newest[0].lat,
                    "long": newest[0].long,
                    "reading": newest[0].reading,
                    "time": newest[0].time
                }
            ]
        }
        return viewdata

class User(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=64)

class Subscriptions(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=False, default=False, on_delete=models.CASCADE)
    label = models.CharField(max_length=50, null=False, default="")
    station = models.CharField(max_length=10)

class StationInformation(models.Model):
    station_reference = models.CharField(primary_key=True, max_length=20)
    RLOIid = models.CharField(max_length=10)
    measure_id = models.CharField(max_length=200)
    label = models.CharField(max_length=40)
    town = models.CharField(max_length=40)
    river_name = models.CharField(max_length=40)
    lat = models.DecimalField(max_digits=9, decimal_places=7)
    long = models.DecimalField(max_digits=10, decimal_places=7)

class StationReadings(models.Model):
    station = models.ForeignKey(StationInformation, on_delete=models.CASCADE)
    reading = models.FloatField()
    time = models.CharField(max_length=20)


    def get_newest_by_cookie(self, id):
        subscriptions = Subscriptions.objects.filter(user=id)
        print(subscriptions)
        viewdata = {
            "pin_data": []
        }
        if subscriptions.count():
            for item in subscriptions:
                print(item.station)
                station = StationInformation.objects.filter(RLOIid=item.station)
                print(station.count())
                newest = StationReadings.objects.filter(station_id=station[0].station_reference).order_by('-time')[:1]
                viewdata["pin_data"].append({
                    "id": newest[0].station.station_reference,
                        "label": newest[0].station.label,
                        "river": newest[0].station.river_name,
                        "town": newest[0].station.town,
                        "lat": newest[0].station.lat,
                        "long": newest[0].station.long,
                        "reading": int(newest[0].reading*1000),
                        "time": newest[0].time
                })

        return viewdata


    def get_newest(self, selected_station):
        newest = StationReadings.objects.all().filter(station=selected_station).order_by('-time')[:1]

        viewdata = {
            "pin_data": [
                {
                    "id": newest[0].station.station_reference,
                    "label": newest[0].station.label,
                    "river": newest[0].station.river_name,
                    "town": newest[0].station.town,
                    "lat": newest[0].station.lat,
                    "long": newest[0].station.long,
                    "reading": newest[0].reading,
                    "time": newest[0].time
                }
            ]
        }
        return viewdata

    def get_all_by_cookie(self, id):
        subscriptions = Subscriptions.objects.filter(user=id)
        print(subscriptions)
        viewdata = {
            "results": []
        }

        for item in subscriptions:
            i = 0
            print(item.station)
            station = StationInformation.objects.filter(RLOIid=item.station)
            newest = StationReadings.objects.filter(station_id=station[0].station_reference).order_by('-time')
            heights_and_times = []
            for val in newest:
                heights_and_times.append((val.time, val.reading * 1000))
            print()
            viewdata["results"].append({
                "id": newest[i].station.label,
                "time_reading": heights_and_times,
                "lat": newest[i].station.lat,
                "long": newest[i].station.long,
                "label": newest[i].station.label,
                "river": newest[i].station.river_name,
                "town": newest[i].station.town,
            })
            i+=1
            print(viewdata["results"])
        return viewdata

class FloodArea(models.Model):
    area_code = models.CharField(primary_key=True, max_length=25)
    label = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    lat = models.DecimalField(max_digits=9, decimal_places=7)
    long = models.DecimalField(max_digits=10, decimal_places=7)

    def get_all(self):
        newest = FloodArea.objects.all()
        viewdata = {
            "results": []
        }
        heights_and_times = []
        for item in newest:
            viewdata["results"].append({
                "area": item.area_code,
                "descr": item.description,
                "label": item.label,
            })
        return viewdata

class FloodAreaPolygon(models.Model):
    flood_area = models.ForeignKey(FloodArea, on_delete=models.CASCADE)
    lat = models.DecimalField(max_digits=9, decimal_places=7)
    long = models.DecimalField(max_digits=10, decimal_places=7)

class FloodAlerts(models.Model):
    flood_area = models.ForeignKey(FloodArea, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    message = models.CharField(max_length=1000)
    severity_rating = models.IntegerField()
    severity_message = models.CharField(max_length=40)
    time = models.DateTimeField(null=True, auto_now=False, auto_now_add=False)
    read = models.BooleanField(default=False)
    flood_id = models.CharField(max_length=80, null=True)

    #based on: https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
    def calculate_distance(self, lon1, lon2, lat1, lat2):
        dlon = radians(lon2) - radians(lon1)
        dlat = radians(lat2) - radians(lat1)
        R = 3961
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        d = R * c
        return d

    def get_alerts(self, u):
        print("SUBSCRIPTIONS")
        flood_alerts = {
            "alert_data": []
        }
        alerts = FloodAlerts.objects.filter(user=u[0])

        for alert in alerts:
            flood_alerts['alert_data'].append(
                {
                    "id": alert.id,
                    'flood_area': alert.flood_area,
                    'message': alert.message,
                    'severity_rating': alert.severity_rating,
                    'severity_message': alert.severity_message,
                    'time': alert.time,
                    'read': alert.read
                }
            )
        print("=======================")
        return(flood_alerts)

    def test_alert(self, alert_id, user):
        area = FloodArea.objects.filter(area_code=alert_id)
        subscriptions = Subscriptions.objects.filter(user_id=user)
        for sub in subscriptions:
            station = StationInformation.objects.filter(RLOIid=sub.station)
            if FloodAlerts.calculate_distance("", float(station[0].long), float(area[0].long),
                                              float(station[0].lat), float(area[0].lat)) < 10:
                return True
        return False

    def send_flood_warning_email(self):
        from flood_monitoring_system import email_notifications
        users = User.objects.all()
        for u in users:
            alerts = FloodAlerts.objects.filter(user=u, read=False)

            if alerts.exists():
                email_notifications.build_and_send_email(u, alerts)

    def send_flood_warning_email_from_dict(self, user, dict):
        from flood_monitoring_system import email_notifications
        usr = User.objects.filter(id=user)
        email_notifications.build_and_send_email(usr[0], dict)
