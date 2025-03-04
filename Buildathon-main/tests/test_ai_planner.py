#!/usr/bin/env python
"""
Test script for the AI Planner endpoint.
"""

import os
import sys
import json
import logging
import requests
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def test_ai_planner(query, transport_mode="walking", max_iterations=2):
    """
    Test the AI Planner endpoint with a given query.
    
    Args:
        query (str): The user's query for planning
        transport_mode (str): The transportation mode to use
        max_iterations (int): Maximum number of verification iterations
        
    Returns:
        dict: The plan response from the API
    """
    # Local server URL
    base_url = "http://localhost:5000"
    endpoint = f"{base_url}/api/plan"
    
    # Request data
    data = {
        "query": query,
        "transport_mode": transport_mode,
        "max_iterations": max_iterations
    }
    
    logger.info(f"Sending request to {endpoint} with data: {data}")
    
    try:
        # Send POST request to the endpoint
        response = requests.post(endpoint, json=data)
        response.raise_for_status()
        
        # Parse the response
        plan_response = response.json()
        
        # Print the summary of the plan
        logger.info("Plan generated successfully")
        if plan_response.get("success", False):
            plan = plan_response.get("plan", {})
            summary = plan.get("summary", "No summary available")
            iterations = plan_response.get("iterations", 0)
            
            logger.info("=" * 50)
            logger.info(f"Plan Summary (after {iterations} iterations):")
            logger.info("=" * 50)
            logger.info(summary)
            logger.info("=" * 50)
            
            # Print any issues found
            issues = plan.get("issues", [])
            if issues:
                logger.warning(f"Found {len(issues)} issues with the plan:")
                for i, issue in enumerate(issues, 1):
                    logger.warning(f"{i}. {issue}")
        else:
            error = plan_response.get("error", "Unknown error")
            logger.error(f"Failed to generate plan: {error}")
        
        return plan_response
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Example queries to test
    test_queries = [
        "I want to see a Broadway show and have dinner in New York tonight",
        "Pizza and a movie in Manhattan this evening",
        "Dinner and jazz in Harlem this weekend"
    ]
    
    # Test with the first query by default, or use command line argument if provided
    query_to_test = sys.argv[1] if len(sys.argv) > 1 else test_queries[0]
    
    # Run the test
    test_result = test_ai_planner(query_to_test)
    
    # Save the result to a JSON file for inspection
    output_file = "test_plan_result.json"
    with open(output_file, "w") as f:
        json.dump(test_result, f, indent=2)
    
    logger.info(f"Test result saved to {output_file}") 