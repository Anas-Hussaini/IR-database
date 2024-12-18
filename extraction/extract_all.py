import os
import json
from extract import process_pdf

# Specify the directory
directory_path = 'raw_data/all_pdf_measurement_reports'
# DOWNLOAD_DIR = "extraction/extraction_json"
DOWNLOAD_DIR = "extraction/truth_json"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# List all files in the directory
filenames = os.listdir(directory_path)
# len(filenames)
i=0

for filename in filenames:
    
    i+=1
    print(f"Extracting file {i}/{len(filenames)} : {filename}")
    
    json_extraction = process_pdf(f"{directory_path}/{filename}")
    
    file_path = f"{DOWNLOAD_DIR}/{filename.replace(".pdf",".json")}"
    
    with open(file_path, 'w') as json_file:
        json.dump(json_extraction, json_file, indent=4)  # 'indent' makes it pretty-printed
    
    print(f"Extracted file {i}/{len(filenames)} : {filename}")

