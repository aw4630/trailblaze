#!/usr/bin/env python3

"""
Validate Modified Itinerary Script

This script allows you to:
1. Load an existing itinerary result JSON file
2. Modify the itinerary directly
3. Re-validate it without regenerating from scratch
4. Save the validated results

Usage:
    python validate_modified_itinerary.py --input <input_file> --output <output_file>
"""

import argparse
import json
import logging
import sys
import os
from typing import Dict, Any

# Import the itinerary validator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_itinerary_validator import ItineraryVerifier

def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        sys.exit(1)

def save_json(data: Dict[str, Any], file_path: str) -> None:
    """Save JSON data to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Results saved to {file_path}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        sys.exit(1)

def modify_itinerary(itinerary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Modify the itinerary as needed.
    This is where you can make programmatic changes to the itinerary.
    """
    # Example modifications (uncomment and customize as needed):
    
    # Change itinerary name
    # itinerary["name"] = "Modified Historical Manhattan Tour"
    
    # Adjust event times
    # if "events" in itinerary and len(itinerary["events"]) > 0:
    #     # Adjust the first event to end 30 minutes earlier
    #     event = itinerary["events"][0]
    #     end_time = event["end_time"]
    #     # Parse the time, subtract 30 minutes, and format back
    #     from datetime import datetime, timedelta
    #     dt = datetime.fromisoformat(end_time)
    #     new_dt = dt - timedelta(minutes=30)
    #     event["end_time"] = new_dt.isoformat()
    
    # Add a new venue
    # if "venues" in itinerary:
    #     itinerary["venues"].append({
    #         "name": "New Museum",
    #         "address": "123 Example St, New York, NY 10001",
    #         "latitude": 40.7128,
    #         "longitude": -74.0060,
    #         "opening_hours": "09:00-17:00"
    #     })
    
    # Print the modified itinerary for verification
    print("Modified itinerary:")
    print(json.dumps(itinerary, indent=2))
    
    return itinerary

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="Validate Modified Itinerary Script")
    parser.add_argument("--input", required=True, help="Input JSON itinerary file")
    parser.add_argument("--output", required=True, help="Output JSON result file")
    parser.add_argument("--use-real-api", action="store_true", help="Use real API instead of mock data")
    parser.add_argument("--skip-modify", action="store_true", help="Skip the modification step")
    parser.add_argument("--fix-issues", action="store_true", help="Attempt to fix any issues found")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('validate_modified.log')
        ]
    )
    
    # Load the itinerary data
    result_data = load_json(args.input)
    print(f"Loaded itinerary data from {args.input}")
    
    # Extract the itinerary from the result
    if "final_itinerary" in result_data:
        itinerary = result_data["final_itinerary"]
    elif "itinerary" in result_data:
        itinerary = result_data["itinerary"]
    else:
        print("Could not find itinerary in the input file")
        sys.exit(1)
    
    # Modify the itinerary (unless skipped)
    if not args.skip_modify:
        itinerary = modify_itinerary(itinerary)
    
    # Create a verifier
    verifier = ItineraryVerifier(force_real_api=args.use_real_api)
    
    # Validate the itinerary
    print("Validating itinerary...")
    verification_result = verifier.verify_itinerary(itinerary)
    
    # Fix issues if requested
    if args.fix_issues and not verification_result.get("is_feasible", False):
        print("Attempting to fix issues...")
        itinerary = verifier.fix_itinerary(itinerary, verification_result)
        # Re-validate after fixing
        verification_result = verifier.verify_itinerary(itinerary)
    
    # Create the result object
    result = {
        "final_itinerary": itinerary,
        "verification": verification_result,
        "is_valid": verification_result.get("is_feasible", False)
    }
    
    # Save the results
    save_json(result, args.output)
    
    # Print summary
    print("\nItinerary Validation Summary:")
    print(f"Valid: {result.get('is_valid', False)}")
    
    issues = verification_result.get("all_issues", [])
    print(f"Issues: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")

if __name__ == "__main__":
    main() 