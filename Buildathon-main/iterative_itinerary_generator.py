#!/usr/bin/env python3
"""
Iterative Itinerary Generator

This script:
1. Takes a user request for an itinerary
2. Sends it to OpenAI for generation
3. Validates the generated itinerary
4. If validation fails, sends the feedback back to OpenAI for correction
5. Repeats until a valid itinerary is generated or max attempts reached
"""

import os
import sys
import json
import logging
import traceback
import argparse
from typing import Dict, Any, List, Optional
import time

# Add project paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("config")

# Import configuration
try:
    import config
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    print("ERROR: Missing configuration or .env file")
    sys.exit(1)

# Import OpenAI
try:
    import openai
    openai.api_key = config.OPENAI_API_KEY
except ImportError:
    print("ERROR: OpenAI package not installed. Run: pip install openai")
    sys.exit(1)

# Import the validator
from test_itinerary_validator import ItineraryVerifier, process_openai_request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('iterative_generator.log')
    ]
)
logger = logging.getLogger("iterative_generator")

class IterativeGenerator:
    """Generates itineraries iteratively with feedback"""
    
    def __init__(self, request_data: Dict[str, Any], max_attempts: int = 3, real_api: bool = False):
        """Initialize the generator"""
        self.request_data = request_data
        self.max_attempts = max_attempts
        self.use_real_api = real_api
        self.verifier = ItineraryVerifier(force_real_api=real_api)
        
        # Track all attempts
        self.attempts = []
        self.best_itinerary = None
        self.best_verification = None
        
    def run(self) -> Dict[str, Any]:
        """Run the iterative generation process"""
        
        for attempt in range(1, self.max_attempts + 1):
            logger.info(f"Attempt {attempt}/{self.max_attempts} to generate a valid itinerary")
            
            # Generate or improve itinerary
            if attempt == 1 or not self.best_itinerary:
                # First attempt - generate new itinerary
                itinerary = self._generate_itinerary()
            else:
                # Subsequent attempts - improve with feedback
                itinerary = self._improve_itinerary(self.best_itinerary, self.best_verification)
            
            # Validate the itinerary
            verification_result = self._validate_itinerary(itinerary)
            
            # Store attempt
            self.attempts.append({
                "attempt": attempt,
                "itinerary": itinerary,
                "verification": verification_result
            })
            
            # Check if valid
            if verification_result["is_feasible"]:
                logger.info(f"Successfully generated a valid itinerary on attempt {attempt}")
                self.best_itinerary = itinerary
                self.best_verification = verification_result
                break
            
            # Track best itinerary so far (with fewest issues)
            if not self.best_verification or verification_result["total_issues"] < self.best_verification["total_issues"]:
                self.best_itinerary = itinerary
                self.best_verification = verification_result
                logger.info(f"Found better itinerary with {verification_result['total_issues']} issues")
            
            # If this is the last attempt, try to fix it directly
            if attempt == self.max_attempts and not verification_result["is_feasible"]:
                logger.info("Last attempt - trying to fix itinerary directly")
                try:
                    fixed_itinerary = self.verifier.fix_itinerary(itinerary, verification_result)
                    fixed_verification = self._validate_itinerary(fixed_itinerary)
                    
                    if fixed_verification["is_feasible"] or fixed_verification["total_issues"] < verification_result["total_issues"]:
                        self.best_itinerary = fixed_itinerary
                        self.best_verification = fixed_verification
                        logger.info(f"Direct fix improved itinerary to {fixed_verification['total_issues']} issues")
                        
                        # Add as an extra attempt
                        self.attempts.append({
                            "attempt": attempt + 1,
                            "itinerary": fixed_itinerary,
                            "verification": fixed_verification
                        })
                except Exception as e:
                    logger.error(f"Error during direct fix: {str(e)}")
        
        # Return the best itinerary and all attempts
        return {
            "final_itinerary": self.best_itinerary, 
            "verification": self.best_verification,
            "is_valid": self.best_verification["is_feasible"],
            "attempts": self.attempts,
            "total_attempts": len(self.attempts)
        }
    
    def _generate_itinerary(self) -> Dict[str, Any]:
        """Generate a new itinerary using OpenAI"""
        logger.info("Generating new itinerary with OpenAI")
        
        # Add schema guidance to the request
        request_with_schema = self._add_schema_guidance(self.request_data)
        
        # Call OpenAI API to generate itinerary
        return process_openai_request(request_with_schema)
    
    def _improve_itinerary(self, itinerary: Dict[str, Any], verification: Dict[str, Any]) -> Dict[str, Any]:
        """Improve an existing itinerary based on validation feedback"""
        logger.info("Sending validation feedback to OpenAI to improve itinerary")
        
        # Format feedback for OpenAI
        feedback = self._format_feedback_for_openai(verification)
        
        # Create system message
        system_message = (
            "You are a travel itinerary planning assistant. Your task is to fix issues in an existing itinerary "
            "based on validation feedback. Ensure your response is a complete, valid JSON object that follows "
            "the required schema and addresses all the issues mentioned in the feedback."
        )
        
        # Create user prompt with the itinerary and feedback
        user_prompt = (
            f"Please fix the following itinerary according to the validation feedback below. "
            f"The itinerary should be for {self.request_data.get('routeName', 'a trip')} in New York City "
            f"with the theme {self.request_data.get('theme', 'general sightseeing')}.\n\n"
            f"CURRENT ITINERARY (needs fixing):\n{json.dumps(itinerary, indent=2)}\n\n"
            f"VALIDATION FEEDBACK (issues to fix):\n{feedback}\n\n"
            f"Please provide a complete fixed JSON object with all required fields and proper formatting. "
            f"Make sure all events have id, name, description, start_time, end_time, venue_name, and cost fields. "
            f"All venues must have name, address, latitude, longitude, and opening_hours fields. "
            f"All dates and times should be in ISO format (YYYY-MM-DDThh:mm:ss)."
        )
        
        try:
            # Set API key directly (for older OpenAI version 0.27.x)
            openai.api_key = config.OPENAI_API_KEY
            
            logger.info("Calling OpenAI API to fix itinerary issues")
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            # Extract response content
            ai_response = response.choices[0].message.content
            logger.info(f"Received improved itinerary from OpenAI (first 100 chars): {ai_response[:100]}...")
            
            # Parse JSON response
            try:
                improved_itinerary = json.loads(ai_response)
                logger.info("Successfully parsed improved itinerary as JSON")
                return improved_itinerary
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in improved itinerary: {str(e)}")
                
                # Try to extract JSON from the response using regex
                import re
                json_match = re.search(r'```json\n(.*?)\n```', ai_response, re.DOTALL)
                if json_match:
                    try:
                        improved_itinerary = json.loads(json_match.group(1))
                        logger.info("Successfully parsed JSON from code block")
                        return improved_itinerary
                    except json.JSONDecodeError:
                        logger.error("Failed to parse JSON from code block")
                
                # If we can't get valid JSON, return the original itinerary
                logger.warning("Returning original itinerary due to JSON parsing errors")
                return itinerary
                
        except Exception as e:
            logger.error(f"Error calling OpenAI to improve itinerary: {str(e)}")
            logger.error(traceback.format_exc())
            return itinerary
    
    def _validate_itinerary(self, itinerary: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an itinerary using the ItineraryVerifier"""
        logger.info("Validating itinerary")
        
        try:
            verification_result = self.verifier.verify_itinerary(itinerary)
            logger.info(f"Validation result: {'VALID' if verification_result['is_feasible'] else 'INVALID'} with {verification_result['total_issues']} issues")
            return verification_result
        except Exception as e:
            logger.error(f"Error validating itinerary: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Return a basic error result
            return {
                "is_feasible": False,
                "total_issues": 1,
                "all_issues": [f"Validation error: {str(e)}"],
                "details": {
                    "validation_error": {
                        "is_feasible": False,
                        "issues": [str(e)]
                    }
                }
            }
    
    def _format_feedback_for_openai(self, verification_result: Dict[str, Any]) -> str:
        """Format the verification results into clear instructions for OpenAI"""
        feedback = []
        
        # Format issue categories
        if verification_result["details"].get("format", {}).get("issues"):
            feedback.append("FORMAT ISSUES:")
            for issue in verification_result["details"]["format"]["issues"]:
                feedback.append(f"- {issue}")
            feedback.append("Please fix the JSON format issues above first.\n")
        
        if verification_result["details"].get("venue_hours", {}).get("issues"):
            feedback.append("VENUE HOURS ISSUES:")
            for issue in verification_result["details"]["venue_hours"]["issues"]:
                feedback.append(f"- {issue}")
            feedback.append("Please adjust event times to occur within venue operating hours.\n")
        
        if verification_result["details"].get("travel_times", {}).get("issues"):
            feedback.append("TRAVEL TIME ISSUES:")
            for issue in verification_result["details"]["travel_times"]["issues"]:
                feedback.append(f"- {issue}")
            feedback.append("Please allow more time between events or choose venues closer together.\n")
        
        if verification_result["details"].get("activity_durations", {}).get("issues"):
            feedback.append("ACTIVITY DURATION ISSUES:")
            for issue in verification_result["details"]["activity_durations"]["issues"]:
                feedback.append(f"- {issue}")
            feedback.append("Please adjust event durations to be more realistic.\n")
        
        if verification_result["details"].get("buffer_times", {}).get("issues"):
            feedback.append("BUFFER TIME ISSUES:")
            for issue in verification_result["details"]["buffer_times"]["issues"]:
                feedback.append(f"- {issue}")
            feedback.append("Please ensure events don't overlap and have sufficient buffer times.\n")
        
        if verification_result["details"].get("overall_timing", {}).get("issues"):
            feedback.append("OVERALL TIMING ISSUES:")
            for issue in verification_result["details"]["overall_timing"]["issues"]:
                feedback.append(f"- {issue}")
            feedback.append("Please adjust the overall timing of the itinerary.\n")
        
        # Add detailed schema guidance
        feedback.append("REQUIRED SCHEMA:")
        feedback.append("1. Each EVENT must include ALL of these fields:")
        feedback.append("   - id: A unique identifier (e.g., 'event1', 'event2')")
        feedback.append("   - name: Name of the event")
        feedback.append("   - description: Description of the event")
        feedback.append("   - start_time: ISO format date and time (e.g., '2023-08-15T19:00:00')")
        feedback.append("   - end_time: ISO format date and time (e.g., '2023-08-15T22:00:00')")
        feedback.append("   - venue_name: Must match EXACTLY with a venue name in the venues array")
        feedback.append("   - cost: Numeric cost in USD (e.g., 120.00)")
        
        feedback.append("2. Each VENUE must include ALL of these fields:")
        feedback.append("   - name: Name of the venue (must match venue_name in events)")
        feedback.append("   - address: Full street address")
        feedback.append("   - latitude: Numeric latitude coordinate (e.g., 40.7580)")
        feedback.append("   - longitude: Numeric longitude coordinate (e.g., -73.9855)")
        feedback.append("   - opening_hours: Hours of operation (e.g., '9:00 AM - 11:00 PM')")
        feedback.append("   - place_id: A unique identifier (can be made up for this exercise)")
        
        feedback.append("3. For a Broadway-themed itinerary, remember:")
        feedback.append("   - Broadway shows typically start at 7:00 PM or 8:00 PM and last 2.5-3 hours")
        feedback.append("   - Include pre-show dining with at least 1.5 hours before showtime")
        feedback.append("   - The Theater District is concentrated around Times Square")
        feedback.append("   - Allow at least 30 minutes for travel between venues in Manhattan")
        
        return "\n".join(feedback)
    
    def _add_schema_guidance(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add schema guidance to the request"""
        enhanced_request = request_data.copy()
        
        # Add schema guidance to the custom prompt
        schema_guidance = (
            "Make sure to format your response as a valid JSON object with the following structure:\n"
            "- Each EVENT must have: id, name, description, start_time (ISO format), end_time (ISO format), venue_name, cost\n"
            "- Each VENUE must have: name, address, latitude, longitude, opening_hours, place_id\n"
            "- Use ISO format for dates and times (YYYY-MM-DDThh:mm:ss)\n"
            "- Make sure venue_name in events matches exactly with name in venues\n"
            "- Broadway shows typically start at 7:00 PM or 8:00 PM and last 2.5-3 hours\n"
        )
        
        if "customPrompt" in enhanced_request:
            enhanced_request["customPrompt"] += "\n\n" + schema_guidance
        else:
            enhanced_request["customPrompt"] = schema_guidance
        
        return enhanced_request

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Iterative Itinerary Generator")
    parser.add_argument("--request", help="Path to JSON file with request data", required=True)
    parser.add_argument("--output", help="Path to save output JSON result")
    parser.add_argument("--max-attempts", type=int, default=3, 
                        help="Maximum number of attempts to generate a valid itinerary")
    parser.add_argument("--use-real-api", action="store_true",
                        help="Use real Google Maps API calls for validation")
    args = parser.parse_args()
    
    # Load request data
    try:
        with open(args.request, 'r') as f:
            request_data = json.load(f)
            logger.info(f"Loaded request data from {args.request}")
    except Exception as e:
        logger.error(f"Error loading request file: {str(e)}")
        sys.exit(1)
    
    # Create generator and run
    start_time = time.time()
    generator = IterativeGenerator(
        request_data=request_data,
        max_attempts=args.max_attempts,
        real_api=args.use_real_api
    )
    result = generator.run()
    end_time = time.time()
    
    # Add some stats
    result["stats"] = {
        "processing_time_seconds": end_time - start_time,
        "is_valid": result["is_valid"],
        "total_attempts": result["total_attempts"]
    }
    
    # Save output
    output_path = args.output if args.output else "iterative_result.json"
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"Output saved to {output_path}")
    logger.info(f"Itinerary {'is' if result['is_valid'] else 'is not'} valid after {result['total_attempts']} attempts")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 