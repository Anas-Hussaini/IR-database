import json
import os
from .extract_functions import convert_to_feet

def compare_json(json1, json2, path="root"):
    """
    Compare two JSON objects and find differences.

    Args:
        json1 (dict): The first JSON object.
        json2 (dict): The second JSON object.
        path (str): Current key path being compared.

    Returns:
        list: A list of differences as strings.
    """
    differences = []

    # Check keys in json1
    for key in json1:
        if key not in json2:
            differences.append(f"Key '{key}' missing in JSON 2 at path: {path}")
        else:
            # Recursive comparison if value is a dict
            if isinstance(json1[key], dict) and isinstance(json2[key], dict):
                differences.extend(compare_json(json1[key], json2[key], f"{path}.{key}"))
            # Check for mismatched values
            elif json1[key] != json2[key]:
                differences.append(
                    f"Mismatch at path: {path}.{key} | JSON 1: {json1[key]} != JSON 2: {json2[key]}"
                )

    # Check for extra keys in json2
    for key in json2:
        if key not in json1:
            differences.append(f"Key '{key}' missing in JSON 1 at path: {path}")

    return differences

def process_directories(dir1, dir2):
    """
    Compare all JSON files in two directories.

    Args:
        dir1 (str): Path to the first directory.
        dir2 (str): Path to the second directory.

    Returns:
        None: Prints the results.
    """
    mismatched_files = []
    matched_files = 0
    total_files = 0

    dir1_files = set(os.listdir(dir1))
    dir2_files = set(os.listdir(dir2))

    # Identify common and uncommon files
    common_files = dir1_files.intersection(dir2_files)
    dir1_only = dir1_files - dir2_files
    dir2_only = dir2_files - dir1_files

    for filename in common_files:
        if filename.endswith('.json'):
            total_files += 1

            # Load JSON files
            with open(os.path.join(dir1, filename), 'r') as file1, open(os.path.join(dir2, filename), 'r') as file2:
                json1 = json.load(file1)
                json2 = json.load(file2)

                # Convert values in json2 to feet where applicable
                for key, value in json2.items():
                    if key not in ['Address', 'TotalRoofArea_sqft']:
                        json2[key] = convert_to_feet(value)

                # Compare the JSONs
                differences = compare_json(json1, json2)

                if differences:
                    mismatched_files.append((filename, differences, json1, json2))
                else:
                    matched_files += 1

    # Calculate percentage match
    if total_files > 0:
        match_percentage = (matched_files / total_files) * 100
    else:
        match_percentage = 0

    if dir1_only:
        print("\nFiles only in Directory 1:")
        for file in dir1_only:
            print(f"- {file}")

    if dir2_only:
        print("\nFiles only in Directory 2:")
        for file in dir2_only:
            print(f"- {file}")

    for filename, diffs, json1, json2 in mismatched_files:
        print(f"\nDifferences in file: {filename}")
        print("JSON 1 Content:")
        print(json.dumps(json1, indent=4))
        print("JSON 2 Content:")
        print(json.dumps(json2, indent=4))
        for diff in diffs:
            print(f"- {diff}")
    
    # Print results
    print(f"Total JSON files compared: {total_files}")
    print(f"Files with mismatches: {len(mismatched_files)}")
    print(f"Match Percentage: {match_percentage:.2f}%")

# # Usage
# dir1 = "extraction/extraction_json"
# # dir1 = "extraction_json"
# # dir2 = "extraction/truth_json"
# # dir2 = "truth_json"
# dir2 = "extraction/false_json"
# # dir2 = "false_json"

# process_directories(dir1, dir2)
