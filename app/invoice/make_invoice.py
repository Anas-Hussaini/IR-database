from extraction.extract import process_pdf
from .endpoint_functions import process_json_and_return_invoice_json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_pdf_and_return_invoice(pdf_path, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge):
    """
    Process the given PDF, extract relevant data, and generate an invoice JSON object.

    Args:
    - pdf_path (str): Path to the PDF file to be processed.
    - number_of_vents (int): Number of vents to be included in the invoice.
    - number_of_pipe_boots (int): Number of pipe boots to be included in the invoice.
    - shingle_color (str): Color of the shingles to be used.
    - type_of_structure (str): Type of the structure (e.g., Normal, Complex).
    - supplier (str): Name or ID of the material supplier.
    - material_delivery_date (str): Date when the materials will be delivered (format: MM/DD/YYYY).
    - installation_date (str): Date when the installation is scheduled (format: MM/DD/YYYY).
    - homeowner_email (str): Email address of the homeowner for correspondence.
    - drip_edge (bool): Whether a drip edge is included (True or False).

    Returns:
    - dict: A JSON object representing the invoice data.
    """
    logger.info(f"Processing PDF file: {pdf_path}")
    
    # Extract data from the provided PDF file
    data = process_pdf(pdf_path)
    logger.debug(f"Extracted data from PDF: {data}")
    
    # Generate invoice JSON from the extracted data and additional parameters
    logger.info("Generating invoice JSON object.")
    invoice_json = process_json_and_return_invoice_json(
        data, 
        number_of_vents, 
        number_of_pipe_boots, 
        shingle_color, 
        type_of_structure, 
        supplier, 
        material_delivery_date, 
        installation_date, 
        homeowner_email, 
        drip_edge
    )
    logger.info("Invoice JSON generation complete.")

    return invoice_json

# Example usage:
# Parameters for generating the invoice
# number_of_vents = 2
# number_of_pipe_boots = 3
# shingle_color = "Default"
# type_of_structure = "Normal"
# supplier = "BEACON"
# material_delivery_date = "09/12/2024"
# installation_date = "09/19/2024"
# homeowner_email = "homeowner@gmail.com"
# drip_edge = True
# pdf_path = "app/invoice/uploaded_files/24_lakeside_drive_stafford_va_22554.pdf"

# Generate the invoice JSON object
# invoice_json = process_pdf_and_return_invoice(pdf_path, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge)

# Print the invoice JSON object
# print(invoice_json)
