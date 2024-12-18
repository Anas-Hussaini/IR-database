import os
import shutil
import time
import fitz  # PyMuPDF
from PyPDF2 import PdfReader
import config
import importlib
importlib.reload(config)
from config import INPUT_DIR,ALL_PDF_REPORTS_DIR,UNPROCESSED_DIR,WASTE_REPORTS_DIR,RETRIES,DELAY,ROOFR_KEYWORD,EAGLEVIEW_KEYWORDS,PAGE_THRESHOLD

# --- Setup Directories ---
def ensure_directories_exist():
    os.makedirs(ALL_PDF_REPORTS_DIR, exist_ok=True)
    os.makedirs(UNPROCESSED_DIR, exist_ok=True)
    os.makedirs(WASTE_REPORTS_DIR, exist_ok=True)

# --- Functionality 1: Classify PDFs and Move Large Reports ---
def classify_and_move_large_reports(input_dir, all_pdf_reports_dir, unprocessed_dir, waste_reports_dir):
    """
    Classifies PDF files based on the presence of specific text: Roofr or EagleView,
    and moves reports with 6 or more pages to a single directory.
    Smaller reports are moved to waste_reports_dir.
    """
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(".pdf"):
                file_path = os.path.join(root, filename)
                retries = RETRIES
                try:
                    while retries > 0:
                        try:
                            with fitz.open(file_path) as pdf:
                                found_company = None
                                for page_num in range(len(pdf)):
                                    text = pdf[page_num].get_text()
                                    if ROOFR_KEYWORD in text:
                                        found_company = "Roofr"
                                        break
                                    elif any(keyword in text for keyword in EAGLEVIEW_KEYWORDS):
                                        found_company = "EagleView"
                                        break

                                # Check page count
                                page_count = len(pdf)
                                if page_count >= PAGE_THRESHOLD:
                                    shutil.move(file_path, os.path.join(all_pdf_reports_dir, filename))
                                    print(f"Moved '{filename}' to {all_pdf_reports_dir} (Pages: {page_count}).")
                                else:
                                    shutil.move(file_path, os.path.join(waste_reports_dir, filename))
                                    print(f"Moved '{filename}' to {waste_reports_dir} (Pages: {page_count}).")
                            break

                        except PermissionError:
                            retries -= 1
                            print(f"File '{filename}' is locked. Retrying in {DELAY} seconds... ({retries} retries left)")
                            time.sleep(DELAY)
                        except Exception as e:
                            print(f"Error processing file '{filename}': {e}")
                            shutil.move(file_path, os.path.join(unprocessed_dir, filename))
                            print(f"Moved '{filename}' to Unprocessed directory.")
                            break
                except Exception as e:
                    print(f"Unexpected error for '{filename}': {e}")
                    shutil.move(file_path, os.path.join(unprocessed_dir, filename))
                    print(f"Moved '{filename}' to Unprocessed directory.")

# --- Functionality 2: Count Files in Directory ---
def count_files(directory):
    return len([f for f in os.listdir(directory) if f.endswith(".pdf")])

# --- Main Execution Flow ---
def main():
    ensure_directories_exist()

    # Step 1: Classify PDFs and Move Large Reports
    classify_and_move_large_reports(INPUT_DIR, ALL_PDF_REPORTS_DIR, UNPROCESSED_DIR, WASTE_REPORTS_DIR)

    # Step 2: Print Report Summary
    print("\n--- Report Summary ---")
    print(f"Total All PDF Measurement Reports: {count_files(ALL_PDF_REPORTS_DIR)}")
    print(f"Total Unprocessed reports: {count_files(UNPROCESSED_DIR)}")
    print(f"Total Waste reports: {count_files(WASTE_REPORTS_DIR)}")

if __name__ == "__main__":
    main()
