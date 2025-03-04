#!/usr/bin/env python
"""
Broadway Show & Event Planner - Enhanced with OpenAI-First approach
Helps users find entertainment events and create itineraries
"""

import os
import logging
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Import services
from services.openai_service import OpenAIService
from services.google_maps_service import GoogleMapsService
from services.google_showtimes_service import GoogleShowtimesService
from services.plan_verification import PlanVerifier

# Import models
from models.embedding import EmbeddingProcessor
from models.event import Event, EventSchedule
from models.user import UserContext, UserPreferences

# Import utilities
from utils.helpers import parse_time_string, extract_budget, format_duration, format_distance

# Import configuration
import sys
sys.path.append("config")
import config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize services (global vars so they can be accessed in routes)
openai_service = None
maps_service = None
showtimes_service = None
embedding_processor = None
plan_verifier = None

# Setup the OpenAI service
try:
    openai_service = OpenAIService()
    logger.info("OpenAI service initialized successfully")
except Exception as e:
    error_traceback = traceback.format_exc()
    logger.error(f"Failed to initialize OpenAI service: {str(e)}")
    logger.error(f"Traceback: {error_traceback}")

# Setup Google Maps service
try:
    maps_service = GoogleMapsService()
    logger.info("Google Maps service initialized successfully")
except Exception as e:
    error_traceback = traceback.format_exc()
    logger.error(f"Failed to initialize Google Maps service: {str(e)}")
    logger.error(f"Traceback: {error_traceback}")

# Setup Google Showtimes service
try:
    showtimes_service = GoogleShowtimesService()
    logger.info("Google Showtimes service initialized successfully")
except Exception as e:
    error_traceback = traceback.format_exc()
    logger.error(f"Failed to initialize Google Showtimes service: {str(e)}")
    logger.error(f"Traceback: {error_traceback}")

# Setup Embedding Processor
try:
    embedding_processor = EmbeddingProcessor()
    logger.info("Embedding processor initialized successfully")
except Exception as e:
    error_traceback = traceback.format_exc()
    logger.error(f"Failed to initialize Embedding processor: {str(e)}")
    logger.error(f"Traceback: {error_traceback}")

# Setup Plan Verifier if Maps and Showtimes services are available
if maps_service and showtimes_service:
    try:
        plan_verifier = PlanVerifier(maps_service, showtimes_service)
        logger.info("Plan verifier initialized successfully")
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to initialize Plan verifier: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")

@app.route('/')
def index():
    """Render the main page."""
    # Check if services are available
    services_status = {
        "openai": openai_service is not None,
        "maps": maps_service is not None,
        "showtimes": showtimes_service is not None,
        "embedding": embedding_processor is not None
    }
    
    if not all(services_status.values()):
        logger.warning(f"Some services are unavailable: {services_status}")
    
    return render_template('index.html')

@app.route('/ai-planner')
def ai_planner():
    """Render the AI-driven planner page."""
    return render_template('ai_planner.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process a chat message and return a response using OpenAI-first approach."""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        logger.info(f"Received message: '{user_message}'")
        
        # Get or create user context
        user_context = get_or_create_user_context()
        
        # Check if we can use the OpenAI service and plan verifier
        if not openai_service:
            return jsonify({
                "error": "OpenAI service is not available",
                "response": "I'm sorry, but the OpenAI service is currently unavailable. Please try again later."
            }), 503
        
        # Create a plan using OpenAI-first approach
        return create_openai_first_plan(user_message, user_context)
            
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error processing chat message: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")
        return jsonify({
            "error": f"Error processing your message: {str(e)}",
            "response": "I'm sorry, but I encountered an error while processing your request. Please try again."
        }), 500

def create_openai_first_plan(user_message, user_context):
    """Create a plan using the OpenAI-first approach and return a chat response."""
    try:
        logger.info("Using OpenAI-first approach for planning")
        
        # Default to walking if no transport preferences
        transport_mode = "walking"
        if hasattr(user_context, 'preferences') and hasattr(user_context.preferences, 'transport_mode'):
            transport_mode = user_context.preferences.transport_mode
        
        # Create context dictionary for OpenAI
        context_dict = {
            "user_id": user_context.user_id,
            "current_time": datetime.now().isoformat(),
            "location": user_context.location.to_dict() if user_context.location else None,
            "preferences": {
                "interests": user_context.preferences.interests,
                "price_range": user_context.preferences.price_range,
                "transport_mode": transport_mode
            }
        }
        
        # Step 1: Generate an initial plan using OpenAI
        logger.info("Generating initial plan using OpenAI")
        initial_plan = openai_service.create_initial_plan(user_message, context_dict)
        
        # If there was an error in creating the plan, return a helpful response
        if 'error' in initial_plan:
            logger.error(f"Error creating initial plan: {initial_plan.get('error')}")
            return jsonify({
                "response": "I'm sorry, but I couldn't create a plan based on your request. Please try again with more details.",
                "events": [],
                "schedule": {}
            })
        
        # Step 2: Verify the plan if plan_verifier is available
        max_iterations = 2  # Limit refinement iterations
        iterations = 0
        has_issues = True
        verified_plan = initial_plan
        
        while plan_verifier and has_issues and iterations < max_iterations:
            logger.info(f"Verifying plan (iteration {iterations + 1})")
            verified_plan = plan_verifier.verify_plan(verified_plan)
            
            issues = verified_plan.get('verification', {}).get('issues', [])
            has_issues = len(issues) > 0
            
            # Break if no issues
            if not has_issues:
                logger.info("Plan verification completed with no issues")
                break
                
            logger.info(f"Found {len(issues)} issues with plan, refining...")
            
            # Refine the plan based on verification results
            refined_plan = openai_service.refine_plan(verified_plan, verified_plan)
            verified_plan = refined_plan
            
            iterations += 1
        
        # Step 3: Generate a natural language summary of the plan
        logger.info("Generating plan summary")
        plan_summary = generate_plan_summary(verified_plan, user_message, transport_mode)
        verified_plan['summary'] = plan_summary
        
        # Step 4: Format the response for the chat interface
        response_data = format_plan_for_chat(verified_plan, user_message, iterations)
        
        logger.info(f"Successfully created plan after {iterations} iterations")
        return jsonify(response_data)
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error in OpenAI-first planning: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")
        return jsonify({
            "response": "I'm sorry, but I encountered an error while creating your plan. Please try again with different details.",
            "events": [],
            "schedule": {}
        })

def format_plan_for_chat(plan, user_message, iterations):
    """Format a plan for the chat interface response."""
    
    # Extract events for the response
    events_list = []
    for event in plan.get('events', []):
        venue_name = event.get('venue_name', '')
        venue = next((v for v in plan.get('venues', []) if v.get('name') == venue_name), {})
        
        # Format times for display
        start_time = event.get('start_time', '')
        end_time = event.get('end_time', '')
        formatted_start = start_time
        formatted_end = end_time
        
        try:
            if start_time:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                formatted_start = start_dt.strftime('%I:%M %p')
            if end_time:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                formatted_end = end_dt.strftime('%I:%M %p')
        except Exception as e:
            logger.warning(f"Error formatting times: {str(e)}")
        
        # Get verification status and issues
        verification = event.get('verification', {})
        
        event_obj = {
            'name': event.get('name', ''),
            'venue': venue_name,
            'address': venue.get('address', ''),
            'start_time': formatted_start,
            'raw_start_time': start_time,
            'end_time': formatted_end,
            'raw_end_time': end_time,
            'price': event.get('price', 0),
            'duration_minutes': event.get('duration_minutes', 0),
            'type': event.get('type', ''),
            'verified': verification.get('verified', False),
            'issues': verification.get('issues', [])
        }
        events_list.append(event_obj)
    
    # Sort events by start time
    events_list.sort(key=lambda x: x.get('raw_start_time', ''))
    
    # Extract routes for the response
    routes_list = []
    for route in plan.get('routes', []):
        # Format travel details
        travel_mode = route.get('travel_mode', 'WALKING')
        distance_meters = route.get('distance_meters', 0)
        duration_seconds = route.get('duration_seconds', 0)
        
        # Convert to more readable formats
        distance_miles = distance_meters / 1609.34  # Convert meters to miles
        duration_minutes = duration_seconds / 60  # Convert seconds to minutes
        
        # Get transit details if available
        transit_details = []
        steps = route.get('steps', [])
        for step in steps:
            if step.get('travel_mode') == 'TRANSIT' and 'transit' in step:
                transit = step.get('transit', {})
                transit_details.append({
                    'line': transit.get('line', ''),
                    'vehicle': transit.get('vehicle', ''),
                    'departure_stop': transit.get('departure_stop', ''),
                    'arrival_stop': transit.get('arrival_stop', ''),
                    'num_stops': transit.get('num_stops', 0)
                })
        
        # Get verification status and issues
        verification = route.get('verification', {})
        
        route_obj = {
            'from': route.get('origin_name', ''),
            'to': route.get('destination_name', ''),
            'travel_mode': travel_mode,
            'distance_meters': distance_meters,
            'distance_miles': round(distance_miles, 2),
            'duration_seconds': duration_seconds,
            'duration_minutes': round(duration_minutes, 1),
            'steps': steps,
            'transit_details': transit_details,
            'verified': verification.get('verified', False),
            'issues': verification.get('issues', [])
        }
        routes_list.append(route_obj)
    
    # Create a schedule structure with timing, routing and pricing
    current_time = datetime.now()
    schedule = {
        'current_time': current_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'formatted_time': current_time.strftime('%I:%M %p'),
        'events': events_list,
        'routes': routes_list,
        'total_duration_hours': plan.get('total_duration_hours', 0),
        'total_duration_minutes': plan.get('total_duration_minutes', 0),
        'total_cost': plan.get('total_cost', 0)
    }
    
    # Include issues if any
    all_issues = plan.get('verification', {}).get('issues', [])
    if all_issues:
        schedule['issues'] = all_issues
    
    # Generate HTML-friendly timeline
    timeline = []
    
    # Interleave events and routes to create a complete timeline
    all_items = []
    
    # Add events first
    for event in events_list:
        all_items.append({
            'type': 'event',
            'data': event,
            'time': event.get('raw_start_time', '')
        })
    
    # Add routes that connect events
    for route in routes_list:
        # Find the event that happens before this route
        for event in events_list:
            if event.get('venue') == route.get('from'):
                # Add route after this event's end time
                all_items.append({
                    'type': 'route',
                    'data': route,
                    'time': event.get('raw_end_time', '')  # Use event end time
                })
                break
    
    # Sort the combined timeline by time
    all_items.sort(key=lambda x: x.get('time', ''))
    
    # Now format for display
    for item in all_items:
        if item['type'] == 'event':
            event = item['data']
            timeline.append({
                'type': 'event',
                'time': event.get('start_time', ''),
                'title': event.get('name', ''),
                'location': event.get('venue', ''),
                'duration': event.get('duration_minutes', 0),
                'verified': event.get('verified', False)
            })
        else:
            route = item['data']
            timeline_item = {
                'type': 'route',
                'from': route.get('from', ''),
                'to': route.get('to', ''),
                'travel_mode': route.get('travel_mode', ''),
                'duration_minutes': route.get('duration_minutes', 0),
                'distance_miles': route.get('distance_miles', 0),
                'verified': route.get('verified', False)
            }
            
            # Add transit details if available
            if route.get('transit_details'):
                timeline_item['transit'] = route.get('transit_details')
            
            timeline.append(timeline_item)
    
    return {
        "response": plan.get('summary', "Here's a plan based on your request."),
        "events": events_list,
        "routes": routes_list,
        "schedule": schedule,
        "timeline": timeline,
        "iterations": iterations,
        "plan": plan  # Include the full plan data
    }

@app.route('/api/profile', methods=['POST'])
def update_profile():
    """Update user profile information."""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Get or create user context
        user_context = get_or_create_user_context()
        
        # Update profile fields
        if 'name' in data:
            user_context.name = data['name']
        
        if 'email' in data:
            user_context.email = data['email']
            
        if 'location' in data:
            location = data['location']
            user_context.location.latitude = location.get('latitude')
            user_context.location.longitude = location.get('longitude')
            user_context.location.address = location.get('address')
            
        logger.info(f"Updated profile for user: {user_id}")
        
        return jsonify({
            "status": "success",
            "profile": {
                "name": user_context.name,
                "email": user_context.email,
                "location": user_context.location.to_dict() if user_context.location else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({
            "error": f"Error updating profile: {str(e)}"
        }), 500

@app.route('/api/preferences', methods=['POST'])
def update_preferences():
    """Update user preferences."""
    try:
        data = request.json
        
        # Get or create user context
        user_context = get_or_create_user_context()
        
        # Update preferences
        if 'interests' in data:
            user_context.preferences.interests = data['interests']
            
        if 'price_range' in data:
            user_context.preferences.price_range = data['price_range']
            
        if 'transport_mode' in data:
            user_context.preferences.transport_mode = data['transport_mode']
            
        logger.info(f"Updated preferences for user")
        
        return jsonify({
            "status": "success",
            "preferences": {
                "interests": user_context.preferences.interests,
                "price_range": user_context.preferences.price_range,
                "transport_mode": user_context.preferences.transport_mode
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        return jsonify({
            "error": f"Error updating preferences: {str(e)}"
        }), 500

@app.route('/api/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences."""
    try:
        # Get or create user context
        user_context = get_or_create_user_context()
        
        return jsonify({
            "status": "success",
            "preferences": {
                "interests": user_context.preferences.interests,
                "price_range": user_context.preferences.price_range,
                "transport_mode": user_context.preferences.transport_mode
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        return jsonify({
            "error": f"Error getting preferences: {str(e)}"
        }), 500

@app.route('/api/service-status', methods=['GET'])
def service_status():
    """Check the status of all services."""
    try:
        # Check OpenAI service
        openai_status = "available"
        openai_error = None
        if not openai_service:
            openai_status = "unavailable"
            openai_error = "Service not initialized"
        
        # Check Google Maps service
        maps_status = "available"
        maps_error = None
        if not maps_service:
            maps_status = "unavailable"
            maps_error = "Service not initialized"
        
        # Check Google Showtimes service
        showtimes_status = "available"
        showtimes_error = None
        if not showtimes_service:
            showtimes_status = "unavailable"
            showtimes_error = "Service not initialized"
        
        # Check Embedding service
        embedding_status = "available"
        embedding_error = None
        if not embedding_processor:
            embedding_status = "unavailable"
            embedding_error = "Service not initialized"
        
        # Check Plan Verifier
        verifier_status = "available"
        verifier_error = None
        if not plan_verifier:
            verifier_status = "unavailable"
            verifier_error = "Service not initialized"
        
        return jsonify({
            "status": "success",
            "services": {
                "openai": {
                    "status": openai_status,
                    "error": openai_error
                },
                "maps": {
                    "status": maps_status,
                    "error": maps_error
                },
                "showtimes": {
                    "status": showtimes_status,
                    "error": showtimes_error
                },
                "embedding": {
                    "status": embedding_status,
                    "error": embedding_error
                },
                "plan_verifier": {
                    "status": verifier_status,
                    "error": verifier_error
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error checking service status: {str(e)}")
        return jsonify({
            "error": f"Error checking service status: {str(e)}"
        }), 500

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Get debug information."""
    try:
        # Check if DEBUG is enabled in environment
        debug_enabled = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        if not debug_enabled:
            return jsonify({
                "status": "error",
                "message": "Debug mode is not enabled. Set DEBUG=True in .env file to enable."
            }), 403
        
        # Get API keys (masked for security)
        openai_key = mask_api_key(os.environ.get('OPENAI_API_KEY', ''))
        maps_key = mask_api_key(os.environ.get('GOOGLE_MAPS_API_KEY', ''))
        showtimes_key = mask_api_key(os.environ.get('GOOGLE_SHOWTIMES_API_KEY', ''))
        
        # Get service initialization status
        services_status = {
            "openai": openai_service is not None,
            "maps": maps_service is not None,
            "showtimes": showtimes_service is not None,
            "embedding": embedding_processor is not None,
            "plan_verifier": plan_verifier is not None
        }
        
        # Get mock data status
        mock_data = os.environ.get('USE_MOCK_DATA', 'False').lower() == 'true'
        
        return jsonify({
            "status": "success",
            "debug_info": {
                "api_keys": {
                    "openai": openai_key,
                    "maps": maps_key,
                    "showtimes": showtimes_key
                },
                "services": services_status,
                "mock_data": mock_data,
                "environment": {
                    "python_version": os.sys.version,
                    "timestamp": datetime.now().isoformat()
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting debug info: {str(e)}")
        return jsonify({
            "error": f"Error getting debug info: {str(e)}"
        }), 500

def mask_api_key(key):
    """Mask API key for security when displaying in debug info."""
    if not key:
        return "Not set"
    
    # Only show first 4 and last 6 characters
    if len(key) > 10:
        return f"{key[:4]}{'*' * (len(key) - 10)}{key[-6:]}"
    
    return "*" * len(key)

def get_or_create_user_context() -> UserContext:
    """Get or create a user context for the current session."""
    # In a real app, this would use session cookies or auth tokens
    # For simplicity, we'll create a new context each time
    
    user_context = UserContext(user_id="user_123")
    logger.info("Created new user context")
    
    return user_context

@app.route('/api/plan', methods=['POST'])
def create_plan():
    """
    Generate a comprehensive plan using OpenAI with verification.
    This endpoint implements a verification loop to ensure the plan is accurate.
    """
    try:
        # Get request data
        data = request.json
        user_query = data.get('query', '')
        transport_mode = data.get('transport_mode', 'walking')
        max_iterations = data.get('max_iterations', 3)  # Default to 3 iterations max
        
        logger.info(f"Received plan request: '{user_query}', transport: {transport_mode}")
        
        # Validate services are available
        if not openai_service:
            return jsonify({
                "success": False,
                "error": "OpenAI service is not available"
            }), 503
            
        if not plan_verifier:
            return jsonify({
                "success": False,
                "error": "Plan verification service is not available"
            }), 503
        
        # Create user context for the request
        user_context = {
            "query": user_query,
            "current_time": datetime.now().isoformat(),
            "transport_mode": transport_mode,
            "location": {
                "city": "New York",  # Default to NYC for Broadway shows
                "latitude": 40.7580,  # Times Square coordinates
                "longitude": -73.9855
            }
        }
        
        # Generate initial plan
        logger.info("Generating initial plan using OpenAI")
        current_plan = openai_service.create_initial_plan(user_query, user_context)
        
        # Check for errors
        if 'error' in current_plan:
            logger.error(f"Failed to create initial plan: {current_plan.get('error')}")
            return jsonify({
                "success": False,
                "error": f"Failed to create initial plan: {current_plan.get('error')}"
            })
        
        # Verify and refine the plan in a loop
        iterations = 0
        perfect_plan = False
        
        while not perfect_plan and iterations < max_iterations:
            # Verify the current plan
            logger.info(f"Verifying plan (iteration {iterations + 1})")
            verified_plan = plan_verifier.verify_plan(current_plan)
            
            # Check if there are issues
            issues = verified_plan.get('verification', {}).get('issues', [])
            
            if not issues:
                logger.info("Plan verification completed with no issues")
                perfect_plan = True
                break
                
            logger.info(f"Found {len(issues)} issues with plan, refining...")
            
            # Refine the plan based on verification results
            refined_plan = openai_service.refine_plan(current_plan, verified_plan)
            current_plan = refined_plan
            
            iterations += 1
        
        # Generate a summary of the final plan
        logger.info("Generating plan summary")
        plan_summary = generate_plan_summary(current_plan, user_query, transport_mode)
        current_plan['summary'] = plan_summary
        
        # Return the plan
        return jsonify({
            "success": True,
            "plan": current_plan,
            "query": user_query,
            "transport_mode": transport_mode,
            "iterations": iterations,
            "perfect": perfect_plan
        })
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error generating plan: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")
        return jsonify({
            "success": False,
            "error": f"Error generating plan: {str(e)}"
        }), 500

def generate_plan_summary(plan: Dict[str, Any], query: str, transport_mode: str) -> str:
    """Generate a natural language summary of the plan."""
    try:
        # Extract the key information for the summary
        venues = plan.get('venues', [])
        events = plan.get('events', [])
        routes = plan.get('routes', [])
        total_cost = plan.get('total_cost', 0)
        total_duration = plan.get('total_duration_hours', 0)
        
        # Create a prompt for OpenAI
        venues_info = "\n".join([f"- {v.get('name')}: {v.get('address')}" for v in venues])
        
        events_info = ""
        for event in sorted(events, key=lambda e: e.get('start_time', '0')):
            venue_name = event.get('venue_name', '')
            start_time = event.get('start_time', '')
            formatted_time = start_time
            try:
                if start_time:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%I:%M %p')
            except:
                pass
            
            events_info += f"- {event.get('name')} at {venue_name} at {formatted_time}\n"
        
        routes_info = "\n".join([
            f"- From {r.get('from')} to {r.get('to')}: {r.get('duration_seconds', 0) // 60} mins by {r.get('travel_mode', transport_mode)}"
            for r in routes
        ])
        
        prompt = f"""
        Create a conversational summary of this plan for the user's query: "{query}"
        
        Venues:
        {venues_info}
        
        Events:
        {events_info}
        
        Routes:
        {routes_info}
        
        Total duration: {total_duration} hours
        Total cost: ${total_cost if isinstance(total_cost, (int, float)) else ''}
        
        Make the summary engaging and conversational. Highlight the main attractions, timing, and any special details.
        Make sure to include practical information about timing, transportation ({transport_mode}), and logistics.
        """
        
        # Call OpenAI for the summary
        response = openai_service.generate_response(prompt)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating plan summary: {str(e)}")
        return f"Here's your plan for {query}. The itinerary includes {len(plan.get('events', []))} events with an estimated total duration of {plan.get('total_duration_hours', 0)} hours."

# Run the app
if __name__ == '__main__':
    # Log configuration info
    logger.info(f"OpenAI API Key configured: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}")
    openai_model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    logger.info(f"Using OpenAI model: {openai_model}")
    logger.info(f"Mock data is {'ENABLED' if os.environ.get('USE_MOCK_DATA', '').lower() == 'true' else 'DISABLED'}")
    
    # Run the Flask app
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting application on {host}:{port}")
    app.run(debug=True, host=host, port=port) 