import csv
import xml.etree.ElementTree as ET

# Read KML data from a file
with open('data.kml', 'r', encoding='utf-8') as kml_file:
    kml_data = kml_file.read()

# Parse the KML data
root = ET.fromstring(kml_data)

# Function to extract attributes recursively
def extract_attributes(element):
    attributes = {}
    for key, value in element.attrib.items():
        attributes[key] = value

    for child in element:
        child_attributes = extract_attributes(child)
        for key, value in child_attributes.items():
            if key not in attributes:
                attributes[key] = value
            else:
                if not isinstance(attributes[key], list):
                    attributes[key] = [attributes[key]]
                attributes[key].append(value)
    
    return attributes

# Extract attributes from root element
all_attributes = extract_attributes(root)

# Write attributes to a CSV file
with open('extracted_attributes.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Write header row
    csv_writer.writerow(['Attribute', 'Value'])
    
    # Write attribute data to the CSV file
    for key, value in all_attributes.items():
        if isinstance(value, list):
            for item in value:
                csv_writer.writerow([key, item])
        else:
            csv_writer.writerow([key, value])

