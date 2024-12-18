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
INSURED_PROJECT/
│
├── extraction/                   # Core extraction logic
│   └── config.py                 # Configuration file for data extraction
│   └── extract_functions.py      # Helper functions for data extraction
│   └── extract.py                # Extract individual pdf data
│   └── extract_all.py            # Extract all pdfs data in batch
│   └── evaluate.py               # Script to match extracted jsons with ground truth
│   └── truth_json                # Directory containing ground truth jsons
│
├── invoice/                      # Invoice generation and evaluation
│   ├── config_invoice.py         # Configuration file for invoice management
│   ├── invoice_functions.py      # Helper functions for invoice processing
│   ├── generate_invoice.py       # Generate individual invoice
│   ├── generate_all.py           # Generate all invoices in batch
│   ├── evaluate_invoice.py       # Script to evaluate a single invoice
│   ├── evaluate_all.py           # Evaluate all invoices
│   └── Data_Invoices_Manual.csv  # Data handling for invoices
│
├── process_raw_data/             # Preprocessing and cleaning raw PDF data
│   ├── classify_pdfs.py          # Classify PDFs for processing
│   ├── match_files.py            # Match files for extraction
│   └── remove_unwanted.py        # Remove unwanted data or files
│
├── raw_data/                     # Raw data input directory (drive data to be downloaded here)
│
├── endpoint/                     # FastAPI endpoint for file uploads and processing
│   ├── config.py                 # Configuration file for FastAPI
│   ├── extract_functions.py      # Functions for data extraction
│   ├── extract.py                # Script for data extraction
│   ├── invoice_functions.py      # Functions to handle invoice creation
│   ├── make_invoice.py           # Script to generate invoices
│   └── fast_api.py               # FastAPI server setup
│   
├── .env                          # Environment variables file
├── .gitignore                    # Git ignore file for version control
└── requirements.txt              # File containing list of required packages


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
  --> Make a .env file and store OPENAI_API_KEY="YOUR-OPENAI-API-KEY-HERE" in it.
  --> Make a virtual environment with python and run "pip install -r requirements.txt" in command line.
all_pdf_mesurement_reports directory has all the pdf files to be processed.

### Download Raw Measrement Data
  --> Download raw measrement data from drive (https://drive.google.com/drive/folders/0AItoAT6ynZkcUk9PVA) to a directory named "raw_data\insured_roofs_drive_data" 

### Process Raw Data
Run process_raw_data\classify_pdfs.py to clean the data.
  --> It will save the needed pdf files in "raw_data\all_pdf_measurement_reports" directory.
  --> It will save the unwanted pdf files (less than 6 pages in this case) in "raw_data\waste_reports" directory.
  --> It will save the unprocessed (locked) pdf files in "raw_data\unprocessed" directory.

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
Run invoice\generate_all.py to generate invoices for all extracted measurement jsons in csv format.
Run invoice\evaluate_all.py to evaluate invoices with grouth truth stored in "invoice\Data_Invoices_Manual.csv"
Run invoice\combine_evaluations.py to make a combined evaluation report in csv format stored in "invoice\combined_evaluation" directory.

### Optional
  --> Run invoice\generate_invoice.py to generate individual invoices.

### Optional
  --> Use "compare_invoice_and_manual_quantities()" in invoice\evaluate_invoice.py to match individual extracted json with ground truth in "extraction\truth_json" directory.

## Endpoint
Run endpoint\fast_api.py to activate Invoice-Generation-API endpoint.
  --> Go to "{localhost}/docs" and test the endpoint by uploading measurement report pdf and enter the required inputs.


