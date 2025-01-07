# # import pandas as pd
# # import math
# # from .config_invoice import products, shingle_ids, cap_ids, product_quantity_formulas, rates

# # def process_json_and_return_invoice_df(data, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge):
# #     """
# #     Process the roof data JSON object, calculate quantities, total prices, and return the invoice DataFrame.
# #     """   

# #     shingle_id = shingle_ids[shingle_color]
# #     cap_id = cap_ids[shingle_color]

# #     # Product IDs
# #     product_ids = [
# #         shingle_id, cap_id, "TRIOSSPL", "TRISHIWPSA1SQ", "TRISRU42286", 
# #         "TRINLSCR114", "TRIPRO4SWN", "TRISBRVAL50BL", "TRISFK338TBB", 
# #         "TRIA1143RPFBL", "DUO516STP", "TRITB374103", "TRIXFL9B7TB"
# #     ]

# #     # Calculate shingles_percentage_wastage
# #     valleys_length = data["ValleysLength_ft"]
# #     hips_length = data["HipsLength_ft"]
    
# #     total_valleys_hips_length = valleys_length + hips_length

# #     if valleys_length > 0 and hips_length == 0:
# #         shingles_percentage_wastage = 1.12 if valleys_length < 40 else 1.15
# #     elif valleys_length > 0 and hips_length > 0:
# #         shingles_percentage_wastage = 1.16 if total_valleys_hips_length <= 40 else 1.2
# #     elif valleys_length == 0 and hips_length > 0:
# #         shingles_percentage_wastage = 1.2
# #     else:
# #         shingles_percentage_wastage = 1.0

# #     # Calculate caps_percentage_wastage
# #     if hips_length > 0:
# #         caps_percentage_wastage = 1.2
# #     else:
# #         caps_percentage_wastage = 1.15

# #     product_quantity_formulas = [
# #     "(shingles_percentage_wastage*TotalRoofArea_sqft/100)*3",  # Shingles
# #     "(caps_percentage_wastage*RidgesHipsLength_ft)/25",  # Caps
# #     "(EavesRakesLength_ft)/100",  # Shingle Starters
# #     "(EavesLength_ft+ValleysLength_ft)/33",  # Sand Ice & Water Shield
# #     "(shingles_percentage_wastage*TotalRoofArea_sqft/100)/10",  # Synthetic Underlayments
# #     "(TotalRoofArea_sqft/100)/18",  # Roofing Nails
# #     "(RidgesLength_ft)/4",  # Ridge Vent System
# #     "Number_of_Vents",  # Back Roof Vent
# #     "(StepFlashingLength_ft)/60",  # Step Flashing
# #     "Number_of_Pipe_Boots",  # Pipe Flashing
# #     "(TotalRoofArea_sqft/100)/8",  # Roofing Staples
# #     "((TotalRoofArea_sqft/100)/8)+1",  # Construction Sealant
# #     "(WallFlashingLength_ft)/10"  # Dormer Flashing Sticks
# #     ]

# #     product_quantity_calculations = [
# #         f"({shingles_percentage_wastage}*{data['TotalRoofArea_sqft']}/100)*3",  # Shingles
# #         f"({caps_percentage_wastage}*{data['RidgesHipsLength_ft']})/25",  # Caps
# #         f"({data['EavesRakesLength_ft']})/100",  # Shingle Starters
# #         f"({data['EavesLength_ft']}+{data['ValleysLength_ft']})/33",  # Sand Ice & Water Shield
# #         f"({shingles_percentage_wastage}*{data['TotalRoofArea_sqft']}/100)/10",  # Synthetic Underlayments
# #         f"({data['TotalRoofArea_sqft']}/100)/18",  # Roofing Nails
# #         f"({data['RidgesLength_ft']})/4",  # Ridge Vent System
# #         f"{number_of_vents}",  # Back Roof Vent
# #         f"({data['StepFlashingLength_ft']})/60",  # Step Flashing
# #         f"{number_of_pipe_boots}",  # Pipe Flashing
# #         f"({data['TotalRoofArea_sqft']}/100)/8",  # Roofing Staples
# #         f"(({data['TotalRoofArea_sqft']}/100)/8)+1",  # Construction Sealant
# #         f"({data['WallFlashingLength_ft']})/10"  # Dormer Flashing Sticks
# #     ]

# #     # Calculate quantities
# #     quantities = [
# #         # math.ceil(eval(formula, {"Number_of_Vents": number_of_vents, "Number_of_Pipe_Boots": number_of_pipe_boots}, data["PropertyDetailsAndRoofMeasurements"])) 
# #         math.ceil(eval(formula, {"Number_of_Vents": number_of_vents, "Number_of_Pipe_Boots": number_of_pipe_boots,"shingles_percentage_wastage": shingles_percentage_wastage , "caps_percentage_wastage": caps_percentage_wastage}, data)) 
# #         if "Number_of_Vents" not in formula and "Number_of_Pipe_Boots" not in formula 
# #         else number_of_vents if "Number_of_Vents" in formula else number_of_pipe_boots 
# #         for formula in product_quantity_formulas
# #     ]
    
# #     # Calculate total prices
# #     total_price = [quantity * rate for quantity, rate in zip(quantities, rates)]

# #     # Create invoice DataFrame
# #     invoice_data = {
# #         'Product': products,
# #         'Product ID': product_ids,
# #         'Formula': product_quantity_formulas,
# #         'Calculation': product_quantity_calculations,
# #         'Quantity': quantities,
# #         'Rate': rates,
# #         'Total Price': total_price
# #     }
# #     invoice_df = pd.DataFrame(invoice_data)

# #     # Calculate the total invoice amount
# #     total_invoice_amount = sum(total_price)
    
# #     # Add additional fields to the invoice
# #     additional_fields = {
# #         "total_invoice_amount"
# #         "Type of Structure": type_of_structure,
# #         "Supplier": supplier,
# #         "Material Delivery Date": material_delivery_date,
# #         "Installation Date": installation_date,
# #         "Homeowner Email": homeowner_email,
# #         "Drip Edge": drip_edge
# #     }
# #     for key, value in additional_fields.items():
# #         invoice_df.loc[len(invoice_df)] = ['', '', '', '', '', key, value]

    
# #     invoice_df.loc[len(invoice_df)] = ['', '', '', '', '', 'Total Invoice', total_invoice_amount]
    
    
# #     return invoice_df


# ###############################################################
# ###############################################################
# ###############################################################

# import pandas as pd
# import math
# # from .config_invoice import products, shingle_ids, cap_ids, product_quantity_formulas, rates
# # from app.invoice.crud_read_only import fetch_all_categories, fetch_formula


# # categories = fetch_all_categories()
# # print(categories)

# # formulas=[]
# # for category in categories:
# #     formulas.append(fetch_formula(category=category).equation)

# # print(formulas)

# def calculate_product_quantities(data, number_of_vents, number_of_pipe_boots):
#     """
#     Calculate the quantities for each product based on the input data.
#     """

#     # # Calculate shingles_percentage_wastage
#     # valleys_length = data["ValleysLength_ft"]
#     # hips_length = data["HipsLength_ft"]
#     # total_valleys_hips_length = valleys_length + hips_length

#     # if valleys_length > 0 and hips_length == 0:
#     #     shingles_percentage_wastage = 1.12 if valleys_length < 40 else 1.15
#     # elif valleys_length > 0 and hips_length > 0:
#     #     shingles_percentage_wastage = 1.16 if total_valleys_hips_length <= 40 else 1.2
#     # elif valleys_length == 0 and hips_length > 0:
#     #     shingles_percentage_wastage = 1.2
#     # else:
#     #     shingles_percentage_wastage = 1.0

#     # # Calculate caps_percentage_wastage
#     # caps_percentage_wastage = 1.2 if hips_length > 0 else 1.15

#     # # Formulas for product quantities
#     # product_quantity_formulas = [
#     #     "(shingles_percentage_wastage * TotalRoofArea_sqft / 100) * 3",  # Shingles
#     #     "(caps_percentage_wastage * RidgesHipsLength_ft) / 25",  # Caps
#     #     "(EavesRakesLength_ft) / 100",  # Shingle Starters
#     #     "(EavesLength_ft + ValleysLength_ft) / 33",  # Sand Ice & Water Shield
#     #     "(shingles_percentage_wastage * TotalRoofArea_sqft / 100) / 10",  # Synthetic Underlayments
#     #     "(TotalRoofArea_sqft / 100) / 18",  # Roofing Nails
#     #     "(RidgesLength_ft) / 4",  # Ridge Vent System
#     #     "Number_of_Vents",  # Back Roof Vent
#     #     "(StepFlashingLength_ft) / 60",  # Step Flashing
#     #     "Number_of_Pipe_Boots",  # Pipe Flashing
#     #     "(TotalRoofArea_sqft / 100) / 8",  # Roofing Staples
#     #     "((TotalRoofArea_sqft / 100) / 8) + 1",  # Construction Sealant
#     #     "(WallFlashingLength_ft) / 10"  # Dormer Flashing Sticks
#     # ]

#     # Calculate quantities
#     quantities = [
#         math.ceil(eval(formula, {"Number_of_Vents": number_of_vents, "Number_of_Pipe_Boots": number_of_pipe_boots,
#                                  "shingles_percentage_wastage": shingles_percentage_wastage,
#                                  "caps_percentage_wastage": caps_percentage_wastage}, data))
#         if "Number_of_Vents" not in formula and "Number_of_Pipe_Boots" not in formula
#         else number_of_vents if "Number_of_Vents" in formula else number_of_pipe_boots
#         for formula in product_quantity_formulas
#     ]
    

#     return quantities

# # from sqlalchemy import create_engine, Column, Integer, String, Float
# # from sqlalchemy.ext.declarative import declarative_base
# # from sqlalchemy.orm import sessionmaker

# # Base = declarative_base()

# # Define the WastageFactor model
# # class WastageFactor(Base):
# #     __tablename__ = 'wastage_factor'
# #     id = Column(Integer, primary_key=True)
# #     category = Column(String)
# #     condition = Column(String)
# #     wastage_factor = Column(Float)

# # # Create database engine and session
# # engine = create_engine('postgresql://username:password@localhost/dbname')
# # Session = sessionmaker(bind=engine)
# # session = Session()

# from sqlalchemy.orm import Session
# from app.models import WastageCondition
# from sqlalchemy import create_engine, Column, Integer, String, Float
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker


# # Function to get wastage factors for all categories
# def get_wastage_factors(db: Session, valleys_length, hips_length):
#     total_length = valleys_length + hips_length
#     local_vars = {
#         "ValleysLength_ft": valleys_length,
#         "HipsLength_ft": hips_length,
#         "Total_Valleys_Hips_Length_ft": total_length
#     }

#     # Fetch wastage factors for each category
#     results = {}
#     categories = db.query(WastageCondition.category).distinct()
#     for category in categories:
#         category = category[0]  # Extract category name
#         conditions = db.query(WastageCondition).filter_by(category=category).all()
        
#         for entry in conditions:
#             if eval(entry.wastage_condition, {}, local_vars):
#                 results[category] = entry.wastage_factor
#                 break  # Stop checking once a condition is met
#         else:
#             results[category] = 1.0  # Default value if no condition matches

#     return results

# # Example Usage
# valleys_length = 35
# hips_length = 5
# # Session = Depends(get_db)
# wastage_factors = get_wastage_factors(valleys_length, hips_length)
# print("Wastage Factors:", wastage_factors)


# def generate_invoice_df(quantities, data, number_of_vents, number_of_pipe_boots, shingle_color,
#                         type_of_structure, supplier, material_delivery_date, installation_date,
#                         homeowner_email, drip_edge):
#     """
#     Generate the invoice DataFrame using quantities and other details.
#     """

#     shingle_id = shingle_ids[shingle_color]
#     cap_id = cap_ids[shingle_color]

#     # Product IDs
#     product_ids = [
#         shingle_id, cap_id, "TRIOSSPL", "TRISHIWPSA1SQ", "TRISRU42286", 
#         "TRINLSCR114", "TRIPRO4SWN", "TRISBRVAL50BL", "TRISFK338TBB", 
#         "TRIA1143RPFBL", "DUO516STP", "TRITB374103", "TRIXFL9B7TB"
#     ]

#     # Calculate total prices
#     total_price = [quantity * rate for quantity, rate in zip(quantities, rates)]

#     # Create invoice DataFrame
#     invoice_data = {
#         'Product': products,
#         'Product ID': product_ids,
#         'Quantity': quantities,
#         'Rate': rates,
#         'Total Price': total_price
#     }
#     invoice_df = pd.DataFrame(invoice_data)

#     # Calculate the total invoice amount
#     total_invoice_amount = sum(total_price)

#     # Add additional fields to the invoice
#     additional_fields = {
#         "Type of Structure": type_of_structure,
#         "Supplier": supplier,
#         "Material Delivery Date": material_delivery_date,
#         "Installation Date": installation_date,
#         "Homeowner Email": homeowner_email,
#         "Drip Edge": drip_edge
#     }
#     for key, value in additional_fields.items():
#         invoice_df.loc[len(invoice_df)] = ['', '', '', '', key, value]

#     # Add total invoice row
#     invoice_df.loc[len(invoice_df)] = ['', '', '', '', 'Total Invoice', total_invoice_amount]

#     return invoice_df






















###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

from typing import Dict
from sqlalchemy.orm import Session
from app.formula.crud import get_formulas

def get_formulas_by_category(db: Session, skip: int = 0, limit: int = 1000) -> Dict[str, list]:
    """
    Retrieves formulas from the database and organizes them into a dictionary
    grouped by category.

    :param db: SQLAlchemy database session.
    :param skip: Number of records to skip.
    :param limit: Maximum number of records to retrieve.
    :return: Dictionary where keys are categories, and values are lists of equations.
    """
    formulas = get_formulas(db, skip=skip, limit=limit)
    
    formulas_dict = {}
    for formula in formulas:
        if formula.category not in formulas_dict:
            formulas_dict[formula.category] = []
        formulas_dict[formula.category].append(formula.equation)
    
    return formulas_dict

### Usage ###
from app.database import SessionLocal

# Assuming `SessionLocal` is your database session factory
db: Session = SessionLocal()

# Call the function to retrieve and group formulas by category
formulas_by_category = get_formulas_by_category(db)

# Print the grouped dictionary
print(formulas_by_category)

##################################################################

from app.models import WastageCondition

# Function to get wastage factors for all categories
def get_wastage_factors(db: Session, valleys_length, hips_length):
    total_length = valleys_length + hips_length
    local_vars = {
        "ValleysLength_ft": valleys_length,
        "HipsLength_ft": hips_length,
        "Total_Valleys_Hips_Length_ft": total_length
    }

    # Fetch wastage factors for each category
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

    return results

# Example Usage
valleys_length = 35
hips_length = 5
# Session = Depends(get_db)
wastage_factors = get_wastage_factors(db, valleys_length, hips_length)
print("Wastage Factors:", wastage_factors)

##################################################################

data = {
    "Address": "Complete address of the property",
    "TotalRoofArea_sqft": 2200,
    "RidgesHipsLength_ft": 46,
    "ValleysLength_ft": 22,
    "RidgesLength_ft": 32,
    "HipsLength_ft": 14,
    "RakesLength_ft": 15,
    "EavesLength_ft": 16,
    "RakesLength_ft": 17,
    "EavesRakesLength_ft": 31,
    "StepFlashingLength_ft": 9,
    "WallFlashingLength_ft": 10
}

number_of_vents = 2
number_of_pipe_boots = 3

import math

# Correcting duplicate keys in data
data = {
    "Address": "Complete address of the property",
    "TotalRoofArea_sqft": 2200,
    "RidgesHipsLength_ft": 46,
    "ValleysLength_ft": 22,
    "RidgesLength_ft": 32,
    "HipsLength_ft": 14,
    "RakesLength_ft": 15,
    "EavesLength_ft": 16,
    "EavesRakesLength_ft": 31,
    "StepFlashingLength_ft": 9,
    "WallFlashingLength_ft": 10
}

number_of_vents = 2
number_of_pipe_boots = 3

def calculate_product_quantities(formulas_by_category, data, number_of_vents, number_of_pipe_boots, wastage_factors):
    """
    Calculate the quantities for each product based on the input data.
    """
    quantities = {}

    # Merge all variables for eval
    variables = {
        "Number_of_Vents": number_of_vents,
        "Number_of_Pipe_Boots": number_of_pipe_boots,
        "shingles_wastage_factor": wastage_factors.get("Shingles", 1),
        "caps_wastage_factor": wastage_factors.get("Caps/Hip and Ridge Shingles", 1)
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
                category_results.append(f"Error: {str(e)}")
        quantities[category] = category_results[0]

    return quantities

# Calculate quantities
quantities = calculate_product_quantities(formulas_by_category, data, number_of_vents, number_of_pipe_boots, wastage_factors)

print(quantities)


####################################################################