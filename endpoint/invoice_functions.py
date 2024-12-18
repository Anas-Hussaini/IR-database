import pandas as pd
import math
import config
import importlib
importlib.reload(config)
from config import products, shingle_ids, cap_ids, product_quantity_formulas, rates

def process_json_and_return_invoice_df(data, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge):
    """
    Process the roof data JSON object, calculate quantities, total prices, and return the invoice DataFrame.
    """   

    shingle_id = shingle_ids[shingle_color]
    cap_id = cap_ids[shingle_color]

    # Product IDs
    product_ids = [
        shingle_id, cap_id, "TRIOSSPL", "TRISHIWPSA1SQ", "TRISRU42286", 
        "TRINLSCR114", "TRIPRO4SWN", "TRISBRVAL50BL", "TRISFK338TBB", 
        "TRIA1143RPFBL", "DUO516STP", "TRITB374103", "TRIXFL9B7TB"
    ]

    # Calculate shingles_percentage_wastage
    valleys_length = data["ValleysLength_ft"]
    hips_length = data["HipsLength_ft"]
    
    total_valleys_hips_length = valleys_length + hips_length

    if valleys_length > 0 and hips_length == 0:
        shingles_percentage_wastage = 1.12 if valleys_length < 40 else 1.15
    elif valleys_length > 0 and hips_length > 0:
        shingles_percentage_wastage = 1.16 if total_valleys_hips_length <= 40 else 1.2
    elif valleys_length == 0 and hips_length > 0:
        shingles_percentage_wastage = 1.2
    else:
        shingles_percentage_wastage = 1.0

    # Calculate caps_percentage_wastage
    if hips_length > 0:
        caps_percentage_wastage = 1.2
    else:
        caps_percentage_wastage = 1.15

    product_quantity_formulas = [
    "(shingles_percentage_wastage*TotalRoofArea_sqft/100)*3",  # Shingles
    "(caps_percentage_wastage*RidgesHipsLength_ft)/25",  # Caps
    "(EavesRakesLength_ft)/100",  # Shingle Starters
    "(EavesLength_ft+ValleysLength_ft)/33",  # Sand Ice & Water Shield
    "(shingles_percentage_wastage*TotalRoofArea_sqft/100)/10",  # Synthetic Underlayments
    "(TotalRoofArea_sqft/100)/18",  # Roofing Nails
    "(RidgesLength_ft)/4",  # Ridge Vent System
    "Number_of_Vents",  # Back Roof Vent
    "(StepFlashingLength_ft)/60",  # Step Flashing
    "Number_of_Pipe_Boots",  # Pipe Flashing
    "(TotalRoofArea_sqft/100)/8",  # Roofing Staples
    "((TotalRoofArea_sqft/100)/8)+1",  # Construction Sealant
    "(WallFlashingLength_ft)/10"  # Dormer Flashing Sticks
    ]

    product_quantity_calculations = [
        f"({shingles_percentage_wastage}*{data["TotalRoofArea_sqft"]}/100)*3",  # Shingles
        f"({caps_percentage_wastage}*{data["RidgesHipsLength_ft"]})/25",  # Caps
        f"({data["EavesRakesLength_ft"]})/100",  # Shingle Starters
        f"({data["EavesLength_ft"]}+{data["ValleysLength_ft"]})/33",  # Sand Ice & Water Shield
        f"({shingles_percentage_wastage}*{data["TotalRoofArea_sqft"]}/100)/10",  # Synthetic Underlayments
        f"({data["TotalRoofArea_sqft"]}/100)/18",  # Roofing Nails
        f"({data["RidgesLength_ft"]})/4",  # Ridge Vent System
        f"{number_of_vents}",  # Back Roof Vent
        f"({data["StepFlashingLength_ft"]})/60",  # Step Flashing
        f"{number_of_pipe_boots}",  # Pipe Flashing
        f"({data["TotalRoofArea_sqft"]}/100)/8",  # Roofing Staples
        f"(({data["TotalRoofArea_sqft"]}/100)/8)+1",  # Construction Sealant
        f"({data["WallFlashingLength_ft"]})/10"  # Dormer Flashing Sticks
    ]

    # Calculate quantities
    quantities = [
        # math.ceil(eval(formula, {"Number_of_Vents": number_of_vents, "Number_of_Pipe_Boots": number_of_pipe_boots}, data["PropertyDetailsAndRoofMeasurements"])) 
        math.ceil(eval(formula, {"Number_of_Vents": number_of_vents, "Number_of_Pipe_Boots": number_of_pipe_boots,"shingles_percentage_wastage": shingles_percentage_wastage , "caps_percentage_wastage": caps_percentage_wastage}, data)) 
        if "Number_of_Vents" not in formula and "Number_of_Pipe_Boots" not in formula 
        else number_of_vents if "Number_of_Vents" in formula else number_of_pipe_boots 
        for formula in product_quantity_formulas
    ]
    
    # Calculate total prices
    total_price = [quantity * rate for quantity, rate in zip(quantities, rates)]

    # Create invoice DataFrame
    invoice_data = {
        'Product': products,
        'Product ID': product_ids,
        'Formula': product_quantity_formulas,
        'Calculation': product_quantity_calculations,
        'Quantity': quantities,
        'Rate': rates,
        'Total Price': total_price
    }
    invoice_df = pd.DataFrame(invoice_data)

    # Calculate the total invoice amount
    total_invoice_amount = sum(total_price)
    
    # Add additional fields to the invoice
    additional_fields = {
        "total_invoice_amount"
        "Type of Structure": type_of_structure,
        "Supplier": supplier,
        "Material Delivery Date": material_delivery_date,
        "Installation Date": installation_date,
        "Homeowner Email": homeowner_email,
        "Drip Edge": drip_edge
    }
    for key, value in additional_fields.items():
        invoice_df.loc[len(invoice_df)] = ['', '', '', '', '', key, value]

    
    invoice_df.loc[len(invoice_df)] = ['', '', '', '', '', 'Total Invoice', total_invoice_amount]
    
    
    return invoice_df


