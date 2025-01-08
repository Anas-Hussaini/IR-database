from extraction.extract import process_pdf
from .get_invoice import process_json_and_return_invoice_df


def process_pdf_and_return_invoice(pdf_path, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge):
    
    data = process_pdf(pdf_path)
    
    invoice_df = process_json_and_return_invoice_df(data, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge)
    
    return invoice_df


# # Usage ##

# number_of_vents=2
# number_of_pipe_boots=3
# shingle_color="Default"
# type_of_structure="Normal"
# supplier="BEACON"
# material_delivery_date="9/12/2024"
# installation_date="19/12/2024"
# homeowner_email="homeowner@gmail.com"
# drip_edge=True
# pdf_path = "29_pinto_lane_stafford_va_22556.pdf"

# invoice_df = process_pdf_and_return_invoice(pdf_path, number_of_vents, number_of_pipe_boots, shingle_color, type_of_structure, supplier, material_delivery_date, installation_date, homeowner_email, drip_edge)

# print(invoice_df)


