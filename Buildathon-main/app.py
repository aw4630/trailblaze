#!/usr/bin/env python3
"""
Broadway Show & Event Planner application.
This is the main application file that integrates OpenAI capabilities.
"""
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import traceback
import sys
import flask
from dotenv import load_dotenv
import re
import openai
import argparse

# Import configuration first
sys.path.append("config")
import config

# Load environment variables from .env file
load_dotenv()

# Set environment variables for the application
os.environ['DEBUG'] = 'True'  # Enable debug mode
os.environ['USE_MOCK_DATA'] = 'False'  # Disable mock data

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
# Set OpenAI service logger to DEBUG level to see all API calls
logging.getLogger("openai_service").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# Import models (after config is loaded)
from models.user import UserContext, UserProfile, UserLocation, UserPreferences
from models.event import Event, EventSchedule
from models.navigation import NavigationPlan

# Import services
from services.openai_service import OpenAIService, DateTimeEncoder
from services.google_maps_service import GoogleMapsService
from services.google_showtimes_service import GoogleShowtimesService
from services.plan_verification import PlanVerifier

# Import embedding processor
from models.embedding import EmbeddingProcessor

# Import utilities
from utils.helpers import parse_time_string, extract_budget, format_duration, format_distance

# Log config values to ensure they're loaded
logger.info(f"Starting application in {'DEBUG' if config.DEBUG else 'PRODUCTION'} mode")
logger.info(f"OPENAI_API_KEY configured: {'Yes' if hasattr(config, 'OPENAI_API_KEY') and config.OPENAI_API_KEY else 'No'}")
logger.info(f"GOOGLE_MAPS_API_KEY configured: {'Yes' if hasattr(config, 'GOOGLE_MAPS_API_KEY') and config.GOOGLE_MAPS_API_KEY else 'No'}")
logger.info(f"GOOGLE_SHOWTIMES_API_KEY configured: {'Yes' if hasattr(config, 'GOOGLE_SHOWTIMES_API_KEY') and config.GOOGLE_SHOWTIMES_API_KEY else 'No'}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)

# Initialize services
openai_service = None
maps_service = None
showtimes_service = None
embedding_processor = None
plan_verifier = None

# Check if we have required API keys
logger.info("Checking for required API keys...")
logger.info(f"GOOGLE_MAPS_API_KEY: {'SET' if hasattr(config, 'GOOGLE_MAPS_API_KEY') and config.GOOGLE_MAPS_API_KEY else 'MISSING'}")
logger.info(f"GOOGLE_SHOWTIMES_API_KEY: {'SET' if hasattr(config, 'GOOGLE_SHOWTIMES_API_KEY') and config.GOOGLE_SHOWTIMES_API_KEY else 'MISSING'}")
logger.info(f"OPENAI_API_KEY: {'SET' if hasattr(config, 'OPENAI_API_KEY') and config.OPENAI_API_KEY else 'MISSING'}")

# Check if OpenAI API key is set
def check_openai_key():
    """Check if the OpenAI API key is set in the environment."""
    return hasattr(config, 'OPENAI_API_KEY') and bool(config.OPENAI_API_KEY)

# Check if Google Maps API key is set
def check_gmaps_key():
    """Check if the Google Maps API key is set in the environment."""
    return hasattr(config, 'GOOGLE_MAPS_API_KEY') and bool(config.GOOGLE_MAPS_API_KEY)

# Check if Google Showtimes API key is set
def check_showtimes_key():
    """Check if the Google Showtimes API key is set in the environment."""
    return hasattr(config, 'GOOGLE_SHOWTIMES_API_KEY') and bool(config.GOOGLE_SHOWTIMES_API_KEY)

# Initialize services
def init_services():
    """Initialize services with proper error handling."""
    global openai_service, showtimes_service
    
    # Check if API keys are set
    openai_api_key = os.getenv('OPENAI_API_KEY')
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    google_showtimes_api_key = os.getenv('GOOGLE_SHOWTIMES_API_KEY')
    
    if not openai_api_key:
        logger.error("OPENAI_API_KEY not set. OpenAI service will not function.")
    else:
        try:
            # Initialize OpenAI service with proper client setup
            # Old OpenAI client was not available, so use regular initialization
            openai_service = OpenAIService()
            logger.info("OpenAI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI service: {str(e)}")
    
    if not google_maps_api_key or not google_showtimes_api_key:
        logger.error("One or more Google API keys not set. Google services will not function.")
    else:
        try:
            # Initialize Google showtimes service with the correct parameter names
            showtimes_service = GoogleShowtimesService()
            logger.info("Google Showtimes service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Showtimes service: {str(e)}")

# Initialize Google Maps service
try:
    maps_service = GoogleMapsService()
    logger.info("Google Maps service initialized successfully")
except Exception as e:
    error_traceback = traceback.format_exc()
    logger.error(f"Failed to initialize Google Maps service: {str(e)}")
    logger.error(f"Traceback: {error_traceback}")
    logger.error(f"API Key configured: {'Yes' if check_gmaps_key() else 'No'}")
    if check_gmaps_key():
        logger.error("Google Maps API key is set but service initialization failed.")
    else:
        logger.error("Google Maps API key is not set. Please set GOOGLE_MAPS_API_KEY in your .env file.")
        sys.exit(1)

# Initialize Google Showtimes service
try:
    showtimes_service = GoogleShowtimesService()
    logger.info("Google Showtimes service initialized successfully")
except Exception as e:
    error_traceback = traceback.format_exc()
    logger.error(f"Failed to initialize Google Showtimes service: {str(e)}")
    logger.error(f"Traceback: {error_traceback}")
    logger.error(f"API Key configured: {'Yes' if check_showtimes_key() else 'No'}")
    if check_showtimes_key():
        logger.error("Google Showtimes API key is set but service initialization failed.")
    else:
        logger.error("Google Showtimes API key is not set. Please set GOOGLE_SHOWTIMES_API_KEY in your .env file.")
        sys.exit(1)

# Initialize Embedding processor
try:
    embedding_processor = EmbeddingProcessor()
    logger.info("Embedding processor initialized successfully")
except Exception as e:
    error_traceback = traceback.format_exc()
    logger.error(f"Failed to initialize Embedding processor: {str(e)}")
    logger.warning("Embedding processor is not available. Some features may be limited.")

# Initialize Plan Verifier if dependencies are available
if maps_service and showtimes_service:
    try:
        plan_verifier = PlanVerifier(maps_service, showtimes_service)
        logger.info("Plan verifier initialized successfully")
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to initialize Plan verifier: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")
        logger.warning("Plan verifier is not available. Plan validation will be limited.")

# Define the system prompt for OpenAI
SYSTEM_PROMPT = """
You are an AI assistant for a Broadway Show & Event Planner application. Your goal is to help users discover Broadway shows, events, and dining options in New York City. 

For all responses, you should return a JSON object with the following structure:
{
  "response": "Your human-friendly response text here",
  "events": [
    {
      "name": "Event name",
      "date": "Date and time",
      "location": "Event location",
      "description": "Brief description"
    }
  ],
  "schedule": {
    "date": "YYYY-MM-DD",
    "events": [
      {
        "time": "HH:MM",
        "activity": "Description of activity",
        "location": "Location"
      }
    ]
  }
}

For restaurant recommendations, include the cuisine type in your response:
{
  "response": "Your human-friendly response text about restaurant recommendations",
  "cuisine": "The type of cuisine (e.g., Italian, Thai, etc.)",
  "events": [],
  "schedule": {}
}

Always be helpful, friendly, and enthusiastic. If you need more specific information from the user, ask clarifying questions.
"""

# Define the global user context
user_context = UserContext()

class UserLocation:
    """Class to represent a user's location."""
    
    def __init__(self, latitude=None, longitude=None, address=None):
        """Initialize a UserLocation object."""
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        
    def to_dict(self):
        """Convert the UserLocation object to a dictionary."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address
        }
        
    def __str__(self):
        """Return a string representation of the UserLocation object."""
        if self.address:
            return f"{self.address} ({self.latitude}, {self.longitude})"
        else:
            return f"({self.latitude}, {self.longitude})"
            
    def __bool__(self):
        """Return True if the UserLocation has valid coordinates."""
        return self.latitude is not None and self.longitude is not None

@app.route('/')
def index():
    """Render the main page."""
    # Check if services are available
    services_status = {
        "openai": openai_service is not None,
        "maps": maps_service is not None,
        "showtimes": showtimes_service is not None,
        "embeddings": embedding_processor is not None,
        "verifier": plan_verifier is not None
    }
    
    return render_template('index.html', 
                          services_status=services_status, 
                          debug=config.DEBUG,
                          use_mock_data=config.USE_MOCK_DATA)


@app.route('/ai-planner')
def ai_planner():
    """Render the AI-driven planner page."""
    return render_template('ai_planner.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the user."""
    try:
        # Get the request data
        data = request.get_json()
        
        # Extract the message and location
        user_message = data.get('message', '')
        location_data = data.get('location', None)
        
        # Create a UserLocation object if location data is provided
        user_location = None
        if location_data:
            user_location = UserLocation(
                latitude=location_data.get('latitude'),
                longitude=location_data.get('longitude'),
                address=location_data.get('address')
            )
        
        # Process the message
        response = process_message(user_message, user_location)
        
        # Return the response
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return jsonify({
            "error": f"Error processing your message: {str(e)}",
            "initial_response": "I'm processing your request...",
            "location_requested": True,
            "response": "I'm sorry, but I encountered an error while processing your request. Please try again."
        })


def create_plan_for_chat(user_message, user_context):
    """Create a plan using OpenAI and return a chat-friendly response."""
    try:
        logger.info(f"Creating plan for chat message: '{user_message}'")
        
        # Get user location if available
        user_location = None
        if hasattr(user_context, 'location') and user_context.location:
            user_location = user_context.location
        
        # Create initial plan using OpenAI directly
        plan_response = openai_service.ask_model(
            system_message=SYSTEM_PROMPT,
            user_message=user_message,
            location=user_location
        )
        
        logger.info(f"OpenAI plan response: {plan_response}")
        
        try:
            # Parse the plan
            plan = json.loads(plan_response)
            return {
                "response": plan.get("response", "I've found some options that might interest you."),
                "events": plan.get("events", []),
                "schedule": plan.get("schedule", {})
            }
        except json.JSONDecodeError:
            logger.error(f"Error parsing plan response: {plan_response}")
            return {
                "response": "I'm sorry, but I encountered an error while processing your request. Please try again.",
                "events": [],
                "schedule": {}
            }
    except Exception as e:
        logger.error(f"Error creating plan: {str(e)}")
        return {
            "response": f"Sorry, I couldn't create a plan: {str(e)}",
            "events": [],
            "schedule": {}
        }


@app.route('/api/profile', methods=['POST'])
def update_profile():
    """Update user profile information."""
    try:
        data = request.json
        logger.info(f"Updating user profile with data: {data}")
        
        # Initialize or get user context from session
        if 'user_context' in session:
            context_dict = json.loads(session['user_context'])
            user_context = UserContext.model_validate(context_dict)
        else:
            user_context = UserContext()
        
        # Update profile information
        if 'email' in data:
            user_context.profile.email = data['email']
            
        if 'accessibility_needs' in data:
            user_context.profile.accessibility_needs = data['accessibility_needs']
            
        if 'walking_capability' in data:
            user_context.profile.walking_capability = data['walking_capability']
            
        # Update location if both latitude and longitude are provided
        if 'latitude' in data and 'longitude' in data:
            user_context.profile.location = UserLocation(
                latitude=data['latitude'],
                longitude=data['longitude'],
                address=data.get('address')
            )
        
        # Save updated context to session
        session['user_context'] = json.dumps(user_context.model_dump())
        logger.info(f"User profile updated successfully")
        
        return jsonify({'success': True, 'profile': user_context.profile.model_dump()})
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/preferences', methods=['POST'])
def update_preferences():
    """Update user preferences."""
    try:
        data = request.json
        logger.info(f"Updating user preferences with data: {data}")
        
        # Initialize or get user context from session
        user_context = get_or_create_user_context()
        
        # Update preferences
        if 'event_theme' in data:
            user_context.preferences.event_theme = data['event_theme']
            
        if 'available_time_start' in data:
            user_context.preferences.available_time_start = data['available_time_start']
            
        if 'available_time_end' in data:
            user_context.preferences.available_time_end = data['available_time_end']
            
        if 'budget' in data:
            user_context.preferences.budget = data['budget']
            
        if 'transport_preferences' in data:
            user_context.preferences.transport_preferences = data['transport_preferences']
        
        # Save updated context to session
        update_user_context(user_context, {})
        logger.info(f"User preferences updated successfully")
        
        return jsonify({'success': True, 'preferences': user_context.preferences.model_dump()})
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences."""
    try:
        if 'user_context' in session:
            context_dict = json.loads(session['user_context'])
            user_context = UserContext.model_validate(context_dict)
            return jsonify({'success': True, 'preferences': user_context.preferences.model_dump()})
        else:
            logger.warning("No user context found in session")
            return jsonify({'success': False, 'error': 'No user context found'}), 404
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/service-status', methods=['GET'])
def service_status():
    """Check if all services are available and properly configured."""
    services = {
        "openai": {
            "available": openai_service is not None,
            "key_configured": bool(config.OPENAI_API_KEY),
            "key_status": "Valid" if openai_service else "Invalid or missing"
        },
        "maps": {
            "available": maps_service is not None,
            "key_configured": bool(config.GOOGLE_MAPS_API_KEY),
            "key_status": "Valid" if maps_service else "Invalid or missing"
        },
        "showtimes": {
            "available": showtimes_service is not None,
            "key_configured": bool(config.GOOGLE_SHOWTIMES_API_KEY),
            "key_status": "Valid" if showtimes_service else "Invalid or missing",
            "using_mock_data": getattr(showtimes_service, '_using_mock_data', False) if showtimes_service else False,
            "mock_data_enabled": config.USE_MOCK_DATA
        },
        "embedding": {
            "available": embedding_processor is not None
        }
    }
    
    # Check if Claude is also available (for backwards compatibility)
    try:
        from services.claude_service import ClaudeService
        claude_available = bool(config.ANTHROPIC_API_KEY)
        services["claude"] = {
            "available": claude_available,
            "key_configured": bool(config.ANTHROPIC_API_KEY),
            "key_status": "Available but not used" if claude_available else "Not available"
        }
    except ImportError:
        services["claude"] = {
            "available": False,
            "key_configured": False,
            "key_status": "Module not found" 
        }
    
    # Required services for operation (OpenAI and maps)
    required_services = ["openai", "maps", "showtimes"]
    all_available = all(services[service]["available"] for service in required_services)
    
    # Add application info
    app_info = {
        "mock_data_enabled": config.USE_MOCK_DATA,
        "debug_mode": config.DEBUG,
        "openai_model": config.OPENAI_MODEL,
        "ai_service_in_use": "openai"
    }
    
    return jsonify({
        "services": services,
        "all_available": all_available,
        "app_info": app_info
    })


@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Get debug information about the application state and configuration."""
    # Only allow in debug mode
    if not config.DEBUG:
        return jsonify({
            'error': 'Debug endpoint is only available when DEBUG=True'
        }), 403
        
    # Collect environment info
    env_info = {
        'python_version': '.'.join(map(str, sys.version_info[:3])),
        'platform': sys.platform,
        'flask_version': flask.__version__
    }
    
    # API key status (show first and last 4 chars for verification)
    api_keys = {
        'OPENAI_API_KEY': mask_api_key(config.OPENAI_API_KEY),
        'GOOGLE_MAPS_API_KEY': mask_api_key(config.GOOGLE_MAPS_API_KEY),
        'GOOGLE_SHOWTIMES_API_KEY': mask_api_key(config.GOOGLE_SHOWTIMES_API_KEY)
    }
    
    # Service initialization status
    services_status = {
        'openai_service': openai_service is not None,
        'maps_service': maps_service is not None,
        'showtimes_service': showtimes_service is not None,
        'embedding_processor': embedding_processor is not None
    }
    
    # Application configuration
    app_config = {
        'DEBUG': config.DEBUG,
        'USE_MOCK_DATA': config.USE_MOCK_DATA,
        'OPENAI_MODEL': config.OPENAI_MODEL,
        'PORT': config.PORT,
        'HOST': config.HOST
    }
    
    return jsonify({
        'env_info': env_info,
        'api_keys': api_keys,
        'services_status': services_status,
        'app_config': app_config
    })
    
def mask_api_key(key):
    """Mask API key to show only first and last 4 chars for verification."""
    if not key:
        return "Not configured"
        
    if len(key) <= 8:
        return "***" # Key too short to mask properly
        
    return f"{key[:4]}...{key[-4:]}"


def get_or_create_user_context() -> UserContext:
    """Get existing user context from session or create a new one."""
    if 'user_context' in session:
        context_dict = json.loads(session['user_context'])
        user_context = UserContext.model_validate(context_dict)
        logger.debug("Retrieved existing user context from session")
    else:
        user_context = UserContext()
        logger.info("Created new user context")
    
    return user_context


def update_user_context(user_context, extracted_data):
    """Update user context with extracted data from user message."""
    user_context.update_from_chat(extracted_data)
    session['user_context'] = json.dumps(user_context.model_dump())
    logger.debug("Updated user context in session")
    return user_context


def search_events_for_user(user_context: UserContext) -> List[Event]:
    """Search for events based on user preferences."""
    events = []
    
    # Get user location if available
    location = None
    if user_context.profile.location:
        location = (
            user_context.profile.location.latitude,
            user_context.profile.location.longitude
        )
        logger.info(f"Using user location: {location}")
    else:
        logger.info("No user location available, searching without location")
    
    # Search for events based on theme
    event_theme = user_context.preferences.event_theme
    if event_theme:
        logger.info(f"Searching for events with theme: '{event_theme}'")
        
        # If the theme contains multiple event types, try to split and search for each
        if "," in event_theme:
            all_events = []
            themes = [theme.strip() for theme in event_theme.split(",")]
            logger.info(f"Split event theme into: {themes}")
            
            theme_errors = []
            for theme in themes:
                logger.info(f"Searching for individual theme: '{theme}'")
                try:
                    theme_events = showtimes_service.search_events(
                        query=theme,
                        location=location
                    )
                    logger.info(f"Found {len(theme_events)} events for theme '{theme}'")
                    all_events.extend(theme_events)
                except Exception as e:
                    logger.error(f"Error searching for theme '{theme}': {str(e)}")
                    theme_errors.append(f"{theme}: {str(e)}")
            
            # If we have errors for all themes and no events, raise an exception
            if theme_errors and not all_events:
                error_message = "No events found for any themes. Errors: " + "; ".join(theme_errors)
                logger.error(error_message)
                if not config.USE_MOCK_DATA:
                    raise ValueError(error_message)
            
            # Remove duplicates if any
            seen_ids = set()
            events = []
            for event in all_events:
                if event.id not in seen_ids:
                    seen_ids.add(event.id)
                    events.append(event)
            
            logger.info(f"Total combined events after removing duplicates: {len(events)}")
        else:
            events = showtimes_service.search_events(
                query=event_theme,
                location=location
            )
            logger.info(f"Found {len(events)} events for theme '{event_theme}'")
    else:
        logger.warning("No event theme available to search for events")
    
    return events


def create_event_schedule(events: List[Event], user_context: UserContext) -> EventSchedule:
    """Create an event schedule based on user preferences."""
    schedule = EventSchedule()
    
    # Sort events by rating (if available)
    sorted_events = sorted(
        events,
        key=lambda e: e.rating if e.rating is not None else 0,
        reverse=True
    )
    
    # For Broadway shows, we want to optimize for:
    # 1. Showtimes that don't overlap
    # 2. Minimize travel distance between venues
    # 3. Higher-rated shows
    
    # Check if this is a Broadway search
    is_broadway_search = user_context.preferences.event_theme and 'broadway' in user_context.preferences.event_theme.lower()
    
    if is_broadway_search:
        logger.info("Broadway search detected - creating optimized Broadway route")
        
        # First, filter out events with no showtimes today
        events_with_showtimes = []
        current_time_utc = datetime.now()
        
        for event in sorted_events:
            if not event.showtimes:
                continue
                
            # Check if any showtimes are today (in venue's timezone)
            has_today_showtimes = False
            for showtime in event.showtimes:
                if showtime.start_time.date() == current_time_utc.date():
                    has_today_showtimes = True
                    break
                    
            if has_today_showtimes:
                events_with_showtimes.append(event)
        
        # Sort shows by start time
        events_with_showtimes.sort(key=lambda e: e.showtimes[0].start_time if e.showtimes else datetime.max)
        
        # Take up to 5 events for Broadway itinerary
        selected_events = events_with_showtimes[:5]
        
        # Add events to schedule
        for event in selected_events:
            schedule.add_event(event)
            
        logger.info(f"Created optimized Broadway schedule with {len(selected_events)} events")
    else:
        # Take top events (limit to 3 for non-Broadway searches)
        top_events = sorted_events[:3]
        logger.info(f"Selected top {len(top_events)} events for schedule")
        
        # Add events to schedule
        for event in top_events:
            schedule.add_event(event)
    
    # Calculate total duration including travel time
    if maps_service and user_context.profile.location and len(schedule.events) > 0:
        # Get preferred transport mode or default to walking for Broadway (usually close together)
        transport_mode = "walking" if is_broadway_search else "driving"
        if user_context.preferences.transport_preferences:
            transport_mode = user_context.preferences.transport_preferences[0]
        
        # Create a list of locations starting with user's current location
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
        
        try:
            # Create a navigation plan for all locations, with Broadway-specific handling if appropriate
            navigation_plan = maps_service.create_navigation_plan(
                locations, 
                transport_mode,
                is_broadway=is_broadway_search
            )
            
            # Add the total travel time to the schedule
            schedule.total_duration += navigation_plan.total_duration
            
            # Store the navigation plan in the schedule for later use
            schedule.navigation_plan = navigation_plan
            logger.info(f"Created navigation plan with {len(navigation_plan.routes)} routes")
        except Exception as e:
            logger.error(f"Error creating navigation plan: {str(e)}")
            # Continue without navigation plan
    else:
        logger.info("Skipping navigation plan creation (no location data or maps service)")
    
    return schedule


def validate_schedule(schedule: EventSchedule, user_context: UserContext) -> Dict[str, Any]:
    """Validate the created schedule against user preferences."""
    try:
        # Prepare validation data
        validation_data = {
            "schedule": schedule.to_dict(),
            "user_context": user_context.to_dict()
        }
        
        # Validate using OpenAI
        validation_result = openai_service.validate_event_data(
            [event.to_dict() for event in schedule.events],
            user_context.to_dict()
        )
        
        logger.info(f"Schedule validation result: valid={validation_result.get('is_valid', False)}")
        return validation_result
    except Exception as e:
        logger.error(f"Error validating schedule: {str(e)}")
        # Return a default validation result if there's an error
        return {
            "is_valid": True,  # Assume valid to continue
            "issues": [f"Could not validate schedule: {str(e)}"],
            "suggestions": []
        }


def create_final_response(schedule: EventSchedule, user_context: UserContext, validation_result: Dict[str, Any]) -> str:
    """Create a final response with the validated schedule."""
    try:
        # Check if this is a Broadway search
        is_broadway_search = user_context.preferences.event_theme and 'broadway' in user_context.preferences.event_theme.lower()
        
        # Create a prompt for OpenAI
        prompt = f"""
        Create a friendly, conversational response for the user that includes:
        
        1. A summary of the events in their schedule
        2. The total cost of the events: {schedule.total_cost}
        3. The total duration including travel time: {format_duration(schedule.total_duration)}
        """
        
        if is_broadway_search:
            prompt += """
        
        This is a Broadway shows search. Please emphasize:
        - These are TODAY'S available showtimes (not tomorrow)
        - Highlight the specific showtimes for each show
        - Suggest a logical order to see shows based on their start times
        - Mention that Broadway theaters are generally within walking distance of each other
        - Note if any show is particularly highly rated
        """
        
        # Add navigation details if available
        if hasattr(schedule, 'navigation_plan') and schedule.navigation_plan:
            navigation_details = []
            
            for i, route in enumerate(schedule.navigation_plan.routes):
                from_location = "your current location" if i == 0 else schedule.events[i-1].name
                to_location = schedule.events[i].name
                
                navigation_details.append(
                    f"- From {from_location} to {to_location}:\n"
                    f"  - Distance: {format_distance(route.distance)}\n"
                    f"  - Travel time: {format_duration(route.duration)}\n"
                    f"  - Travel mode: {route.travel_mode.value}"
                )
            
            prompt += f"""
        
        4. Navigation details:
        {chr(10).join(navigation_details)}
        """
        
        prompt += f"""
        
        User preferences:
        {json.dumps(user_context.preferences.model_dump(exclude_none=True), indent=2)}
        
        Events in the schedule:
        {json.dumps([event.to_dict() for event in schedule.events], cls=DateTimeEncoder, indent=2)}
        
        Make the response friendly and conversational, as if you're chatting with the user.
        Include specific navigation instructions between locations.
        """
        
        # Generate response from OpenAI
        response = openai_service.generate_response(prompt)
        
        return response
    except Exception as e:
        logger.error(f"Error creating final response: {str(e)}")
        # Return a simple response if there's an error
        events_text = ", ".join([event.name for event in schedule.events])
        return f"I found these events that might interest you: {events_text}. The total cost is ${schedule.total_cost:.2f}."


@app.route('/api/route', methods=['POST'])
def generate_route():
    """
    Generate a comprehensive route that combines venues, events, and navigation.
    Returns a unified JSON structure for the UI to display an integrated experience.
    """
    try:
        data = request.json
        query = data.get('query', '')
        transport_mode = data.get('transport_mode', 'walking')
        
        logger.info(f"Generating route for query: '{query}', transport mode: {transport_mode}")
        
        # Check if services are available
        if not showtimes_service:
            logger.error("Showtimes service is unavailable")
            return jsonify({
                'error': "Showtimes service unavailable",
                'message': "The event search service is currently unavailable."
            }), 503
            
        if not maps_service:
            logger.error("Maps service is unavailable")
            return jsonify({
                'error': "Maps service unavailable",
                'message': "The routing service is currently unavailable."
            }), 503
        
        # Get or create user context
        user_context = get_or_create_user_context()
        
        # Update user context with the query
        user_context.preferences.event_theme = query
        update_user_context(user_context, {})
        
        # Set transport preferences
        user_context.preferences.transport_preferences = [transport_mode]
        
        # Detect if this is a Broadway search
        is_broadway = 'broadway' in query.lower()
        
        # Search for events
        logger.info(f"Searching for events with query: '{query}'")
        events = search_events_for_user(user_context)
        
        if not events:
            logger.warning(f"No events found for query: '{query}'")
            return jsonify({
                'error': "No events found",
                'message': f"No events were found matching '{query}'.",
                'query': query
            }), 404
        
        logger.info(f"Found {len(events)} events")
        
        # Create an event schedule based on the events
        schedule = create_event_schedule(events, user_context)
        
        # Build the unified route response
        route_data = {
            'query': query,
            'is_broadway': is_broadway,
            'transport_mode': transport_mode,
            'events': [event.to_dict() for event in schedule.events],
            'total_duration': schedule.total_duration,
            'total_cost': schedule.total_cost
        }
        
        # Add navigation data if available
        if hasattr(schedule, 'navigation_plan') and schedule.navigation_plan:
            route_data['navigation'] = {
                'total_distance': schedule.navigation_plan.total_distance,
                'total_travel_time': schedule.navigation_plan.total_duration,
                'routes': []
            }
            
            # Add each route segment
            for i, route in enumerate(schedule.navigation_plan.routes):
                from_location = "Current Location" if i == 0 else schedule.events[i-1].name
                to_location = schedule.events[i].name
                
                route_segment = {
                    'from': {
                        'name': from_location,
                        'location': route.origin
                    },
                    'to': {
                        'name': to_location,
                        'location': route.destination
                    },
                    'distance': route.distance,
                    'duration': route.duration,
                    'travel_mode': route.travel_mode.value,
                    'polyline': route.polyline,
                    'steps': [step.model_dump() for step in route.steps]
                }
                
                route_data['navigation']['routes'].append(route_segment)
        
        logger.info(f"Successfully generated unified route response with {len(schedule.events)} events")
        return jsonify(route_data)
        
    except Exception as e:
        logger.error(f"Error generating route: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': "An error occurred while generating your route."
        }), 500


@app.route('/api/plan', methods=['POST'])
def create_plan():
    """Create a complete plan using OpenAI and verify with Google APIs."""
    try:
        # Extract user input from request
        data = request.json
        query = data.get('query', '')
        transport_mode = data.get('transport_mode', 'transit')
        max_iterations = data.get('max_iterations', 3)
        
        logger.info(f"Generating plan for query: '{query}' with transport: {transport_mode}")
        
        # Make sure we have the required services
        if not openai_service:
            return jsonify({"error": "OpenAI service is not available. Please check your API key."}), 500
        
        if not plan_verifier:
            return jsonify({"error": "Plan verification service is not available. Check Google API keys."}), 500
                
        # Generate initial plan with OpenAI (using web search)
        initial_plan = openai_service.create_initial_plan(query, transport_mode)
        
        if not initial_plan:
            return jsonify({"error": "Failed to generate initial plan"}), 500
        
        # Verify and refine the plan
        iterations = 0
        current_plan = initial_plan
        issues_found = True
        
        verification_history = []
        
        while issues_found and iterations < max_iterations:
            iterations += 1
            logger.info(f"Plan verification iteration {iterations}/{max_iterations}")
            
            # Verify the plan
            verified_plan = plan_verifier.verify_plan(current_plan)
            
            # Record verification results
            verification_step = {
                "iteration": iterations,
                "issues_count": len(verified_plan.get("verification_issues", [])),
                "issues": verified_plan.get("verification_issues", [])
            }
            verification_history.append(verification_step)
            
            # Check if there are any issues
            issues = verified_plan.get("verification_issues", [])
            if not issues:
                logger.info("Plan verified successfully - no issues found")
                issues_found = False
                current_plan = verified_plan
                break
            
            logger.info(f"Verification found {len(issues)} issues. Refining plan...")
            
            # Refine the plan based on verification results
            refined_plan = openai_service.refine_plan(verified_plan, transport_mode)
            
            if not refined_plan:
                logger.warning("Failed to refine plan, using verified plan with issues")
                current_plan = verified_plan
                break
            
            current_plan = refined_plan
        
        # Generate a summary of the plan using OpenAI
        summary = generate_plan_summary(current_plan)
        
        # Format the response
        response = {
            "query": query,
            "transport_mode": transport_mode,
            "iterations": iterations,
            "verification_history": verification_history,
            "plan": current_plan,
            "summary": summary
        }
        
        logger.info(f"Plan generated successfully after {iterations} iterations")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error creating plan: {str(e)}")
        return jsonify({"error": f"Failed to create plan: {str(e)}"}), 500


def generate_plan_summary(plan: Dict[str, Any]) -> str:
    """Generate a text summary of the plan using OpenAI."""
    if not openai_service:
        # If openai service is not available, return a simple summary
        query = plan.get('user_query', 'your request')
        return f"Plan for {query} with {len(plan.get('events', []))} events"
    
    try:
        # Extract query and transport mode from plan if they're available
        query = plan.get('user_query', 'your request')
        transport_mode = plan.get('transport_mode', 'walking')
        
        # Create a summary prompt
        venues_str = "\n".join([f"- {v.get('name')}: {v.get('address')}" for v in plan.get('venues', [])])
        
        events_str = ""
        for e in plan.get('events', []):
            start_time = e.get('start_time', 'Unknown time')
            if isinstance(start_time, str):
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    start_time = dt.strftime("%I:%M %p")
                except ValueError:
                    pass
            
            events_str += f"- {e.get('name')} at {e.get('venue_name')} ({start_time}): ${e.get('price', 'N/A')}\n"
        
        routes_str = "\n".join([
            f"- From {r.get('from')} to {r.get('to')}: {format_distance(r.get('distance_meters', 0))}, {format_duration(r.get('duration_seconds', 0))}"
            for r in plan.get('routes', [])
        ])
        
        total_cost = plan.get('total_cost', 0)
        total_duration = plan.get('total_duration_hours', 0)
        
        prompt = f"""
        Create a concise but friendly summary of this plan for the user query: "{query}"
        
        Venues:
        {venues_str}
        
        Events:
        {events_str}
        
        Routes (using {transport_mode}):
        {routes_str}
        
        Total Cost: ${total_cost}
        Total Duration: {total_duration} hours
        
        Keep it conversational and highlight the most interesting aspects of the plan.
        Include specific information about starting times, locations, and any transit recommendations.
        Limit your response to 3-4 paragraphs maximum.
        """
        
        # Generate the summary
        summary = openai_service.generate_response(prompt)
        return summary
    
    except Exception as e:
        logger.error(f"Error generating plan summary: {str(e)}")
        return f"Plan for {query} with {len(plan.get('events', []))} events"


@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """Return metadata about the application configuration."""
    return jsonify({
        "version": config.VERSION,
        "debug_mode": config.DEBUG,
        "maps_api_key_set": bool(config.GOOGLE_MAPS_API_KEY),
        "places_api_key_set": bool(config.GOOGLE_SHOWTIMES_API_KEY),
        "openai_api_key_set": bool(config.OPENAI_API_KEY)
    })


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Return the current application settings."""
    return jsonify({
        'DEBUG': config.DEBUG,
        'VERSION': config.VERSION,
        'HOST': config.HOST,
        'PORT': config.PORT,
        'OPENAI_MODEL': config.OPENAI_MODEL
    })


def format_restaurant_response(restaurants, plan=None):
    """Format restaurant data into a human-readable response."""
    if not restaurants or len(restaurants) == 0:
        return "I'm sorry, but I couldn't find any restaurants matching your criteria. Would you like to try a different type of cuisine or location?"
    
    # Extract base response text from plan if available
    base_response = ""
    if plan and isinstance(plan, dict):
        base_response = plan.get("response", "")
    
    # If no base response, create a generic one
    if not base_response:
        base_response = "Here are some restaurants that match your criteria:"
    
    # Add restaurant details
    restaurant_texts = []
    for i, restaurant in enumerate(restaurants[:5], 1):
        name = restaurant.get("name", "Unknown restaurant")
        address = restaurant.get("address", "Address not available")
        rating = restaurant.get("rating", "Not rated")
        
        # Format price level if available
        price_level = restaurant.get("price_level")
        price_text = ""
        if price_level:
            if isinstance(price_level, int):
                price_text = f" • Price: {'$' * price_level}"
            else:
                price_text = f" • Price: {price_level}"
        
        restaurant_text = f"{i}. {name} ({rating}/5{price_text})\n   {address}"
        restaurant_texts.append(restaurant_text)
    
    # Combine all parts into a final response
    combined_response = f"{base_response}\n\n" + "\n\n".join(restaurant_texts)
    
    # Convert to dictionary format for the API response
    return {
        "text_response": combined_response,
        "events": restaurants,
        "schedule": {}
    }


def process_message(user_message, user_location=None):
    """Process an incoming message and generate a response."""
    try:
        logger.info(f"Processing message: '{user_message}'")
        
        # Check if message is empty
        if not user_message:
            return {
                "text_response": "Please provide a message.",
                "events": [],
                "schedule": {}
            }
        
        # Detect if this is a food query
        is_food_query = False
        for food_term in ['food', 'eat', 'restaurant', 'dinner', 'lunch', 'breakfast', 'cuisine', 'hungry']:
            if food_term in user_message.lower():
                is_food_query = True
                break
                
        if is_food_query:
            logger.info("Detected food query.")
            # First get a response from OpenAI to structure our search
            system_prompt = SYSTEM_PROMPT
            plan_response = openai_service.ask_model(system_prompt, user_message, user_location)
            logger.info(f"OpenAI plan response: {plan_response}")
            
            # Parse the response to extract cuisine type and other info
            try:
                plan = json.loads(plan_response)
                cuisine_type = plan.get("cuisine", "")
                response_text = plan.get("response", "")
                logger.info(f"Extracted cuisine type from OpenAI: '{cuisine_type}'")
                
                # Use the cuisine type from OpenAI for the restaurant search
                if cuisine_type:
                    logger.info(f"Looking for {cuisine_type} restaurants based on OpenAI plan")
                    
                    try:
                        # Convert UserLocation to tuple format (lat, lng) if available
                        location_tuple = None
                        if user_location:
                            location_tuple = (user_location.latitude, user_location.longitude)
                            
                        # Search for restaurants with the specific cuisine type
                        restaurants = showtimes_service.find_restaurants(f"{cuisine_type} restaurants", location_tuple)
                        
                        if restaurants:
                            # Format the restaurant data for the response
                            final_response = format_restaurant_response(restaurants, plan)
                            return final_response
                        else:
                            # No restaurants found, but we had a valid API call
                            return {
                                "text_response": f"I'm sorry, but I couldn't find any {cuisine_type} restaurants matching your criteria. Would you like to try a different type of cuisine or location?",
                                "events": [],
                                "schedule": {}
                            }
                    except Exception as e:
                        logger.error(f"Error finding restaurants: {str(e)}")
                        error_msg = str(e)
                        
                        # Check for common API issues
                        if "REQUEST_DENIED" in error_msg and "not authorized" in error_msg:
                            return {
                                "text_response": "I'm sorry, but I encountered an issue with the Google Places API. The API key is not authorized to use the Places service. Please ensure your Google API key has the Places API enabled in the Google Cloud Console.",
                                "events": [],
                                "schedule": {}
                            }
                        elif "OVER_QUERY_LIMIT" in error_msg:
                            return {
                                "text_response": "I'm sorry, but the Google Places API query limit has been exceeded. Please try again later.",
                                "events": [],
                                "schedule": {}
                            }
                        else:
                            # Generic API error
                            return {
                                "text_response": f"I found information about {cuisine_type} restaurants, but I'm having trouble retrieving specific details due to an API error. Error details: {error_msg}",
                                "events": [],
                                "schedule": {}
                            }
                else:
                    # No cuisine type specified, try a generic search
                    try:
                        # Convert UserLocation to tuple format
                        location_tuple = None
                        if user_location:
                            location_tuple = (user_location.latitude, user_location.longitude)
                            
                        # Generic restaurant search
                        restaurants = showtimes_service.find_restaurants(user_message, location_tuple)
                        
                        if restaurants:
                            final_response = format_restaurant_response(restaurants, plan)
                            return final_response
                        else:
                            # No restaurants found but API call was successful
                            return {
                                "text_response": "I'm sorry, but I couldn't find any restaurants matching your criteria. Would you like to try a different type of cuisine or location?",
                                "events": [],
                                "schedule": {}
                            }
                    except Exception as e:
                        logger.error(f"Error in generic restaurant search: {str(e)}")
                        # API error - provide a helpful response
                        return {
                            "text_response": "I'm having trouble retrieving restaurant information right now. Please try again later or check Google Maps for dining options near your location.",
                            "events": [],
                            "schedule": {}
                        }
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing OpenAI response: {str(e)}")
                # JSON parse error - provide a fallback
                return {
                    "text_response": "I'm sorry, but I encountered an error processing your request. Please try again with a more specific request, such as 'Find me Italian restaurants near Times Square'.",
                    "events": [],
                    "schedule": {}
                }
        elif "broadway" in user_message.lower() or "show" in user_message.lower() or "theater" in user_message.lower() or "play" in user_message.lower():
            logger.info("Detected Broadway show query.")
            
            try:
                # Always consult OpenAI first to create a plan
                plan_response = openai_service.ask_model(
                    system_message=SYSTEM_PROMPT,
                    user_message=user_message,
                    location=user_location
                )
                
                logger.info(f"OpenAI plan response: {plan_response}")
                
                try:
                    # Try to parse the plan
                    plan = json.loads(plan_response)
                    
                    # Search for Broadway shows matching the user's query
                    try:
                        if user_location:
                            # Convert UserLocation to tuple format (lat, lng)
                            location_tuple = (user_location.latitude, user_location.longitude)
                            shows = showtimes_service.search_events(user_message, location_tuple)
                        else:
                            shows = showtimes_service.search_events(user_message)
                        
                        if shows:
                            # Refine plan with show data
                            refined_plan = openai_service.refine_plan_with_data(plan, shows=shows)
                            
                            try:
                                # Try to parse the refined plan
                                if isinstance(refined_plan, str):
                                    refined_plan_dict = json.loads(refined_plan)
                                else:
                                    refined_plan_dict = refined_plan
                                    
                                # Format the response
                                response = refined_plan_dict.get("response", "")
                                events = refined_plan_dict.get("events", [])
                                schedule = refined_plan_dict.get("schedule", {})
                                
                                # Return response with all components
                                return {
                                    "text_response": response,
                                    "events": events,
                                    "schedule": schedule
                                }
                            except json.JSONDecodeError as e:
                                logger.error(f"Error parsing refined plan: {str(e)}")
                                # Return basic response with shows if parsing fails
                                basic_response = "Here are some Broadway shows that might interest you:\n\n"
                                for i, show in enumerate(shows[:5], 1):
                                    basic_response += f"{i}. {show.get('name', 'Unknown show')}\n"
                                    if 'location' in show:
                                        basic_response += f"   Location: {show['location']}\n"
                                    if 'date' in show:
                                        basic_response += f"   Date: {show['date']}\n"
                                    basic_response += "\n"
                                return {
                                    "text_response": basic_response,
                                    "events": shows,
                                    "schedule": {}
                                }
                        else:
                            # No shows found
                            return {
                                "text_response": "I'm sorry, but I couldn't find any Broadway shows matching your criteria. Would you like to try a different search?",
                                "events": [],
                                "schedule": {}
                            }
                    except Exception as e:
                        logger.error(f"Error searching for Broadway shows: {str(e)}")
                        error_msg = str(e)
                        
                        # Provide specific error messages based on the type of error
                        if "REQUEST_DENIED" in error_msg and "not authorized" in error_msg:
                            return {
                                "text_response": "I'm sorry, but I encountered an issue with the Google Places API. The API key is not authorized to use the Places service. Please ensure your Google API key has the Places API enabled in the Google Cloud Console.",
                                "events": [],
                                "schedule": {}
                            }
                        elif "OVER_QUERY_LIMIT" in error_msg:
                            return {
                                "text_response": "I'm sorry, but the Google Places API query limit has been exceeded. Please try again later.",
                                "events": [],
                                "schedule": {}
                            }
                        elif "Invalid JSON payload" in error_msg or "400" in error_msg:
                            return {
                                "text_response": "I'm sorry, but there was an error with the format of the request to the Google Places API. This might be due to a change in the API format. Please check the API documentation for updates.",
                                "events": [],
                                "schedule": {}
                            }
                        else:
                            return {
                                "text_response": f"I'm sorry, but I encountered an error while searching for Broadway shows. Error details: {error_msg}",
                                "events": [], 
                                "schedule": {}
                            }
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing plan response: {str(e)}")
                    logger.error(f"Response that failed to parse: {plan_response}")
                    
                    # Try to extract any useful information from the malformed JSON
                    # Fallback to a direct show search
                    shows = showtimes_service.search_events(user_message)
                    
                    if shows:
                        basic_response = "Here are some Broadway shows that might interest you:\n\n"
                        for i, show in enumerate(shows[:5], 1):
                            basic_response += f"{i}. {show.get('name', 'Unknown show')}\n"
                            if 'location' in show:
                                basic_response += f"   Location: {show['location']}\n"
                            if 'date' in show:
                                basic_response += f"   Date: {show['date']}\n"
                            basic_response += "\n"
                        return {
                            "text_response": basic_response,
                            "events": shows,
                            "schedule": {}
                        }
                    else:
                        return {
                            "text_response": "I'm sorry, but I couldn't find any Broadway shows matching your criteria. Would you like to try a different search?",
                            "events": [],
                            "schedule": {}
                        }
            
            except Exception as e:
                logger.error(f"Error processing Broadway show query: {str(e)}")
                # Provide a more specific error message based on the exception
                return {
                    "text_response": f"I'm sorry, but I encountered an error while processing your request for Broadway shows. Error details: {str(e)}",
                    "events": [],
                    "schedule": {}
                }
        else:
            # Generic handler for other queries - always consult OpenAI first
            logger.info("Generic query detected - consulting OpenAI")
            
            try:
                # Create a plan with OpenAI
                plan_response = openai_service.ask_model(
                    system_message=SYSTEM_PROMPT,
                    user_message=user_message,
                    location=user_location
                )
                
                logger.info(f"OpenAI plan response: {plan_response}")
                
                try:
                    # Parse the plan
                    plan = json.loads(plan_response)
                    response = plan.get("response", "")
                    events = plan.get("events", [])
                    schedule = plan.get("schedule", {})
                    
                    return {
                        "text_response": response,
                        "events": events,
                        "schedule": schedule
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing plan response: {str(e)}")
                    # Extract response from malformed JSON
                    # Find the response part if possible
                    match = re.search(r'"response"\s*:\s*"([^"]+)"', plan_response)
                    if match:
                        response = match.group(1)
                        return {
                            "text_response": response,
                            "events": [],
                            "schedule": {}
                        }
                    else:
                        return {
                            "text_response": "I'm not sure how to help with that specific request. Could you provide more details or try asking about Broadway shows or restaurant recommendations?",
                            "events": [],
                            "schedule": {}
                        }
            except Exception as e:
                logger.error(f"Error processing generic query: {str(e)}")
                return {
                    "text_response": "I'm sorry, but I encountered an error while processing your request. Please try again.",
                    "events": [],
                    "schedule": {}
                }
    
    except Exception as e:
        logger.error(f"Error in process_message: {str(e)}")
        return {
            "text_response": "I'm sorry, but I encountered an error while processing your request. Please try again.",
            "events": [],
            "schedule": {}
        }


def run_app():
    """Run the Flask application."""
    # Initialize all services
    init_services()
    
    # Setup Flask app
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    
    # Configure logging for Flask
    if app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Determine host based on debug mode
    if app.debug:
        host = '0.0.0.0'  # Accessible from other devices on network in debug mode
    else:
        host = '127.0.0.1'  # Only accessible locally in production
    
    # Run the Flask app
    app.run(host=host, port=5000, debug=app.debug)


if __name__ == "__main__":
    # Check command line arguments
    parser = argparse.ArgumentParser(description='Run the Broadway Show & Event Planner application')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()
    
    # Set debug mode based on command line argument
    app.debug = args.debug
    
    # Set up logging based on debug mode
    if app.debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.info("Running in DEBUG mode")
    else:
        logging.basicConfig(level=logging.INFO)
        logger.setLevel(logging.INFO)
        logger.info("Running in PRODUCTION mode")
    
    # Log details about the environment and configuration
    logger.info(f"Python version: {sys.version}")
    logger.info(f"OpenAI API key set: {check_openai_key()}")
    logger.info(f"Google Maps API key set: {check_gmaps_key()}")
    logger.info(f"Google Showtimes API key set: {check_showtimes_key()}")
    logger.info(f"Mock data disabled: {not config.USE_MOCK_DATA if hasattr(config, 'USE_MOCK_DATA') else True}")
    
    # Run the app
    run_app() 