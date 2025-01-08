from sqlalchemy.orm import Session
from app.database import SessionLocal
from invoice.invoice_functions import get_formulas_by_category, get_wastage_factors, calculate_product_quantities, generate_invoice_df

db: Session = SessionLocal()

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
    
    formulas_by_category = get_formulas_by_category(db)
    valleys_length = data["ValleysLength_ft"]
    hips_length = data["HipsLength_ft"]
    wastage_factors = get_wastage_factors(db, valleys_length, hips_length)
    print(wastage_factors)
    quantities = calculate_product_quantities(formulas_by_category, data, number_of_vents, number_of_pipe_boots, wastage_factors)
    
    supplier_id=supplier
    colour=shingle_color
    
    # Generate the invoice DataFrame
    products_df = generate_invoice_df(
        quantities,
        type_of_structure,
        supplier_id,
        material_delivery_date,
        installation_date,
        homeowner_email,
        drip_edge,
        categories,
        colour,
        db
    )

    return products_df

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
# print(products_df)
# products_df.to_csv("test_invoice.csv")
