import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import re
import json
from openai import OpenAI
# import config
# import importlib
# importlib.reload(config)
from .config import dotenv_path, prompt

load_dotenv(dotenv_path, override=True)

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Set OpenAI
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
            # text=text.strip()
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def get_json_from_openai(text,model):
    """
    Sends extracted text to OpenAI and retrieves information in JSON format.
    """
    try:
        base_prompt = f"""
        You are an AI expert in document analysis and data extraction. I will provide a document, and your task is to extract relevant information and present it in a **clean JSON format**. Ensure all fields are accurately filled based on the data provided. If a field is not available in the document, mark it as `null`.

        ### Extract the following data in JSON format:
        {prompt}
        Text:
        {text}
        """
        response = client.chat.completions.create(
            model=model,  # You can use "gpt-3.5-turbo" if needed
            messages=[{"role": "system", "content": "You are a helpful assistant for extracting knowledge in JSON format."},
                      {"role": "user", "content": base_prompt}],
            temperature=0
        )
        # Extract the content of the assistant's response
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error communicating with OpenAI: {e}")
        return None

def json_string_to_json(json_output):
    """
    Processes a JSON string, extracts the JSON data if embedded within other text,
    and returns it.

    Args:
        json_output (str): The JSON data or text containing JSON.

    Returns:
        dict or None: The parsed JSON object if successful, or None if no valid JSON is found.
    """
    if not json_output:
        print("No JSON output provided.")
        return None

    # Try to extract the JSON part using regex
    json_match = re.search(r'({.*})', json_output, re.DOTALL)
    if json_match:
        json_string = json_match.group(1)  # Extract the JSON part

        try:
            # Parse the extracted JSON string
            json_object = json.loads(json_string)
            return json_object
        except json.JSONDecodeError:
            print("Failed to parse JSON string.")
    else:
        print("No JSON data found in the output.")

    return None

# Define a helper function to convert length strings to feet
def convert_to_feet(length):
    if length is None:  # Handle None case
        return 0
    
    feet = 0
    inches = 0
    
    # Normalize the input (strip spaces and collapse multiple spaces into one)
    length = length.strip() if length else ''
    length = re.sub(r'\s+', ' ', length)  # Replace multiple spaces with a single space
    
    # Handle cases like 'null', 'none', 'None', 'Null', etc., by returning 0
    if length.lower() in ['null', 'none', 'None', 'Null']:
        return 0
    
    # Handle case where only inches are mentioned (e.g., '0in' or '0 in')
    if 'in' in length and len(length) <= 3:  # '0in' or '0 in'
        return 0
    
    # Handle case where both "ft" and "in" are mentioned together (e.g., "10ft 3in" or "10 ft 3 in")
    if 'ft' in length and 'in' in length:
        parts = length.split(" ")
        for part in parts:
            if "ft" in part:
                feet = int(part.replace("ft", "").strip()) if part.replace("ft", "").strip() else 0  # Safely extract feet
            elif "in" in part:
                inches = int(part.replace("in", "").strip()) if part.replace("in", "").strip() else 0  # Safely extract inches
    
    # Handle case where only "ft" is mentioned (e.g., "10ft" or "10 ft")
    elif 'ft' in length:
        feet = int(length.replace("ft", "").strip()) if length.replace("ft", "").strip() else 0  # Safely extract feet
    
    # Handle case where only "in" is mentioned (e.g., "102 in")
    elif 'in' in length:
        inches = int(length.replace("in", "").strip()) if length.replace("in", "").strip() else 0  # Safely extract inches
    
    # If neither 'ft' nor 'in' is found, assume the value is in feet
    elif length.isdigit():
        feet = float(length)  # Treat as feet if no unit is provided
    
    # Convert inches to feet and return total feet
    total_feet = feet + (inches / 12)  # Convert inches to feet and add to total
    
    # If the value is zero, return 0 as an integer
    if total_feet == 0:
        return 0
    
    return round(total_feet, 2)
