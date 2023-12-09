import csv
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from geopy.geocoders import Nominatim

 # Open CSV file for writing
with open('extracted_data.csv', mode='a', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    # Write header row
    csv_writer.writerow([
        'TYPE', 
        'NAME', 
        'DESC', 
        'SAMPLE_ID', 
        'VISIBLE_ID', 
        'LATITUDE', 
        'LONGITUDE', 
        'TOWN', 
        'LGA',
        'STATE',
        'COUNTRY'
        ])

    folder_path = Path('extract_folder_path')
    for filename in folder_path.iterdir():
        if filename.is_file():
            # Load the KML file
            tree = ET.parse(filename)
            root = tree.getroot()

            # Namespace for KML


            ns = {'kml': 'http://www.opengis.net/kml/2.2'}

            # Find all placemarks in the KML file
            placemarks = root.findall('.//kml:Placemark', ns)

            for placemark in placemarks:
                name = placemark.find('.//kml:name', ns).text\
                if placemark.find('.//kml:name', ns) is not None else 'NULL'
                desc = placemark.find('.//kml:description', ns).text\
                if placemark.find('.//kml:description', ns) is not None else 'NULL'
                sampleid = placemark.find('.//kml:ExtendedData/kml:Data[@name="sampleId"]/kml:value', ns).text\
                if placemark.find('.//kml:ExtendedData/kml:Data[@name="sampleId"]/kml:value', ns) is not None else ''
                visibleid = placemark.find('.//kml:ExtendedData/kml:Data[@name="visibleId"]/kml:value', ns).text\
                if placemark.find('.//kml:ExtendedData/kml:Data[@name="visibleId"]/kml:value', ns) is not None else ''
                coordinates = placemark.find('.//kml:coordinates', ns).text\
                if placemark.find('.//kml:coordinates', ns) is not None else 'NULL'
                #print(coordinates)
                
                # Split coordinates into latitude, longitude, and altitude
                coordinates = coordinates.split(',') if coordinates else ['NULL', 'NULL', 'NULL']

                # creating a search pattern
                pattern = r'\b\d+\.\d+\s+\d+\.\d+\b'
                for point in coordinates:
                    match = re.search(pattern, point)
                    if match:
                        found_coodinates = match.group()
                        latitude, longitude = found_coodinates.split()
                        break
                attempt = 3
                for _ in range(attempt):
                    try:
                        geolocation = Nominatim(user_agent="kml_parser")
                        location = geolocation.reverse(f"{latitude}, {longitude}")
                        #print(location)
                        break
                    except Exception as e:
                        print(f"Geocoding service error: {e}. Retrying...")
                    print("result to default value")
                    location = ['NULL', 'NULL', 'NULL', 'NULL']
            print(location.raw.get('address'))
            csv_writer.writerow(['T', 
                name,
                desc,
                sampleid,
                visibleid,
                latitude,
                longitude,
                location.raw.get('address', {}).get('village', 'NULL'),
                location.raw.get('address', {}).get('county')\
                if location.raw.get('address', {}).get('county')\
                else location.raw.get('address', {}).get('town', 'NULL'),
                location.raw.get('address', {}).get('state',  'NULL'),
                location.raw.get('address', {}).get('country', 'NULL')
                ])
