import os
import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from datetime import date
from enum import Enum
from .make_invoice import process_pdf_and_return_invoice

# Define the directories
UPLOAD_DIR = "app/invoice/uploaded_files"
DOWNLOAD_DIR = "app/invoice/saved_invoices"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_unique_filename(directory, base_name):
    """
    Generate a unique filename in the specified directory.
    """
    counter = 1
    while True:
        file_name = f"{base_name}({counter}).csv"
        file_path = os.path.join(directory, file_name)
        if not os.path.exists(file_path):
            return file_path
        counter += 1

# Create a new router
router = APIRouter()

# Enum classes for dropdown options
class ShingleColor(str, Enum):
    Charcoal = "Charcoal"
    WeatherWood = "Weather Wood"
    Barkwood = "Barkwood"
    Driftwood = "Driftwood"
    PewterGray = "Pewter Gray"
    Hickory = "Hickory"
    Shakewood = "Shakewood"

class StructureType(str, Enum):
    Normal = "Normal"
    Medium = "Medium"
    Complex = "Complex"

class Supplier(str, Enum):
    beacon_supplies = "Beacon Supplies"
    xyz_materials = "XYZ Materials"
    roof_master = "Roof Master"

@router.post("/get-invoice/")
async def get_invoice(
    file: UploadFile = File(...),
    number_of_vents: int = Form(...),
    number_of_pipe_boots: int = Form(...),
    shingle_color: ShingleColor = Form(...),  # Use Enum for dropdown
    type_of_structure: StructureType = Form(...),  # Use Enum for dropdown
    supplier: Supplier = Form(...),  # Use Enum for dropdown
    material_delivery_date: date = Form(...),  # Use date type for calendar input
    installation_date: date = Form(...),  # Use date type for calendar input
    homeowner_email: str = Form(...),
    drip_edge: bool = Form(...)
):
    """
    Endpoint to process the uploaded file, generate invoices, and return a downloadable CSV.
    """
    try:
        logging.info(f"Received PDF report file: {file.filename}")
        
        # Save the uploaded file
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        logging.info(f"File saved at: {save_path}")
        
        # Process and generate invoices
        invoice_df = process_pdf_and_return_invoice(
            pdf_path=save_path,
            number_of_vents=number_of_vents,
            number_of_pipe_boots=number_of_pipe_boots,
            shingle_color=shingle_color.value,  # Get value from Enum
            type_of_structure=type_of_structure.value,  # Get value from Enum
            supplier=supplier.value,  # Get value from Enum
            material_delivery_date=str(material_delivery_date),  # Convert date to string
            installation_date=str(installation_date),  # Convert date to string
            homeowner_email=homeowner_email,
            drip_edge=drip_edge,
        )
        
        logging.info(f"Successfully processed file: {save_path}")
        
        # Save the DataFrame to a uniquely named CSV file
        csv_file_path = get_unique_filename(DOWNLOAD_DIR, "invoice")
        invoice_df.to_csv(csv_file_path, index=False)
        logging.info(f"CSV file saved at: {csv_file_path}")
        
        # Delete the uploaded file after processing
        os.remove(save_path)
        logging.info(f"Uploaded file deleted: {save_path}")
        
        return FileResponse(
            path=csv_file_path,
            media_type="text/csv",
            filename=os.path.basename(csv_file_path)
        )
    
    except Exception as e:
        logging.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process the file: {str(e)}"
        )
