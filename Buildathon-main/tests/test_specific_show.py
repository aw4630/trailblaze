#!/usr/bin/env python
"""
Test script to diagnose issues with finding specific shows like 'The Great Gatsby - The Musical'.
"""

import logging
import pytz
import json
from datetime import datetime
from services.google_showtimes_service import GoogleShowtimesService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_specific_show():
    """Test finding a specific show - The Great Gatsby Musical at Broadway Theatre."""
    
    # Initialize the service
    service = GoogleShowtimesService()
    
    # Log current times for reference
    now_utc = datetime.now(pytz.UTC)
    ny_time = now_utc.astimezone(pytz.timezone("America/New_York"))
    
    logger.info(f"Current UTC time: {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info(f"Current New York time: {ny_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Test with increasingly specific queries
    queries = [
        "Broadway shows",
        "Broadway Theatre New York",
        "The Great Gatsby Musical Broadway",
        "The Great Gatsby Musical Broadway Theatre New York"
    ]
    
    for query in queries:
        logger.info(f"\n\n----- Testing Query: '{query}' -----")
        
        # First, get all matching places without filtering to see what the API returns
        logger.info(f"Getting all matching places for '{query}':")
        places = service.get_all_matching_places(query)
        
        logger.info(f"Found {len(places)} matching places")
        
        # Print the first 3 places to see what we're getting
        for i, place in enumerate(places[:3]):
            display_name = place.get('displayName', {}).get('text', 'Unknown')
            address = place.get('formattedAddress', 'Unknown address')
            
            logger.info(f"Place {i+1}: {display_name} - {address}")
            
            # Check for any useful fields that might have show information
            interesting_fields = ['types', 'currentOpeningHours', 'displayName', 'editorialSummary']
            for field in interesting_fields:
                if field in place:
                    logger.info(f"  - {field}: {json.dumps(place[field], indent=2)}")
        
        # Now search for events to see what we process
        logger.info(f"\nSearching for events with query '{query}':")
        events = service.search_events(query)
        
        logger.info(f"Found {len(events)} events")
        
        # Check for any event that might match our target
        found_target = False
        for event in events:
            # Check if this event might be related to Great Gatsby
            if "gatsby" in event.name.lower():
                found_target = True
                logger.info(f"\nFOUND TARGET EVENT: {event.name}")
                logger.info(f"Location: {event.location.name} - {event.location.address}")
                logger.info(f"Category: {event.category}")
                logger.info(f"Description: {event.description}")
                
                if event.showtimes:
                    logger.info(f"Number of showtimes: {len(event.showtimes)}")
                    for i, showtime in enumerate(event.showtimes):
                        start_time = showtime.start_time
                        logger.info(f"Showtime {i+1}: {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                        # Check if this is today or tomorrow in NY timezone
                        start_time_ny = start_time.astimezone(pytz.timezone("America/New_York"))
                        if start_time_ny.date() == ny_time.date():
                            logger.info(f"  - This is TODAY in New York")
                        elif start_time_ny.date() > ny_time.date():
                            days_diff = (start_time_ny.date() - ny_time.date()).days
                            logger.info(f"  - This is {days_diff} day(s) in the future")
                else:
                    logger.info("No showtimes available")
        
        if not found_target:
            logger.info("Target 'Great Gatsby' event not found in results")
        
        # Also print basic info for first 3 events
        for i, event in enumerate(events[:3]):
            if not "gatsby" in event.name.lower():  # Skip if already detailed above
                logger.info(f"\nEvent {i+1}: {event.name}")
                logger.info(f"Location: {event.location.name} - {event.location.address}")
                
                if event.showtimes:
                    first_showtime = event.showtimes[0].start_time
                    logger.info(f"First showtime: {first_showtime.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    
                    # Check if this is today or tomorrow in NY timezone
                    first_time_ny = first_showtime.astimezone(pytz.timezone("America/New_York"))
                    if first_time_ny.date() == ny_time.date():
                        logger.info(f"  - This is TODAY in New York")
                    elif first_time_ny.date() > ny_time.date():
                        days_diff = (first_time_ny.date() - ny_time.date()).days
                        logger.info(f"  - This is {days_diff} day(s) in the future")
                else:
                    logger.info("No showtimes available")

    # Try a very direct test
    logger.info("\n\n----- Direct Test for Broadway Theatre -----")
    # Try to test with Google Places directly
    broadway_theatre_place_id = None
    broadway_name = "Broadway Theatre"
    
    # First, search for Broadway Theatre specifically
    direct_places = service.get_all_matching_places("Broadway Theatre New York")
    
    for place in direct_places:
        display_name = place.get('displayName', {}).get('text', 'Unknown')
        if broadway_name.lower() in display_name.lower():
            broadway_theatre_place_id = place.get('id')
            logger.info(f"Found Broadway Theatre with place ID: {broadway_theatre_place_id}")
            
            # Get full details for this place
            if broadway_theatre_place_id:
                logger.info("Getting full details for Broadway Theatre")
                details = service._get_place_details_full(broadway_theatre_place_id)
                
                # Log interesting fields
                important_fields = [
                    'displayName', 'formattedAddress', 'currentOpeningHours',
                    'regularOpeningHours', 'websiteUri', 'editorialSummary'
                ]
                
                for field in important_fields:
                    if field in details:
                        logger.info(f"{field}: {json.dumps(details[field], indent=2)}")
            
            break

if __name__ == "__main__":
    test_specific_show() 