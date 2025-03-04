#!/usr/bin/env python
"""
Test script for verifying timezone handling in real search_events calls.
"""

import logging
import pytz
from datetime import datetime
from services.google_showtimes_service import GoogleShowtimesService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_events_timezone():
    """Test timezone handling with real search_events calls."""
    
    # Initialize the service
    service = GoogleShowtimesService()
    
    # Log current times for reference
    now_utc = datetime.now(pytz.UTC)
    ny_time = now_utc.astimezone(pytz.timezone("America/New_York"))
    la_time = now_utc.astimezone(pytz.timezone("America/Los_Angeles"))
    
    logger.info(f"Current UTC time: {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info(f"Current New York time: {ny_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info(f"Current Los Angeles time: {la_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Test Broadway shows (should use New York timezone)
    logger.info("\n----- Testing Broadway Shows (New York) -----")
    ny_events = service.search_events("Broadway shows")
    
    print(f"Found {len(ny_events)} events in New York")
    
    # Print timezone information for the first few events
    for i, event in enumerate(ny_events[:3]):
        print(f"\nEvent {i+1}: {event.name}")
        print(f"  Location: {event.location.address}")
        
        if event.showtimes:
            # Get the first showtime
            showtime = event.showtimes[0]
            start_time = showtime.start_time
            
            # Check if timezone info is attached
            if start_time.tzinfo:
                print(f"  First showtime: {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                
                # Convert to other timezones to verify
                utc_time = start_time.astimezone(pytz.UTC)
                la_time = start_time.astimezone(pytz.timezone("America/Los_Angeles"))
                
                print(f"  Same time in UTC: {utc_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"  Same time in LA: {la_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            else:
                print(f"  WARNING: First showtime has no timezone: {start_time}")
        else:
            print(f"  No showtimes available")
    
    # Test LA movie theaters (should use Los Angeles timezone)
    logger.info("\n----- Testing Movie Theaters (Los Angeles) -----")
    la_events = service.search_events("Movie theaters in Los Angeles")
    
    print(f"Found {len(la_events)} events in Los Angeles")
    
    # Print timezone information for the first few events
    for i, event in enumerate(la_events[:3]):
        print(f"\nEvent {i+1}: {event.name}")
        print(f"  Location: {event.location.address}")
        
        if event.showtimes:
            # Get the first showtime
            showtime = event.showtimes[0]
            start_time = showtime.start_time
            
            # Check if timezone info is attached
            if start_time.tzinfo:
                print(f"  First showtime: {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                
                # Convert to other timezones to verify
                utc_time = start_time.astimezone(pytz.UTC)
                ny_time = start_time.astimezone(pytz.timezone("America/New_York"))
                
                print(f"  Same time in UTC: {utc_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"  Same time in NY: {ny_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            else:
                print(f"  WARNING: First showtime has no timezone: {start_time}")
        else:
            print(f"  No showtimes available")

if __name__ == "__main__":
    test_events_timezone() 