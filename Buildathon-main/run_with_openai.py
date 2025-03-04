#!/usr/bin/env python3
"""
Run script for the Broadway Show & Event Planner application.
This script starts the application with OpenAI capabilities enabled.
"""
import os
import sys
import logging
import subprocess
from dotenv import load_dotenv

# Add config directory to path
sys.path.append("config")
import config

# Set up logging with enhanced settings for OpenAI service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
# Set OpenAI service logger to DEBUG level to see all API calls
logging.getLogger("openai_service").setLevel(logging.DEBUG)
logger = logging.getLogger("run_with_openai")

def check_openai_key():
    """Check if the OpenAI API key is set in the environment."""
    return bool(config.OPENAI_API_KEY)

def check_google_maps_key():
    """Check if the Google Maps API key is set in the environment."""
    return bool(config.GOOGLE_MAPS_API_KEY)

def check_google_showtimes_key():
    """Check if the Google Showtimes API key is set in the environment."""
    return bool(config.GOOGLE_SHOWTIMES_API_KEY)

def main():
    """Run the application with OpenAI integration."""
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Log application mode
        logger.info(f"Starting application in {'DEBUG' if config.DEBUG else 'PRODUCTION'} mode")
        
        # Check if we have required API keys
        logger.info("Checking for required API keys...")
        logger.info(f"GOOGLE_MAPS_API_KEY: {'SET' if config.GOOGLE_MAPS_API_KEY else 'MISSING'}")
        logger.info(f"GOOGLE_SHOWTIMES_API_KEY: {'SET' if config.GOOGLE_SHOWTIMES_API_KEY else 'MISSING'}")
        logger.info(f"OPENAI_API_KEY: {'SET' if config.OPENAI_API_KEY else 'MISSING'}")
        logger.info("All API services are required - mock data has been disabled")
        
        # Check if OpenAI API key is set
        if not check_openai_key():
            logger.error("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
            return 1
        
        # Check Google Maps API key
        if not check_google_maps_key():
            logger.error("Google Maps API key not found. Please set GOOGLE_MAPS_API_KEY in your .env file.")
            return 1
        
        # Check Google Showtimes API key
        if not check_google_showtimes_key():
            logger.error("Google Showtimes API key not found. Please set GOOGLE_SHOWTIMES_API_KEY in your .env file.")
            return 1
        
        # Set environment variables for the application
        os.environ['DEBUG'] = 'True'  # Enable debug mode
        os.environ['USE_MOCK_DATA'] = 'False'  # Disable mock data
        
        # Import app after setting environment variables
        import app
        
        # Configure logging for the app
        if config.DEBUG:
            logger.info("Debug mode enabled")
            logger.info(f"Using OpenAI model: {config.OPENAI_MODEL}")
        
        # Initialize services
        try:
            from services.google_maps_service import GoogleMapsService
            maps_service = GoogleMapsService()
            logger.info("GoogleMapsService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GoogleMapsService: {str(e)}")
            sys.exit(1)
            
        try:
            from services.google_showtimes_service import GoogleShowtimesService
            showtimes_service = GoogleShowtimesService()
            logger.info("GoogleShowtimesService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GoogleShowtimesService: {str(e)}")
            sys.exit(1)
        
        # Run the application
        logger.info(f"Starting application on {config.HOST}:{config.PORT}")
        app.run_app()
        
        return 0
    except Exception as e:
        logger.error(f"Error running application: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 