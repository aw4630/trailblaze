#!/usr/bin/env python3

"""
Simple Example Script

This is a minimal example showing how to use the IterativeGenerator
with hardcoded JSON data directly.
"""

import sys
import os
import json
import logging

# Import the IterativeGenerator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from iterative_itinerary_generator import IterativeGenerator

# Setup basic logging
logging.basicConfig(level=logging.INFO)

# Hardcoded example JSON
example_json = {
    "route_name": "Simple Manhattan Tour",
    "distance": 2,
    "transportation_modes": ["Walk"],
    "theme": "Historical Sites",
    "budget": 100,
    "requirements": [
        "Include at least one museum"
    ],
    "preferences": {
        "start_time": "10:00",
        "end_time": "16:00"
    },
    "location": {
        "city": "New York",
        "neighborhood": "Manhattan",
        "coordinates": {
            "latitude": 40.7831,
            "longitude": -73.9712
        }
    }
}

def main():
    """Run a simple example of the itinerary generator"""
    print("Starting simple example with hardcoded JSON...")
    
    # Create the generator with the hardcoded JSON
    generator = IterativeGenerator(
        request_data=example_json,
        max_attempts=2,  # Limit to 2 attempts for this example
        real_api=False   # Use mock data by default
    )
    
    # Run the generator
    print("Running itinerary generator...")
    result = generator.run()
    
    # Save the result
    output_file = "simple_example_result.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Print summary
    print(f"\nResult saved to {output_file}")
    print(f"Valid: {result.get('is_valid', False)}")
    print(f"Total attempts: {result.get('total_attempts', 0)}")
    
    if result.get('verification') and result.get('verification').get('all_issues'):
        issues = result['verification']['all_issues']
        print(f"Issues: {len(issues)}")
        for issue in issues:
            print(f"  - {issue}")

if __name__ == "__main__":
    main() 