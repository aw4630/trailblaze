#!/usr/bin/env python
"""
Test script for OpenAI-first planning approach
This script sends a test query to the OpenAI-first planning endpoint
and prints the result.
"""

import sys
import os
import json
import requests
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Default test query
DEFAULT_QUERY = "Broadway shows and dinner in New York tonight"

def test_openai_first_planning(query, transport_mode="WALKING", max_iterations=3):
    """
    Test the OpenAI-first planning approach by sending a request to the plan endpoint.
    
    Args:
        query (str): The user query to process
        transport_mode (str): The mode of transportation (WALKING, DRIVING, etc.)
        max_iterations (int): Maximum number of refinement iterations
        
    Returns:
        dict: The response from the server
    """
    url = "http://localhost:5000/api/plan"
    
    payload = {
        "query": query,
        "transport_mode": transport_mode,
        "max_iterations": max_iterations
    }
    
    logger.info(f"Sending request to {url} with query: '{query}'")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        return {"error": str(e)}

def print_plan_details(plan):
    """
    Print formatted details of the plan
    
    Args:
        plan (dict): The plan response from the server
    """
    if "error" in plan:
        logger.error(f"Error in plan: {plan['error']}")
        return
    
    # Print summary
    print("\n" + "="*80)
    print("PLAN SUMMARY".center(80))
    print("="*80)
    print(plan.get("summary", "No summary available"))
    print("-"*80)
    
    # Print metadata
    metadata = plan.get("metadata", {})
    print(f"Query: {metadata.get('query', 'N/A')}")
    print(f"Transport Mode: {metadata.get('transport_mode', 'N/A')}")
    print(f"Iterations: {metadata.get('iterations', 0)}")
    print(f"Total Duration: {metadata.get('total_duration_minutes', 0)} minutes")
    print(f"Total Cost Estimate: {metadata.get('total_cost', 'N/A')}")
    print("-"*80)
    
    # Print venues
    venues = plan.get("plan", {}).get("venues", [])
    print(f"\nVENUES ({len(venues)}):")
    for i, venue in enumerate(venues, 1):
        verification = venue.get("verification", {})
        verified = "✓" if verification.get("verified", False) else "✗"
        print(f"{i}. {venue.get('name', 'Unknown')} [{verified}]")
        print(f"   Address: {venue.get('address', 'N/A')}")
        print(f"   Type: {venue.get('type', 'N/A')}")
        if not verification.get("verified", False):
            print(f"   Verification Failed: {verification.get('issues', 'Unknown reason')}")
        print()
    
    # Print events
    events = plan.get("plan", {}).get("events", [])
    print(f"\nEVENTS ({len(events)}):")
    for i, event in enumerate(events, 1):
        verification = event.get("verification", {})
        verified = "✓" if verification.get("verified", False) else "✗"
        print(f"{i}. {event.get('name', 'Unknown')} [{verified}]")
        print(f"   Venue: {event.get('venue_name', 'N/A')}")
        print(f"   Time: {event.get('start_time', 'N/A')} - {event.get('end_time', 'N/A')}")
        if not verification.get("verified", False):
            print(f"   Verification Failed: {verification.get('issues', 'Unknown reason')}")
        print()
    
    # Print routes
    routes = plan.get("plan", {}).get("routes", [])
    print(f"\nROUTES ({len(routes)}):")
    for i, route in enumerate(routes, 1):
        verification = route.get("verification", {})
        verified = "✓" if verification.get("verified", False) else "✗"
        print(f"{i}. {route.get('origin_name', 'Unknown')} → {route.get('destination_name', 'Unknown')} [{verified}]")
        print(f"   Distance: {route.get('distance_meters', 'N/A')} meters")
        print(f"   Duration: {route.get('duration_seconds', 'N/A')} seconds")
        if not verification.get("verified", False):
            print(f"   Verification Failed: {verification.get('issues', 'Unknown reason')}")
        print()
    
    # Print issues
    issues = plan.get("plan", {}).get("verification", {}).get("issues", [])
    if issues:
        print(f"\nISSUES ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    
    print("\n" + "="*80)

def main():
    """Main function to run the test"""
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = DEFAULT_QUERY
        
    transport_mode = "WALKING"
    if len(sys.argv) > 2:
        transport_mode = sys.argv[2]
        
    max_iterations = 3
    if len(sys.argv) > 3:
        try:
            max_iterations = int(sys.argv[3])
        except ValueError:
            logger.warning(f"Invalid max_iterations value: {sys.argv[3]}. Using default: 3")
    
    logger.info(f"Testing OpenAI-first planning with query: '{query}'")
    start_time = datetime.now()
    
    plan = test_openai_first_planning(query, transport_mode, max_iterations)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_plan_details(plan)
    
    logger.info(f"Test completed in {duration:.2f} seconds")
    
    # Save the plan to a file for reference
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"openai_first_plan_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(plan, f, indent=2)
    logger.info(f"Plan saved to {filename}")

if __name__ == "__main__":
    main() 