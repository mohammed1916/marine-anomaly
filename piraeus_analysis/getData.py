import requests
import json

# Define Piraeus bounding box (lon/lat)
bbox = {
    "west": 23.63,  # min longitude
    "south": 37.93, # min latitude
    "east": 23.66,  # max longitude
    "north": 37.96  # max latitude
}

# Temporal range
start_date = "2018-01-01T00:00:00Z"
end_date   = "2018-01-31T23:59:59Z"

# OData endpoint for Sentinel-1 GRD
odata_url = "https://scihub.copernicus.eu/dhus/odata/v1/Products"

# Build query parameters
params = {
    "$filter": f"substringof('IW', SensingMode) and " +
               f"substringof('GRD', ProductType) and " +
               f"BeginPosition ge {start_date} and EndPosition le {end_date}",
    "$top": 10,
    "$format": "json"
}

# Send GET request
response = requests.get(odata_url, params=params)
data = response.json()

# Print product titles and download links
for entry in data['value']:
    print("Title:", entry['Name'])
    print("URL:", entry['__metadata']['media_src'])
    print("-" * 40)
