#!/usr/bin/env python
"""
Test script for verifying timezone handling in the GoogleShowtimesService.
"""

import logging
import pytz
from datetime import datetime
from services.google_showtimes_service import GoogleShowtimesService
from models.event import EventLocation

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_timezone_handling():
    """Test timezone handling for venues in different locations."""
    
    # Initialize the service
    service = GoogleShowtimesService()
    
    # Current time in UTC and various timezones for reference
    now_utc = datetime.now(pytz.UTC)
    logger.info(f"Current UTC time: {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Log current time in various timezones for reference
    timezones = {
        "New York": "America/New_York",
        "Los Angeles": "America/Los_Angeles", 
        "London": "Europe/London",
        "Tokyo": "Asia/Tokyo",
    }
    
    for city, tz_name in timezones.items():
        tz = pytz.timezone(tz_name)
        local_time = now_utc.astimezone(tz)
        logger.info(f"Current time in {city} ({tz_name}): {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Test venue locations with different timezones
    test_locations = [
        EventLocation(
            place_id="test_nyc", 
            name="Broadway Theatre", 
            address="1681 Broadway, New York, NY 10019", 
            latitude=40.7625, 
            longitude=-73.9835
        ),
        EventLocation(
            place_id="test_la",
            name="TCL Chinese Theatre",
            address="6925 Hollywood Blvd, Hollywood, CA 90028",
            latitude=34.1022,
            longitude=-118.3415
        ),
        EventLocation(
            place_id="test_london",
            name="West End Theatre",
            address="London, UK",
            latitude=51.5074,
            longitude=-0.1278
        )
    ]
    
    # Generate showtimes for each location and check timezone handling
    for location in test_locations:
        logger.info(f"\nTesting location: {location.name} in {location.address}")
        
        # Generate demo showtimes using the venue's timezone
        showtimes = service._generate_demo_showtimes(location)
        
        if showtimes:
            logger.info(f"Generated {len(showtimes)} showtimes for {location.name}")
            for i, showtime in enumerate(showtimes):
                start_time = showtime.start_time
                
                # Verify the timezone is attached to the datetime
                logger.info(f"Showtime {i+1}: {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                
                # Convert to different timezones to demonstrate the difference
                ny_time = start_time.astimezone(pytz.timezone("America/New_York"))
                la_time = start_time.astimezone(pytz.timezone("America/Los_Angeles"))
                london_time = start_time.astimezone(pytz.timezone("Europe/London"))
                
                logger.info(f"  Same time in New York: {ny_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                logger.info(f"  Same time in Los Angeles: {la_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                logger.info(f"  Same time in London: {london_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        else:
            logger.warning(f"No showtimes generated for {location.name}")

    # Test with the search_events method for a Broadway show
    logger.info("\nTesting search_events for Broadway shows (NYC timezone):")
    events = service.search_events("Broadway shows")
    
    if events:
        logger.info(f"Found {len(events)} events")
        for i, event in enumerate(events[:3]):  # Check the first 3 events
            logger.info(f"\nEvent {i+1}: {event.name} in {event.location.address}")
            
            if event.showtimes:
                for j, showtime in enumerate(event.showtimes):
                    start_time = showtime.start_time
                    logger.info(f"  Showtime {j+1}: {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    
                    # Verify we can convert to other timezones correctly
                    utc_time = start_time.astimezone(pytz.UTC)
                    logger.info(f"    Same time in UTC: {utc_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        logger.warning("No Broadway events found")
    
    # Test with the search_events method for LA movie theaters
    logger.info("\nTesting search_events for LA movie theaters (LA timezone):")
    events = service.search_events("Movie theaters in Los Angeles")
    
    if events:
        logger.info(f"Found {len(events)} events")
        for i, event in enumerate(events[:3]):  # Check the first 3 events
            logger.info(f"\nEvent {i+1}: {event.name} in {event.location.address}")
            
            if event.showtimes:
                for j, showtime in enumerate(event.showtimes):
                    start_time = showtime.start_time
                    logger.info(f"  Showtime {j+1}: {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    
                    # Verify we can convert to other timezones correctly
                    utc_time = start_time.astimezone(pytz.UTC)
                    logger.info(f"    Same time in UTC: {utc_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        logger.warning("No LA movie events found")

if __name__ == "__main__":
    test_timezone_handling() 