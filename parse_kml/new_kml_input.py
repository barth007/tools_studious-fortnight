import csv
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from geopy.geocoders import Nominatim

# Collect data in a list of lists
data_rows = []

folder_path = Path('extract_folder_path')
for filename in folder_path.iterdir():
    if filename.is_file():
        tree = ET.parse(filename)
        root = tree.getroot()
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        placemarks = root.findall('.//kml:Placemark', ns)

        for placemark in placemarks:
            name = placemark.find('.//kml:name', ns).text if placemark.find('.//kml:name', ns) is not None else 'NULL'
            desc = placemark.find('.//kml:description', ns).text if placemark.find('.//kml:description', ns) is not None else 'NULL'
            sampleid = placemark.find('.//kml:ExtendedData/kml:Data[@name="sampleId"]/kml:value', ns).text if placemark.find('.//kml:ExtendedData/kml:Data[@name="sampleId"]/kml:value', ns) is not None else ''
            visibleid = placemark.find('.//kml:ExtendedData/kml:Data[@name="visibleId"]/kml:value', ns).text if placemark.find('.//kml:ExtendedData/kml:Data[@name="visibleId"]/kml:value', ns) is not None else ''
            coordinates = placemark.find('.//kml:coordinates', ns).text if placemark.find('.//kml:coordinates', ns) is not None else 'NULL'

            coordinates = coordinates.split(',') if coordinates else ['NULL', 'NULL', 'NULL']
            pattern = r'\b\d+\.\d+\s+\d+\.\d+\b'
            for point in coordinates:
                match = re.search(pattern, point)
                if match:
                    found_coordinates = match.group()
                    latitude, longitude = found_coordinates.split()
                    break

            attempt = 3
            for _ in range(attempt):
                try:
                    geolocation = Nominatim(user_agent="kml_parser")
                    location = geolocation.reverse(f"{latitude}, {longitude}")
                    break
                except Exception as e:
                    print(f"Geocoding service error: {e}. Retrying...")
                print("result to default value")
                #location = ['NULL', 'NULL', 'NULL', 'NULL']
                location = {'raw': {'address': {'village': 'NULL', 'county': 'NULL', 'state': 'NULL', 'country': 'NULL'}}}


            data_rows.append([
                'T', name, desc, sampleid, visibleid, latitude, longitude,
                location.raw.get('address', {}).get('village', 'NULL'),
                location.raw.get('address', {}).get('county') if location.raw.get('address', {}).get('county') else location.raw.get('address', {}).get('town', 'NULL'),
                location.raw.get('address', {}).get('state', 'NULL'),
                location.raw.get('address', {}).get('country', 'NULL')
            ])

# Sort the data based on the 'SAMPLE_ID'
sorted_data = sorted(data_rows, key=lambda x: x[3] if x[3] else '')
print(sorted_data)

# Write the sorted data to the CSV file
with open('extracted_data.csv', mode='a', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    if csv_file.tell() == 0:
        csv_writer.writerow([
            'TYPE', 'NAME', 'DESC', 'SAMPLE_ID', 'VISIBLE_ID', 
            'LATITUDE', 'LONGITUDE', 'VILLAGE', 'LGA', 'STATE', 'COUNTRY'
        ])
    
    for row in sorted_data:
        csv_writer.writerow(row)

