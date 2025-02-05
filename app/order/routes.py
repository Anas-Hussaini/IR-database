import os
import logging
import pandas as pd
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from .functions import process_order, review_order, get_order_history  # Import your existing process_order function

router = APIRouter()

# Directory for uploaded files (Adjust paths as necessary)
UPLOAD_DIR = "app/order/saved_csvs"
DOWNLOAD_DIR = "app/order/downloads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to generate a unique filename in the specified directory
def get_unique_filename(directory, base_name):
    """
    Generate a unique filename in the specified directory.
    """
    counter = 1
    while True:
        file_name = f"{base_name}({counter}).csv"
        file_path = os.path.join(directory, file_name)
        if not os.path.exists(file_path):
            return file_path
        counter += 1

@router.post("/submit-order/")
async def submit_order(file: UploadFile = File(...)):
    """
    Process the uploaded CSV file, generate the order submission, and return a downloadable CSV with the results.
    """
    try:
        logging.info(f"Received order file: {file.filename}")

        # Save the uploaded CSV file
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        logging.info(f"File saved at: {save_path}")

        # Read CSV file into DataFrame
        df = pd.read_csv(save_path)

        # Process the order using the provided CSV file
        response = process_order(df=df)

        logging.info(f"Successfully processed order from file: {save_path}")


        # Return the file response
        return response

    except Exception as e:
        logging.error(f"Error processing order from file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process the order: {str(e)}"
        )


@router.post("/review-order/")
async def process_review_order(file: UploadFile = File(...)):
    """
    Process the uploaded CSV file, generate the order review, and return a downloadable CSV with the results.
    """
    try:
        logging.info(f"Received order file: {file.filename}")

        # Save the uploaded CSV file
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        logging.info(f"File saved at: {save_path}")

        # Read CSV file into DataFrame
        df = pd.read_csv(save_path)

        # Process the order using the provided CSV file
        review_df = review_order(df=df)

        logging.info(f"Successfully processed review from file: {save_path}")

        # Return the file response
        # Save the DataFrame to a uniquely named CSV file
        csv_file_path = get_unique_filename(DOWNLOAD_DIR, "review")
        review_df.to_csv(csv_file_path, index=False)
        logging.info(f"CSV file saved at: {csv_file_path}")
        
        # Delete the uploaded file after processing
        os.remove(save_path)
        logging.info(f"Uploaded file deleted: {save_path}")
        
        # Return the file response
        return FileResponse(
            path=csv_file_path,
            media_type="text/csv",
            filename=os.path.basename(csv_file_path)
        )

    except Exception as e:
        logging.error(f"Error processing review from file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to make review for order: {str(e)}"
        )

@router.get("/order-history/")
async def order_history(
    page_number: Optional[int] = 1, 
    page_size: Optional[int] = 10
):
    """
    Fetch order history with optional page_number and page_size.

    Args:
        page_number (int): Page number for pagination (default is 1).
        page_size (int): Number of records per page (default is 10).

    Returns:
        dict: Order history response.
    """
    try:
        logging.info("Fetching order history.")
        logging.info(f"Received parameters: page_number={page_number}, page_size={page_size}")
        
        # Call the function to fetch order history
        response = get_order_history(page_number=page_number, page_size=page_size)

        logging.info("Order history fetched successfully.")
        return response

    except Exception as e:
        logging.error(f"Error occurred while processing order history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed: {str(e)}"
        )
