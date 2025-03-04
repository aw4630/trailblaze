#!/usr/bin/env python3

"""
Manual Itinerary Test Script

This script provides a function to generate an itinerary from JSON input.
It uses the IterativeGenerator from iterative_itinerary_generator.py.

Usage:
    from manual_itinerary_test import generate_from_json
    result = generate_from_json(your_json_data)
"""

import json
import logging
import sys
import os
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Example JSON data
ExampleJSON = {
    "routeName": "Custom Manhattan Tour",
    "distance": 3,
    "transportModes": ["Walk", "Public Transport"],
    "theme": "Historical Events",
    "budget": 150,
    "requirements": ["I want to visit the Statue of Liberty, Ellis Island, and the Tenement Museum."],
    "preferences": {
        "startTime": "09:00",
        "endTime": "17:00",
        "maxWalkingDistance": 2,
        "accessibility": "wheelchair"
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

# Import the itinerary generator module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from iterative_itinerary_generator import IterativeGenerator

def convert_to_api_format(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert user-friendly JSON format to the expected API format.
    
    Args:
        json_data: The user-friendly JSON data
        
    Returns:
        The converted API format JSON
    """
    api_format = {
        "routeName": json_data.get("routeName", "Custom Tour"),
        "measurementValue": json_data.get("distance", 3),
        "transportModes": json_data.get("transportModes", ["Walk"]),
        "theme": json_data.get("theme", "General"),
    }
    
    # Handle budget as an object with 'max' property
    if "budget" in json_data:
        if isinstance(json_data["budget"], dict) and "max" in json_data["budget"]:
            api_format["budget"] = json_data["budget"]
        else:
            api_format["budget"] = {"max": json_data["budget"]}
    else:
        api_format["budget"] = {"max": 100}
    
    # Combine requirements and preferences into customPrompt
    custom_prompt_parts = []
    
    if "requirements" in json_data and json_data["requirements"]:
        custom_prompt_parts.extend(json_data["requirements"])
    
    if "preferences" in json_data:
        prefs = json_data["preferences"]
        if "startTime" in prefs and "endTime" in prefs:
            custom_prompt_parts.append(f"Start at {prefs['startTime']} and end by {prefs['endTime']}.")
        
        if "maxWalkingDistance" in prefs:
            custom_prompt_parts.append(f"Maximum walking distance of {prefs['maxWalkingDistance']} miles.")
        
        if "accessibility" in prefs:
            custom_prompt_parts.append(f"The itinerary should be {prefs['accessibility']} accessible.")
    
    api_format["customPrompt"] = ", ".join(custom_prompt_parts)
    
    # Add location information if available
    if "location" in json_data:
        location = json_data["location"]
        if "city" in location:
            api_format["city"] = location["city"]
        if "neighborhood" in location:
            api_format["neighborhood"] = location["neighborhood"]
        if "coordinates" in location:
            api_format["coordinates"] = location["coordinates"]
    
    return api_format

def generate_from_json(json_data: Optional[Dict[str, Any]] = None, 
                      max_attempts: int = 3,
                      use_real_api: bool = True) -> Optional[Dict[str, Any]]:
    """
    Generate an itinerary from JSON input.
    
    Args:
        json_data: The JSON data to use for generation (uses ExampleJSON if None)
        max_attempts: Maximum number of attempts to generate a valid itinerary
        use_real_api: Whether to use real API calls or mock data
        
    Returns:
        The generated itinerary result or None if generation failed
    """
    try:
        # Use example JSON if none provided
        if json_data is None:
            json_data = ExampleJSON
            print("Using default example JSON data for itinerary generation")
        else:
            print("Using provided JSON data for itinerary generation")
        
        # Convert to API format
        api_format = convert_to_api_format(json_data)
        print("Converted to API format:")
        print(json.dumps(api_format, indent=2))
        
        # Generate itinerary
        print(f"Generating itinerary with max {max_attempts} attempts...")
        generator = IterativeGenerator(
            request_data=api_format,
            max_attempts=max_attempts,
            real_api=use_real_api
        )
        
        result = generator.run()
        
        # Print summary
        print("\nItinerary Generation Summary:")
        print(f"Valid: {result.get('is_valid', False)}")
        print(f"Total attempts: {result.get('total_attempts', 0)}")
        
        if result.get('verification') and result.get('verification').get('all_issues'):
            issues = result['verification']['all_issues']
            print(f"Issues: {len(issues)}")
            for issue in issues:
                print(f"  - {issue}")
        
        return result
    except Exception as e:
        logger.error(f"Error generating itinerary: {str(e)}", exc_info=True)
        print(f"Failed to generate itinerary: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    # You can call the function directly with custom JSON
    custom_json = {
        "routeName": "Quick NYC Tour",
        "distance": 2,
        "transportModes": ["Walk"],
        "theme": "Art and Culture",
        "budget": 200,
        "requirements": ["Include at least one art gallery"],
        "preferences": {
            "startTime": "10:00",
            "endTime": "16:00"
        },
        "location": {
            "city": "New York",
            "neighborhood": "SoHo"
        }
    }
    
    # Uncomment to use custom JSON
    # result = generate_from_json(custom_json)
    
    # Or use the default example
    result = generate_from_json()
    
    # Optionally save to file if needed
    with open("quick_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("Result saved to quick_result.json") 