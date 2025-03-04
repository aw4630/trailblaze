import openai
import logging
import json
from typing import Dict, Any, List, Optional, Union
import traceback
import config
from datetime import datetime
import os
import re
import time

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
        self.logger = logging.getLogger("openai_service")
        # Enhanced logging for OpenAI calls
        self.enable_detailed_logging = True
        self.logger.info(f"OpenAI Service initialized with model: {self.model}")
    
    def log_api_call(self, request_data, response_data, method_name):
        """Log detailed information about OpenAI API calls"""
        if not self.enable_detailed_logging:
            return
            
        self.logger.info(f"====== OpenAI API Call: {method_name} ======")
        self.logger.info(f"Model: {self.model}")
        self.logger.info(f"Request: {json.dumps(request_data, indent=2)}")
        
        # For response, limit the output size to avoid overly verbose logs
        if isinstance(response_data, dict):
            # Clone and truncate content for logging if it's too large
            response_for_log = response_data.copy() if hasattr(response_data, 'copy') else response_data
            if 'choices' in response_for_log and response_for_log['choices']:
                for choice in response_for_log['choices']:
                    if 'message' in choice and 'content' in choice['message']:
                        content = choice['message']['content']
                        if len(content) > 500:
                            choice['message']['content'] = content[:250] + "... [truncated] ..." + content[-250:]
            
            self.logger.info(f"Response: {json.dumps(response_for_log, indent=2)}")
        else:
            self.logger.info(f"Response: {response_data}")
        
        self.logger.info("=" * 50)

    def _call_openai_api(self, messages, model="gpt-4o", max_tokens=2000, temperature=0.7, response_format=None):
        """Make a call to the OpenAI API with retry and error handling."""
        try:
            logger.info(f"Calling OpenAI API with model: {model}, max_tokens: {max_tokens}")
            
            # Set up API call parameters
            params = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            
            # Add response_format if provided
            if response_format:
                params["response_format"] = response_format
                
            # Make the API call with the format that works with the installed OpenAI version
            response = openai.ChatCompletion.create(**params)
            
            # For compatibility - ensure we're returning a structure with the content
            # accessible via response.choices[0].message.content
            # Check if it's already in the expected object format
            if hasattr(response, 'choices') and hasattr(response.choices[0], 'message'):
                return response
            
            # If it's a dictionary (older OpenAI client or newer one depending on version)
            # create a compatible object structure
            class ResponseWrapper:
                def __init__(self, content):
                    self.content = content

                def __getattr__(self, name):
                    if name in self.__dict__:
                        return self.__dict__[name]
                    return None

            class ChoiceWrapper:
                def __init__(self, message):
                    self.message = message

            class ResponseObj:
                def __init__(self, choices):
                    self.choices = choices
            
            if isinstance(response, dict) and 'choices' in response and response['choices']:
                message_content = response['choices'][0]['message']['content']
                message_obj = ResponseWrapper(message_content)
                choice_obj = ChoiceWrapper(message_obj)
                return ResponseObj([choice_obj])
            
            # Fallback for unexpected response formats
            logger.warning("Unexpected response format from OpenAI, creating fallback response")
            message_obj = ResponseWrapper("I'm sorry, I couldn't generate a response.")
            choice_obj = ChoiceWrapper(message_obj)
            return ResponseObj([choice_obj])
            
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise

    def generate_response(self, prompt: str) -> str:
        """Generate a response to a prompt using OpenAI."""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            
            request_data = {
                "model": self.model,
                "messages": messages
            }
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages
            )
            
            # Log the API call
            self.log_api_call(request_data, response, "generate_response")
            
            # Extract the response content
            if response and 'choices' in response and response['choices']:
                return response['choices'][0]['message']['content']
            else:
                logger.warning("Empty or invalid response from OpenAI")
                return "I'm sorry, I couldn't generate a response."
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}"
    
    def create_initial_plan(self, query: str, user_context: Union[Dict[str, Any], str] = None) -> Dict[str, Any]:
        """Create an initial plan using OpenAI."""
        try:
            logger.info(f"Creating initial plan for query: '{query}'")
            
            # Check if this is a food/restaurant query that needs clarification
            if self._is_food_query(query) and not self._has_specific_cuisine(query):
                # Return a conversation request instead of a plan
                return {
                    "conversation_needed": True,
                    "type": "food_clarification",
                    "response": "I'd be happy to help you find a great place for dinner! " +
                               "What type of cuisine are you interested in? For example, Italian, Japanese, " +
                               "American, vegetarian, etc. Also, do you have any price range preferences?"
                }
            
            # Format user context
            if isinstance(user_context, dict):
                context_str = json.dumps(user_context, cls=DateTimeEncoder)
            else:
                context_str = str(user_context) if user_context else "{}"
            
            # Format date for OpenAI
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            # Build the system prompt
            system_prompt = """You are an AI assistant that creates accurate travel and event plans using web search capabilities."""
            
            # Build the user prompt
            user_prompt = f"""
            I need a complete itinerary plan for a user with the following request:
            "{query}"
            
            User context: {context_str}
            
            Today's date is {today_date}. The user is in New York City.
            
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
            
            # Call OpenAI API with specific parameters
            response = self._call_openai_api(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            if response and 'content' in response:
                try:
                    plan = json.loads(response['content'])
                    logger.info(f"Successfully created initial plan with {len(plan.get('venues', []))} venues and {len(plan.get('events', []))} events")
                    return plan
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse response from OpenAI as JSON: {str(e)}")
                    logger.error(f"Response content: {response['content']}")
                    return {"error": "Failed to create a valid plan. The AI response was not in the expected format."}
            else:
                logger.error("No valid response from OpenAI")
                return {"error": "Failed to get a response from OpenAI."}
                
        except Exception as e:
            logger.error(f"Error creating initial plan: {str(e)}")
            return {"error": f"An error occurred: {str(e)}"}
            
    def _is_food_query(self, query: str) -> bool:
        """Check if the query is related to food or restaurants."""
        food_keywords = ["dinner", "lunch", "breakfast", "food", "restaurant", "eat", "dining"]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in food_keywords)
        
    def _has_specific_cuisine(self, query: str) -> bool:
        """Check if the query specifies a cuisine type."""
        cuisine_types = ["italian", "french", "chinese", "japanese", "mexican", "indian", 
                        "thai", "vietnamese", "greek", "mediterranean", "spanish", 
                        "korean", "american", "bbq", "vegetarian", "vegan", "seafood"]
        query_lower = query.lower()
        return any(cuisine in query_lower for cuisine in cuisine_types)
    
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

    def ask_model(self, system_message, user_message, location=None, max_retries=3):
        """Ask the OpenAI model a question using the provided system and user messages."""
        try:
            # Include location information if available
            location_info = ""
            if location:
                location_info = f"The user's current location is: Latitude {location.latitude}, Longitude {location.longitude}"
                if location.address:
                    location_info += f", Address: {location.address}"
            
            # Build conversation with system and user messages
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{user_message}\n\n{location_info}"}
            ]
            
            # Track retries
            attempts = 0
            
            while attempts < max_retries:
                try:
                    logger.info(f"Sending request to OpenAI with messages: {messages}")
                    
                    # Reduce max_tokens if we've had truncation issues
                    max_tokens = 2000
                    if attempts > 0:
                        # Gradually reduce tokens to avoid truncation
                        max_tokens = 1600 - (attempts * 400)
                    
                    # Make API call with retry logic
                    response = self._call_openai_api(
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=0.7,
                        response_format={"type": "json_object"}
                    )
                    
                    # Extract response content - response should now be an object with proper attributes
                    content = response.choices[0].message.content
                    logger.info(f"Response from OpenAI: {content}")
                    
                    # Validate JSON
                    try:
                        # Just test if it's valid JSON - don't actually convert
                        json.loads(content)
                        # If we get here, JSON is valid
                        return content
                    except json.JSONDecodeError as e:
                        logger.warning(f"OpenAI response was not valid JSON: {str(e)}")
                        # If this is not the last attempt, try again
                        if attempts < max_retries - 1:
                            attempts += 1
                            logger.info(f"Retrying OpenAI request (attempt {attempts+1}/{max_retries})")
                            continue
                        else:
                            # On final attempt, fix the response format
                            logger.info("Final attempt, trying to fix JSON format")
                            # Try to extract valid JSON portion
                            match = re.search(r'(\{.*\})', content, re.DOTALL)
                            if match:
                                possible_json = match.group(1)
                                try:
                                    # Validate extracted JSON
                                    json.loads(possible_json)
                                    return possible_json
                                except:
                                    pass
                            
                            # If extraction failed, return a minimal valid JSON
                            return json.dumps({
                                "response": "I found some options that might interest you, but I'm having trouble formatting the results. Let me share what I found.",
                                "events": [],
                                "schedule": {}
                            })
                            
                    # If we get here, we have valid JSON
                    return content
                    
                except Exception as e:
                    logger.error(f"Error in OpenAI API call: {str(e)}")
                    attempts += 1
                    if attempts >= max_retries:
                        raise
                    time.sleep(1)  # Wait before retrying
            
            raise Exception(f"Failed to get response after {max_retries} attempts")
            
        except Exception as e:
            logger.error(f"Error in ask_model: {str(e)}")
            # Return a JSON string with an error message
            return json.dumps({
                "response": "I'm sorry, but I encountered an error while processing your request. Please try again.",
                "events": [],
                "schedule": {}
            }) 

    def refine_plan_with_data(self, plan, restaurants=None, shows=None):
        """Refine a plan with actual data from APIs."""
        try:
            # Convert plan to string if it's not already
            if not isinstance(plan, str):
                plan_str = json.dumps(plan)
            else:
                plan_str = plan
                
            # Create a system message explaining the task
            system_message = """
            You are an AI assistant that helps refine event plans. 
            You'll be given an initial plan and real data from APIs. 
            Your task is to update the plan with the real data to make it more accurate and useful.
            Always return your response in valid JSON format with the structure from the original plan.
            """
            
            # Create user message with the plan and data
            user_message = f"Here is the initial plan: {plan_str}\n\n"
            
            # Add restaurant data if provided
            if restaurants:
                user_message += "Here are the restaurant options found:\n"
                for i, restaurant in enumerate(restaurants[:5], 1):
                    name = restaurant.get('name', 'Unknown')
                    address = restaurant.get('address', 'Address not available')
                    rating = restaurant.get('rating', 'No rating')
                    
                    user_message += f"{i}. {name}\n"
                    user_message += f"   Address: {address}\n"
                    user_message += f"   Rating: {rating}/5\n\n"
            
            # Add show data if provided
            if shows:
                user_message += "Here are the Broadway shows found:\n"
                for i, show in enumerate(shows[:5], 1):
                    name = show.get('name', 'Unknown show')
                    location = show.get('location', 'Location not available')
                    date = show.get('date', 'Date not available')
                    
                    user_message += f"{i}. {name}\n"
                    user_message += f"   Location: {location}\n"
                    user_message += f"   Date: {date}\n\n"
            
            # Request to update the plan
            user_message += "Please update the plan with these real options. Make it more specific and actionable. Return your response in valid JSON format with the same structure as the original plan."
            
            # Get response from OpenAI
            response = self.ask_model(
                system_message=system_message,
                user_message=user_message
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error refining plan with data: {str(e)}")
            # Return the original plan if refinement fails
            return plan 