import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import copy
import re
import traceback

# Import services
from services.google_maps_service import GoogleMapsService
from services.google_showtimes_service import GoogleShowtimesService

logger = logging.getLogger(__name__)

class PlanVerifier:
    """Service for verifying AI-generated plans using Google APIs."""
    
    def __init__(self, maps_service: GoogleMapsService, showtimes_service: GoogleShowtimesService):
        """Initialize the plan verifier with required services."""
        self.maps_service = maps_service
        self.showtimes_service = showtimes_service
        logger.info("Plan verifier initialized")
        
        # Define standard durations for different activities (in minutes)
        self.standard_durations = {
            "dinner": 90,  # Average dinner duration
            "lunch": 60,   # Average lunch duration
            "breakfast": 45,  # Average breakfast duration
            "coffee": 30,  # Coffee/dessert duration
            "show": 150,   # Average Broadway show duration
            "museum": 120,  # Average museum visit
            "tour": 90,    # Average tour duration
            "shopping": 60  # Average shopping duration
        }
        
        # Define minimum travel buffer times (in minutes)
        self.travel_buffers = {
            "show": 30,    # Buffer before a show
            "dinner": 15,  # Buffer before dinner reservation
            "default": 10  # Default buffer
        }
    
    def verify_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify an AI-generated plan using Google APIs.
        Checks venues, events, and routes for accuracy.
        """
        try:
            logger.info("Starting plan verification")
            
            # Create a copy of the plan for verification
            verified_plan = copy.deepcopy(plan)
            
            # Track all issues found during verification
            all_issues = []
            
            # Step 1: Verify venues
            venue_issues = self._verify_venues(verified_plan)
            all_issues.extend(venue_issues)
            
            # Step 2: Verify events and showtimes
            event_issues = self._verify_events(verified_plan)
            all_issues.extend(event_issues)
            
            # Step 3: Verify routes
            route_issues = self._verify_routes(verified_plan)
            all_issues.extend(route_issues)
            
            # Step 4: Verify overall timing logic
            timing_issues = self._verify_timing(verified_plan)
            all_issues.extend(timing_issues)
            
            # Add verification metadata to the plan
            verified_plan['verification'] = {
                'timestamp': datetime.now().isoformat(),
                'has_issues': len(all_issues) > 0,
                'issues': all_issues,
                'verified_venues': len(verified_plan.get('venues', [])),
                'verified_events': len(verified_plan.get('events', [])),
                'verified_routes': len(verified_plan.get('routes', []))
            }
            
            logger.info(f"Plan verification completed with {len(all_issues)} issues found")
            return verified_plan
            
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error during plan verification: {str(e)}")
            logger.error(f"Traceback: {error_traceback}")
            
            return {
                'error': f"Verification failed: {str(e)}",
                'original_plan': plan,
                'verification': {
                    'timestamp': datetime.now().isoformat(),
                    'has_issues': True,
                    'issues': [f"Verification error: {str(e)}"]
                }
            }
    
    def _verify_venues(self, plan: Dict[str, Any]) -> List[str]:
        """Verify venues using the Google Places API."""
        issues = []
        
        # Check if venues are present
        if 'venues' not in plan or not plan['venues']:
            issues.append("No venues found in plan")
            return issues
        
        verified_venues = []
        
        for venue in plan.get('venues', []):
            venue_name = venue.get('name', 'Unknown venue')
            venue_address = venue.get('address', '')
            
            try:
                logger.info(f"Verifying venue: {venue_name}")
                
                # Search for the venue using Google Places API
                search_query = f"{venue_name} {venue_address}"
                places = self.showtimes_service.get_all_matching_places(search_query)
                
                if not places:
                    issues.append(f"Venue not found: {venue_name}")
                    venue['verified'] = False
                    venue['verification_issue'] = "Venue not found in Google Places API"
                    verified_venues.append(venue)
                    continue
                
                # Find the best match
                best_match = None
                for place in places:
                    place_name = place.get('name', '')
                    place_address = place.get('formatted_address', place.get('vicinity', ''))
                    
                    # Check for name similarity
                    if self._name_similarity(venue_name, place_name) > 0.6:
                        best_match = place
                        break
                
                if not best_match:
                    best_match = places[0]  # Use first result if no good match
                
                # Update venue with verified data
                verified_venue = venue.copy()
                verified_venue['verified'] = True
                verified_venue['place_id'] = best_match.get('place_id')
                verified_venue['name'] = best_match.get('name', venue_name)
                verified_venue['address'] = best_match.get('formatted_address', best_match.get('vicinity', venue_address))
                verified_venue['latitude'] = best_match.get('geometry', {}).get('location', {}).get('lat', venue.get('latitude'))
                verified_venue['longitude'] = best_match.get('geometry', {}).get('location', {}).get('lng', venue.get('longitude'))
                verified_venue['rating'] = best_match.get('rating', venue.get('rating'))
                verified_venue['price_level'] = best_match.get('price_level', venue.get('price_level'))
                
                # Get additional details if we have a place_id
                if 'place_id' in verified_venue:
                    try:
                        place_details = self.showtimes_service.get_place_details(verified_venue['place_id'])
                        
                        # Update with additional details
                        if place_details:
                            verified_venue['phone_number'] = place_details.get('formatted_phone_number')
                            verified_venue['website'] = place_details.get('website')
                            verified_venue['opening_hours'] = place_details.get('opening_hours', {}).get('weekday_text', [])
                            
                            # Check if the venue is open today
                            is_open_now = place_details.get('opening_hours', {}).get('open_now')
                            verified_venue['open_now'] = is_open_now
                            
                            if is_open_now is False:
                                issues.append(f"Venue is currently closed: {venue_name}")
                            
                    except Exception as e:
                        logger.warning(f"Error getting details for venue {venue_name}: {str(e)}")
                
                verified_venues.append(verified_venue)
                logger.info(f"Successfully verified venue: {verified_venue['name']}")
                
            except Exception as e:
                logger.error(f"Error verifying venue {venue_name}: {str(e)}")
                issues.append(f"Error verifying venue {venue_name}: {str(e)}")
                venue['verified'] = False
                venue['verification_issue'] = str(e)
                verified_venues.append(venue)
        
        # Replace venues with verified ones
        plan['venues'] = verified_venues
        
        return issues
    
    def _verify_events(self, plan: Dict[str, Any]) -> List[str]:
        """Verify events and showtimes."""
        issues = []
        
        # Check if events are present
        if 'events' not in plan or not plan['events']:
            issues.append("No events found in plan")
            return issues
        
        verified_events = []
        venue_map = {venue.get('name'): venue for venue in plan.get('venues', [])}
        
        for event in plan.get('events', []):
            event_name = event.get('name', 'Unknown event')
            venue_name = event.get('venue_name', '')
            
            try:
                logger.info(f"Verifying event: {event_name} at {venue_name}")
                
                # Check if venue exists
                if venue_name not in venue_map:
                    issues.append(f"Event {event_name} references unknown venue: {venue_name}")
                    event['verified'] = False
                    event['verification_issue'] = f"Unknown venue: {venue_name}"
                    verified_events.append(event)
                    continue
                
                venue = venue_map[venue_name]
                
                # For Broadway shows and events with showtimes, verify the showtimes
                if 'broadway' in event_name.lower() or 'show' in event_name.lower() or 'theater' in event_name.lower():
                    try:
                        logger.info(f"Searching for showtimes for: {event_name}")
                        
                        # Search for showtimes
                        showtime_query = f"{event_name} {venue_name}"
                        showtime_events = self.showtimes_service.search_events(showtime_query)
                        
                        if not showtime_events:
                            # Try more generic query
                            showtime_events = self.showtimes_service.search_events(f"shows at {venue_name}")
                        
                        # If we found showtimes, validate them
                        if showtime_events:
                            matching_event = None
                            for se in showtime_events:
                                if self._name_similarity(se.name, event_name) > 0.6:
                                    matching_event = se
                                    break
                            
                            if not matching_event and showtime_events:
                                matching_event = showtime_events[0]
                            
                            if matching_event and matching_event.showtimes:
                                # Get the original start time
                                original_start = event.get('start_time')
                                
                                # Find the closest showtime
                                closest_showtime = None
                                min_diff = timedelta(days=365)
                                
                                for st in matching_event.showtimes:
                                    if not original_start:
                                        closest_showtime = st
                                        break
                                        
                                    original_dt = datetime.fromisoformat(original_start.replace('Z', '+00:00')) if isinstance(original_start, str) else original_start
                                    diff = abs(st.start_time - original_dt) if original_dt else timedelta(days=1)
                                    
                                    if diff < min_diff:
                                        min_diff = diff
                                        closest_showtime = st
                                
                                if closest_showtime:
                                    event['start_time'] = closest_showtime.start_time.isoformat()
                                    event['end_time'] = closest_showtime.end_time.isoformat() if closest_showtime.end_time else None
                                    event['price'] = closest_showtime.price if closest_showtime.price else event.get('price')
                                    event['verified'] = True
                                    
                                    logger.info(f"Verified showtime for {event_name}: {event['start_time']}")
                                else:
                                    issues.append(f"No matching showtimes found for {event_name}")
                                    event['verified'] = False
                                    event['verification_issue'] = "No matching showtimes"
                            else:
                                issues.append(f"No showtimes found for {event_name}")
                                event['verified'] = False
                                event['verification_issue'] = "No showtimes found"
                        else:
                            issues.append(f"No showtimes found for {event_name}")
                            event['verified'] = False
                            event['verification_issue'] = "No showtimes found"
                            
                    except Exception as e:
                        logger.error(f"Error verifying showtimes for {event_name}: {str(e)}")
                        issues.append(f"Error verifying showtimes for {event_name}: {str(e)}")
                        event['verified'] = False
                        event['verification_issue'] = str(e)
                else:
                    # For restaurants and other venues without formal showtimes
                    event['verified'] = True
                    
                    # Check if start_time and end_time are in ISO format
                    for time_field in ['start_time', 'end_time']:
                        if event.get(time_field) and isinstance(event[time_field], str):
                            try:
                                # Ensure time is in ISO format
                                dt = datetime.fromisoformat(event[time_field].replace('Z', '+00:00'))
                                event[time_field] = dt.isoformat()
                            except ValueError:
                                issues.append(f"Invalid time format for {event_name} {time_field}: {event[time_field]}")
                                event['verification_issue'] = f"Invalid time format for {time_field}"
                
                verified_events.append(event)
                
            except Exception as e:
                logger.error(f"Error verifying event {event_name}: {str(e)}")
                issues.append(f"Error verifying event {event_name}: {str(e)}")
                event['verified'] = False
                event['verification_issue'] = str(e)
                verified_events.append(event)
        
        # Replace events with verified ones
        plan['events'] = verified_events
        
        return issues
    
    def _verify_routes(self, plan: Dict[str, Any]) -> List[str]:
        """Verify routes using Google Maps API."""
        issues = []
        
        # Check if routes are present
        if 'routes' not in plan or not plan['routes']:
            # Generate routes if not present but we have venues
            if 'venues' in plan and len(plan.get('venues', [])) > 0:
                try:
                    logger.info("Generating routes for plan")
                    routes = self._generate_routes(plan)
                    plan['routes'] = routes
                    return issues
                except Exception as e:
                    logger.error(f"Error generating routes: {str(e)}")
                    issues.append(f"Error generating routes: {str(e)}")
                    return issues
            else:
                issues.append("No routes or insufficient venues found in plan")
                return issues
        
        verified_routes = []
        venue_map = {venue.get('name'): venue for venue in plan.get('venues', [])}
        
        for route in plan.get('routes', []):
            from_name = route.get('from', 'Unknown origin')
            to_name = route.get('to', 'Unknown destination')
            travel_mode = route.get('travel_mode', 'walking')
            
            try:
                logger.info(f"Verifying route from {from_name} to {to_name}")
                
                # Check if venues exist
                if from_name not in venue_map and from_name != "Current Location":
                    issues.append(f"Route references unknown origin venue: {from_name}")
                    route['verified'] = False
                    route['verification_issue'] = f"Unknown origin venue: {from_name}"
                    verified_routes.append(route)
                    continue
                
                if to_name not in venue_map:
                    issues.append(f"Route references unknown destination venue: {to_name}")
                    route['verified'] = False
                    route['verification_issue'] = f"Unknown destination venue: {to_name}"
                    verified_routes.append(route)
                    continue
                
                # Get coordinates for origin and destination
                from_coords = None
                if from_name == "Current Location":
                    from_coords = (40.7580, -73.9855)  # Default to Times Square if no user location
                else:
                    from_venue = venue_map[from_name]
                    from_coords = (from_venue.get('latitude'), from_venue.get('longitude'))
                
                to_venue = venue_map[to_name]
                to_coords = (to_venue.get('latitude'), to_venue.get('longitude'))
                
                # Verify route using Google Maps Directions API
                try:
                    routes_result = self.maps_service.get_directions(
                        origin=from_coords,
                        destination=to_coords,
                        mode=travel_mode
                    )
                    
                    if routes_result and 'routes' in routes_result and routes_result['routes']:
                        map_route = routes_result['routes'][0]
                        leg = map_route['legs'][0]
                        
                        # Update route with verified data
                        route['verified'] = True
                        route['distance_meters'] = leg['distance']['value']
                        route['duration_seconds'] = leg['duration']['value']
                        
                        # Add polyline for map display
                        route['polyline'] = map_route['overview_polyline']['points'] if 'overview_polyline' in map_route else None
                        
                        # Add step-by-step directions
                        steps = []
                        for step in leg['steps']:
                            steps.append({
                                'instruction': re.sub('<[^<]+?>', '', step['html_instructions']),  # Remove HTML tags
                                'distance_meters': step['distance']['value'],
                                'duration_seconds': step['duration']['value']
                            })
                        
                        route['steps'] = steps
                        
                        logger.info(f"Successfully verified route from {from_name} to {to_name}")
                    else:
                        issues.append(f"No route found from {from_name} to {to_name}")
                        route['verified'] = False
                        route['verification_issue'] = "No route found"
                except Exception as e:
                    logger.error(f"Error getting directions for route from {from_name} to {to_name}: {str(e)}")
                    
                    # If API error, use mock route
                    route['verified'] = False
                    route['verification_issue'] = f"Directions API error: {str(e)}"
                    
                    # Calculate straight-line distance as fallback
                    if from_coords and to_coords:
                        distance = self._haversine_distance(from_coords[0], from_coords[1], to_coords[0], to_coords[1])
                        route['distance_meters'] = int(distance * 1000)  # Convert km to meters
                        
                        # Estimate duration based on travel mode
                        speeds = {
                            'walking': 5,  # km/h
                            'bicycling': 15,
                            'transit': 25,
                            'driving': 40
                        }
                        speed = speeds.get(travel_mode, 5)
                        route['duration_seconds'] = int((distance / speed) * 3600)  # Convert hours to seconds
                        
                        issues.append(f"Used estimated distance ({route['distance_meters']} m) for route from {from_name} to {to_name}")
                
                verified_routes.append(route)
                
            except Exception as e:
                logger.error(f"Error verifying route from {from_name} to {to_name}: {str(e)}")
                issues.append(f"Error verifying route from {from_name} to {to_name}: {str(e)}")
                route['verified'] = False
                route['verification_issue'] = str(e)
                verified_routes.append(route)
        
        # Replace routes with verified ones
        plan['routes'] = verified_routes
        
        return issues
    
    def _verify_timing(self, plan: Dict[str, Any]) -> List[str]:
        """Verify overall timing logic of the plan."""
        issues = []
        
        # Check if we have both events and routes
        if ('events' not in plan or not plan['events']) or ('routes' not in plan or not plan['routes']):
            return issues
        
        events = plan.get('events', [])
        routes = plan.get('routes', [])
        
        # Sort events by start time
        try:
            sorted_events = sorted(events, key=lambda e: datetime.fromisoformat(e['start_time'].replace('Z', '+00:00')) if e.get('start_time') else datetime.max)
            
            # Check for overlapping events
            for i in range(len(sorted_events) - 1):
                current = sorted_events[i]
                next_event = sorted_events[i + 1]
                
                if 'end_time' in current and current['end_time'] and 'start_time' in next_event and next_event['start_time']:
                    current_end = datetime.fromisoformat(current['end_time'].replace('Z', '+00:00'))
                    next_start = datetime.fromisoformat(next_event['start_time'].replace('Z', '+00:00'))
                    
                    # Find the route between these venues
                    route_time = 0
                    for route in routes:
                        if route.get('from') == current.get('venue_name') and route.get('to') == next_event.get('venue_name'):
                            route_time = route.get('duration_seconds', 0)
                            break
                    
                    # Convert route time to timedelta
                    route_delta = timedelta(seconds=route_time)
                    
                    # Check if there's enough time between events
                    if current_end + route_delta > next_start:
                        buffer = timedelta(minutes=15)  # Add a buffer
                        if current_end + route_delta + buffer > next_start:
                            issues.append(f"Not enough time between {current['name']} and {next_event['name']} including travel time")
                            
                            # Mark both events with timing issue
                            current['timing_issue'] = True
                            next_event['timing_issue'] = True
            
            # Calculate total duration of plan
            if sorted_events:
                first_event = sorted_events[0]
                last_event = sorted_events[-1]
                
                if 'start_time' in first_event and 'end_time' in last_event and last_event['end_time']:
                    first_start = datetime.fromisoformat(first_event['start_time'].replace('Z', '+00:00'))
                    last_end = datetime.fromisoformat(last_event['end_time'].replace('Z', '+00:00'))
                    
                    total_duration = (last_end - first_start).total_seconds() / 3600  # Convert to hours
                    plan['total_duration_hours'] = round(total_duration, 2)
            
            # Calculate total cost
            total_cost = sum(float(event.get('price', 0)) for event in events)
            plan['total_cost'] = round(total_cost, 2)
            
        except Exception as e:
            logger.error(f"Error verifying timing logic: {str(e)}")
            issues.append(f"Error verifying timing logic: {str(e)}")
        
        return issues
    
    def _generate_routes(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate routes between venues in the plan."""
        venues = plan.get('venues', [])
        events = plan.get('events', [])
        
        if not venues or len(venues) < 2:
            return []
        
        # Create a mapping of event to venue
        event_venues = []
        for event in sorted(events, key=lambda e: datetime.fromisoformat(e['start_time'].replace('Z', '+00:00')) if e.get('start_time') else datetime.max):
            venue_name = event.get('venue_name')
            if venue_name:
                event_venues.append(venue_name)
        
        # If no events with venues, use all venues
        if not event_venues:
            event_venues = [venue.get('name') for venue in venues]
        
        # Create routes between consecutive venues
        routes = []
        
        # Add route from "Current Location" to first venue
        if event_venues:
            first_venue = event_venues[0]
            first_venue_obj = next((v for v in venues if v.get('name') == first_venue), None)
            
            if first_venue_obj:
                routes.append({
                    'from': "Current Location",
                    'to': first_venue,
                    'travel_mode': "walking",
                    'distance_meters': 1000,  # Default distance
                    'duration_seconds': 600,  # Default duration
                    'description': f"Walk from your location to {first_venue}"
                })
        
        # Add routes between venues
        for i in range(len(event_venues) - 1):
            from_venue = event_venues[i]
            to_venue = event_venues[i + 1]
            
            routes.append({
                'from': from_venue,
                'to': to_venue,
                'travel_mode': "walking",
                'distance_meters': 1000,  # Default distance
                'duration_seconds': 600,  # Default duration
                'description': f"Walk from {from_venue} to {to_venue}"
            })
        
        return routes
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate the similarity between two venue names."""
        if not name1 or not name2:
            return 0
            
        # Normalize names
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        
        # Exact match
        if name1 == name2:
            return 1.0
            
        # Check if one contains the other
        if name1 in name2 or name2 in name1:
            return 0.8
        
        # Simple word overlap
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        common_words = words1.intersection(words2)
        
        if not common_words:
            return 0.0
            
        return len(common_words) / max(len(words1), len(words2))
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        from math import radians, cos, sin, asin, sqrt
        
        # Convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r 