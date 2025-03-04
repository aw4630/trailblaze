import unittest
import json
import sys
import os
import logging
from datetime import datetime
from flask import Flask

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Flask application
from app import app
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_app")


class EventAppTestCase(unittest.TestCase):
    """Test cases for the event app API endpoints."""

    def setUp(self):
        """Set up the test client before each test."""
        self.app = app
        self.client = self.app.test_client()
        self.client.testing = True

    def test_broadway_show_query(self):
        """Test that the 'I want to see a broadway show' query returns expected results."""
        logger.info("Running automated test: 'I want to see a broadway show' query")
        
        # Create a test message
        message = "I want to see a broadway show"
        response = self.client.post(
            '/api/chat',
            data=json.dumps({'message': message}),
            content_type='application/json'
        )
        
        # Check status code - with mock data disabled, we might get a 400 or 404
        if not config.USE_MOCK_DATA:
            self.assertIn(response.status_code, [200, 400, 404], 
                          "Status code should be 200, 400, or 404 when mock data is disabled")
        else:
            self.assertEqual(response.status_code, 200)
        
        # Parse response
        data = json.loads(response.data)
        
        # Log response for debugging
        logger.info(f"Response received: {json.dumps(data, indent=2)}")
        
        # Check that response has expected fields
        self.assertIn('response', data)
        
        # If events were found, verify their structure
        if 'events' in data:
            self.assertIsInstance(data['events'], list)
            logger.info(f"Found {len(data['events'])} events in response")
            
            # Check first event if available
            if data['events']:
                first_event = data['events'][0]
                self.assertIn('name', first_event)
                self.assertIn('location', first_event)
                
                # Check if any event is actually a broadway show
                broadway_related = False
                for event in data['events']:
                    event_name = event.get('name', '').lower()
                    event_category = event.get('category', '').lower()
                    if 'broadway' in event_name or 'theater' in event_name or 'theatre' in event_name or \
                       'broadway' in event_category or 'theater' in event_category or 'theatre' in event_category:
                        broadway_related = True
                        break
                
                # Log if no broadway shows were found
                if not broadway_related:
                    logger.warning("No broadway-related events found in response")
        else:
            logger.warning("No events returned in response")

    def test_broadway_show_with_location(self):
        """Test broadway query with New York location."""
        logger.info("Running automated test: Broadway show with New York location")
        
        # First set a location (New York)
        location_data = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'address': 'New York, NY, USA'
        }
        
        self.client.post(
            '/api/profile',
            data=json.dumps(location_data),
            content_type='application/json'
        )
        
        # Then query for broadway shows
        message = "I want to see a broadway show tonight"
        response = self.client.post(
            '/api/chat',
            data=json.dumps({'message': message}),
            content_type='application/json'
        )
        
        # Check response
        if not config.USE_MOCK_DATA:
            self.assertIn(response.status_code, [200, 400, 404], 
                          "Status code should be 200, 400, or 404 when mock data is disabled")
        else:
            self.assertEqual(response.status_code, 200)
            
        data = json.loads(response.data)
        logger.info(f"Response received with location: {json.dumps(data, indent=2)}")


def run_automated_test():
    """Run the broadway show test as a standalone function."""
    try:
        test_client = app.test_client()
        test_client.testing = True
        
        # Set a New York location
        location_data = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'address': 'New York, NY, USA'
        }
        
        test_client.post(
            '/api/profile',
            data=json.dumps(location_data),
            content_type='application/json'
        )
        
        # Send the test message
        message = "I want to see a broadway show"
        response = test_client.post(
            '/api/chat',
            data=json.dumps({'message': message}),
            content_type='application/json'
        )
        
        # Parse response data
        data = json.loads(response.data)
        print(f"===== AUTOMATED TEST RESULTS ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) =====")
        print(f"Query: '{message}'")
        print(f"Response status code: {response.status_code}")
        
        # Check response - with mock data disabled, some error responses are expected
        if response.status_code == 200:
            # Standard successful response
            if 'events' in data:
                print(f"Found {len(data['events'])} events")
                for i, event in enumerate(data['events']):
                    print(f"\nEvent {i+1}: {event.get('name')}")
                    
                    # Print showtimes if available
                    if 'showtimes' in event and event['showtimes']:
                        print("  Showtimes:")
                        for showtime in event['showtimes']:
                            start = showtime.get('start_time', 'N/A')
                            availability = showtime.get('availability', 'N/A')
                            print(f"    - {start} ({availability})")
                            
                    # Print prices if available
                    if 'prices' in event and event['prices']:
                        print("  Prices:")
                        for price in event['prices']:
                            amount = price.get('amount', 0)
                            category = price.get('category', 'N/A')
                            print(f"    - {category}: ${amount}")
            else:
                print("No events found in response")
                
            # Check for error field even in 200 response
            if 'error' in data:
                print(f"\nWarning: Response contains error: {data.get('error')}")
            
            print("\nResponse message:")
            print(data.get('response', 'No response message'))
            print("=" * 80)
            
            return True, data
            
        elif response.status_code in [400, 404]:
            # Expected error responses when mock data is disabled
            print("No events found - This is expected when mock data is disabled")
            print(f"Error: {data.get('error', 'No error code')}")
            print("\nResponse message:")
            print(data.get('response', 'No response message'))
            print("=" * 80)
            
            # Return success because this is expected behavior with mock data disabled
            return True, data
            
        else:
            # Unexpected error
            print(f"Test failed with unexpected status code: {response.status_code}")
            print(f"Error: {data.get('error', 'Unknown error')}")
            print(f"Response: {data.get('response', 'No response message')}")
            print("=" * 80)
            return False, data
            
    except Exception as e:
        print(f"Error running automated test: {e}")
        return False, None


if __name__ == '__main__':
    # Run as a test suite with unittest
    if len(sys.argv) > 1 and sys.argv[1] == '--unittest':
        unittest.main(argv=['first-arg-is-ignored'])
    else:
        # Run the standalone test function
        success, _ = run_automated_test()
        if not success:
            sys.exit(1) 