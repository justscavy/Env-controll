#from influxdb_client import InfluxDBClient
#DELETS ALL UR LOCAL HISTORZ CARE
# Replace with your InfluxDB details
url = ""
token = ""
org = ""
bucket = ""

client = InfluxDBClient(url=url, token=token, org=org)

delete_api = client.delete_api()


start = "1970-01-01T00:00:00Z"
stop = "2024-12-31T23:59:59Z"

delete_api.delete(start, stop, '_measurement="sensor_data"', bucket=bucket, org=org)

client.close()
