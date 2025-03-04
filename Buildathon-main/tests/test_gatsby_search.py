#!/usr/bin/env python
"""
Test script to ensure we can find "The Great Gatsby - The Musical" at Broadway Theatre.
This specifically tests the search pattern from the Google URL shared by the user.
"""

import logging
import pytz
from datetime import datetime
from services.google_showtimes_service import GoogleShowtimesService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gatsby_search():
    """Test searching for The Great Gatsby as specified in the Google URL pattern."""
    
    # Initialize the service
    service = GoogleShowtimesService()
    
    # Log current times for reference
    now_utc = datetime.now(pytz.UTC)
    ny_time = now_utc.astimezone(pytz.timezone("America/New_York"))
    
    logger.info(f"Current UTC time: {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info(f"Current New York time: {ny_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # This is the exact search pattern from the Google URL
    search_query = "The Great Gatsby - The Musical - New York, Broadway Theatre, 1 Mar"
    
    logger.info(f"\nSearching with query: '{search_query}'")
    
    # First, get all matching places to see what the API returns
    places = service.get_all_matching_places(search_query)
    
    logger.info(f"Found {len(places)} matching places")
    
    # Print all places to see what we're getting
    for i, place in enumerate(places):
        display_name = place.get('displayName', {}).get('text', 'Unknown')
        address = place.get('formattedAddress', 'Unknown address')
        
        logger.info(f"Place {i+1}: {display_name} - {address}")
        
        # Log the types to see if it's recognized as a theater
        if 'types' in place:
            types = place.get('types', [])
            logger.info(f"  Types: {types}")
    
    # Search for events
    events = service.search_events(search_query)
    
    logger.info(f"\nFound {len(events)} events with showtimes")
    
    # Look for The Great Gatsby
    gatsby_events = []
    for event in events:
        if "gatsby" in event.name.lower():
            gatsby_events.append(event)
    
    if gatsby_events:
        logger.info(f"Found {len(gatsby_events)} Great Gatsby events")
        
        for i, event in enumerate(gatsby_events):
            logger.info(f"\nGatsby Event {i+1}: {event.name}")
            logger.info(f"  Location: {event.location.name} - {event.location.address}")
            logger.info(f"  Category: {event.category}")
            
            if event.showtimes:
                logger.info(f"  Number of showtimes: {len(event.showtimes)}")
                for j, showtime in enumerate(event.showtimes):
                    start_time = showtime.start_time
                    logger.info(f"  Showtime {j+1}: {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    
                    # Check if this is today or tomorrow in NY timezone
                    start_time_ny = start_time.astimezone(pytz.timezone("America/New_York"))
                    if start_time_ny.date() == ny_time.date():
                        logger.info(f"    - This is TODAY in New York")
                    elif start_time_ny.date() > ny_time.date():
                        days_diff = (start_time_ny.date() - ny_time.date()).days
                        logger.info(f"    - This is {days_diff} day(s) in the future")
                
                # Also print the first price if available
                if event.prices:
                    for price in event.prices:
                        if price.category == "adult":
                            logger.info(f"  Adult Price: ${price.amount:.2f}")
                            break
            else:
                logger.info("  No showtimes available")
    else:
        logger.info("No Great Gatsby events found!")
        
        # Print general events that were found
        logger.info("\nGeneral events found:")
        for i, event in enumerate(events[:5]):
            logger.info(f"Event {i+1}: {event.name}")
            logger.info(f"  Location: {event.location.address}")
            
            if event.showtimes:
                first_showtime = event.showtimes[0].start_time
                logger.info(f"  First showtime: {first_showtime.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Also try specifically searching for Broadway Theatre to see what shows it has
    logger.info("\n\nChecking Broadway Theatre directly:")
    
    broadway_search = "Broadway Theatre New York"
    broadway_events = service.search_events(broadway_search)
    
    if broadway_events:
        logger.info(f"Found {len(broadway_events)} events at Broadway Theatre")
        
        for i, event in enumerate(broadway_events):
            logger.info(f"Broadway Event {i+1}: {event.name}")
            
            if event.showtimes:
                logger.info(f"  Number of showtimes: {len(event.showtimes)}")
                first_showtime = event.showtimes[0].start_time
                logger.info(f"  First showtime: {first_showtime.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        logger.info("No events found at Broadway Theatre!")

if __name__ == "__main__":
    test_gatsby_search() 