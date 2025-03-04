import googlemaps
from typing import Dict, Any, List, Optional, Tuple
import config
from models.navigation import Route, RouteStep, TransportMode, NavigationPlan
import logging

logger = logging.getLogger(__name__)

class GoogleMapsService:
    """Service for interacting with Google Maps API."""
    
    def __init__(self):
        """Initialize the Google Maps service with API key."""
        self.client = googlemaps.Client(key=config.GOOGLE_MAPS_API_KEY)
        # Cache for routes to avoid redundant API calls
        self._route_cache = {}
        logger.info("Google Maps service initialized successfully")
    
    def _get_cache_key(self, origin: Tuple[float, float], destination: Tuple[float, float], mode: str) -> str:
        """Generate a cache key for a route."""
        return f"{origin[0]},{origin[1]}|{destination[0]},{destination[1]}|{mode}"
    
    def get_directions(
        self, 
        origin: Tuple[float, float], 
        destination: Tuple[float, float], 
        mode: str = "driving",
        departure_time: Optional[str] = None,
        use_cache: bool = True,
        alternatives: bool = False,
        transit_routing_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get directions between two locations using the Routes API.
        
        Args:
            origin: (lat, lng) tuple for starting point
            destination: (lat, lng) tuple for ending point
            mode: Transport mode
            departure_time: Optional departure time
            use_cache: Whether to use cached results
            alternatives: Whether to request alternative routes
            transit_routing_preference: Transit routing preference
            
        Returns:
            A dictionary with routes data in a format compatible with the old Directions API
            to maintain compatibility with existing code.
        """
        # Check cache first if enabled
        if use_cache:
            cache_key = self._get_cache_key(origin, destination, mode)
            if cache_key in self._route_cache:
                return self._route_cache[cache_key]
        
        try:
            # Convert mode string to TransportMode enum
            travel_mode = TransportMode(mode.lower())
            
            # Format origin and destination for Routes API
            origin_location = {"latLng": {"latitude": origin[0], "longitude": origin[1]}}
            destination_location = {"latLng": {"latitude": destination[0], "longitude": destination[1]}}
            
            # Set travel mode for Routes API
            route_travel_mode = {
                "driving": "DRIVE",
                "walking": "WALK",
                "bicycling": "BICYCLE",
                "transit": "TRANSIT"
            }
            
            # Call the Routes API directly
            logger.info(f"Calling Routes API for directions from {origin} to {destination} via {mode}")
            
            # Use the newer Routes API
            response = self.client.routes(
                **{"body": {"origin": origin_location, 
                            "destination": destination_location,
                            "travelMode": route_travel_mode.get(travel_mode.value, "DRIVE"),
                            "computeAlternativeRoutes": alternatives}}
            )
            
            # Convert the Routes API response to a format compatible with the old Directions API
            # for backward compatibility with existing code
            converted_response = self._convert_routes_to_directions_format(response, origin, destination, travel_mode)
            
            # Cache the response if caching is enabled
            if use_cache:
                cache_key = self._get_cache_key(origin, destination, mode)
                self._route_cache[cache_key] = converted_response
            
            return converted_response
                
        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg or "REQUEST_DENIED" in error_msg:
                logger.error(f"Routes API authorization error: {e}")
                logger.error("This may be due to an invalid API key or the Routes API not being enabled for this key")
                logger.error("Please ensure the Routes API is enabled in your Google Cloud Console")
            else:
                logger.error(f"Error calling Routes API: {e}")
            return None
    
    def _convert_routes_to_directions_format(self, routes_response: Dict[str, Any], 
                                           origin: Tuple[float, float], 
                                           destination: Tuple[float, float],
                                           travel_mode: TransportMode) -> Dict[str, Any]:
        """
        Convert a Routes API response to a format compatible with the old Directions API.
        
        Args:
            routes_response: Response from the Routes API
            origin: Origin coordinates
            destination: Destination coordinates
            travel_mode: Transport mode
            
        Returns:
            A dictionary in Directions API format
        """
        # Initialize the directions-compatible response
        directions_response = {"routes": []}
        
        # Check if we have any routes
        if not routes_response or "routes" not in routes_response or not routes_response["routes"]:
            return directions_response
        
        # Process each route
        for route in routes_response["routes"]:
            # Extract the legs from the route
            if "legs" not in route:
                continue
                
            legs = []
            for leg in route.get("legs", []):
                # Convert the leg to directions format
                formatted_leg = {
                    "distance": {
                        "text": f"{int(leg.get('distanceMeters', 0) / 1000)} km",
                        "value": leg.get("distanceMeters", 0)
                    },
                    "duration": {
                        "text": f"{int(leg.get('duration', '').get('seconds', 0) / 60)} mins",
                        "value": leg.get("duration", {}).get("seconds", 0)
                    },
                    "start_location": {
                        "lat": origin[0],
                        "lng": origin[1]
                    },
                    "end_location": {
                        "lat": destination[0],
                        "lng": destination[1]
                    },
                    "steps": []
                }
                
                # Process steps if available
                for step in leg.get("steps", []):
                    formatted_step = {
                        "distance": {
                            "text": f"{int(step.get('distanceMeters', 0) / 1000)} km",
                            "value": step.get("distanceMeters", 0)
                        },
                        "duration": {
                            "text": f"{int(step.get('duration', '').get('seconds', 0) / 60)} mins",
                            "value": step.get("duration", {}).get("seconds", 0)
                        },
                        "start_location": {
                            "lat": step.get("startLocation", {}).get("latLng", {}).get("latitude", origin[0]),
                            "lng": step.get("startLocation", {}).get("latLng", {}).get("longitude", origin[1])
                        },
                        "end_location": {
                            "lat": step.get("endLocation", {}).get("latLng", {}).get("latitude", destination[0]),
                            "lng": step.get("endLocation", {}).get("latLng", {}).get("longitude", destination[1])
                        },
                        "html_instructions": step.get("navigationInstruction", {}).get("instructions", "Continue"),
                        "travel_mode": travel_mode.value.upper()
                    }
                    formatted_leg["steps"].append(formatted_step)
                
                legs.append(formatted_leg)
            
            # Create a formatted route
            formatted_route = {
                "legs": legs,
                "overview_polyline": {
                    "points": route.get("polyline", {}).get("encodedPolyline", "")
                },
                "summary": route.get("description", ""),
                "warnings": [],
                "waypoint_order": []
            }
            
            directions_response["routes"].append(formatted_route)
        
        return directions_response
    
    def create_navigation_plan(
        self, 
        waypoints: List[Dict[str, Any]], 
        mode: str = "driving",
        start_location: Optional[Dict[str, float]] = None
    ) -> NavigationPlan:
        """
        Create a navigation plan with routes between multiple waypoints.
        
        Args:
            waypoints: List of waypoints with lat/lng
            mode: Transport mode
            start_location: Optional starting location
        """
        try:
            # Create a list of locations (start + waypoints)
            locations = []
            
            # Add start location if provided
            if start_location:
                locations.append({
                    'name': 'Start',
                    'lat': start_location['lat'],
                    'lng': start_location['lng']
                })
            
            # Add waypoints
            for waypoint in waypoints:
                locations.append({
                    'name': waypoint.get('name', 'Waypoint'),
                    'lat': waypoint['lat'],
                    'lng': waypoint['lng']
                })
            
            # Calculate routes between consecutive locations
            routes = []
            for i in range(len(locations) - 1):
                origin = (locations[i]['lat'], locations[i]['lng'])
                destination = (locations[i + 1]['lat'], locations[i + 1]['lng'])
                
                # Get route between locations
                route_result = self.get_directions(origin, destination, mode)
                
                # Convert the dictionary response to Route object
                if route_result and 'routes' in route_result and route_result['routes']:
                    route_data = route_result['routes'][0]
                    leg = route_data['legs'][0]
                    
                    # Create route steps
                    steps = []
                    for step_data in leg['steps']:
                        step = RouteStep(
                            instruction=step_data['html_instructions'],
                            distance=step_data['distance']['value'],
                            duration=step_data['duration']['value'],
                            start_location={
                                'lat': step_data['start_location']['lat'],
                                'lng': step_data['start_location']['lng']
                            },
                            end_location={
                                'lat': step_data['end_location']['lat'],
                                'lng': step_data['end_location']['lng']
                            },
                            travel_mode=TransportMode(mode.lower()),
                            html_instructions=step_data['html_instructions']
                        )
                        steps.append(step)
                    
                    # Create the route
                    route = Route(
                        origin={
                            'lat': origin[0],
                            'lng': origin[1]
                        },
                        destination={
                            'lat': destination[0],
                            'lng': destination[1]
                        },
                        distance=leg['distance']['value'],
                        duration=leg['duration']['value'],
                        steps=steps,
                        travel_mode=TransportMode(mode.lower()),
                        polyline=route_data.get('overview_polyline', {}).get('points')
                    )
                    
                    # Add route to list
                    routes.append(route)
            
            # Create navigation plan
            return NavigationPlan(
                routes=routes,
                total_distance=sum(route.distance for route in routes),
                total_duration=sum(route.duration for route in routes),
                travel_mode=TransportMode(mode.lower())
            )
        except Exception as e:
            logger.error(f"Error creating navigation plan: {e}")
            return NavigationPlan(
                routes=[],
                total_distance=0,
                total_duration=0,
                travel_mode=TransportMode(mode.lower())
            )
    
    def compute_route(self, from_venue: Dict[str, Any], to_venue: Dict[str, Any], mode: str = "walking") -> Dict[str, Any]:
        """Compute a route between two venues."""
        try:
            # Extract coordinates
            origin = (from_venue.get('latitude'), from_venue.get('longitude'))
            destination = (to_venue.get('latitude'), to_venue.get('longitude'))
            
            # Get directions
            route_result = self.get_directions(origin, destination, mode)
            
            # Process the dictionary response
            if route_result and 'routes' in route_result and route_result['routes']:
                route_data = route_result['routes'][0]
                leg = route_data['legs'][0]
                
                return {
                    'distance': leg['distance']['value'],
                    'duration': leg['duration']['value'],
                    'from_venue': from_venue.get('name'),
                    'to_venue': to_venue.get('name'),
                    'polyline': route_data.get('overview_polyline', {}).get('points'),
                    'travel_mode': mode
                }
            else:
                logger.warning(f"No route found between {from_venue.get('name')} and {to_venue.get('name')}")
                return {
                    'distance': 0,
                    'duration': 0,
                    'from_venue': from_venue.get('name'),
                    'to_venue': to_venue.get('name'),
                    'polyline': None,
                    'travel_mode': mode,
                    'error': 'No route found'
                }
        except Exception as e:
            logger.error(f"Error computing route: {e}")
            return {
                'distance': 0,
                'duration': 0,
                'from_venue': from_venue.get('name', 'Unknown'),
                'to_venue': to_venue.get('name', 'Unknown'),
                'polyline': None,
                'travel_mode': mode,
                'error': str(e)
            }
    
    def compute_route_by_addresses(
        self, from_address: str, to_address: str, mode: str = "walking"
    ) -> Dict[str, Any]:
        """Compute a route between two addresses."""
        try:
            # Geocode addresses
            from_result = self.client.geocode(from_address)
            to_result = self.client.geocode(to_address)
            
            if not from_result or not to_result:
                logger.warning(f"Could not geocode addresses: {from_address} -> {to_address}")
                return {
                    'distance': 0,
                    'duration': 0,
                    'from_address': from_address,
                    'to_address': to_address,
                    'polyline': None,
                    'travel_mode': mode,
                    'error': 'Geocoding failed'
                }
            
            # Extract coordinates
            from_loc = from_result[0]['geometry']['location']
            to_loc = to_result[0]['geometry']['location']
            
            origin = (from_loc['lat'], from_loc['lng'])
            destination = (to_loc['lat'], to_loc['lng'])
            
            # Get directions
            route_result = self.get_directions(origin, destination, mode)
            
            # Process the dictionary response
            if route_result and 'routes' in route_result and route_result['routes']:
                route_data = route_result['routes'][0]
                leg = route_data['legs'][0]
                
                return {
                    'distance': leg['distance']['value'],
                    'duration': leg['duration']['value'],
                    'from_address': from_address,
                    'to_address': to_address,
                    'polyline': route_data.get('overview_polyline', {}).get('points'),
                    'travel_mode': mode
                }
            else:
                logger.warning(f"No route found between {from_address} and {to_address}")
                return {
                    'distance': 0,
                    'duration': 0,
                    'from_address': from_address,
                    'to_address': to_address,
                    'polyline': None,
                    'travel_mode': mode,
                    'error': 'No route found'
                }
        except Exception as e:
            logger.error(f"Error computing route by addresses: {e}")
            return {
                'distance': 0,
                'duration': 0,
                'from_address': from_address,
                'to_address': to_address,
                'polyline': None,
                'travel_mode': mode,
                'error': str(e)
            }
    
    def estimate_travel_time(
        self, 
        origin: Tuple[float, float], 
        destination: Tuple[float, float], 
        mode: str = "driving"
    ) -> Optional[int]:
        """Estimate travel time between two locations in seconds."""
        # Check cache first to avoid redundant API calls
        cache_key = self._get_cache_key(origin, destination, mode)
        if cache_key in self._route_cache:
            route_result = self._route_cache[cache_key]
            if route_result and 'routes' in route_result and route_result['routes']:
                return route_result['routes'][0]['legs'][0]['duration']['value']
        
        # If not in cache, get the route
        route_result = self.get_directions(origin, destination, mode)
        if route_result and 'routes' in route_result and route_result['routes']:
            return route_result['routes'][0]['legs'][0]['duration']['value']
        return None
    
    def clear_cache(self) -> None:
        """Clear the route cache."""
        self._route_cache = {}
        logger.info("Route cache cleared") 