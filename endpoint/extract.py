import sys
sys.path.append('../')
import config
import importlib
importlib.reload(config)
from config import model
from extract_functions import extract_text_from_pdf, get_json_from_openai, json_string_to_json, convert_to_feet

def process_pdf(pdf_path):
    """
    Reads the PDF, extracts text, and gets structured JSON information.
    """
    text = extract_text_from_pdf(pdf_path)
    if text:
        json_output = get_json_from_openai(text, model)
        data2 =  json_string_to_json(json_output)
        data=data2['PropertyDetailsAndRoofMeasurements']
        
        for key, value in data.items():
            if key not in ['Address', 'TotalRoofArea_sqft']:
                data[key] = convert_to_feet(value)
                
        return data
    else:
        print("No text extracted from the PDF.")
        return None
    