### CLASSIFY RAW DATA CONFIG ###

# --- Directory Paths ---
INPUT_DIR = "raw_data/insured_roofs_drive_data"
ALL_PDF_REPORTS_DIR = "raw_data/all_pdf_measurement_reports"
UNPROCESSED_DIR = "raw_data/unprocessed"
WASTE_REPORTS_DIR = "raw_data/waste_reports"

# --- Retry Configuration ---
RETRIES = 3  # Number of retries for locked files
DELAY = 2  # Delay in seconds between retries

# --- Keywords for Classification ---
ROOFR_KEYWORD = "Roofr"
EAGLEVIEW_KEYWORDS = ["EagleView", "Eagle View"]
PAGE_THRESHOLD = 6  # Minimum number of pages to qualify as a measurement report

### PROCESS PDF CONFIG ###

dotenv_path=".env"

model="gpt-4o-mini"

prompt = f"""
 ```json
        {{
        "PropertyDetailsAndRoofMeasurements": {{
            "Address": "Complete address of the property",
            "TotalRoofArea_sqft": "Total area of the roof in square feet in float form",
            "RidgesHipsLength_ft": "Total length of ridges and hips in feet and inches",
            "ValleysLength_ft": "Total length of valleys in feet and inches",
            "RidgesLength_ft": "Total length of ridges in feet and inches",
            "HipsLength_ft": "Total length of hips in feet and inches",
            "RakesLength_ft": "Total length of rakes in feet and inches",
            "EavesLength_ft": "Total length of eaves in feet and inches",
            "RakesLength_ft": "Total length of rakes in feet and inches",
            "EavesRakesLength_ft": "Total combined length of eaves and rakes in feet and inches",
            "StepFlashingLength_ft": "Total length of step flashing in feet and inches",
            "WallFlashingLength_ft": "Total length of flashing in feet and inches"
        }}
        }}```
"""

prompt_eagleview = f"""
                ```json
        {{
        "PropertyDetails": {{
            "Address": "Complete address of the property",
            "Longitude": "Geographical longitude of the property",
            "Latitude": "Geographical latitude of the property",
            "TotalRoofArea_sqft": "Total area of the roof in square feet",
            "NumberOfRoofFacets": "Number of roof facets",
            "PredominantRoofPitch": "Predominant pitch of the roof"
        }},
        "PropertyDetailsAndRoofMeasurements": {{
            "Address": "Complete address of the property",
            "TotalRoofArea_sqft": "Total area of the roof in square feet in integer form",
            "RidgesHipsLength_ft": "Total length of ridges and hips in feet",
            "ValleysLength_ft": "Total length of valleys in feet",
            "RidgesLength_ft": "Total length of ridges in feet",
            "HipsLength_ft": "Total length of hips in feet",
            "RakesLength_ft": "Total length of rakes in feet",
            "EavesLength_ft": "Total length of eaves in feet",
            "RakesLength_ft": "Total length of rakes in feet",
            "EavesRakesLength_ft": "Total length of eaves and rakes in feet",
            "StepFlashingLength_ft": "Total length of step flashing in feet",
            "WallFlashingLength_ft": "Total length of flashing in feet"
        }},
        "WasteCalculations": {{
            "TotalRoofAreaForWasteCalculation_sqft": "Total roof area considered for waste calculation in square feet",
            "WastePercentage_AsphaltShingle": "Waste percentage for asphalt shingle roofing"
        }},
        "WastageData": {{
            "WastePercentage": "Waste percentage for the roofing type",
            "Area_sqft": "Total area of the roof in square feet after applying the waste percentage",
            "Squares": "Total number of squares required for the roof including waste"
        
        }},
        "StructureComplexity": {{
            "Category": "Complexity category of the roof structure (e.g., Simple, Normal, Complex)"
        }},
        "Notes": {{
            "StructuralChanges": "Details about any structural changes in the past",
            "SpecialRemarks": "Any additional remarks or notes"
        }}
        }}```
        """