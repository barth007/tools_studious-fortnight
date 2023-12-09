import csv
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from geopy.geocoders import Nominatim

class KMLParser:
    def __init__(self):
        self.csv_file = 'extracted_data.csv'
        self.header_row = [
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
        ]
        self.geolocation = Nominatim(user_agent="kml_parser")

    def write_header_row(self):
        with open(self.csv_file, mode='a', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            if csv_file.tell() == 0:
                csv_writer.writerow(self.header_row)

    def parse_coordinates(self, coordinates):
        coordinates = coordinates.split(',') if coordinates else ['NULL', 'NULL', 'NULL']
        pattern = r'\b\d+\.\d+\s+\d+\.\d+\b'
        for point in coordinates:
            match = re.search(pattern, point)
            if match:
                found_coordinates = match.group()
                latitude, longitude = found_coordinates.split()
                return latitude, longitude
        return 'NULL', 'NULL'

    def parse_placemark(self, placemark, ns):
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
        return name, desc, sampleid, visibleid, coordinates

    def parse_location(self, latitude, longitude):
        attempts = 3  # Set the maximum number of attempts
        for _ in range(attempts):
            try:
                location = self.geolocation.reverse(f"{latitude}, {longitude}")
                print(location)
                return [
                    location.raw.get('address', {}).get('city', 'NULL'),
                    location.raw.get('address', {}).get('county', 'NULL'),
                    location.raw.get('address', {}).get('state', 'NULL'),
                    location.raw.get('address', {}).get('country', 'NULL')
                    ]
            except Exception as e:
                print(f"Geocoding service error: {e}. Retrying...")
                print(f"Unable to retrieve location after {attempts} attempts. Returning default values.")
                return ['NULL', 'NULL', 'NULL', 'NULL']

    def parse_kml(self, folder_path):
        self.write_header_row()
        with open(self.csv_file, mode='a', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            for filename in folder_path.iterdir():
                if filename.is_file():
                    tree = ET.parse(filename)
                    root = tree.getroot()
                    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
                    placemarks = root.findall('.//kml:Placemark', ns)
                    for placemark in placemarks:
                        name, desc, sampleid, visibleid, coordinates = self.parse_placemark(placemark, ns)
                        print(name, desc, sampleid, visibleid, coordinates)
                        #if coordinates and sampleid and visibleid:
                        latitude, longitude = self.parse_coordinates(coordinates)
                        town, county, state, country = self.parse_location(latitude, longitude)
                        csv_writer.writerow(['T',
                            name,
                            desc,
                            sampleid,
                            visibleid,
                            latitude,
                            longitude,
                            town,
                            county,
                            state,
                            country])
                        #else:
                            #pass

# Usage example
if __name__ == "__main__":
    parser = KMLParser()
    folder_path = Path('extract_folder_path')
    parser.parse_kml(folder_path)

