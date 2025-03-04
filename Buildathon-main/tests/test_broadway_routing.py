#!/usr/bin/env python
"""
Test script to verify Broadway showtimes and route planning functionality.
This ensures that Broadway showtimes correctly default to today's date,
and that route planning works effectively between venues.
"""

import sys
import os
import logging
from datetime import datetime
import pytz

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from services.google_showtimes_service import GoogleShowtimesService
from services.google_maps_service import GoogleMapsService
from models.user import UserContext, UserProfile, UserLocation, UserPreferences
from models.event import EventSchedule
import config

# Temporarily enable mock data for testing
config.USE_MOCK_DATA = True
logging.info(f"Test mode: Mock data temporarily ENABLED for testing")

# Set up logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_broadway_showtimes():
    """Test Broadway showtimes to ensure they default to today's date."""
    logger.info("=== Testing Broadway Showtimes ===")
    
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

if __name__ == "__main__":
    # Test Broadway showtimes
    test_broadway_showtimes()
    
    # Test Broadway routing
    test_broadway_routing()
    
    # Restore original mock data setting
    config.USE_MOCK_DATA = False
    logger.info("All tests completed")
    logger.info("Mock data setting restored to original state") 