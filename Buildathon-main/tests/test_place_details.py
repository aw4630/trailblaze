#!/usr/bin/env python
"""
Test script for examining place details from the Places API New.
"""

import json
import logging
from services.google_showtimes_service import GoogleShowtimesService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_place_details():
    """Test fetching place details for Broadway shows."""
    service = GoogleShowtimesService()
    
    # Get places
    logger.info("Getting places for 'Broadway shows'")
    places = service.get_all_matching_places('Broadway shows')
    
    if not places:
        logger.error("No places found!")
        return
    
    logger.info(f"Found {len(places)} places")
    
    # Get details for first place
    place = places[0]
    place_id = place.get('id')
    name = place.get('displayName', {}).get('text', 'Unknown')
    
    logger.info(f"Getting details for {name} (ID: {place_id})")
    details = service._get_place_details_full(place_id)
    
    # Print full details
    logger.info("Place details:")
    print(json.dumps(details, indent=2))
    
    # Check for critical fields
    logger.info("Checking important fields:")
    print(f"Has businessStatus: {'businessStatus' in details}")
    print(f"Has currentOpeningHours: {'currentOpeningHours' in details}")
    print(f"Has editorialSummary: {'editorialSummary' in details}")
    print(f"Has priceLevel: {'priceLevel' in details}")
    
    # If we have opening hours, examine them
    if 'currentOpeningHours' in details:
        logger.info("Opening hours details:")
        opening_hours = details['currentOpeningHours']
        print(f"Has periods: {'periods' in opening_hours}")
        print(f"Has weekdayDescriptions: {'weekdayDescriptions' in opening_hours}")
        
        if 'periods' in opening_hours:
            periods = opening_hours['periods']
            print(f"Number of periods: {len(periods)}")
            if periods:
                print("First period:")
                print(json.dumps(periods[0], indent=2))

if __name__ == "__main__":
    test_place_details() 