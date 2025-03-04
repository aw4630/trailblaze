import json
from typing import Dict, Any, Optional, List
import anthropic
import config
from anthropic import Anthropic
from datetime import datetime

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class ClaudeService:
    """Service for interacting with Claude AI."""
    
    def __init__(self):
        """Initialize the Claude service with API key."""
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.CLAUDE_MODEL
        self.max_tokens = config.MAX_TOKENS
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response from Claude AI."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system="You are a helpful assistant providing information about events and navigation.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error generating response from Claude: {e}")
            return f"Error: {str(e)}"
    
    def process_user_query(self, prompt: str) -> Dict[str, Any]:
        """Process a user query and extract structured information."""
        system_prompt = """
        You are an AI assistant helping users find events and navigate to them.
        Extract the following information from the user's query:
        - Event theme or type (be specific - if they mention movies, art galleries, or shows, include those exact terms)
        - Location information (city, neighborhood, etc.)
        - Available time (start and end)
        - Budget
        - Transportation preferences
        
        If the user mentions multiple types of events (like "movie, art gallery, and broadway show"), 
        combine them into a single event_theme string like "movie, art gallery, broadway show".
        
        If they mention a specific location like "new york" or "Washington square campus", include that in the event_theme.
        
        IMPORTANT: For event themes, be very liberal in extracting anything that could be considered an event interest.
        If the user mentions wanting to see a movie, extract "movie" as the event theme.
        If the user mentions art galleries, extract "art gallery" as part of the event theme.
        If the user mentions shows or Broadway, extract those terms as part of the event theme.
        Even vague references to entertainment activities should be extracted.
        
        Return the information in JSON format with the following structure:
        {
            "event_theme": "string or null",
            "available_time_start": "HH:MM format or null",
            "available_time_end": "HH:MM format or null",
            "budget": number or null,
            "transport_preferences": ["list", "of", "preferences"] or []
        }

        IMPORTANT: If the message directly contains event types such as "Broadway show," "art gallery," "movie,"
        make sure to set the event_theme accordingly, even if no other context is provided.
        """
        
        try:
            print(f"DEBUG - Sending user message to process: {prompt}")
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract JSON from response
            response_text = message.content[0].text
            print(f"DEBUG - Claude response for processing: {response_text}")
            
            # Find JSON in the response (it might be surrounded by markdown code blocks)
            # First look for markdown JSON blocks
            if "```json" in response_text:
                json_block_start = response_text.find("```json") + 7
                json_block_end = response_text.find("```", json_block_start)
                if json_block_end > json_block_start:
                    json_str = response_text[json_block_start:json_block_end].strip()
                    print(f"DEBUG - Extracted JSON from markdown block: {json_str}")
                    return json.loads(json_str)
            
            # Fall back to looking for JSON without markdown
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                print(f"DEBUG - Extracted raw JSON: {json_str}")
                parsed_json = json.loads(json_str)
                
                # Special case: Direct mention of events with no additional context
                if prompt.lower().strip() in ["broadway show, art gallery, and movie", 
                                             "movie, art gallery, and broadway show",
                                             "art gallery, broadway show, and movie"]:
                    parsed_json["event_theme"] = prompt.lower().strip()
                    print(f"DEBUG - Special case: Setting event theme to: {parsed_json['event_theme']}")
                
                return parsed_json
            else:
                # Manual parsing for simple inputs that should be event themes
                if any(event_type in prompt.lower() for event_type in ["movie", "art gallery", "broadway", "show"]):
                    print(f"DEBUG - JSON not found but event keywords detected in: {prompt}")
                    return {
                        "event_theme": prompt.strip(),
                        "available_time_start": None,
                        "available_time_end": None, 
                        "budget": None,
                        "transport_preferences": []
                    }
                
                # Fallback if JSON not found
                print(f"DEBUG - No JSON found in response: {response_text}")
                return {
                    "event_theme": None,
                    "available_time_start": None,
                    "available_time_end": None,
                    "budget": None,
                    "transport_preferences": []
                }
                
        except Exception as e:
            print(f"Error processing user query: {e}")
            # Return empty structure on error
            return {
                "event_theme": None,
                "available_time_start": None,
                "available_time_end": None,
                "budget": None,
                "transport_preferences": []
            }
    
    def validate_event_data(self, events: List[Dict[str, Any]], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event data for conflicts and accuracy."""
        validation_prompt = f"""
        Please validate the following event data against the user's preferences and requirements:
        
        User Context:
        {json.dumps(user_context, indent=2, cls=DateTimeEncoder)}
        
        Event Data:
        {json.dumps(events, indent=2, cls=DateTimeEncoder)}
        
        Check for the following issues:
        1. Time conflicts between events
        2. Budget compatibility
        3. Accessibility compatibility
        4. Travel time feasibility
        
        Return a JSON response with the following structure:
        {{
            "is_valid": true/false,
            "issues": ["list", "of", "issues"],
            "suggestions": ["list", "of", "suggestions"]
        }}
        """
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system="You are a validation assistant that checks event schedules against user preferences.",
                messages=[
                    {"role": "user", "content": validation_prompt}
                ]
            )
            
            # Extract JSON from response
            response_text = message.content[0].text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback if JSON not found
                return {
                    "is_valid": False,
                    "issues": ["Failed to parse validation response"],
                    "suggestions": []
                }
                
        except Exception as e:
            print(f"Error validating event data: {e}")
            return {
                "is_valid": False,
                "issues": [f"Error: {str(e)}"],
                "suggestions": []
            } 