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
from .endpoint_functions import process_json_and_return_invoice_df, process_measurement_data_and_calculate_product_quantities, process_quantities_and_return_invoice

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

# Endpoint to process uploaded file, generate invoices, and return a downloadable CSV
@router.post("/get-invoice/")
async def get_invoice(
    file: UploadFile = File(...),
    number_of_vents: int = Form(...),
    number_of_pipe_boots: int = Form(...),
    shingle_color: ShingleColor = Form(...),
    type_of_structure: StructureType = Form(...),
    supplier: Supplier = Form(...),
    material_delivery_date: date = Form(...),
    installation_date: date = Form(...),
    homeowner_email: str = Form(...),
    drip_edge: bool = Form(...)
):
    """
    Process the uploaded file, generate invoices, and return a downloadable CSV.
    """
    try:
        logging.info(f"Received PDF report file: {file.filename}")
        
        # Save the uploaded file
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        logging.info(f"File saved at: {save_path}")
        
        # Normalize the shingle color (treat 'Default' as 'Charcoal')
        normalized_shingle_color = normalize_shingle_color(shingle_color)
        
        # Process and generate invoices
        invoice_df = process_pdf_and_return_invoice(
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
        
        logging.info(f"Successfully processed file: {save_path}")
        
        # Save the DataFrame to a uniquely named CSV file
        csv_file_path = get_unique_filename(DOWNLOAD_DIR, "invoice")
        invoice_df.to_csv(csv_file_path, index=False)
        logging.info(f"CSV file saved at: {csv_file_path}")
        
        # Delete the uploaded file after processing
        os.remove(save_path)
        logging.info(f"Uploaded file deleted: {save_path}")
        
        # Return the file response
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

# Endpoint to extract data from PDF reports and return the extracted data
@router.post("/extract-data-from-pdf-report/")
async def extract_data_from_pdf_report(file: UploadFile = File(...)):
    """
    Process the uploaded file, extract measurement data, and return it.
    """
    try:
        logging.info(f"Received PDF report file: {file.filename}")
        
        # Save the uploaded file
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        logging.info(f"File saved at: {save_path}")
        
        # Process and extract measurement data
        extracted_data = process_pdf(pdf_path=save_path)
        
        logging.info(f"Successfully processed file: {save_path}")
        
        # Delete the uploaded file after processing
        os.remove(save_path)
        logging.info(f"Uploaded file deleted: {save_path}")
        
        return extracted_data
    
    except Exception as e:
        logging.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process the file: {str(e)}"
        )

# Endpoint to process extracted data and generate invoices from it
@router.post("/get-invoice-with-data-only/")
async def get_invoice_with_data_only(
    Address: str = Form(...),
    TotalRoofArea_sqft: float = Form(...),
    RidgesHipsLength_ft: float = Form(...),
    ValleysLength_ft: float = Form(...),
    RidgesLength_ft: float = Form(...),
    HipsLength_ft: float = Form(...),
    RakesLength_ft: float = Form(...),
    EavesLength_ft: float = Form(...),
    EavesRakesLength_ft: float = Form(...),
    StepFlashingLength_ft: float = Form(...),
    WallFlashingLength_ft: float = Form(...),
    number_of_vents: int = Form(...),
    number_of_pipe_boots: int = Form(...),
    shingle_color: ShingleColor = Form(...),
    type_of_structure: StructureType = Form(...),
    supplier: Supplier = Form(...),
    material_delivery_date: date = Form(...),
    installation_date: date = Form(...),
    homeowner_email: str = Form(...),
    drip_edge: bool = Form(...)
):
    """
    Process extracted data, generate invoices, and return a downloadable CSV.
    """
    try:
        # Construct the data dictionary
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
        
        # Normalize the shingle color (treat 'Default' as 'Charcoal')
        normalized_shingle_color = normalize_shingle_color(shingle_color)
        
        # Process and generate invoices
        invoice_df = process_json_and_return_invoice_df(
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
        
        logging.info("Successfully processed the extracted data and generated invoice")
        
        # Save the DataFrame to a uniquely named CSV file
        csv_file_path = get_unique_filename(DOWNLOAD_DIR, "invoice")
        invoice_df.to_csv(csv_file_path, index=False)
        logging.info(f"CSV file saved at: {csv_file_path}")
        
        return FileResponse(
            path=csv_file_path,
            media_type="text/csv",
            filename=os.path.basename(csv_file_path)
        )
    
    except Exception as e:
        logging.error(f"Error processing data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process the data: {str(e)}"
        )

# Endpoint to calculate product quantities based on input data
@router.post("/calculate-product-quantities/")
async def calculate_product_quantities(
    Address: str = Form(...),
    TotalRoofArea_sqft: float = Form(...),
    RidgesHipsLength_ft: float = Form(...),
    ValleysLength_ft: float = Form(...),
    RidgesLength_ft: float = Form(...),
    HipsLength_ft: float = Form(...),
    RakesLength_ft: float = Form(...),
    EavesLength_ft: float = Form(...),
    EavesRakesLength_ft: float = Form(...),
    StepFlashingLength_ft: float = Form(...),
    WallFlashingLength_ft: float = Form(...),
    number_of_vents: int = Form(...),
    number_of_pipe_boots: int = Form(...)
):
    """
    Calculate product quantities based on input roof measurement data.
    """
    try:
        # Construct the data dictionary
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
        
        # Calculate product quantities
        quantities = process_measurement_data_and_calculate_product_quantities(
            data=data,
            number_of_vents=number_of_vents,
            number_of_pipe_boots=number_of_pipe_boots
        )
        
        logging.info(f"Calculated product quantities successfully")
        
        return quantities
    
    except Exception as e:
        logging.error(f"Error calculating product quantities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate product quantities: {str(e)}"
        )

# Endpoint to process quantities and return invoices
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
    drip_edge: bool = Form(...)
):
    """
    Process the quantities and return an invoice.
    """
    try:
        # Construct the data dictionary
        quantities = {
            "Shingle Starters": shingle_starters,
            "Sand Ice Water Shield/Ice Water Underlayments": sand_ice_water_shield,
            "Roofing Nails/Coil Roofing Nails": roofing_nails,
            "Ridge Vent System/Hip Vents": ridge_vent_system,
            "Back Roof Vent/Ventilation": back_roof_vent,
            "Step Flashing/Flashings": step_flashing,
            "Pipe Flashing/Flashings": pipe_flashing,
            "Roofing Staples/Staples": roofing_staples,
            "Construction Sealant/Adhesives Caulks Sealants": construction_sealant,
            "Dormer Flashing Sticks/Flashings": dormer_flashing_sticks,
            "Caps/Hip And Ridge Shingles": caps,
            "Drip Edge/Flashings": drip_edges,
            "Shingles": shingles,
            "Synthetic Underlayments": synthetic_underlayments
        }
        
        # Normalize the shingle color (treat 'Default' as 'Charcoal')
        normalized_shingle_color = normalize_shingle_color(shingle_color)
        
        # Process quantities and generate invoices
        invoice_df = process_quantities_and_return_invoice(
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
        
        # Save the DataFrame to a uniquely named CSV file
        csv_file_path = get_unique_filename(DOWNLOAD_DIR, "invoice")
        invoice_df.to_csv(csv_file_path, index=False)
        logging.info(f"CSV file saved at: {csv_file_path}")
        
        return FileResponse(
            path=csv_file_path,
            media_type="text/csv",
            filename=os.path.basename(csv_file_path)
        )
    
    except Exception as e:
        logging.error(f"Error processing quantities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process the quantities: {str(e)}"
        )
