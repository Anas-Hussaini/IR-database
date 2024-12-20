import os
import json
from .invoice_functions import process_json_and_return_invoice_df
from .config_invoice import EXTRACTION_DIR

number_of_vents=2
number_of_pipe_boots=2
shingle_color="Charcoal"
type_of_structure="Normal"
supplier="Beacon"
material_delivery_date="9/12/2024"
installation_date="19/12/2024"
homeowner_email="homeowner@gmail.com"
drip_edge=False

# Specify the directory
PDF_DIR = 'raw_data/all_pdf_measurement_reports'
# JSON_DIR = "extraction/truth_json"
DOWNLOAD_INVOICE_DIR = "invoice/invoices"

os.makedirs(DOWNLOAD_INVOICE_DIR, exist_ok=True)

# List all files in the directory
filenames = os.listdir(PDF_DIR)
# len(filenames)
i=0

for filename in filenames:
    
    i+=1
    print(f"Processing json file {i}/{len(filenames)} of pdf_file: {filename}")
    
    pdf_path = f"{PDF_DIR}/{filename}"
    
    file_path = f"{EXTRACTION_DIR}/{os.path.basename(pdf_path).replace(".pdf", ".json")}"

    with open(file_path, 'r') as file:
        data = json.load(file)
    
    invoice_df = process_json_and_return_invoice_df(data, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge)
    
    print(invoice_df)
    
    # Save invoice to directory
    invoice_df.to_csv(f'{DOWNLOAD_INVOICE_DIR}/{filename.replace('.pdf','')}_invoice.csv',index=False)
    
    print(f"Saved invoice {i}/{len(filenames)} of pdf_file: {filename}")


