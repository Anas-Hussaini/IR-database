import os

# Variables for user inputs
directory1 = "all_pdf_mesurement_reports"
directory2 = "raw_data/all_pdf_measurement_reports"

def list_files(directory):
    """
    List all files in the given directory.
    """
    return set(os.listdir(directory))

def compare_directories(dir1, dir2):
    """
    Compare files between two directories and print details.
    """
    # Get filenames from both directories
    files_dir1 = list_files(dir1)
    files_dir2 = list_files(dir2)

    # Print filenames from both directories
    print(f"Files in Directory 1 ({dir1}):")
    for file in sorted(files_dir1):
        print(f"  {file}")

    print(f"\nFiles in Directory 2 ({dir2}):")
    for file in sorted(files_dir2):
        print(f"  {file}")

    # Find common and extra files
    common_files = files_dir1 & files_dir2
    extra_in_dir1 = files_dir1 - files_dir2
    extra_in_dir2 = files_dir2 - files_dir1

    # Print results
    print("\nCommon Files:")
    for file in sorted(common_files):
        print(f"  {file}")

    print("\nExtra Files in Directory 1:")
    for file in sorted(extra_in_dir1):
        print(f"  {file}")

    print("\nExtra Files in Directory 2:")
    for file in sorted(extra_in_dir2):
        print(f"  {file}")

if __name__ == "__main__":
    # Check if paths are valid
    if not os.path.isdir(directory1):
        print(f"Error: {directory1} is not a valid directory.")
    elif not os.path.isdir(directory2):
        print(f"Error: {directory2} is not a valid directory.")
    else:
        # Compare the two directories
        compare_directories(directory1, directory2)
