import os
import json
import logging
from pydantic import BaseModel, field_validator
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Body
from fastapi.responses import FileResponse
from datetime import date
from enum import Enum
from .make_invoice import process_pdf_and_return_invoice
from extraction.extract import process_pdf
from .endpoint_functions import process_json_and_return_invoice_json, process_measurement_data_and_calculate_product_quantities, process_quantities_and_return_invoice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the directories for file upload and download
UPLOAD_DIR = "app/invoice/uploaded_files"
DOWNLOAD_DIR = "app/invoice/saved_invoices"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to generate a unique filename in the specified directory
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
    Default = "Default"
    Charcoal = "Charcoal"
    WeatherWood = "Weather Wood"
    Barkwood = "Barkwood"
    Driftwood = "Driftwood"
    PewterGray = "Pewter Gray"
    Hickory = "Hickory"
    Shakewood = "Shakewood"

# Helper function to normalize the shingle color
def normalize_shingle_color(color: ShingleColor) -> str:
    # If the color is 'Default', treat it as 'Charcoal'
    if color == ShingleColor.Default:
        return ShingleColor.Charcoal.value
    return color.value

class StructureType(str, Enum):
    Normal = "Normal"
    Medium = "Medium"
    Complex = "Complex"

class Supplier(str, Enum):
    beacon_supplies = "BEACON BUILDING PRODUCTS"
    xyz_materials = "XYZ Materials"
    roof_master = "Roof Master"
    
# Define the data model
class RoofDataModel(BaseModel):
    Address: str
    TotalRoofArea_sqft: float
    RidgesHipsLength_ft: float
    ValleysLength_ft: float
    RidgesLength_ft: float
    HipsLength_ft: float
    RakesLength_ft: float
    EavesLength_ft: float
    EavesRakesLength_ft: float
    StepFlashingLength_ft: float
    WallFlashingLength_ft: float

# Endpoint to process an uploaded PDF file, generate invoices, and return a downloadable CSV response.
@router.post("/get-invoice/")
async def get_invoice(
    file: UploadFile = File(...),  # Uploaded PDF file containing the necessary data.
    number_of_vents: int = Form(...),  # Number of vents to include in the invoice.
    number_of_pipe_boots: int = Form(...),  # Number of pipe boots to include in the invoice.
    shingle_color: ShingleColor = Form(...),  # Selected shingle color for the roof.
    type_of_structure: StructureType = Form(...),  # Type of structure (e.g., residential, commercial).
    supplier: Supplier = Form(...),  # Supplier for the materials.
    material_delivery_date: date = Form(...),  # Delivery date for the materials.
    installation_date: date = Form(...),  # Installation date for the roof.
    homeowner_email: str = Form(...),  # Email address of the homeowner.
    drip_edge: bool = Form(...)  # Whether a drip edge is included (True/False).
):
    """
    Processes an uploaded PDF file to extract data, generates an invoice in JSON format, 
    and returns the details as a downloadable CSV file.
    """
    try:
        logging.info(f"Received PDF report file: {file.filename}")
        
        # Save the uploaded file to the server
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        logging.info(f"File saved at: {save_path}")
        
        # Normalize the shingle color (e.g., 'Default' is treated as 'Charcoal')
        normalized_shingle_color = normalize_shingle_color(shingle_color)
        
        # Process the PDF file and generate an invoice in JSON format
        invoice_json = process_pdf_and_return_invoice(
            pdf_path=save_path,
            number_of_vents=number_of_vents,
            number_of_pipe_boots=number_of_pipe_boots,
            shingle_color=normalized_shingle_color,
            type_of_structure=type_of_structure.value,
            supplier=supplier.value,
            material_delivery_date=str(material_delivery_date),
            installation_date=str(installation_date),
            homeowner_email=homeowner_email,
            drip_edge=drip_edge,
        )
        
        logging.info(f"Successfully processed the file: {save_path}")
        
        # Remove the uploaded file from the server after processing to free up space
        os.remove(save_path)
        logging.info(f"Uploaded file deleted: {save_path}")
        
        # Return the generated invoice data as a response
        return invoice_json
    
    except Exception as e:
        logging.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process the file: {str(e)}"
        )


# Endpoint to upload a PDF report, extract measurement data, and return the extracted data.
@router.post("/extract-data-from-pdf-report/")
async def extract_data_from_pdf_report(file: UploadFile = File(...)):  
    """
    Processes an uploaded PDF report, extracts measurement data from it, 
    and returns the extracted data as a JSON response.
    """
    try:
        logging.info(f"Received PDF report file: {file.filename}")
        
        # Save the uploaded file to the server's upload directory
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        logging.info(f"File saved at: {save_path}")
        
        # Extract measurement data from the saved PDF file
        extracted_data = process_pdf(pdf_path=save_path)
        logging.info(f"Successfully processed the file: {save_path}")
        
        # Remove the uploaded file from the server to free up storage space
        os.remove(save_path)
        logging.info(f"Uploaded file deleted: {save_path}")
        
        # Return the extracted data as a response
        return extracted_data
    
    except Exception as e:
        logging.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process the file: {str(e)}"
        )

# Endpoint to generate invoices from provided extracted data without requiring a PDF upload.
@router.post("/get-invoice-with-data-only/")
async def get_invoice_with_data_only(
    Address: str = Form(...),  # Address of the property for the invoice.
    TotalRoofArea_sqft: float = Form(...),  # Total roof area in square feet.
    RidgesHipsLength_ft: float = Form(...),  # Total length of ridges and hips in feet.
    ValleysLength_ft: float = Form(...),  # Total length of valleys in feet.
    RidgesLength_ft: float = Form(...),  # Total length of ridges in feet.
    HipsLength_ft: float = Form(...),  # Total length of hips in feet.
    RakesLength_ft: float = Form(...),  # Total length of rakes in feet.
    EavesLength_ft: float = Form(...),  # Total length of eaves in feet.
    EavesRakesLength_ft: float = Form(...),  # Combined length of eaves and rakes in feet.
    StepFlashingLength_ft: float = Form(...),  # Total length of step flashing in feet.
    WallFlashingLength_ft: float = Form(...),  # Total length of wall flashing in feet.
    number_of_vents: int = Form(...),  # Number of vents required.
    number_of_pipe_boots: int = Form(...),  # Number of pipe boots required.
    shingle_color: ShingleColor = Form(...),  # Selected shingle color for the roof.
    type_of_structure: StructureType = Form(...),  # Type of structure (e.g., residential, commercial).
    supplier: Supplier = Form(...),  # Supplier for the materials.
    material_delivery_date: date = Form(...),  # Delivery date for the materials.
    installation_date: date = Form(...),  # Scheduled installation date.
    homeowner_email: str = Form(...),  # Email address of the homeowner.
    drip_edge: bool = Form(...)  # Whether a drip edge is included (True/False).
):
    """
    Processes the provided extracted data, generates an invoice in JSON format, 
    and returns the details for download as a CSV file.
    """
    try:
        # Construct a dictionary to hold the roof and flashing data
        data = {
            "Address": Address,
            "TotalRoofArea_sqft": TotalRoofArea_sqft,
            "RidgesHipsLength_ft": RidgesHipsLength_ft,
            "ValleysLength_ft": ValleysLength_ft,
            "RidgesLength_ft": RidgesLength_ft,
            "HipsLength_ft": HipsLength_ft,
            "RakesLength_ft": RakesLength_ft,
            "EavesLength_ft": EavesLength_ft,
            "EavesRakesLength_ft": EavesRakesLength_ft,
            "StepFlashingLength_ft": StepFlashingLength_ft,
            "WallFlashingLength_ft": WallFlashingLength_ft
        }
        
        # Normalize the shingle color (e.g., treat 'Default' as 'Charcoal')
        normalized_shingle_color = normalize_shingle_color(shingle_color)
        
        # Generate invoice JSON using the provided data
        invoice_json = process_json_and_return_invoice_json(
            data=data, 
            number_of_vents=number_of_vents,
            number_of_pipe_boots=number_of_pipe_boots,
            shingle_color=normalized_shingle_color,
            type_of_structure=type_of_structure.value,
            supplier=supplier.value,
            material_delivery_date=str(material_delivery_date),
            installation_date=str(installation_date),
            homeowner_email=homeowner_email,
            drip_edge=drip_edge,
        )
        
        logging.info("Successfully processed the extracted data and generated the invoice.")
        
        # Return the generated invoice as a response
        return invoice_json
    
    except Exception as e:
        logging.error(f"Error processing data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process the data: {str(e)}"
        )

# Endpoint to calculate product quantities based on provided roof measurement data
@router.post("/calculate-product-quantities/")
async def calculate_product_quantities(
    Address: str = Form(...),  # Address of the property for which quantities are calculated
    TotalRoofArea_sqft: float = Form(...),  # Total roof area in square feet
    RidgesHipsLength_ft: float = Form(...),  # Combined length of ridges and hips in feet
    ValleysLength_ft: float = Form(...),  # Total length of valleys in feet
    RidgesLength_ft: float = Form(...),  # Length of ridges only, in feet
    HipsLength_ft: float = Form(...),  # Length of hips only, in feet
    RakesLength_ft: float = Form(...),  # Total length of rakes in feet
    EavesLength_ft: float = Form(...),  # Total length of eaves in feet
    EavesRakesLength_ft: float = Form(...),  # Combined length of eaves and rakes in feet
    StepFlashingLength_ft: float = Form(...),  # Total length of step flashing in feet
    WallFlashingLength_ft: float = Form(...),  # Total length of wall flashing in feet
    number_of_vents: int = Form(...),  # Number of vents required
    number_of_pipe_boots: int = Form(...),  # Number of pipe boots required
    drip_edge: bool = Form(...)
):
    """
    Calculate the quantities of roofing materials and accessories required based on the roof measurement data.
    """
    try:
        # Construct a dictionary with roof measurement data
        data = {
            "Address": Address,
            "TotalRoofArea_sqft": TotalRoofArea_sqft,
            "RidgesHipsLength_ft": RidgesHipsLength_ft,
            "ValleysLength_ft": ValleysLength_ft,
            "RidgesLength_ft": RidgesLength_ft,
            "HipsLength_ft": HipsLength_ft,
            "RakesLength_ft": RakesLength_ft,
            "EavesLength_ft": EavesLength_ft,
            "EavesRakesLength_ft": EavesRakesLength_ft,
            "StepFlashingLength_ft": StepFlashingLength_ft,
            "WallFlashingLength_ft": WallFlashingLength_ft
        }
        
        # Calculate quantities using the measurement data and additional parameters
        quantities = process_measurement_data_and_calculate_product_quantities(
            data=data,
            number_of_vents=number_of_vents,
            number_of_pipe_boots=number_of_pipe_boots,
            drip_edge=drip_edge
        )
        
        logging.info(f"Successfully calculated product quantities for address: {Address}")
        
        # Return the calculated quantities as a JSON response
        return quantities
    
    except Exception as e:
        # Log the error for debugging purposes
        logging.error(f"Error calculating product quantities: {str(e)}")
        
        # Raise an HTTP exception with a 500 status code and detailed error message
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate product quantities: {str(e)}"
        )

# Endpoint to process quantities and generate an invoice
@router.post("/process-quantities-and-generate-invoice/")
async def process_quantities_and_generate_invoice(
    shingle_starters: int = Form(...),
    sand_ice_water_shield: int = Form(...),
    roofing_nails: int = Form(...),
    ridge_vent_system: int = Form(...),
    back_roof_vent: int = Form(...),
    step_flashing: int = Form(...),
    pipe_flashing: int = Form(...),
    roofing_staples: int = Form(...),
    construction_sealant: int = Form(...),
    dormer_flashing_sticks: int = Form(...),
    caps: int = Form(...),
    drip_edges: int = Form(...),
    shingles: int = Form(...),
    synthetic_underlayments: int = Form(...),
    shingle_color: ShingleColor = Form(...),
    type_of_structure: StructureType = Form(...),
    supplier: Supplier = Form(...),
    material_delivery_date: date = Form(...),
    installation_date: date = Form(...),
    homeowner_email: str = Form(...),
    drip_edge: bool = Form(...),
):
    """
    Process the quantities provided by the user and generate an invoice.
    """
    try:
        # Create a dictionary to store the quantities of various materials
        quantities = {
            "Shingle Starters": shingle_starters,
            "Sand Ice & Water Shield": sand_ice_water_shield,
            "Coil Roofing Nails": roofing_nails,
            "Ridge Vent System": ridge_vent_system,
            "Back Roof Vent": back_roof_vent,
            "Step Flashing": step_flashing,
            "Pipe Flashing": pipe_flashing,
            "Roofing Staples": roofing_staples,
            "Construction Sealant": construction_sealant,
            "Dormer Flashing Sticks": dormer_flashing_sticks,
            "Caps": caps,
            "Drip Edge": drip_edges,
            "Shingles": shingles,
            "Synthetic Underlayments": synthetic_underlayments
        }
        
        # Normalize the shingle color (default to 'Charcoal' if the value is 'Default')
        normalized_shingle_color = normalize_shingle_color(shingle_color)
        
        # Process the quantities and generate the invoice based on the provided details
        invoice_json = process_quantities_and_return_invoice(
            quantities=quantities,
            shingle_color=normalized_shingle_color,
            type_of_structure=type_of_structure.value,
            supplier=supplier.value,
            material_delivery_date=str(material_delivery_date),
            installation_date=str(installation_date),
            homeowner_email=homeowner_email,
            drip_edge=drip_edge,
        )
        
        logging.info("Successfully processed quantities and generated invoice")
        
        # Return the generated invoice
        return invoice_json
    
    except Exception as e:
        logging.error(f"Error processing quantities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process the quantities: {str(e)}"
        )

