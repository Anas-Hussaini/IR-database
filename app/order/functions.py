import logging
from fastapi import HTTPException
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from ..config import ACCOUNT_ID, API_SITE_ID, SHIPPING_BRANCH, BEACON_USERNAME, BEACON_PASSWORD, SITE_ID, PERSISTENT_LOGIN_TYPE, USER_AGENT, BEACON_LOGIN_TIME_LIMIT, TAX_PERCENTAGE, OTHER_CHARGES

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables to store cookies and login time
SESSION_DATA = {
    "cookies": None,
    "login_time": None
}

base_url = "https://beacon-uat-ng.becn.com/v1/rest/com/becn"
login_endpoint = "/login"
submit_endpoint = "/submitOrder"
item_details_endpoint = "/items"
order_history_endpoint = "/orderhistory"

credentials = {
    "username": BEACON_USERNAME,
    "password": BEACON_PASSWORD,
    "siteId": SITE_ID,
    "persistentLoginType": PERSISTENT_LOGIN_TYPE,
    "userAgent": USER_AGENT,
    "apiSiteId": API_SITE_ID
}

def convert_to_line_items(df):
    line_items = [
        {"itemNumber": str(int(row["Product_ID"])), "quantity": int(row["Quantity"]), "unitOfMeasure": row["Unit"]}
        for _, row in df.iterrows()
    ]
    logger.debug("Converted DataFrame to line items: %s", line_items)
    return line_items

def login(base_url, login_endpoint, credentials):
    global SESSION_DATA
    current_time = datetime.now()

    # Check if already logged in and session is valid
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

        # Save cookies and login time
        SESSION_DATA["cookies"] = response.cookies
        SESSION_DATA["login_time"] = current_time

        return response.cookies, response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error logging in: %s", e)
        return None, None

def submit_order(base_url, endpoint, payload, cookies):
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
    payload = {
        "accountId": account_id,
        "apiSiteId": api_site_id,
        "job": {
            "jobNumber": "999"
        },
        "purchaseOrderNo": "UAT test",
        "lineItems": items,
        "shipping": {
            "shippingMethod": "O",
            "shippingBranch": shipping_branch,
            "address": {
                "address1": "ROOF DEPOT MOUNTAIN",
                "address2": "address2",
                "city": "ROCKVILLE",
                "postalCode": "80112",
                "state": "MD"
            }
        },
        "specialInstruction": "This is a test order please ignore.",
        "pickupDate": pickup_date,
        "pickupTime": "Afternoon"
    }
    logger.debug("Generated payload: %s", payload)
    return payload

def process_order(df: pd.DataFrame):

    try:
        logger.info("Processing order.")
        
        # Locate the row with 'Material Delivery Date' in the 'Quantity' column
        matching_row = df.loc[df['Quantity'] == 'Material Delivery Date']
        
        # Extract value from the 'Total Price' column
        if not matching_row.empty:
            material_delivery_date = matching_row['Total Price'].values[0]
            logging.info(f"Material Delivery Date found: {material_delivery_date}")
        
        # Filter the data
        filtered_df = df[df['Product_ID'].notna() & (df['Product_ID'] != '')]

        # Extract the necessary columns
        items_df = filtered_df[["Product_ID", "Unit", "Quantity"]]
        line_items = convert_to_line_items(items_df)
        
        # Generate the payload for the order submission
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
            # Submit order
            response = submit_order(base_url, submit_endpoint, generated_payload, cookies)
            if response:
                logger.info("Order submitted successfully: %s", response)
            else:
                logger.error("Failed to submit the order.")
                raise HTTPException(status_code=400, detail="Failed to submit the order.")

            # # Perform logout
            # if not logout(base_url, logout_endpoint, cookies):
            #     logger.error("Logout failed.")
            #     raise HTTPException(status_code=400, detail="Logout failed.")
        else:
            logger.error("Login failed.")
            raise HTTPException(status_code=400, detail="Login failed.")
    except Exception as e:
        logger.error("Error processing order: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    return response

def fetch_item_details(base_url, items_endpoint, item_number, cookies):
    """
    Fetch item details using the `/items` endpoint with a query parameter `itemNumber`.
    """
    url = f"{base_url}{items_endpoint}?itemNumber={item_number}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        logger.info("Fetching item details for itemNumber: %s", item_number)
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching item details: %s", e)
        raise HTTPException(status_code=400, detail="Failed to fetch item details.")

def review_order(df: pd.DataFrame):
    """
    Review an order by fetching item details from the `/items` endpoint
    and generating an invoice.

    Args:
        df (pd.DataFrame): DataFrame containing 'Product_ID' and 'Quantity'.

    Returns:
        pd.DataFrame: Invoice with item details and total cost.
    """
    try:
        logger.info("Starting order review process.")

        # Perform login to get session cookies
        cookies, login_response = login(base_url, login_endpoint, credentials)
        if not cookies or not login_response:
            logger.error("Login failed.")
            raise HTTPException(status_code=400, detail="Login failed.")
        logger.info("Login successful.")

        # Filter valid items from the DataFrame
        valid_items_df = df[df['Product_ID'].notna() & (df['Product_ID'] != '')]
        logger.info(f"Filtered valid items: {len(valid_items_df)} items.")

        # Prepare a list to store item details and total cost
        invoice_data = []
        for _, row in valid_items_df.iterrows():
            item_number = str(int(row['Product_ID']))
            quantity = int(row['Quantity'])

            logger.info(f"Fetching details for item {item_number} with quantity {quantity}.")

            # Fetch item details from the API
            item_details = fetch_item_details(base_url, item_details_endpoint, item_number, cookies)
            if item_details:
                item_details_2 = item_details["currentSKU"]
                unit_price = item_details_2["unitPrice"]
                logger.info(f"Unit_Price: {unit_price}.")
                unit = item_details_2["currentUOM"]
                logger.info(f"UnitofMeasure: {unit}.")
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

        # Generate invoice DataFrame
        invoice_df = pd.DataFrame(invoice_data)
        logger.info("Invoice DataFrame generated.")

        matching_row = df.loc[df['Quantity'] == 'Material Delivery Date']
        material_delivery_date = "N/A"

        # Extract value from the 'Total Price' column
        if not matching_row.empty:
            material_delivery_date = matching_row['Total Price'].values[0]
            logger.info(f"Material delivery date extracted: {material_delivery_date}.")

        sub_total = invoice_df["Total Price"].sum()
        logger.info(f"Order subtotal calculated: {sub_total}.")

        sub_total_after_charges = sub_total + OTHER_CHARGES
        logger.info(f"Subtotal after other charges: {sub_total_after_charges}.")

        tax = sub_total_after_charges * (TAX_PERCENTAGE / 100)
        logger.info(f"Tax calculated: {tax}.")

        total_invoice_amount = sub_total_after_charges + tax
        logger.info(f"Total invoice amount: {total_invoice_amount}.")

        # Add additional fields as separate rows
        additional_fields = {
            "Material Delivery Date": material_delivery_date,
            "Order Subtotal": sub_total,
            "Other Charges": OTHER_CHARGES,
            "Tax": tax,
            "Total Invoice Amount": total_invoice_amount,
        }

        for key, value in additional_fields.items():
            invoice_df.loc[len(invoice_df)] = ['', '', '', '', key, value]
            logger.info(f"Added additional field {key}: {value}.")

        logger.info("Order review process completed successfully.")
        return invoice_df

    except Exception as e:
        logger.error("Error reviewing order: %s", e)
        raise HTTPException(status_code=500, detail=str(e))



def get_order_history(page_number=1, page_size=5):
    """
    Fetches order history for a specific account ID from the Beacon API, with login authentication.

    Args:
        base_url (str): The base URL of the Beacon API.
        login_endpoint (str): The endpoint for login.
        credentials (dict): Login credentials (e.g., {"username": "user", "password": "pass"}).
        account_id (str): The account ID for which to fetch order history.
        page_size (int): Number of records to retrieve per page. Default is 5.

    Returns:
        dict: JSON response from the API if successful.
        str: Error message if the request fails.
    """
    try:
        logger.info("Starting order review process.")

        # Perform login to get session cookies
        cookies, login_response = login(base_url, login_endpoint, credentials)
        if not cookies or not login_response:
            logger.error("Login failed.")
            raise HTTPException(status_code=400, detail="Login failed.")
        
        logger.info("Login successful.")

        # Set up the parameters for the order history request
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
