import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from invoice.invoice_functions import get_formulas_by_category, get_wastage_factors, calculate_product_quantities, generate_invoice_json
from ..formula.crud import get_categories_with_variation_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the database session
db: Session = SessionLocal()

def process_json_and_return_invoice_json(data, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge):
    """
    Process the input JSON data and generate the invoice JSON.

    Args:
        data (dict): Roof measurement data.
        number_of_vents (int): Number of vents to include in the calculation.
        number_of_pipe_boots (int): Number of pipe boots to include in the calculation.
        shingle_color (str): The color of the shingles.
        type_of_structure (str): Type of structure (e.g., "Normal", "Complex").
        supplier (str): Supplier ID or name.
        material_delivery_date (str): Expected material delivery date.
        installation_date (str): Planned installation date.
        homeowner_email (str): Homeowner's email address.
        drip_edge (bool): Whether a drip edge is included.

    Returns:
        dict: Invoice data in JSON format.
    """
    logger.info("Fetching formulas by category from the database.")
    formulas_by_category = get_formulas_by_category(db)

    logger.info("Calculating wastage factors based on valleys and hips length.")
    valleys_length = data["ValleysLength_ft"]
    hips_length = data["HipsLength_ft"]
    wastage_factors = get_wastage_factors(db, valleys_length, hips_length)
    logger.info(f"Wastage factors calculated: {wastage_factors}")

    logger.info("Calculating product quantities based on formulas and input data.")
    quantities = calculate_product_quantities(formulas_by_category, data, number_of_vents, number_of_pipe_boots, wastage_factors)
    logger.info(f"Product quantities calculated: {quantities}")

    logger.info("Fetching category variations from the database.")
    categories_with_colour, categories_with_no_variation = get_categories_with_variation_type(db)
    logger.info(f"Categories with color variation: {categories_with_colour}, without variation: {categories_with_no_variation}")

    logger.info("Generating the invoice JSON.")
    products_json = generate_invoice_json(
        quantities,
        type_of_structure,
        supplier,
        material_delivery_date,
        installation_date,
        homeowner_email,
        drip_edge,
        categories_with_colour,
        categories_with_no_variation,
        shingle_color,
        db
    )
    logger.info("Invoice JSON generation complete.")
    return products_json

def process_measurement_data_and_calculate_product_quantities(data, number_of_vents, number_of_pipe_boots):
    """
    Process roof measurement data and calculate product quantities.

    Args:
        data (dict): Roof measurement data.
        number_of_vents (int): Number of vents to include.
        number_of_pipe_boots (int): Number of pipe boots to include.

    Returns:
        dict: Calculated product quantities.
    """
    logger.info("Fetching formulas by category from the database.")
    formulas_by_category = get_formulas_by_category(db)

    logger.info("Calculating wastage factors based on valleys and hips length.")
    valleys_length = data["ValleysLength_ft"]
    hips_length = data["HipsLength_ft"]
    wastage_factors = get_wastage_factors(db, valleys_length, hips_length)
    logger.info(f"Wastage factors calculated: {wastage_factors}")

    logger.info("Calculating product quantities.")
    quantities = calculate_product_quantities(formulas_by_category, data, number_of_vents, number_of_pipe_boots, wastage_factors)
    logger.info(f"Product quantities calculated: {quantities}")

    return quantities

def process_quantities_and_return_invoice(quantities, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge):
    """
    Process calculated quantities and generate the invoice JSON.

    Args:
        quantities (dict): Calculated product quantities.
        shingle_color (str): Color of the shingles.
        type_of_structure (str): Type of structure (e.g., "Normal", "Complex").
        supplier (str): Supplier ID or name.
        material_delivery_date (str): Expected material delivery date.
        installation_date (str): Planned installation date.
        homeowner_email (str): Homeowner's email address.
        drip_edge (bool): Whether a drip edge is included.

    Returns:
        dict: Invoice data in JSON format.
    """
    logger.info("Fetching category variations from the database.")
    categories_with_colour, categories_with_no_variation = get_categories_with_variation_type(db)
    logger.info(f"Categories with color variation: {categories_with_colour}, without variation: {categories_with_no_variation}")

    logger.info("Generating the invoice JSON.")
    invoice_json = generate_invoice_json(
        quantities=quantities,
        type_of_structure=type_of_structure,
        supplier_id=supplier,
        material_delivery_date=material_delivery_date,
        installation_date=installation_date,
        homeowner_email=homeowner_email,
        drip_edge=drip_edge,
        categories_with_colour=categories_with_colour,
        categories_with_no_variation=categories_with_no_variation,
        colour=shingle_color,
        db=db
    )
    logger.info("Invoice JSON generation complete.")
    return invoice_json
