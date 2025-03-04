#!/usr/bin/env python
"""
Automated test runner for the Broadway Show Query application.
This script runs the automated test for querying about Broadway shows.
"""

import sys
import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the test function and config
from tests.test_app import run_automated_test
import config

# Add parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import services and config
from services.google_maps_service import GoogleMapsService
from services.google_showtimes_service import GoogleShowtimesService
from services.embedding_processor import EmbeddingProcessor
from services.openai_service import OpenAIService

def run_tests():
    """Run tests for the API services."""
    logger.info("Running API service tests")
    logger.info("=========================")
    logger.info(f"Testing with API keys:")
    logger.info(f"- Google Maps API Key: {'✅ Set' if config.GOOGLE_MAPS_API_KEY else '❌ Not set'}")
    logger.info(f"- Google Showtimes API Key: {'✅ Set' if config.GOOGLE_SHOWTIMES_API_KEY else '❌ Not set'}")
    logger.info(f"- OpenAI API Key: {'✅ Set' if config.OPENAI_API_KEY else '❌ Not set'}")
    logger.info(f"- All API services are required - mock data has been disabled")
    
    # Initialize services
    try:
        maps_service = GoogleMapsService()
        logger.info("✅ GoogleMapsService initialized")
    except Exception as e:
        logger.error(f"❌ GoogleMapsService initialization failed: {str(e)}")
        return
    
    try:
        showtimes_service = GoogleShowtimesService()
        logger.info("✅ GoogleShowtimesService initialized")
    except Exception as e:
        logger.error(f"❌ GoogleShowtimesService initialization failed: {str(e)}")
        return
    
    # Test Google Maps Directions API
    try:
        logger.info("Testing Google Maps Directions API...")
        origin = "Times Square, New York, NY"
        destination = "Empire State Building, New York, NY"
        
        directions = maps_service.get_directions(origin, destination, "walking")
        
        if directions and 'routes' in directions and len(directions['routes']) > 0:
            route = directions['routes'][0]
            distance = route['legs'][0]['distance']['text']
            duration = route['legs'][0]['duration']['text']
            logger.info(f"✅ Directions API returned: Distance: {distance}, Duration: {duration}")
        else:
            logger.warning("⚠️ Directions API returned no routes")
    except Exception as e:
        logger.error(f"❌ Directions API test failed: {str(e)}")
    
    # Test Google Showtimes API - search for events
    try:
        logger.info("Testing Google Showtimes API - searching for Broadway shows...")
        location = (40.7580, -73.9855)  # Times Square approximate location
        events = showtimes_service.search_events("Broadway shows", location)
        
        if events:
            logger.info(f"✅ Found {len(events)} events")
            # Log the first few events
            for i, event in enumerate(events[:3]):
                logger.info(f"  Event {i+1}: {event.name} at {event.location.name}")
                if event.showtimes:
                    logger.info(f"    Showtimes: {len(event.showtimes)} available")
                    for j, showtime in enumerate(event.showtimes[:2]):
                        logger.info(f"      {j+1}: {showtime.start_time.strftime('%Y-%m-%d %H:%M')} - {showtime.end_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            logger.warning("⚠️ No events found")
    except Exception as e:
        logger.error(f"❌ Showtimes API test failed: {str(e)}")
    
    logger.info("Tests completed.")

if __name__ == "__main__":
    run_tests() 