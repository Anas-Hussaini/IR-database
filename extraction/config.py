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

