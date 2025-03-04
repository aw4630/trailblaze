import openai
import logging
import json
from typing import Dict, Any, List, Optional
import traceback
import config
from datetime import datetime

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder for datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize the OpenAI service with API key."""
        openai.api_key = config.OPENAI_API_KEY
        self.model = config.OPENAI_MODEL
        logger.info(f"OpenAI service initialized with model: {self.model}")
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response to a prompt using OpenAI."""
        try:
            logger.debug(f"Generating OpenAI response for prompt: {prompt[:100]}...")
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides detailed information about events, venues, and travel routes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            logger.debug(f"OpenAI response: {response_text[:100]}...")
            return response_text
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error generating OpenAI response: {str(e)}")
            logger.error(f"Traceback: {error_traceback}")
            return f"I'm sorry, but I encountered an error while generating a response: {str(e)}"
    
    def create_initial_plan(self, user_query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an initial plan using OpenAI's web browsing capability.
        This creates a complete itinerary based on user's request.
        """
        try:
            logger.info(f"Creating initial plan for query: '{user_query}'")
            
            # Format the user context for the prompt
            context_str = json.dumps(user_context, cls=DateTimeEncoder, indent=2)
            
            # Create a prompt that asks OpenAI to search the web and create a plan
            prompt = f"""
            I need a complete itinerary plan for a user with the following request:
            "{user_query}"
            
            User context: {context_str}
            
            Today's date is {datetime.now().strftime('%Y-%m-%d')}. The user is in New York City.
            
            Please search the web to find:
            1. Real venues that match this request (restaurants, theaters, etc.)
            2. Actual showtimes or availability for today
            3. Realistic travel times between locations
            
            Create a detailed plan with:
            - Specific venue names with real addresses
            - Actual showtimes for events (if applicable)
            - Realistic price estimates
            - Travel time estimates between locations
            
            Return your plan as a JSON object with the following structure:
            {{
                "venues": [
                    {{
                        "name": "Venue Name",
                        "address": "Full Address",
                        "latitude": 40.7123, // Approximate is fine
                        "longitude": -73.9456, // Approximate is fine
                        "rating": 4.5, // If available
                        "price_level": 2, // 1-4 scale if available
                        "description": "Brief description"
                    }}
                ],
                "events": [
                    {{
                        "name": "Event Name",
                        "venue_name": "Venue Name", // Must match a venue above
                        "start_time": "2023-10-06T19:30:00", // ISO format
                        "end_time": "2023-10-06T22:00:00", // ISO format
                        "price": 120.00, // Estimated price
                        "description": "Brief description"
                    }}
                ],
                "routes": [
                    {{
                        "from": "Starting Venue Name",
                        "to": "Destination Venue Name",
                        "travel_mode": "walking", // walking, driving, transit
                        "distance_meters": 1200,
                        "duration_seconds": 900,
                        "description": "Brief walking directions"
                    }}
                ],
                "total_duration_hours": 5.5,
                "total_cost": 250.00
            }}
            
            Only return the JSON with no other explanation.
            """
            
            # Call OpenAI with web search capability
            logger.debug("Calling OpenAI to create initial plan with web search")
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that creates accurate travel and event plans using web search capabilities."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content.strip()
            logger.debug(f"Initial plan response: {response_text[:200]}...")
            
            # Parse the JSON response
            try:
                # Clean up the JSON string if it contains markdown formatting
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "", 1)
                if response_text.endswith("```"):
                    response_text = response_text.replace("```", "", 1)
                
                plan_data = json.loads(response_text.strip())
                logger.info(f"Successfully created initial plan with {len(plan_data.get('venues', []))} venues and {len(plan_data.get('events', []))} events")
                return plan_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI plan response: {str(e)}")
                logger.error(f"Response text: {response_text}")
                return {
                    "error": "Failed to parse plan data",
                    "raw_response": response_text
                }
                
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error creating initial plan: {str(e)}")
            logger.error(f"Traceback: {error_traceback}")
            return {
                "error": f"Failed to create initial plan: {str(e)}"
            }
    
    def refine_plan(self, original_plan: Dict[str, Any], verified_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine a plan based on verification results from Google APIs.
        This method takes the verification issues and asks OpenAI to fix them.
        
        Args:
            original_plan: The original plan generated by OpenAI
            verified_plan: The plan after verification with Google APIs
            
        Returns:
            A refined plan addressing the verification issues
        """
        try:
            # Extract issues from the verified plan
            issues = verified_plan.get('verification', {}).get('issues', [])
            
            if not issues:
                logger.info("No issues to refine in the plan")
                return verified_plan
            
            # Get current time for time-based adjustments
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            
            # Create a prompt for OpenAI to refine the plan
            prompt = f"""
            You need to refine an itinerary plan based on verification against real-world data.
            
            CURRENT TIME: {current_time}
            
            Original Plan:
            {json.dumps(original_plan, indent=2)}
            
            Verification Issues:
            {json.dumps(issues, indent=2)}
            
            Please fix these issues by:
            1. Adjusting event timing to ensure feasibility (considering real-world timing constraints)
            2. Correcting venue information when needed
            3. Ensuring there's sufficient time for travel between venues (using the route durations provided)
            4. Accounting for realistic meal durations (minimum 90 mins for dinner, 60 mins for lunch)
            5. Adding appropriate buffer times (30 mins before shows, 15 mins before dining)
            
            Special Timing Rules:
            - Broadway shows typically require 30 minutes buffer time before the start
            - Dinner at a restaurant typically takes 90 minutes minimum
            - Lunch typically takes 60 minutes minimum
            - Always consider public transit waiting times (5-15 minutes) when using TRANSIT mode
            - For transit routes, include specific subway/bus lines in the plan
            
            Return a fully updated JSON plan that fixes ALL the identified issues. The JSON should have the exact same structure as the original plan.
            Use the same keys and format, but fix the problematic values.

            IMPORTANT: Your response must be a valid JSON object and ONLY the JSON object. 
            Do not include anything else in your response - no explanations or text outside the JSON object.
            """
            
            # Call OpenAI with the prompt
            logger.info(f"Refining plan to address {len(issues)} issues")
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert travel planner AI that creates realistic itineraries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more focused corrections
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            response_content = response.choices[0].message.content
            
            try:
                refined_plan = json.loads(response_content)
                
                # Ensure the refined plan has a verification section
                if 'verification' not in refined_plan:
                    refined_plan['verification'] = {
                        'timestamp': datetime.now().isoformat(),
                        'issues': []
                    }
                
                # Keep track of which issues were addressed
                refined_plan['verification']['previous_issues'] = issues
                
                logger.info("Successfully refined plan")
                return refined_plan
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {str(e)}")
                logger.error(f"Response content: {response_content}")
                
                # Return the verified plan with an additional issue
                verified_plan['verification']['issues'].append(f"Failed to refine plan: {str(e)}")
                return verified_plan
                
        except Exception as e:
            logger.error(f"Error refining plan: {str(e)}")
            
            # Return the verified plan with an additional issue
            verified_plan['verification']['issues'].append(f"Failed to refine plan: {str(e)}")
            return verified_plan
    
    def process_user_query(self, user_message: str) -> Dict[str, Any]:
        """Process a user query to extract structured information."""
        try:
            logger.debug(f"Sending user message to process: {user_message}")
            
            system_prompt = """
            Extract structured information from the user's message about event preferences.
            Return a JSON object with the following fields (use null if not present):
            - event_theme: Type of event they're interested in (movie, show, gallery, etc.)
            - available_time_start: When they can start (ISO datetime or null)
            - available_time_end: When they need to end (ISO datetime or null)
            - budget: Their budget as a number (or null)
            - transport_preferences: List of preferred transport modes (walking, driving, transit, etc.)
            
            Respond ONLY with the JSON object, no explanations.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            logger.debug(f"OpenAI response for processing: {response_text}")
            
            # Clean up the response to ensure it's valid JSON
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "", 1)
            if response_text.endswith("```"):
                response_text = response_text.replace("```", "", 1)
            
            response_text = response_text.strip()
            logger.debug(f"Extracted raw JSON: {response_text}")
            
            # Parse the JSON
            extracted_data = json.loads(response_text)
            return extracted_data
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error processing user query with OpenAI: {str(e)}")
            logger.error(f"Traceback: {error_traceback}")
            # Return empty data if there's an error
            return {
                "event_theme": None,
                "available_time_start": None,
                "available_time_end": None,
                "budget": None,
                "transport_preferences": []
            }
    
    def validate_event_data(self, events: List[Dict[str, Any]], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that events match user preferences."""
        try:
            # Prepare the prompt for OpenAI
            events_json = json.dumps(events, cls=DateTimeEncoder)
            user_context_json = json.dumps(user_context, cls=DateTimeEncoder)
            
            prompt = f"""
            Validate if these events match the user's preferences:
            
            User preferences:
            {user_context_json}
            
            Events:
            {events_json}
            
            Generate a JSON response with these fields:
            - is_valid: true or false
            - issues: array of strings describing why events don't match preferences (empty if valid)
            - suggestions: array of strings with alternative suggestions
            
            Only respond with the JSON.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a validation assistant that checks if events match user preferences."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up the response to ensure it's valid JSON
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "", 1)
            if response_text.endswith("```"):
                response_text = response_text.replace("```", "", 1)
            
            response_text = response_text.strip()
            
            # Parse the JSON
            validation_result = json.loads(response_text)
            return validation_result
        except Exception as e:
            logger.error(f"Error validating event data with OpenAI: {str(e)}")
            # Return a default validation result if there's an error
            return {
                "is_valid": True,  # Assume valid to continue
                "issues": [f"Could not validate events: {str(e)}"],
                "suggestions": []
            } 