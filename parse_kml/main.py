import zipfile
import os

def unzipfile(path, extract_folder_path):
    if not os.path.exists(extract_folder_path):
        os.makedirs(extract_folder_path)

    # Unzip the contents of the ZIP file
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder_path)
    zip_ref.close()

if __name__ == "__main__":
    unzipfile('kml_sample2.zip', 'extract_folder_path')