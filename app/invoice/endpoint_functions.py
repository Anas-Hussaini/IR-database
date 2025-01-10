import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from invoice.invoice_functions import get_formulas_by_category, get_wastage_factors, calculate_product_quantities, generate_invoice_df

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database session
db: Session = SessionLocal()

# List of product categories
categories = [
    "Shingles",
    "Caps/Hip and Ridge Shingles",
    "Shingle Starters",
    "Sand Ice & Water Shield/Ice & Water Underlayments",
    "Synthetic Underlayments",
    "Roofing Nails/Coil Roofing Nails",
    "Ridge Vent System/Hip Vents",
    "Back Roof Vent/Ventilation",
    "Step Flashing/Flashings",
    "Pipe Flashing/Flashings",
    "Roofing Staples/Staples",
    "Construction Sealant/Adhesives, Caulks & Sealants",
    "Dormer Flashing Sticks/Flashings",
    "Drip Edge/Flashings"
]

def process_json_and_return_invoice_df(data, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge):
    """
    Process the input JSON data and generate the invoice DataFrame.

    Args:
    - data: Dictionary containing roof measurement data.
    - number_of_vents: Number of vents to be included.
    - number_of_pipe_boots: Number of pipe boots to be included.
    - shingle_color: Color of the shingles.
    - type_of_structure: Type of the structure (e.g., Normal, Complex).
    - supplier: ID or name of the supplier.
    - material_delivery_date: Date when materials are expected to be delivered.
    - installation_date: Date when the installation is planned.
    - homeowner_email: Email address of the homeowner.
    - drip_edge: Boolean indicating if drip edge is included.

    Returns:
    - A DataFrame representing the invoice.
    """
    logger.info("Fetching formulas by category from the database.")
    formulas_by_category = get_formulas_by_category(db)

    logger.info("Calculating wastage factors based on valleys and hips length.")
    valleys_length = data["ValleysLength_ft"]
    hips_length = data["HipsLength_ft"]
    wastage_factors = get_wastage_factors(db, valleys_length, hips_length)
    logger.debug(f"Wastage factors calculated: {wastage_factors}")

    logger.info("Calculating product quantities based on formulas and input data.")
    quantities = calculate_product_quantities(formulas_by_category, data, number_of_vents, number_of_pipe_boots, wastage_factors)
    logger.debug(f"Product quantities calculated: {quantities}")

    logger.info("Generating the invoice DataFrame.")
    products_df = generate_invoice_df(
        quantities,
        type_of_structure,
        supplier,
        material_delivery_date,
        installation_date,
        homeowner_email,
        drip_edge,
        categories,
        shingle_color,
        db
    )
    logger.info("Invoice DataFrame generation complete.")

    return products_df

def process_measurement_data_and_calculate_product_quantities(data, number_of_vents, number_of_pipe_boots):
    """
    Process the measurement data and calculate the product quantities.

    Args:
    - data: Dictionary containing roof measurement data.
    - number_of_vents: Number of vents to be included.
    - number_of_pipe_boots: Number of pipe boots to be included.

    Returns:
    - A dictionary of product quantities.
    """
    logger.info("Fetching formulas by category from the database.")
    formulas_by_category = get_formulas_by_category(db)

    logger.info("Calculating wastage factors based on valleys and hips length.")
    valleys_length = data["ValleysLength_ft"]
    hips_length = data["HipsLength_ft"]
    wastage_factors = get_wastage_factors(db, valleys_length, hips_length)
    logger.debug(f"Wastage factors calculated: {wastage_factors}")

    logger.info("Calculating product quantities.")
    quantities = calculate_product_quantities(formulas_by_category, data, number_of_vents, number_of_pipe_boots, wastage_factors)
    logger.debug(f"Product quantities calculated: {quantities}")

    return quantities

def process_quantities_and_return_invoice(quantities, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge):
    """
    Process the calculated quantities and generate the invoice DataFrame.

    Args:
    - quantities: Dictionary of product quantities.
    - shingle_color: Color of the shingles.
    - type_of_structure: Type of the structure (e.g., Normal, Complex).
    - supplier: ID or name of the supplier.
    - material_delivery_date: Date when materials are expected to be delivered.
    - installation_date: Date when the installation is planned.
    - homeowner_email: Email address of the homeowner.
    - drip_edge: Boolean indicating if drip edge is included.

    Returns:
    - A DataFrame representing the invoice.
    """
    logger.info("Generating the invoice DataFrame.")
    invoice_df = generate_invoice_df(
        quantities,
        type_of_structure,
        supplier,
        material_delivery_date,
        installation_date,
        homeowner_email,
        drip_edge,
        categories,
        shingle_color,
        db
    )
    logger.info("Invoice DataFrame generation complete.")

    return invoice_df

# Example Usage:
# type_of_structure = "Normal"
# supplier_id = "BEACON"
# material_delivery_date = "string"
# installation_date = "string"
# homeowner_email = "string"
# drip_edge = True

# colour = "Default"

# Assuming `SessionLocal` is your database session factory

# # Retrieve formulas and wastage factors from the database
# logger.info("Retrieving formulas and wastage factors from the database.")
# formulas_by_category = get_formulas_by_category(db)
# valleys_length = 35
# hips_length = 5
# wastage_factors = get_wastage_factors(db, valleys_length, hips_length)

# data = {
#     "Address": "Complete address of the property",
#     "TotalRoofArea_sqft": 2200,
#     "RidgesHipsLength_ft": 46,
#     "ValleysLength_ft": 22,
#     "RidgesLength_ft": 32,
#     "HipsLength_ft": 14,
#     "RakesLength_ft": 15,
#     "EavesLength_ft": 16,
#     "EavesRakesLength_ft": 31,
#     "StepFlashingLength_ft": 9,
#     "WallFlashingLength_ft": 10
# }

# number_of_vents = 2
# number_of_pipe_boots = 3
# Calculate product quantities
# quantities = calculate_product_quantities(formulas_by_category, data, number_of_vents, number_of_pipe_boots, wastage_factors)

# # Generate the invoice DataFrame
# products_df = generate_invoice_df(
#     quantities,
#     type_of_structure,
#     supplier_id,
#     material_delivery_date,
#     installation_date,
#     homeowner_email,
#     drip_edge,
#     categories,
#     colour,
#     db
# )

# # Print the DataFrame and save it as CSV
# logger.info("Printing and saving the invoice DataFrame as CSV.")
# print(products_df)
# products_df.to_csv("test_invoice.csv")
