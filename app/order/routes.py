import os
import json
import logging
import pandas as pd
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from .functions import process_order, review_order, get_order_history  # Import relevant functions for processing orders
from ..schemas import OrderData

router = APIRouter()

# Directories for saving uploaded files and downloads (adjust paths as necessary)
UPLOAD_DIR = "app/order/saved_csvs"
DOWNLOAD_DIR = "app/order/downloads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create upload directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # Create download directory if it doesn't exist

def get_unique_filename(directory, base_name):
    """
    Generate a unique filename in the specified directory.

    Args:
        directory (str): The directory where the file is saved.
        base_name (str): The base name for the file.

    Returns:
        str: A unique filename suitable for saving.
    """
    counter = 1
    while True:
        # Construct the potential filename
        file_name = f"{base_name}({counter}).csv"
        file_path = os.path.join(directory, file_name)
        if not os.path.exists(file_path):  # Check if the file already exists
            return file_path  # Return the unique filename if it doesn't exist
        counter += 1  # Increment the counter for the next filename

@router.post("/submit-order/")
async def submit_order(data: OrderData):
    """
    Process the provided order data, generate the order submission, and return the response.

    Args:
        data (OrderData): The order data submitted in the request.

    Returns:
        dict: The response from processing the order submission.
    """
    try:
        logging.info(f"Received order data: {data} : {type(data)}")

        # Convert the OrderData instance into a dictionary
        order_data_dict = data.dict()

        # Convert the dictionary to a formatted JSON string
        json_data = json.dumps(order_data_dict, indent=4)
        
        # Process the order using the provided JSON data
        response = process_order(json_data)
        logging.info(f"Order processing result: {response}")

        # Return the processed response
        return response
    
    except Exception as e:
        logging.error(f"Error processing order: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process the order: {str(e)}"
        )

@router.post("/review-order/")
async def process_review_order(data: OrderData):
    """
    Review the provided order data and return the review result in JSON format.

    Args:
        data (OrderData): The order data submitted in the request.

    Returns:
        dict: The review result of the order.
    """
    try:
        logging.info(f"Received review data: {data} : {type(data)}")

        # Convert the OrderData instance into a dictionary
        order_data_dict = data.dict()

        # Convert the dictionary to a formatted JSON string
        json_data = json.dumps(order_data_dict, indent=4)

        # Process the order review using the provided JSON data
        review_json = review_order(json_data)
        logging.info(f"Order review processing result: {review_json}")

        # Return the review result as JSON
        return review_json

    except Exception as e:
        logging.error(f"Error processing review: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process order review: {str(e)}"
        )

@router.get("/order-history/")
async def order_history(
    page_number: Optional[int] = 1, 
    page_size: Optional[int] = 10
):
    """
    Fetch order history with optional pagination parameters.

    Args:
        page_number (int, optional): The page number for pagination (default is 1).
        page_size (int, optional): The number of records to retrieve per page (default is 10).

    Returns:
        dict: The response containing order history data.
    """
    try:
        logging.info("Fetching order history.")
        logging.info(f"Received parameters: page_number={page_number}, page_size={page_size}")
        
        # Call the function to fetch order history based on pagination parameters
        response = get_order_history(page_number=page_number, page_size=page_size)

        logging.info("Order history fetched successfully.")
        return response

    except Exception as e:
        logging.error(f"Error occurred while processing order history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch order history: {str(e)}"
        )