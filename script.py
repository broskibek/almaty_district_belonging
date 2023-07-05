import json
import requests
from shapely.geometry import shape, Point
import pandas as pd

# Step 1: Load the JSON file containing the district polygons
json_url = "https://raw.githubusercontent.com/akilbekov/almaty.geo.json/master/almaty-districts.geo.json"
response = requests.get(json_url)
json_data = json.loads(response.text)

# Step 2: Extract the district polygons from the JSON data
districts = []
for feature in json_data['features']:
    polygon = shape(feature['geometry'])
    district_name = feature['properties']['name']
    districts.append((district_name, polygon))

# Step 3: Read the CSV file containing the coordinates
csv_file = 'Coordinates.csv'
df = pd.read_csv(csv_file)

# Step 4: Assign district names based on the coordinates
district_names = []
for index, row in df.iterrows():
    # xlsx file should have 2 columns: Latitude and Longitude respectively
    point = Point(row['Longitude'], row['Latitude'])
    district_name = None
    for name, district in districts:
        if district.contains(point):
            district_name = name
            break
    if district_name is None:
        district_name = "Unknown"  # Assign a default value for unknown districts
    district_names.append(district_name)

# Step 5: Add the district names as a new column in the DataFrame
df['district'] = district_names

# Step 6: Write the updated DataFrame back to the CSV file
df.to_csv(csv_file, index=False)

# Confirm the update
print("District names successfully assigned and saved to the CSV file.")
