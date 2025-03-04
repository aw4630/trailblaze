import requests
import json
import sys

def send_test_request(message, location=None):
    """Send a test request to the server."""
    url = "http://localhost:5000/api/chat"
    
    # Build the request data
    data = {
        "message": message
    }
    
    # Add location if provided
    if location:
        data["location"] = location
    
    # Print the request data
    print(f"Sending request to {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    # Send the request
    try:
        # Print the raw request for debugging
        print(f"Raw request data: {data}")
        
        response = requests.post(url, json=data)
        
        # Print the response status code
        print(f"Response status code: {response.status_code}")
        
        # Print the response content
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"Response: {json.dumps(response_json, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response (not JSON): {response.text}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error sending request: {str(e)}")

if __name__ == "__main__":
    # Default message and location
    message = "I want to see a Broadway show tonight"
    location = {
        "latitude": 40.758896,
        "longitude": -73.985130,
        "address": "Times Square, New York, NY"
    }
    
    # Use command line arguments if provided
    if len(sys.argv) > 1:
        message = sys.argv[1]
    
    # Print the location object for debugging
    print(f"Location object: {location}")
    
    # Send the request
    send_test_request(message, location) 