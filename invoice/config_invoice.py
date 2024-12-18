EXTRACTION_DIR = "extraction/extraction_json"

# List of products
products = [
    "Shingles", "Caps/Hip and Ridge Shingles", "Shingle Starters", "Sand Ice & Water Shield/Ice & Water Underlayments", 
    "Synthetic Underlayments", "Roofing Nails/Coil Roofing Nails", "Ridge Vent System/Hip Vents", 
    "Back Roof Vent/Ventilation", "Step Flashing/Flashings", "Pipe Flashing/Flashings", "Roofing Staples/Staples", 
    "Construction Sealant/Adhesives, Caulks & Sealants", "Dormer Flashing Sticks/Flashings"
]

# Product IDs (based on color for shingles and caps)
shingle_ids = {
    "Charcoal": "GAFTMBLBAHDZCH",
    "Weather Wood": "GAFMCTLUHDDSWW",
    "Barkwood": "GAFTMBLBAHDZBA",
    "Driftwood": "OCFDTDKEDW",
    "Pewter Gray": "GAFTMBLBAHDZPG",
    "Hickory": "GAFTMBLBAHDZHI",
    "Shakewood": "GAFTMBLBAHDZSH"
}
cap_ids = {
    "Charcoal": "GAFSARMOCH",
    "Weather Wood": "GAFSARMOWW",
    "Barkwood": "GAFSARMOBA",
    "Driftwood": "OCFHRPEIVDW",
    "Pewter Gray": "GAFSARMOPG",
    "Hickory": "GAFSARMOHI",
    "Shakewood": "GAFSARMOSH"
}

# List of formulas for quantities
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

# Rates for products
rates = [
    39.3300, # Shingles
    58.6700, # Caps
    47.0700, # Shingle Starters
    40.8200, # Sand Ice & Water Shield
    67.3200, # Synthetic Underlayments
    50.8600, # Roofing Nails
    10.1000, # Ridge Vent System
    15.6177, # Back Roof Vent
    38.1558, # Step Flashing
    9.0931, # Pipe Flashing
    7.3500, # Roofing Staples
    6.8100, # Construction Sealant
    12.5000 # Dormer Flashing Sticks
]
