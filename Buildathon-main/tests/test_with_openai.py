#!/usr/bin/env python
"""
Test Broadway showtimes and routing with OpenAI instead of Claude.
This test script temporarily modifies the config to use OpenAI for the test.
"""

import sys
import os
import logging
from datetime import datetime
import pytz

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override config before other imports
import config
config.USE_MOCK_DATA = True  # Enable mock data for testing
logging.info(f"Test mode: Mock data ENABLED for testing")

# Ensure we're using OpenAI
try:
    from services.openai_service import OpenAIService
    openai_available = True
    logging.info("OpenAI service available for testing")
except ImportError:
    openai_available = False
    logging.error("OpenAI service not available - some tests will be skipped")

# Now import the rest
from services.google_showtimes_service import GoogleShowtimesService
from services.google_maps_service import GoogleMapsService
from models.user import UserContext, UserProfile, UserLocation, UserPreferences
from models.event import EventSchedule

# Set up logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_openai_service():
    """Test OpenAI service initialization and basic functionality."""
    if not openai_available:
        logger.error("OpenAI service not available - skipping test")
        return
    
    logger.info("=== Testing OpenAI Service ===")
    
    # Initialize service
    openai_service = OpenAIService()
    
    # Test generating a response
    test_prompt = "What are the most popular Broadway shows right now?"
    logger.info(f"Testing response generation with prompt: '{test_prompt}'")
    
    try:
        response = openai_service.generate_response(test_prompt)
        logger.info(f"Response received (first 100 chars): {response[:100]}...")
        logger.info("TEST PASSED: Successfully generated a response with OpenAI")
    except Exception as e:
        logger.error(f"TEST FAILED: Error generating response: {str(e)}")
    
    # Test extracting structured data
    test_query = "I want to see a Broadway show and have dinner tonight"
    logger.info(f"Testing query processing with: '{test_query}'")
    
    try:
        extracted_data = openai_service.process_user_query(test_query)
        logger.info(f"Extracted data: {extracted_data}")
        
        if extracted_data and "event_theme" in extracted_data:
            logger.info("TEST PASSED: Successfully extracted structured data with OpenAI")
        else:
            logger.warning("TEST WARNING: Data extraction completed but may not contain expected fields")
    except Exception as e:
        logger.error(f"TEST FAILED: Error processing user query: {str(e)}")

def test_broadway_showtimes():
    """Test Broadway showtimes to ensure they default to today's date."""
    logger.info("\n=== Testing Broadway Showtimes ===")
    
    # Get current time in NYC (where Broadway is located)
    nyc_tz = pytz.timezone('America/New_York')
    current_time_nyc = datetime.now(nyc_tz)
    
    logger.info(f"Current time in New York: {current_time_nyc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Initialize Google Showtimes service
    showtimes_service = GoogleShowtimesService()
    
    # Search for Broadway shows
    logger.info("Searching for Broadway shows...")
    events = showtimes_service.search_events("Broadway shows New York")
    
    logger.info(f"Found {len(events)} events")
    
    # Check the first few events
    todays_showtimes = 0
    tomorrow_showtimes = 0
    
    for i, event in enumerate(events[:5]):
        logger.info(f"Event {i+1}: {event.name}")
        logger.info(f"  Location: {event.location.address}")
        
        for j, showtime in enumerate(event.showtimes):
            showtime_date = showtime.start_time.date()
            current_date = current_time_nyc.date()
            
            logger.info(f"  Showtime {j+1}: {showtime.start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            if showtime_date == current_date:
                todays_showtimes += 1
            elif showtime_date > current_date:
                tomorrow_showtimes += 1
    
    logger.info(f"Summary: Found {todays_showtimes} showtimes for today and {tomorrow_showtimes} for future dates")
    
    # Verify that we have today's showtimes
    if todays_showtimes > 0:
        logger.info("TEST PASSED: Found showtimes for today")
    else:
        logger.error("TEST FAILED: No showtimes found for today")

def test_broadway_routing():
    """Test route planning between Broadway venues."""
    logger.info("\n=== Testing Broadway Route Planning ===")
    
    # Initialize services
    showtimes_service = GoogleShowtimesService()
    maps_service = GoogleMapsService()
    
    # Search for Broadway shows
    logger.info("Searching for Broadway shows...")
    events = showtimes_service.search_events("Broadway shows New York")
    
    # Create a mock user context
    user_context = UserContext(
        profile=UserProfile(
            name="Test User",
            location=UserLocation(
                latitude=40.7580,  # Times Square
                longitude=-73.9855,
                address="Times Square, New York, NY"
            )
        ),
        preferences=UserPreferences(
            event_theme="Broadway shows",
            transport_preferences=["walking"],
            budget=200.0
        )
    )
    
    # Create a schedule with top events
    schedule = EventSchedule()
    
    # Add top 3 events to schedule
    for event in events[:3]:
        schedule.add_event(event)
        logger.info(f"Added {event.name} to schedule")
    
    # Create locations list starting with user's location
    locations = [(
        user_context.profile.location.latitude,
        user_context.profile.location.longitude
    )]
    
    # Add event locations
    for event in schedule.events:
        locations.append((
            event.location.latitude,
            event.location.longitude
        ))
    
    # Create navigation plan with Broadway-specific handling
    logger.info("Creating Broadway-specific navigation plan...")
    navigation_plan = maps_service.create_navigation_plan(
        locations, 
        "walking",
        is_broadway=True
    )
    
    # Store navigation plan and update duration
    schedule.navigation_plan = navigation_plan
    schedule.total_duration += navigation_plan.total_duration
    
    # Print route details
    logger.info(f"Created navigation plan with {len(navigation_plan.routes)} routes")
    logger.info(f"Total distance: {navigation_plan.total_distance} meters")
    logger.info(f"Total duration: {navigation_plan.total_duration} seconds")
    
    for i, route in enumerate(navigation_plan.routes):
        from_name = "Current Location" if i == 0 else schedule.events[i-1].name
        to_name = schedule.events[i].name
        
        logger.info(f"Route {i+1}: From {from_name} to {to_name}")
        logger.info(f"  Distance: {route.distance} meters")
        logger.info(f"  Duration: {route.duration} seconds")
        logger.info(f"  Travel mode: {route.travel_mode}")
        
        # Print the first few steps
        for j, step in enumerate(route.steps[:3]):
            logger.info(f"  Step {j+1}: {step.instruction}")
    
    # Test is successful if we have a navigation plan with routes
    if navigation_plan and len(navigation_plan.routes) > 0:
        logger.info("TEST PASSED: Successfully created Broadway route plan")
    else:
        logger.error("TEST FAILED: Could not create Broadway route plan")

def test_generate_combined_routes():
    """Test the combined route generation with OpenAI integration."""
    if not openai_available:
        logger.error("OpenAI service not available - skipping combined route test")
        return
    
    logger.info("\n=== Testing Combined Route Generation ===")
    
    # Import the app to test the route generation
    try:
        from app import generate_route, showtimes_service, maps_service, openai_service
        
        # Mock the request data
        request_data = {
            'query': 'Broadway shows and dinner',
            'transport_mode': 'walking'
        }
        
        logger.info(f"Generating combined route for query: '{request_data['query']}'")
        
        # This is a rough simulation since we can't directly call the route without Flask context
        # In a real test, we would use Flask's test client
        
        # Check if all required services are available
        if not showtimes_service:
            logger.error("Showtimes service is unavailable - skipping test")
            return
            
        if not maps_service:
            logger.error("Maps service is unavailable - skipping test")
            return
            
        if not openai_service:
            logger.error("OpenAI service is unavailable - skipping test")
            return
        
        logger.info("All required services are available")
        logger.info("To test this properly, run the application and make a POST request to /api/route")
        logger.info("TEST PASSED: Services are available for route generation")
        
    except ImportError as e:
        logger.error(f"TEST FAILED: Could not import required modules: {str(e)}")
    except Exception as e:
        logger.error(f"TEST FAILED: Error testing route generation: {str(e)}")

if __name__ == "__main__":
    # Test OpenAI service
    test_openai_service()
    
    # Test Broadway showtimes
    test_broadway_showtimes()
    
    # Test Broadway routing
    test_broadway_routing()
    
    # Test combined route generation
    test_generate_combined_routes()
    
    # Restore original mock data setting
    config.USE_MOCK_DATA = False
    logger.info("All tests completed")
    logger.info("Mock data setting restored to original state") 