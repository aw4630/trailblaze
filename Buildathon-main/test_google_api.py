import requests
import json
import os
import sys
from config.config import GOOGLE_SHOWTIMES_API_KEY

def test_google_places_api(query="Broadway shows", location=(40.758896, -73.985130), format_type="circle"):
    """
    Test the Google Places API with different request formats.
    
    Args:
        query: The search query
        location: Tuple of (latitude, longitude)
        format_type: The format type to use ("circle", "rectangle", or "none")
    """
    print(f"Testing Google Places API with format: {format_type}")
    print(f"Query: {query}")
    print(f"Location: {location}")
    
    # Set up the API endpoint and headers
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_SHOWTIMES_API_KEY,
        "X-Goog-FieldMask": "*"  # Request all available fields
    }
    
    # Build the payload based on the format type
    payload = {
        "textQuery": query,
        "maxResultCount": 10
    }
    
    if format_type == "circle" and location:
        lat, lng = location
        payload["locationBias"] = {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lng
                },
                "radius": 5000.0
            }
        }
    elif format_type == "rectangle" and location:
        lat, lng = location
        # Create a rectangle around the location
        payload["locationBias"] = {
            "rectangle": {
                "low": {
                    "latitude": lat - 0.05,
                    "longitude": lng - 0.05
                },
                "high": {
                    "latitude": lat + 0.05,
                    "longitude": lng + 0.05
                }
            }
        }
    
    # Print the request payload
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    print(f"Request headers: {headers}")
    
    # Send the request
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # Print the response status code
        print(f"Response status code: {response.status_code}")
        
        # Print the response content
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"Response: {json.dumps(response_json, indent=2)}")
                
                # Print the number of places found
                places = response_json.get("places", [])
                print(f"Found {len(places)} places")
                
                # Print the first place name if available
                if places:
                    first_place = places[0]
                    name = first_place.get("displayName", {}).get("text", "Unknown")
                    print(f"First place: {name}")
                
            except json.JSONDecodeError:
                print(f"Response (not JSON): {response.text}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error sending request: {str(e)}")

if __name__ == "__main__":
    # Parse command line arguments
    format_type = "circle"  # Default format
    query = "Broadway shows"  # Default query
    
    if len(sys.argv) > 1:
        format_type = sys.argv[1]
    
    if len(sys.argv) > 2:
        query = sys.argv[2]
    
    # Run the test
    test_google_places_api(query=query, format_type=format_type) 