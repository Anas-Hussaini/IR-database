import os

# Set directory path and file names to remove from directory
directory = "raw_data/all_pdf_measurement_reports"
files_to_remove = [
    "59900183.pdf",
    "60283228.pdf",
]

def remove_files(directory, files_to_remove):
    """
    Remove specified files from the given directory.
    """
    for file in files_to_remove:
        file_path = os.path.join(directory, file.strip())
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Removed: {file_path}")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":

    # Validate the directory
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
    elif not isinstance(files_to_remove, list):
        print("Error: Files to remove must be provided as a list.")
    else:
        # Remove specified files
        remove_files(directory, files_to_remove)
