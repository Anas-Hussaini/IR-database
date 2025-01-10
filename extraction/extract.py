import logging
from .config import model
from .extract_functions import extract_text_from_pdf, get_json_from_openai, json_string_to_json, convert_to_feet

# Configure logging
logging.basicConfig(
    filename='pdf_processing.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

def process_pdf(pdf_path):
    """
    Reads the PDF, extracts text, and gets structured JSON information.
    """
    try:
        logging.info(f"Processing PDF file: {pdf_path}")
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        if not text:
            logging.warning("No text extracted from the PDF.")
            return None

        # Communicate with OpenAI and get JSON data
        json_output = get_json_from_openai(text, model)
        if not json_output:
            logging.warning("No JSON output received from OpenAI.")
            return None

        # Parse JSON and extract required information
        data2 = json_string_to_json(json_output)
        if not data2:
            logging.warning("Failed to parse JSON output.")
            return None

        data = data2.get('PropertyDetailsAndRoofMeasurements')
        if not data:
            logging.warning("No 'PropertyDetailsAndRoofMeasurements' found in JSON.")
            return None

        # Convert measurements to feet
        for key, value in data.items():
            if key not in ['Address', 'TotalRoofArea_sqft']:
                try:
                    data[key] = convert_to_feet(value)
                except Exception as e:
                    logging.error(f"Error converting value for '{key}': {e}")
                    data[key] = None

        logging.info("PDF processing completed successfully.")
        return data

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
