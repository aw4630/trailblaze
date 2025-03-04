#!/usr/bin/env python
"""
Test script for verifying Google Places API configuration.
This script helps diagnose API connection issues independent of the main application.
"""

import os
import sys
import json
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Your API key
API_KEY = "AIzaSyArWxtJ37sM3qBogEo9pG-e4Omv3gDKttw"

def print_colored(text, color):
    """Print colored text to the console."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def test_api_endpoint(name, url):
    """Test an API endpoint and return the response."""
    print_colored(f"Testing {name}...", "blue")
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Print full response for debugging
        print_colored("Raw Response:", "yellow")
        print(json.dumps(data, indent=2))
        
        if response.status_code != 200:
            print_colored(f"❌ {name} failed with HTTP status: {response.status_code}", "red")
            return False
            
        if data.get("status") == "REQUEST_DENIED":
            print_colored(f"❌ {name} failed with status: {data['status']}", "red")
            if "error_message" in data:
                print_colored(f"Error message: {data['error_message']}", "red")
            return False
        else:
            print_colored(f"✅ {name} successful with status: {data.get('status', 'OK')}", "green")
            return True
    except requests.exceptions.RequestException as e:
        print_colored(f"❌ {name} failed with error: {str(e)}", "red")
        return False
    except json.JSONDecodeError:
        print_colored(f"❌ {name} returned invalid JSON. Raw response:", "red")
        print(response.text)
        return False

def test_places_api_new_endpoint(name, url, method="GET", json_payload=None):
    """Test a Places API (New) endpoint."""
    print_colored(f"Testing {name}...", "blue")
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": API_KEY,
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress"
            }
            response = requests.post(url, json=json_payload, headers=headers, timeout=10)
        else:
            print_colored(f"Unsupported method: {method}", "red")
            return False
        
        # Try to parse the JSON response
        try:
            data = response.json()
            print_colored("Raw Response:", "yellow")
            print(json.dumps(data, indent=2))
            
            # Check for error field which is common in Places API (New) error responses
            if "error" in data:
                error_message = data["error"].get("message", "Unknown error")
                print_colored(f"❌ {name} failed with error: {error_message}", "red")
                return False
            else:
                print_colored(f"✅ {name} successful!", "green")
                return True
                
        except json.JSONDecodeError:
            print_colored(f"❌ {name} returned invalid JSON. Raw response:", "red")
            print(response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print_colored(f"❌ {name} failed with error: {str(e)}", "red")
        return False

def run_tests():
    """Run all API tests."""
    print_colored("=== STARTING DETAILED API TESTS ===", "blue")
    print_colored(f"Testing API key: {API_KEY[:8]}...{API_KEY[-5:]}", "blue")
    print()

    # Test both legacy Places API and Places API (New)
    print_colored("==== TESTING LEGACY PLACES API ENDPOINTS ====", "blue")
    print()

    # Test 1: Legacy Places Nearby API
    print_colored("TEST 1: Legacy Places Nearby API", "blue")
    test_api_endpoint(
        "Places Nearby API (Legacy)",
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670,151.1957&radius=500&type=restaurant&key={API_KEY}"
    )
    print()

    # Test 2: Legacy Places Details API
    print_colored("TEST 2: Legacy Places Details API", "blue")
    test_api_endpoint(
        "Places Details API (Legacy)",
        f"https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJ3S-JXmauEmsRUcIaWtf4MzE&fields=name,rating,formatted_phone_number&key={API_KEY}"
    )
    print()

    # Test 3: Legacy Places Text Search API
    print_colored("TEST 3: Legacy Places Text Search API", "blue")
    test_api_endpoint(
        "Places Text Search API (Legacy)",
        f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurants+in+Sydney&key={API_KEY}"
    )
    print()
    
    print_colored("==== TESTING PLACES API (NEW) ENDPOINTS ====", "blue")
    print()
    
    # Test 4: Places API (New) - Nearby Search (POST method)
    print_colored("TEST 4: Places API (New) - Nearby Search", "blue")
    nearby_payload = {
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": -33.8670,
                    "longitude": 151.1957
                },
                "radius": 500.0
            }
        },
        "maxResultCount": 10,
        "rankPreference": "DISTANCE"
    }
    test_places_api_new_endpoint(
        "Places Nearby Search API (New)",
        "https://places.googleapis.com/v1/places:searchNearby",
        method="POST",
        json_payload=nearby_payload
    )
    print()
    
    # Test 5: Places API (New) - Text Search (POST method)
    print_colored("TEST 5: Places API (New) - Text Search", "blue")
    text_search_payload = {
        "textQuery": "restaurants in Sydney",
        "maxResultCount": 10
    }
    test_places_api_new_endpoint(
        "Places Text Search API (New)",
        "https://places.googleapis.com/v1/places:searchText",
        method="POST",
        json_payload=text_search_payload
    )
    print()
    
    # Test 6: Places API (New) - Place Details (GET method)
    print_colored("TEST 6: Places API (New) - Place Details", "blue")
    test_places_api_new_endpoint(
        "Places Details API (New)",
        f"https://places.googleapis.com/v1/places/ChIJ3S-JXmauEmsRUcIaWtf4MzE?fields=displayName,formattedAddress&key={API_KEY}"
    )
    print()

    # Test 7: Geocoding API (for comparison)
    print_colored("TEST 7: Geocoding API", "blue")
    test_api_endpoint(
        "Geocoding API",
        f"https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key={API_KEY}"
    )
    print()

    print_colored("=== TESTS COMPLETED ===", "blue")
    print()
    print_colored("TROUBLESHOOTING RECOMMENDATIONS:", "blue")
    print_colored("1. Check if the Places API (New) is specifically enabled in Google Cloud Console", "blue")
    print_colored("2. Verify billing is set up for your project", "blue")
    print_colored("3. Check API key restrictions - they might be too limiting", "blue")
    print_colored("4. Look for any specific error messages in the test results above", "blue")
    print_colored("5. If only the legacy API or the new API works, you'll need to align your code with the working version", "blue")

if __name__ == "__main__":
    run_tests() 