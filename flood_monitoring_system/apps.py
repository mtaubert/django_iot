from django.apps import AppConfig
import ttn
import base64, time, datetime
import _thread, threading
import urllib.request, json


class FloodMonitoringSystemConfig(AppConfig):
    name = 'flood_monitoring_system'

    def ready(self):

        # app_id = ""
        # access_key = ""
        # port = ""
        # address = ""
        #
        # def uplink_callback(msg, client):
        #     try:
        #         from flood_monitoring_system.models import MqttWaterLevelData
        #         print("Received uplink from ", msg.dev_id)
        #         print("----------------------------------------------------------------------------------------------------------------")
        #         print(msg.hardware_serial)
        #         print(msg.metadata.time)
        #         print(msg.payload_raw)
        #         print(msg.metadata.altitude)
        #         print(msg.metadata.longitude)
        #         print(msg.metadata.latitude)
        #         MQTTData = MqttWaterLevelData()
        #         MQTTData.hardware_serial = msg.hardware_serial
        #         MQTTData.longitude = msg.metadata.longitude
        #         MQTTData.latitude = msg.metadata.latitude
        #         MQTTData.altitude = msg.metadata.altitude
        #         MQTTData.river_height_mm = int.from_bytes(base64.b64decode(""+msg.payload_raw+""), 'big')  # int(base64.b64decode(msg.payload_raw).encode('hex'), 16)
        #         dt = ""+msg.metadata.time+"" #daytime
        #         d = dt.split("T")[0]   #day
        #         t = dt.split(".")[0].split("T")[1] #time
        #         MQTTData.time = int(time.mktime(time.strptime(d+" "+t, '%Y-%m-%d %H:%M:%S'))) * 1000 #timestamp milliseconds
        #         MQTTData.save()
        #         print("----------------------------------------------------------------------------------------------------------------")
        #     except Exception as error:
        #         print("Error: ", repr(error))
        #         raise
        # print("start mqtt detection")
        #
        # mqtt_client = ttn.MQTTClient(app_id, access_key, mqtt_address=address)
        # mqtt_client.set_uplink_callback(uplink_callback)
        # mqtt_client.connect()

        def query_new_water_levels(url, delay):
            from flood_monitoring_system.models import StationInformation, StationReadings

            while(1):
                try:
                    with urllib.request.urlopen(url) as json_url:
                        httpStatusCode = json_url.getcode()
                        if httpStatusCode == 200:
                            readings = json.loads(json_url.read().decode())
                except:
                    httpStatusCode = 0;

                if not httpStatusCode == 200:
                    print("Can't connect to: " + url)
                else:
                    print("Getting new water level data")
                    stations = StationInformation.objects.all()
                    station_measures = []

                    for s in stations:
                        station_measures.append(s.measure_id)

                    for reading in readings['items']:
                        if reading['measure'] in station_measures:
                            current_station = stations[station_measures.index(reading['measure'])]
                            #print(current_station.station_reference)
                            if not reading['value'] == StationReadings.get_newest("", current_station)["pin_data"][0]["reading"]:
                                # print(current_station.station_reference)
                                # print(str(
                                #     StationReadings.get_newest("", current_station)["pin_data"][0]["reading"]))
                                # print(str(reading['value']))
                                new_reading = StationReadings()
                                new_reading.station = current_station
                                new_reading.reading = reading["value"]

                                dt = "" + reading["dateTime"] + ""  # daytime
                                d = dt.split("T")[0]  # day
                                t = dt.split("Z")[0].split("T")[1]  # time

                                new_reading.time = int(
                                    time.mktime(time.strptime(d + " " + t, '%Y-%m-%d %H:%M:%S'))) * 1000
                                # print(new_reading.station)
                                # print(new_reading.reading)
                                # print(new_reading.time)
                                new_reading.save()
                    print("Water level data updated")
                    time.sleep(delay)

        def query_flood_warnings(url, delay):
            from flood_monitoring_system.models import FloodAlerts, FloodArea, User, Subscriptions, StationInformation
            while(1):
                try:
                    with urllib.request.urlopen(url) as flood_data_url:
                        httpStatusCode = flood_data_url.getcode()
                        if httpStatusCode == 200:
                            floodData = json.loads(flood_data_url.read().decode())
                except:
                    httpStatusCode = 0;

                if not httpStatusCode == 200:
                    print("Can't connect to: " + url)
                else:
                    print("Getting flood data")
                    sendEmail = False
                    for warning in floodData['items']:
                        if "Great Stour" in warning['floodArea']["riverOrSea"]:
                            floodArea = FloodArea.objects.filter(area_code=warning['floodAreaID'])[0]

                            for u in User.objects.all():
                                warningSet = False
                                for s in Subscriptions.objects.filter(user=u):
                                    for a in StationInformation.objects.filter(RLOIid=s.station):
                                        if FloodAlerts.calculate_distance("", float(a.long),
                                                                          float(floodArea.long),
                                                                          float(a.lat),
                                                                          float(floodArea.lat)) < 10:
                                            if not warningSet and not FloodAlerts.objects.filter(user=u ,flood_id=warning['@id']):
                                                new_alert = FloodAlerts()
                                                new_alert.flood_area = floodArea
                                                new_alert.user = u
                                                new_alert.message = warning['message']
                                                new_alert.severity_rating = warning['severityLevel']
                                                new_alert.severity_message = warning['severity']
                                                new_alert.time = warning['timeRaised']
                                                new_alert.flood_id = warning['@id']
                                                new_alert.save()
                                                warningSet = True
                                                sendEmail = True
                if sendEmail:
                    FloodAlerts.send_flood_warning_email("")
                time.sleep(delay)

        #Grabs the details for the station at the given url
        def query_station_details(url):
            from flood_monitoring_system.models import StationInformation

            #Check if the website is responsive
            try:
                with urllib.request.urlopen(url) as json_url:
                    httpStatusCode = json_url.getcode()
                    if httpStatusCode == 200: #only try to load the json if there is a connection
                        station_data = json.loads(json_url.read().decode())
            except:
                httpStatusCode = 0; #No connection

            if not httpStatusCode == 200: #Anything other than a 200 will abort the database update
                print("Can't connect to: " + url)
            else:
                print("Gathing station data")
                for station in station_data["items"]:
                    if 'RLOIid' in station and 'measures' in station and not StationInformation.objects.filter(station_reference=station["notation"]).exists():
                        new_station = StationInformation()
                        new_station.station_reference = station["notation"]
                        new_station.RLOIid = station["RLOIid"]
                        new_station.measure_id = station["measures"][0]["@id"]
                        new_station.label = station["label"]
                        new_station.river_name = station["riverName"]
                        new_station.town = station["town"]
                        new_station.lat = station["lat"]
                        new_station.long = station["long"]
                        new_station.save()

        #Digs for the last couple weeks of data from the stations stored in the database and adds the data to the readings database
        def query_historic_data(url_start, url_end):
            from flood_monitoring_system.models import StationInformation, StationReadings
            stations = StationInformation.objects.all()
            for s in stations:
                if not StationReadings.objects.filter(station=s.station_reference).exists():
                    reading_url = url_start + s.station_reference + url_end
                    print(reading_url)
                    try:
                        with urllib.request.urlopen(reading_url) as json_url:
                            httpStatusCode = json_url.getcode()
                            if httpStatusCode == 200:
                                reading_data = json.loads(json_url.read().decode())
                    except:
                        httpStatusCode = 0;

                    if not httpStatusCode == 200:
                        print("Cannot get historic data for station: " + s.station_reference)
                    else:
                        previous_reading = -100
                        for r in reading_data["items"]:
                            if not r['value'] == previous_reading: #Only adds data if its different than the last value to prevent saving
                                print(s.station_reference + ": " + str(r["value"]))
                                new_reading = StationReadings()
                                new_reading.station = StationInformation.objects.filter(station_reference=s.station_reference)[0]
                                new_reading.reading = r["value"]

                                dt = "" + r["dateTime"] + ""  # daytime
                                d = dt.split("T")[0]  # day
                                t = dt.split("Z")[0].split("T")[1]  # time

                                new_reading.time = int(
                                    time.mktime(time.strptime(d + " " + t, '%Y-%m-%d %H:%M:%S'))) * 1000
                                new_reading.save()
                                previous_reading = r['value']

        #Removes duplicate station readings data to save space
        #Only for debugging use, this should be handled by the historic data query
        def remove_station_readings_duplicates():
            from flood_monitoring_system.models import StationInformation, StationReadings
            stations = StationInformation.objects.all()
            for s in stations:
                readings = StationReadings.objects.filter(station=s)
                readings_count = StationReadings.objects.filter(station=s).count()
                print(s.station_reference + ": " + str(readings_count))
                previous_reading = -100
                for r in readings:
                    if r.reading == previous_reading:
                        r.delete()
                    else:
                        previous_reading = r.reading

        def get_flood_polygons(url):
            from flood_monitoring_system.models import FloodArea, FloodAreaPolygon

            try:
                with urllib.request.urlopen(url) as json_url:
                    httpStatusCode = json_url.getcode()
                    if httpStatusCode == 200: #only try to load the json if there is a connection
                        flood_areas_data = json.loads(json_url.read().decode())
            except:
                httpStatusCode = 0; #No connection

            if not httpStatusCode == 200:
                print("Flood areas data not accessible")
            else:
                for area in flood_areas_data['items']:
                    if "Great Stour" in area['riverOrSea'] and not FloodArea.objects.filter(area_code=area['fwdCode']).exists():
                        print("Added flood area: " + area['fwdCode'])
                        flood_area = FloodArea()
                        flood_area.area_code = area['fwdCode']
                        flood_area.label = area['label']
                        flood_area.description = area['description']
                        flood_area.lat = area['lat']
                        flood_area.long = area['long']
                        flood_area.save()

        api_base_url = 'https://environment.data.gov.uk/flood-monitoring/'
        query_station_details(api_base_url + "id/stations?riverName=Great%20Stour")
        query_historic_data(api_base_url + "id/stations/", "/readings?_sorted")
        get_flood_polygons(api_base_url + "id/floodAreas?county=Kent")

        #remove_station_readings_duplicates()
        try:
            _thread.start_new_thread(query_new_water_levels, ("https://environment.data.gov.uk/flood-monitoring/data/readings?latest", 900))
            _thread.start_new_thread(query_flood_warnings, (api_base_url +"id/floods", 900))
        except:
            print("Error starting thread")
