from typing import Dict
from sqlalchemy.orm import Session
from app.formula.crud import get_formulas
from app.product.crud import get_product_by_category_supplier_colour, get_product_by_category_supplier
from app.models import WastageCondition
import math
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to retrieve formulas from the database and organize them by category
def get_formulas_by_category(db: Session, skip: int = 0, limit: int = 1000) -> Dict[str, list]:
    """
    Retrieves formulas from the database and organizes them into a dictionary grouped by category.

    :param db: SQLAlchemy database session.
    :param skip: Number of records to skip.
    :param limit: Maximum number of records to retrieve.
    :return: Dictionary where keys are categories, and values are lists of equations.
    """
    logger.info("Fetching formulas from the database with skip=%d, limit=%d", skip, limit)
    formulas = get_formulas(db, skip=skip, limit=limit)
    
    formulas_dict = {}
    for formula in formulas:
        if formula.category not in formulas_dict:
            formulas_dict[formula.category] = []
        formulas_dict[formula.category].append(formula.equation)
    
    logger.info("Organized formulas into %d categories", len(formulas_dict))
    return formulas_dict

# Function to retrieve product details by category, supplier, and color
def get_product_by_category_supplier_and_colour(db: Session, category: str, supplier_id: str, colour: str) -> Dict[str, list]:
    """
    Retrieves product from the database and organizes them into a dictionary grouped by category, colour, and supplier.

    :param db: SQLAlchemy database session.
    :param category: The product category.
    :param supplier_id: The supplier's ID.
    :param colour: The product's color.
    :return: Dictionary containing product details.
    """
    logger.info("Fetching product details for category=%s, supplier_id=%s, colour=%s", category, supplier_id, colour)
    product = get_product_by_category_supplier_colour(db, category=category, supplier_id=supplier_id, colour=colour)
    
    logger.info("Retrieved product details: %s", product.product_id)
    return {
        "product_id": product.product_id,
        "description": product.description,
        "unit_price": product.unit_price,
        "unit": product.unit,
        "supplier": product.supplier,
        "colour": product.colour
    }

def get_product_by_category_and_supplier(db: Session, category: str, supplier_id: str) -> Dict[str, list]:
    """
    Retrieves product from the database and organizes them into a dictionary grouped by category and supplier.

    :param db: SQLAlchemy database session.
    :param category: The product category.
    :param supplier_id: The supplier's ID.
    :return: Dictionary containing product details.
    """
    logger.info("Fetching product details for category=%s, supplier_id=%s", category, supplier_id)
    
    # Fetch product details using the updated function
    product = get_product_by_category_supplier(db, category=category, supplier_id=supplier_id)

    logger.info("Retrieved product details: %s", product.product_id)
    
    return {
        "product_id": product.product_id,
        "description": product.description,
        "unit_price": product.unit_price,
        "unit": product.unit,
        "supplier": product.supplier,
        "colour": product.colour
    }


# Function to calculate wastage factors based on valleys and hips lengths
def get_wastage_factors(db: Session, valleys_length: float, hips_length: float) -> Dict[str, float]:
    """
    Calculates the wastage factors for different categories based on valleys and hips lengths.

    :param db: SQLAlchemy database session.
    :param valleys_length: Length of valleys.
    :param hips_length: Length of hips.
    :return: Dictionary containing wastage factors for each category.
    """
    logger.info("Calculating wastage factors for valleys_length=%.2f, hips_length=%.2f", valleys_length, hips_length)
    total_length = valleys_length + hips_length
    local_vars = {
        "ValleysLength_ft": valleys_length,
        "HipsLength_ft": hips_length,
        "Total_Valleys_Hips_Length_ft": total_length
    }

    results = {}
    categories = db.query(WastageCondition.category).distinct()

    for category in categories:
        category = category[0]  # Extract category name
        conditions = db.query(WastageCondition).filter_by(category=category).all()
        
        for entry in conditions:
            if eval(entry.wastage_condition, {}, local_vars):
                results[category] = entry.wastage_factor
                break  # Stop checking once a condition is met
        else:
            results[category] = 1.0  # Default value if no condition matches

    logger.info("Calculated wastage factors: %s", results)
    return results

# Function to fetch one product for each category using the provided fetching function
def fetch_all_products(db: Session, categories_with_colour: list, categories_with_no_variation: list, supplier: str, colour: str):
    """
    Fetch one product for each category using the provided fetching function.
    
    :param db: SQLAlchemy database session.
    :param categories: List of categories to fetch products for.
    :param supplier: Supplier ID.
    :param color: Product color.
    :return: List of dictionaries containing product details.
    """
    logger.info("Fetching products for categories=%s, supplier=%s, colour=%s", categories_with_colour + categories_with_no_variation, supplier, colour)
    products = []
    for category in categories_with_colour:
        product = get_product_by_category_supplier_and_colour(
            db=db, category=category, supplier_id=supplier, colour=colour
        )
        products.append({
            "Product_ID": product["product_id"],
            "Description": product["description"],
            "Colour": product["colour"],
            "Category": category,
            "Supplier": product["supplier"],
            "Unit": product["unit"],
            "Unit_Price": product["unit_price"],
        })
    for category in categories_with_no_variation:
        product = get_product_by_category_and_supplier(
            db=db, category=category, supplier_id=supplier
        )
        products.append({
            "Product_ID": product["product_id"],
            "Description": product["description"],
            "Colour": product["colour"],
            "Category": category,
            "Supplier": product["supplier"],
            "Unit": product["unit"],
            "Unit_Price": product["unit_price"],
        })
    logger.info("Fetched %d products", len(products))
    return products

# Function to calculate product quantities based on formulas, data, and wastage factors
def calculate_product_quantities(formulas_by_category, data, number_of_vents: int, number_of_pipe_boots: int, wastage_factors: Dict[str, float]) -> Dict[str, int]:
    """
    Calculate the quantities for each product based on the input data.

    :param formulas_by_category: Dictionary containing formulas grouped by category.
    :param data: Input data containing roof dimensions and other details.
    :param number_of_vents: Number of vents required.
    :param number_of_pipe_boots: Number of pipe boots required.
    :param wastage_factors: Dictionary containing wastage factors for each category.
    :return: Dictionary containing calculated quantities for each product category.
    """
    logger.info("Calculating product quantities based on formulas and input data")
    quantities = {}

    # Merge all variables for eval
    variables = {
        "Number_of_Vents": number_of_vents,
        "Number_of_Pipe_Boots": number_of_pipe_boots,
        "shingles_wastage_factor": wastage_factors.get("Shingles", 1),
        "caps_wastage_factor": wastage_factors.get("Caps", 1)
    }
    variables.update(data)  # Add data keys

    # Evaluate each formula
    for category, formulas in formulas_by_category.items():
        category_results = []
        for formula in formulas:
            try:
                result = math.ceil(eval(formula, {}, variables))
                category_results.append(result)
            except Exception as e:
                logger.error("Error evaluating formula: %s", formula)
                category_results.append(f"Error: {str(e)}")
        quantities[category] = category_results[0] if category_results else None
    logger.info("Calculated product quantities: %s", quantities)
    return quantities

# Function to generate the invoice DataFrame by fetching one product per category and including other details
def generate_invoice_df(quantities: Dict[str, int], type_of_structure: str, supplier_id: str, material_delivery_date: str, installation_date: str, homeowner_email: str, drip_edge: bool, categories_with_colour: list, categories_with_no_variation: list, colour: str, db: Session) -> pd.DataFrame:
    """
    Generate the invoice DataFrame by fetching one product per category and including other details.

    :param quantities: Dictionary containing quantities calculated for each product category.
    :param type_of_structure: Type of the structure (e.g., Normal, Complex).
    :param supplier_id: Supplier ID.
    :param material_delivery_date: Date of material delivery.
    :param installation_date: Date of installation.
    :param homeowner_email: Email of the homeowner.
    :param drip_edge: Boolean indicating if drip edge is required.
    :param categories: List of product categories.
    :param colour: Product color.
    :param db: SQLAlchemy database session.
    :return: DataFrame containing product details along with calculated quantities and total prices.
    """
    logger.info("Generating invoice DataFrame")
    # Fetch products for all categories
    products = fetch_all_products(db, categories_with_colour, categories_with_no_variation, supplier_id, colour)
    
    logger.info("Fetched products= %s", products)
    
    # Check if fetched products exist, otherwise raise an error
    if not products:
        raise ValueError("No products fetched for the given categories, supplier, and color.")
    
    # Convert the fetched product data into a DataFrame
    products_df = pd.DataFrame(products)
    
    # If fetched products dataframe is empty, return an empty DataFrame
    if products_df.empty:
        logger.warning("No products fetched, returning an empty DataFrame")
        return pd.DataFrame()
    
    # Ensure the quantities provided match the number of fetched product categories
    if len(quantities) != len(products_df):
        raise ValueError("The number of quantities does not match the number of fetched products.")
    
    # Add quantities and calculate total prices
    logger.info("Calculating quantities and total prices")
    
    products_df['Quantity'] = products_df.apply(lambda x: quantities.get(x['Category'], 0), axis=1)
    logger.info("Calculated quantities:", products_df['Quantity'])

    products_df['Total Price'] = products_df['Quantity'] * products_df['Unit_Price']
    logger.info("Calculated total price:", products_df['Quantity'])

    # Calculate the total invoice amount
    total_invoice_amount = products_df['Total Price'].sum()
    logger.info("Calculated total invoice amount: %.2f", total_invoice_amount)
    
    # Add additional fields as separate rows
    additional_fields = {
        "Type of Structure": type_of_structure,
        "Supplier": supplier_id,
        "Material Delivery Date": material_delivery_date,
        "Installation Date": installation_date,
        "Homeowner Email": homeowner_email,
        "Drip Edge": drip_edge,
        "Total Invoice Amount": total_invoice_amount,
    }
    
    for key, value in additional_fields.items():
        products_df.loc[len(products_df)] = ['', '', '', '', '', '', '', key, value]
        
    logger.info("Generated invoice DataFrame with %d rows", len(products_df))
    return products_df


# # Example Usage:
# type_of_structure = "Normal"
# supplier_id = "BEACON"
# material_delivery_date = "string"
# installation_date = "string"
# homeowner_email = "string"
# drip_edge = True
# categories = [
#     "Shingles",
#     "Caps/Hip and Ridge Shingles",
#     "Shingle Starters",
#     "Sand Ice & Water Shield/Ice & Water Underlayments",
#     "Synthetic Underlayments",
#     "Roofing Nails/Coil Roofing Nails",
#     "Ridge Vent System/Hip Vents",
#     "Back Roof Vent/Ventilation",
#     "Step Flashing/Flashings",
#     "Pipe Flashing/Flashings",
#     "Roofing Staples/Staples",
#     "Construction Sealant/Adhesives, Caulks & Sealants",
#     "Dormer Flashing Sticks/Flashings",
#     "Drip Edge/Flashings"
# ]
# colour = "Default"

# from app.database import SessionLocal

# # Assuming `SessionLocal` is your database session factory
# db: Session = SessionLocal()

# # Retrieve formulas and wastage factors from the database
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
# # Calculate product quantities
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
# print(products_df)
# products_df.to_csv("test_invoice.csv")
