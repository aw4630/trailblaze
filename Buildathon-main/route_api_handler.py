#!/usr/bin/env python
"""
Route API Handler

This script acts as an API handler for the /api/routes endpoint, using the iterative
itinerary generator to process requests and return validated routes.

It takes a request in the specified format, processes it through the iterative generator
cycle, and returns the completed route.
"""

import json
import logging
import argparse
import sys
import time
from typing import Dict, Any, Optional, Union, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('route_api_handler')

# Import our iterative generator
try:
    from iterative_itinerary_generator import IterativeGenerator
    from test_itinerary_validator import ItineraryVerifier
except ImportError:
    logger.error("Could not import required modules. Make sure iterative_itinerary_generator.py and test_itinerary_validator.py are in the same directory.")
    sys.exit(1)

class RouteAPIHandler:
    """Handles API requests for route generation using the iterative generator."""
    
    def __init__(self, max_attempts: int = 3, use_real_api: bool = True):
        """Initialize the API handler.
        
        Args:
            max_attempts: Maximum number of attempts to generate a valid itinerary
            use_real_api: Whether to use real APIs or mock data
        """
        self.max_attempts = max_attempts
        self.use_real_api = use_real_api
        logger.info(f"Route API Handler initialized with max_attempts={max_attempts}, use_real_api={use_real_api}")
    
    def process_request(self, request_body: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """Process a route request using the iterative generator.
        
        Args:
            request_body: The request body as specified in the API schema
            
        Returns:
            Tuple containing (response_data, success)
            - response_data: The generated itinerary or error information
            - success: Whether the generation was successful
        """
        start_time = time.time()
        logger.info(f"Processing route request: {request_body.get('routeName', 'Unnamed Route')}")
        
        try:
            # Validate the request
            self._validate_request(request_body)
            
            # Initialize the generator with the request data
            generator = IterativeGenerator(
                request_data=request_body,
                max_attempts=self.max_attempts,
                real_api=self.use_real_api
            )
            
            # Run the generator to produce an itinerary
            itinerary = generator.run()
            
            # Check if the final itinerary is valid
            is_valid = False
            issues = []
            
            if generator.best_verification:
                is_valid = generator.best_verification.get('feasible', False)
                # Collect all issues
                for issue_type in ['venue_hours_issues', 'travel_time_issues', 
                                 'activity_duration_issues', 'buffer_time_issues',
                                 'overall_timing_issues', 'format_issues']:
                    if issue_type in generator.best_verification:
                        issues.extend(generator.best_verification.get(issue_type, []))
            
            # Prepare the response
            processing_time = time.time() - start_time
            attempt_count = len(generator.attempts)
            
            if is_valid:
                logger.info(f"Successfully generated valid itinerary for {request_body.get('routeName')} in {processing_time:.2f} seconds after {attempt_count} attempts")
                return {
                    "success": True,
                    "message": "Successfully generated itinerary",
                    "processing_time_seconds": processing_time,
                    "itinerary": itinerary,
                    "attempt_count": attempt_count
                }, True
            else:
                logger.warning(f"Generated itinerary for {request_body.get('routeName')} with {len(issues)} issues after {attempt_count} attempts")
                return {
                    "success": False,
                    "message": "Generated itinerary has issues",
                    "processing_time_seconds": processing_time,
                    "issues_found": True,
                    "issues": issues,
                    "itinerary": itinerary,
                    "attempt_count": attempt_count
                }, False
                
        except Exception as e:
            logger.error(f"Error processing route request: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Error processing request: {str(e)}",
                "processing_time_seconds": time.time() - start_time
            }, False
    
    def _validate_request(self, request_body: Dict[str, Any]) -> None:
        """Validate that the request has all required fields.
        
        Args:
            request_body: The request body to validate
            
        Raises:
            ValueError: If the request is missing required fields
        """
        required_fields = [
            "routeName", "measurementType", "measurementValue", 
            "transportModes", "theme", "budget"
        ]
        
        for field in required_fields:
            if field not in request_body:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate enum fields
        if request_body["measurementType"] not in ["distance", "time"]:
            raise ValueError(f"Invalid measurementType: {request_body['measurementType']}")
        
        valid_transport_modes = ["Walk", "Car", "Public Transport", "Cycling"]
        for mode in request_body["transportModes"]:
            if mode not in valid_transport_modes:
                raise ValueError(f"Invalid transport mode: {mode}")
        
        valid_themes = ["Parks", "Landmarks", "Ancient Buildings", "New Buildings", 
                        "Movie Scenes", "Historical Events"]
        if request_body["theme"] not in valid_themes:
            raise ValueError(f"Invalid theme: {request_body['theme']}")
        
        # Validate budget
        if not isinstance(request_body["budget"], dict) or "max" not in request_body["budget"]:
            raise ValueError("Budget must be an object with a 'max' property")


def process_cli_request():
    """Process a route request from command line arguments."""
    parser = argparse.ArgumentParser(description='Process a route request using the iterative generator')
    parser.add_argument('--request', type=str, help='Path to JSON file containing the request body')
    parser.add_argument('--request-inline', type=str, help='JSON string containing the request body')
    parser.add_argument('--output', type=str, help='Path to save the response JSON')
    parser.add_argument('--max-attempts', type=int, default=3, help='Maximum number of attempts to generate a valid itinerary')
    parser.add_argument('--use-mock-data', action='store_true', help='Use mock data instead of real APIs')
    
    args = parser.parse_args()
    
    if not args.request and not args.request_inline:
        parser.error("Either --request or --request-inline must be provided")
    
    # Load the request body
    if args.request:
        try:
            with open(args.request, 'r') as f:
                request_body = json.load(f)
        except Exception as e:
            logger.error(f"Error loading request file: {str(e)}")
            sys.exit(1)
    else:
        try:
            request_body = json.loads(args.request_inline)
        except Exception as e:
            logger.error(f"Error parsing inline request JSON: {str(e)}")
            sys.exit(1)
    
    # Extract just the requestBody part if the full API format is provided
    if "requestBody" in request_body:
        request_body = request_body["requestBody"]
    
    # Process the request
    handler = RouteAPIHandler(
        max_attempts=args.max_attempts, 
        use_real_api=not args.use_mock_data
    )
    response, success = handler.process_request(request_body)
    
    # Print the response to stdout
    print(json.dumps(response, indent=2))
    
    # Save the response to a file if requested
    if args.output:
        try:
            with open(args.output, 'w') as f:
                json.dump(response, f, indent=2)
            logger.info(f"Response saved to {args.output}")
        except Exception as e:
            logger.error(f"Error saving response to file: {str(e)}")
    
    # Return exit code based on success
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    process_cli_request() 