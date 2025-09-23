#!/usr/bin/env python3
"""
Script to analyze JSON result files and output results in CSV format.
Processes all JSON files in a folder and displays results as CSV for Google Sheets.
Can filter between core problems (1-109) and non-core problems (110+).
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

def filter_data(data: Dict[str, float], core_only: bool) -> Dict[str, float]:
    """
    Filter data based on whether we want core or non-core problems.
    
    Args:
        data: Dictionary with string keys and float values
        core_only: If True, return only keys 1-109; if False, return only keys 110+
        
    Returns:
        Filtered dictionary
    """
    filtered_data = {}
    
    for key, value in data.items():
        try:
            key_num = int(key)
            if core_only and 1 <= key_num <= 109:
                filtered_data[key] = value
            elif not core_only and key_num >= 110:
                filtered_data[key] = value
        except ValueError:
            # Skip non-numeric keys
            continue
    
    return filtered_data

def calculate_metrics(data: Dict[str, float], core_only: bool) -> Tuple[float, float]:
    """
    Calculate the average score and pass rate from JSON data.
    
    Args:
        data: Dictionary with string keys and float values
        core_only: If True, analyze only core problems (1-109); if False, non-core (110+)
        
    Returns:
        Tuple of (average_score, pass_rate)
    """
    # Filter data based on core_only flag
    filtered_data = filter_data(data, core_only)
    values = list(filtered_data.values())
    
    if not values:
        return 0.0, 0.0
    
    # Calculate average
    average_score = sum(values) / len(values)
    
    # Calculate pass rate (proportion of values that equal 1.0)
    pass_count = sum(1 for value in values if value == 1.0)
    pass_rate = pass_count / len(values)
    
    return average_score, pass_rate

def process_json_files(folder_path: str, core_only: bool) -> List[Tuple[str, float, float]]:
    """
    Process all JSON files in the given folder and calculate metrics.
    
    Args:
        folder_path: Path to the folder containing JSON files
        core_only: If True, analyze only core problems (1-109); if False, non-core (110+)
        
    Returns:
        List of tuples (filename_without_extension, average_score, pass_rate)
    """
    results = []
    folder = Path(folder_path)
    
    # Find all JSON files
    json_files = list(folder.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {folder_path}")
        return results
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Calculate metrics with filtering
            avg_score, pass_rate = calculate_metrics(data, core_only)
            
            # Only include files that have data after filtering
            filtered_data = filter_data(data, core_only)
            if filtered_data:  # Only add if there's data after filtering
                filename_no_ext = json_file.stem
                results.append((filename_no_ext, avg_score, pass_rate))
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error processing {json_file}: {e}")
            continue
    
    return results

def display_csv_results(results: List[Tuple[str, float, float]], core_only: bool) -> None:
    """Display results in CSV format."""
    if not results:
        problem_type = "core" if core_only else "non-core"
        print(f"No {problem_type} results to display.")
        return
    
    # Sort alphabetically by filename
    sorted_results = sorted(results, key=lambda x: x[0])
    
    # Print CSV header
    print("Filename,Average Score,Pass Rate")
    
    # Print CSV data
    for filename, avg_score, pass_rate in sorted_results:
        print(f"{filename},{avg_score:.4f},{pass_rate:.4f}")

def main():
    """Main function to run the analysis."""
    # Get folder path
    folder_path = "results/whole_file" 
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    core_only = True
    
    print(f"\nProcessing JSON files in: {os.path.abspath(folder_path)}")
    total_files = len(list(Path(folder_path).glob('*.json')))
    print(f"Total JSON files found: {total_files}")
    print(f"Analyzing {'core' if core_only else 'complete'} problems")
    print(f"\n--- CSV OUTPUT (copy everything below this line) ---")
    
    # Process files and display results
    results = process_json_files(folder_path, core_only)
    display_csv_results(results, core_only)

if __name__ == "__main__":
    main()