from extraction.extract import process_pdf
from .endpoint_functions import process_json_and_return_invoice_df
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_pdf_and_return_invoice(pdf_path, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge):
    """
    Process the given PDF, extract relevant data, and generate an invoice DataFrame.

    Args:
    - pdf_path: Path to the PDF file to be processed.
    - number_of_vents: Number of vents to be included.
    - number_of_pipe_boots: Number of pipe boots to be included.
    - shingle_color: Color of the shingles.
    - type_of_structure: Type of the structure (e.g., Normal, Complex).
    - supplier: ID or name of the supplier.
    - material_delivery_date: Date when materials are expected to be delivered.
    - installation_date: Date when the installation is planned.
    - homeowner_email: Email address of the homeowner.
    - drip_edge: Boolean indicating if drip edge is included.

    Returns:
    - A DataFrame representing the invoice.
    """
    logger.info(f"Processing PDF file: {pdf_path}")
    
    # Extract data from PDF
    data = process_pdf(pdf_path)
    logger.debug(f"Extracted data from PDF: {data}")
    
    # Generate invoice DataFrame from the extracted data
    logger.info("Generating invoice DataFrame.")
    invoice_df = process_json_and_return_invoice_df(
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
    logger.info("Invoice DataFrame generation complete.")

    return invoice_df

# Example Usage:
# number_of_vents=2
# number_of_pipe_boots=3
# shingle_color="Default"
# type_of_structure="Normal"
# supplier="BEACON"
# material_delivery_date="9/12/2024"
# installation_date="19/12/2024"
# homeowner_email="homeowner@gmail.com"
# drip_edge=True
# pdf_path = "app/invoice/uploaded_files/24_lakeside_drive_stafford_va_22554.pdf"

# invoice_df = process_pdf_and_return_invoice(pdf_path, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge)

# print(invoice_df)
