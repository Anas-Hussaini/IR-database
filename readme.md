# INSURED PROJECT

## Table of Contents

1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [Features](#features)
4. [Usage](#usage)

---

## Project Overview

The **INSURED PROJECT** provides a robust pipeline for processing raw PDF data, extracting information, evaluating results, and managing invoices. The project combines modular components for:
- PDF classification and extraction
- Invoice generation
- Raw data management and cleanup
- Evaluating extraction accuracy against ground truth data

The project is designed for scalability, modularity, and ease of integration.

---

## Directory Structure

```plaintext
INSURED_ROOFS_PROJECT/
├── .gitignore  # Specifies files and directories to be ignored by Git
├── __init__.py  # Initializes the Python package
│
├── app/  # Core application module
│   ├── __init__.py  # Initializes the app package
│   ├── config.py  # Configuration settings for the application
│   ├── database.py  # Database connection and ORM models
│   ├── formula/  # Module for formulas or calculations
│   │   ├── __init__.py  # Initializes the formula package
│   │   ├── crud.py  # CRUD operations for formula-related data
│   │   └── routes.py  # API routes for formula-related endpoints
│   │
│   ├── invoice/  # Module for invoice management
│   │   ├── __init__.py  # Initializes the invoice package
│   │   ├── crud_read_only.py  # Read-only operations for invoice-related data
│   │   ├── endpoint_functions.py  # Functions for invoice API endpoints
│   │   ├── make_invoice.py  # Script to generate invoices
│   │   ├── routes.py  # API routes for invoice-related endpoints
│   │   ├── saved_invoices/  # Directory to store generated invoices
│   │   │
│   │   └── uploaded_files/  # Directory to handle uploaded files for invoices
│   │
│   ├── main.py  # Main application entry point
│   ├── models.py  # Database models definition
│   ├── product/  # Module for product management
│   │   ├── __init__.py  # Initializes the product package
│   │   ├── crud.py  # CRUD operations for product-related data
│   │   └── routes.py  # API routes for product-related endpoints
│   │
│   ├── schemas.py  # Pydantic models or data schemas
│   ├── supplier/  # Module for supplier management
│   │   ├── __init__.py  # Initializes the supplier package
│   │   ├── crud.py  # CRUD operations for supplier-related data
│   │   └── routes.py  # API routes for supplier-related endpoints
│   │
│   └── wastage/  # Module for managing wastage data
│       ├── __init__.py  # Initializes the wastage package
│       ├── crud.py  # CRUD operations for wastage-related data
│       └── routes.py  # API routes for wastage-related endpoints
│
├── config.py  # General project configuration file
├── extraction/  # Module for data extraction
│   ├── __init__.py  # Initializes the extraction package
│   ├── config.py  # Configuration file for data extraction settings
│   ├── evaluate.py  # Script to evaluate extracted data
│   ├── extract.py  # Script to extract individual PDF data
│   ├── extract_all.py  # Script to extract all PDF data in batch
│   ├── extract_functions.py  # Helper functions for data extraction
│   └── truth_json/  # Directory containing ground truth JSON files
│
├── invoice/  # Module for invoice management
│   ├── __init__.py  # Initializes the invoice package
│   ├── config_invoice.py  # Configuration file for invoice management
│   ├── generate_all.py  # Script to generate all invoices in batch
│   └── invoice_functions.py  # Helper functions for invoice processing
│
├── process_raw_data/  # Module for preprocessing and cleaning raw PDF data
│   ├── classify_pdfs.py  # Script to classify PDFs for processing
│   ├── match_files.py  # Script to match files for extraction
│   └── remove_unwanted_files.py  # Script to remove unwanted files or data
│
├── readme.md  # Project documentation file
└── requirements.txt  # List of required packages for the project


```
---

## Features

- Extraction
- Invoice Generation
- Evalutaion
- Endpoint

---

# Usage #

pip install -r requirements.txt

### Evaluation
  1. Make a .env file and store OPENAI_API_KEY="YOUR-OPENAI-API-KEY-HERE" and "DB_PASSWORD="YOUR-POSTGRES-DATABASE-PASSWORD" in it.
  2. Make a virtual environment with python and run "pip install -r requirements.txt" in command line.
all_pdf_mesurement_reports directory has all the pdf files to be processed.

### Download Raw Measurement Data
  - Download raw measrement data from drive (https://drive.google.com/drive/folders/0AItoAT6ynZkcUk9PVA) to a directory named "raw_data\insured_roofs_drive_data" 

### Process Raw Data
Run process_raw_data\classify_pdfs.py to clean the data.
  - It will save the needed pdf files in "raw_data\all_pdf_measurement_reports" directory.
  - It will save the unwanted pdf files (less than 6 pages in this case) in "raw_data\waste_reports" directory.
  - It will save the unprocessed (locked) pdf files in "raw_data\unprocessed" directory.

### Optional
  --> Run process_raw_data\match_files.py to compare files between two different directories.

### Optional
  --> Run process_raw_data\remove_unwanted_files.py to remove unwanted files in a directory.

## Extraction
Run extraction\extract_all.py to extract measurement data in json format from all pdfs in "raw_data\all_pdf_measurement_reports" directory.

### Optional
  --> Use "process_pdf()" in extraction\extract.py to extract individual pdf data.

### Optional
  --> Run extraction\evaluate.py to match extracted jsons with ground truth in "extraction\truth_json" directory.

## Invoice Generation
- Run invoice\generate_all.py to generate invoices for all extracted measurement jsons in csv format.
- Run invoice\evaluate_all.py to evaluate invoices with grouth truth stored in "invoice\Data_Invoices_Manual.csv"
- Run invoice\combine_evaluations.py to make a combined evaluation report in csv format stored in "invoice\combined_evaluation" directory.

### Optional
  --> Run invoice\generate_invoice.py to generate individual invoices.

### Optional
  --> Use "compare_invoice_and_manual_quantities()" in invoice\evaluate_invoice.py to match individual extracted json with ground truth in "extraction\truth_json" directory.




## Running the Service

To run the service, navigate to the project root directory and use one of the following commands:

1. Using Uvicorn:
  ```bash
  uvicorn app.main:app --reload
  ```

  - Go to "localhost:8000/docs" and test the endpoint enter the required inputs.