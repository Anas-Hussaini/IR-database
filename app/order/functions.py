import logging
from fastapi import HTTPException
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from ..config import ACCOUNT_ID, API_SITE_ID, SHIPPING_BRANCH, BEACON_USERNAME, BEACON_PASSWORD, SITE_ID, PERSISTENT_LOGIN_TYPE, USER_AGENT, BEACON_LOGIN_TIME_LIMIT, TAX_PERCENTAGE, OTHER_CHARGES
from ..schemas import OrderData


# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables to store cookies and login timestamp
SESSION_DATA = {
    "cookies": None,
    "login_time": None
}

base_url = "https://beacon-uat-ng.becn.com/v1/rest/com/becn"
login_endpoint = "/login"
submit_endpoint = "/submitOrder"
item_details_endpoint = "/items"
order_history_endpoint = "/orderhistory"

# User credentials for API authentication
credentials = {
    "username": BEACON_USERNAME,
    "password": BEACON_PASSWORD,
    "siteId": SITE_ID,
    "persistentLoginType": PERSISTENT_LOGIN_TYPE,
    "userAgent": USER_AGENT,
    "apiSiteId": API_SITE_ID
}

def convert_to_line_items(data_list: list):
    """
    Convert a list of product data into the format required for line items in an order.

    Args:
        data_list (list): A list of dictionaries containing 'Product_ID', 'Quantity', and 'Unit'.

    Returns:
        list: A list of formatted line items.
    """
    line_items = [
        {"itemNumber": str(int(item["Product_ID"])), "quantity": int(item["Quantity"]), "unitOfMeasure": item["Unit"]}
        for item in data_list
    ]
    logger.debug("Converted data list to line items: %s", line_items)
    return line_items

def login(base_url, login_endpoint, credentials):
    """
    Log in to the Beacon API, storing session cookies for future requests.

    Args:
        base_url (str): The base URL of the API.
        login_endpoint (str): The endpoint for login.
        credentials (dict): User credentials for login.

    Returns:
        tuple: A tuple containing session cookies and a JSON response message.
    """
    global SESSION_DATA
    current_time = datetime.now()

    # Check if already logged in and if session is still valid
    if SESSION_DATA["cookies"] and SESSION_DATA["login_time"]:
        time_elapsed = current_time - SESSION_DATA["login_time"]
        if time_elapsed < timedelta(minutes=BEACON_LOGIN_TIME_LIMIT):
            logger.info("Using existing session, no need to login again.")
            return SESSION_DATA["cookies"], {"message": "Reused existing login session."}

    url = f"{base_url}{login_endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        logger.info("Attempting to login with credentials for user: %s", credentials["username"])
        response = requests.post(url, headers=headers, data=json.dumps(credentials))
        response.raise_for_status()
        logger.info("Login successful.")

        # Save cookies and login timestamp
        SESSION_DATA["cookies"] = response.cookies
        SESSION_DATA["login_time"] = current_time

        return response.cookies, response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error logging in: %s", e)
        return None, None

def submit_order(base_url, endpoint, payload, cookies):
    """
    Submit an order to the Beacon API.

    Args:
        base_url (str): The base URL of the API.
        endpoint (str): The endpoint for order submission.
        payload (dict): The order data to submit.
        cookies (requests.cookies.RequestsCookieJar): Session cookies for authentication.

    Returns:
        dict: The JSON response from the API after order submission.
    """
    url = f"{base_url}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        logger.info("Submitting order with payload: %s", payload)
        response = requests.post(url, headers=headers, cookies=cookies, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error submitting order: %s", e)
        return None

def generate_payload(account_id, api_site_id, items, shipping_branch, pickup_date):
    """
    Generate the payload for order submission.

    Args:
        account_id (str): The account ID.
        api_site_id (str): The API site ID.
        items (list): List of line items.
        shipping_branch (str): The shipping branch.
        pickup_date (str): The pickup date for the order.

    Returns:
        dict: The structured payload for the API.
    """
    payload = {
        "accountId": account_id,
        "apiSiteId": api_site_id,
        "job": {
            "jobNumber": "999"  # Placeholder job number
        },
        "purchaseOrderNo": "UAT test",  # Example purchase order number
        "lineItems": items,
        "shipping": {
            "shippingMethod": "O",  # Shipping method type, "O" stands for Overland
            "shippingBranch": shipping_branch,
            "address": {
                "address1": "ROOF DEPOT MOUNTAIN",
                "address2": "address2",  # Placeholder address data
                "city": "ROCKVILLE",
                "postalCode": "80112",
                "state": "MD"
            }
        },
        "specialInstruction": "This is a test order please ignore.",
        "pickupDate": pickup_date,
        "pickupTime": "Afternoon"  # Fixed pickup time
    }
    logger.debug("Generated payload: %s", payload)
    return payload

def process_order(json_data: str):
    """
    Process the incoming order JSON data, perform login, and submit the order.

    Args:
        json_data (str): The JSON string representing the order.

    Returns:
        dict: The response from the API after order submission.
    """
    try:
        logger.info("Processing order.")

        data = json.loads(json_data)  # Parse the incoming JSON

        logger.info(f"Process STARTED with data: {data} : {type(data)}")
        
        # Extract the delivery date from the summary section
        material_delivery_date = data["Summary"]["Material_Delivery_Date"]
        if material_delivery_date:
            logger.info(f"Material Delivery Date found: {material_delivery_date}")
        else:
            raise ValueError("Material Delivery Date is missing in the input data.")

        # Extract invoice details
        invoice_details = data["Invoice_Details"]
        if not invoice_details:
            raise ValueError("No Invoice Details found in the input data.")

        # Convert invoice details to line items 
        line_items = convert_to_line_items(invoice_details)
        logger.info(f"line_items: {line_items}")
        
        # Generate the payload for order submission
        generated_payload = generate_payload(
            account_id=ACCOUNT_ID,
            api_site_id=API_SITE_ID,
            items=line_items,
            shipping_branch=SHIPPING_BRANCH,
            pickup_date=material_delivery_date
        )

        # Perform login
        cookies, login_response = login(base_url, login_endpoint, credentials)
        if cookies and login_response:
            # Submit the order with the generated payload and session cookies
            response = submit_order(base_url, submit_endpoint, generated_payload, cookies)
            if response:
                logger.info("Order submitted successfully: %s", response)
            else:
                logger.error("Failed to submit the order.")
                raise HTTPException(status_code=400, detail="Failed to submit the order.")
        else:
            logger.error("Login failed.")
            raise HTTPException(status_code=400, detail="Login failed.")
        
        # Uncomment if logout is necessary
        # if not logout(base_url, logout_endpoint, cookies):
        #     logger.error("Logout failed.")
        #     raise HTTPException(status_code=400, detail="Logout failed.")

    except ValueError as ve:
        logger.error("Value error: %s", ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error("Error processing order: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    return response

def fetch_item_details(base_url, items_endpoint, item_number, cookies):
    """
    Fetch item details from the API for a specific item.

    Args:
        base_url (str): The base URL of the API.
        items_endpoint (str): The endpoint for fetching item details.
        item_number (str): The item number to fetch details for.
        cookies (requests.cookies.RequestsCookieJar): Session cookies for authentication.

    Returns:
        dict: The item details returned from the API.
    """
    url = f"{base_url}{items_endpoint}?itemNumber={item_number}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        logger.info("Fetching item details for item number: %s", item_number)
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching item details: %s", e)
        raise HTTPException(status_code=400, detail="Failed to fetch item details.")

def review_order(json_data: str):
    """
    Review an order by fetching item details and generating an invoice.

    Args:
        json_data (str): The JSON string containing the invoice details.

    Returns:
        dict: A JSON-formatted invoice containing item details and total costs.
    """
    try:
        logger.info("Starting order review process")
        
        data = json.loads(json_data)  # Parse the incoming JSON
        logger.info(f"Review process started with data: {data} : {type(data)}")
        
        # Perform login to get session cookies
        cookies, login_response = login(base_url, login_endpoint, credentials)
        if not cookies or not login_response:
            logger.error("Login failed.")
            raise HTTPException(status_code=400, detail="Login failed.")
        logger.info("Login successful.")

        # Prepare a list to store item details and total costs
        invoice_data = []
        
        invoice_details_list = data["Invoice_Details"]
        material_delivery_date = data["Summary"]["Material_Delivery_Date"]
        
        for item in invoice_details_list:
            item_number = str(int(item["Product_ID"]))
            quantity = int(item["Quantity"])
            
            logger.info(f"Fetching details for item {item_number} with quantity {quantity}.")

            # Fetch item details from the API
            item_details = fetch_item_details(base_url, item_details_endpoint, item_number, cookies)
            if item_details:
                item_details_2 = item_details["currentSKU"]
                unit_price = item_details_2["unitPrice"]
                unit = item_details_2["currentUOM"]
                description = item_details_2["productName"]

                total_price = unit_price * quantity

                # Add item details to invoice
                invoice_data.append({
                    "Item Number": item_number,
                    "Description": description,
                    "Unit": unit,
                    "Unit Price": unit_price,
                    "Quantity": quantity,
                    "Total Price": total_price
                })
                logger.info(f"Added item {item_number} to the invoice.")

        sub_total = sum(item["Total Price"] for item in invoice_data)
        logger.info(f"Order subtotal calculated: {sub_total}.")

        sub_total_after_charges = sub_total + OTHER_CHARGES
        logger.info(f"Subtotal after other charges: {sub_total_after_charges}.")

        total_invoice_amount = sub_total_after_charges
        logger.info(f"Total invoice amount: {total_invoice_amount}.")

        # Add additional fields to the JSON response
        additional_fields = {
            "Material Delivery Date": material_delivery_date,
            "Order Subtotal": sub_total,
            "Other Charges": OTHER_CHARGES,
            "Tax": "Not Applied Yet",
            "Total Invoice Amount": f"{total_invoice_amount} + tax",  # Note: Tax not calculated yet
        }

        # Combine item details and additional fields into the final invoice response
        invoice_response = {
            "Invoice Details": invoice_data,
            "Summary": additional_fields
        }

        logger.info("Order review process completed successfully.")
        return invoice_response

    except Exception as e:
        logger.error("Error reviewing order: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


def get_order_history(page_number=1, page_size=5):
    """
    Fetch order history for a specific account ID from the Beacon API.

    Args:
        page_number (int): The page number for pagination (default is 1).
        page_size (int): The number of records per page (default is 5).

    Returns:
        dict: The JSON response from the API containing order history data.
    """
    try:
        logger.info("Starting order history retrieval process.")

        # Perform login to get session cookies
        cookies, login_response = login(base_url, login_endpoint, credentials)
        if not cookies or not login_response:
            logger.error("Login failed.")
            raise HTTPException(status_code=400, detail="Login failed.")
        
        logger.info("Login successful.")

        # Set up parameters for the order history request
        order_history_url = f"{base_url}/{order_history_endpoint}"
        params = {
            "accountId": ACCOUNT_ID,
            "pageNo": page_number,
            "pageSize": page_size
        }

        # Make the GET request with session cookies
        response = requests.get(order_history_url, params=params, cookies=cookies)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Log success and return the JSON response
        logger.info("Order history fetched successfully.")
        return response.json()

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        return {"error": e.detail}
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": str(e)}