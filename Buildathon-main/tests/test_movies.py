#!/usr/bin/env python
"""
Test script for verifying the search_events method works with movies in LA.
"""

import logging
from services.google_showtimes_service import GoogleShowtimesService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_movies():
    """Test fetching movie theater events."""
    service = GoogleShowtimesService()
    
    # Get events with showtimes
    logger.info("Searching for movie theaters in Los Angeles")
    events = service.search_events('Movie theaters near Los Angeles')
    
    print(f"Found {len(events)} movie theater events")
    
    # Print details of the first few events
    for i, event in enumerate(events[:5]):
        print(f"\nEvent {i+1}: {event.name}")
        print(f"  Category: {event.category}")
        print(f"  Location: {event.location.address}")
        print(f"  Rating: {event.rating}")
        print(f"  Number of showtimes: {len(event.showtimes)}")
        
        # Print first showtime
        if event.showtimes:
            print(f"  First showtime: {event.showtimes[0].start_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"  Availability: {event.showtimes[0].availability}")
        
        # Print price info
        if event.prices:
            print(f"  Adult price: ${event.prices[0].amount:.2f}")
            
        print(f"  Description: {event.description[:100]}..." if len(event.description) > 100 else event.description)

if __name__ == "__main__":
    test_movies() 