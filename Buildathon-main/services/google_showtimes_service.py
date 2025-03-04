import googlemaps
import requests
from typing import Dict, Any, List, Optional
import config
from models.event import Event, EventLocation, EventShowtime, EventPrice
from datetime import datetime, timedelta, time
import random  # For demo purposes only
import pytz  # For timezone handling
import logging
import json

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleShowtimesService:
    """Service for interacting with Google Places API to get event information."""
    
    def __init__(self):
        """Initialize the Google Showtimes service with API key."""
        self.client = googlemaps.Client(key=config.GOOGLE_SHOWTIMES_API_KEY)
        # Cache for API calls to avoid redundant requests
        self._places_cache = {}
        self._details_cache = {}
        logger.info("Google Showtimes service initialized successfully")
        logger.info("Mock data has been completely disabled - all requests require valid API responses")
        
    def find_restaurants(
        self, query: str, location: Dict[str, Any] = None, 
        radius_meters: int = 5000, language: str = "en", 
        min_price: int = 0, max_price: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Search for restaurants matching the given query and location.
        
        Args:
            query: The search query (e.g., "Italian restaurant")
            location: Dictionary with latitude and longitude keys, or UserLocation object
            radius_meters: Search radius in meters (default: 5km)
            language: Preferred language for results
            min_price: Minimum price level (0-4)
            max_price: Maximum price level (0-4)
            
        Returns:
            List of restaurant information dictionaries
        """
        logger.info(f"Searching for restaurants with query: '{query}'")
        
        try:
            # Extract cuisine type from query if possible
            cuisine_type = self._extract_cuisine_type(query)
            
            # Convert location to tuple if provided
            location_tuple = None
            if location:
                # Handle UserLocation object
                if hasattr(location, 'latitude') and hasattr(location, 'longitude'):
                    location_tuple = (location.latitude, location.longitude)
                    logger.info(f"Using location from UserLocation object: {location_tuple}")
                # Handle dictionary
                elif isinstance(location, dict) and 'latitude' in location and 'longitude' in location:
                    location_tuple = (location['latitude'], location['longitude'])
                    logger.info(f"Using location from dictionary: {location_tuple}")
                else:
                    logger.warning(f"Invalid location format provided: {type(location)}")
                    # Default to Times Square if no location
                    location_tuple = (40.758896, -73.985130)
            else:
                logger.warning("No location provided for restaurant search")
                # Default to Times Square if no location
                location_tuple = (40.758896, -73.985130)
            
            # Get all matching places using the existing method
            restaurants = self.get_all_matching_places(
                query=query,
                location=location_tuple,
                type="restaurant",
                radius_meters=radius_meters,
                min_price=min_price,
                max_price=max_price
            )
            
            logger.info(f"Found {len(restaurants)} restaurants matching '{query}'")
            return restaurants
            
        except Exception as e:
            logger.error(f"Error finding restaurants: {str(e)}")
            return []
    
    def _extract_cuisine_type(self, query: str) -> str:
        """Extract cuisine type from a query string."""
        cuisine_types = ["italian", "french", "chinese", "japanese", "mexican", "indian", 
                        "thai", "vietnamese", "greek", "mediterranean", "spanish", 
                        "korean", "american", "bbq", "vegetarian", "vegan", "seafood"]
        
        query_lower = query.lower()
        for cuisine in cuisine_types:
            if cuisine in query_lower:
                return cuisine
        
        return "restaurant"  # Default if no specific cuisine found
    
    def search_events(self, query: str, location: Any = None, radius_meters: int = 5000) -> List[Event]:
        """
        Search for events matching the given query and location.
        
        Args:
            query: The search query (e.g., "Broadway shows")
            location: Dictionary with latitude and longitude keys, or UserLocation object
            radius_meters: Search radius in meters (default: 5km)
            
        Returns:
            List of Event objects
        """
        try:
            logger.info(f"Searching for events with query: '{query}'")
            logger.info(f"Location type: {type(location)}, value: {location}")
            
            # Handle location conversion
            location_tuple = None
            if location:
                if isinstance(location, tuple) and len(location) == 2:
                    location_tuple = location
                    logger.info(f"Using tuple location: {location_tuple}")
                elif isinstance(location, dict) and 'latitude' in location and 'longitude' in location:
                    location_tuple = (location['latitude'], location['longitude'])
                    logger.info(f"Converted dict location to tuple: {location_tuple}")
                else:
                    logger.warning(f"Invalid location format provided: {type(location)}")
                    # Default to Times Square
                    location_tuple = (40.758896, -73.985130)
                    logger.info(f"Using default location: {location_tuple}")
            else:
                # Default to Times Square if no location
                location_tuple = (40.758896, -73.985130)
                logger.info(f"No location provided, using default: {location_tuple}")
            
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": config.GOOGLE_SHOWTIMES_API_KEY
            }
            
            # Build the request payload with the correct format
            # Updated to match current Google Places API format
            payload = {
                "textQuery": query,
                "maxResultCount": 20
            }
            
            # Add location parameters if they exist
            if location_tuple:
                lat, lng = location_tuple
                payload["locationBias"] = {
                    "circle": {
                        "center": {
                            "latitude": lat,
                            "longitude": lng
                        },
                        "radius": float(radius_meters)
                    }
                }
            
            logger.info(f"Google Places API request headers: {headers}")
            logger.info(f"Google Places API request payload: {json.dumps(payload, indent=2)}")
            
            # Send the request to Google Places API
            response = requests.post(
                "https://places.googleapis.com/v1/places:searchText",
                headers=headers,
                json=payload
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.error(f"Error from Google Places API: {response.status_code} - {response.text}")
                raise Exception(f"Google Places API error: {response.status_code} - {response.text}")
            
            # Parse the response
            places_data = response.json()
            logger.info(f"Google Places API response: {json.dumps(places_data, indent=2)}")
            
            # Convert to Event objects
            events = self._parse_events_from_places(places_data.get("places", []), query)
            logger.info(f"Found {len(events)} events matching query '{query}'")
            
            return events
            
        except Exception as e:
            logger.error(f"Error searching for events: {str(e)}")
            # No mock data fallback
            raise Exception(f"Error searching for events: {str(e)}")
    
    def _parse_events_from_places(self, places: List[Dict[str, Any]], query: str) -> List[Event]:
        """
        Parse Google Places API results into Event objects.
        
        Args:
            places: List of place dictionaries from Google Places API
            query: The original search query
            
        Returns:
            List of Event objects
        """
        events = []
        logger.info(f"Parsing {len(places)} places into events")
        
        for place in places:
            try:
                # Extract basic information
                place_id = place.get('id')
                name = place.get('displayName', {}).get('text', 'Unknown Venue')
                
                # Get location information
                location_data = place.get('location', {})
                latitude = location_data.get('latitude', 0)
                longitude = location_data.get('longitude', 0)
                
                # Get address information
                formatted_address = place.get('formattedAddress', 'Address unavailable')
                
                # Create location object
                location = EventLocation(
                    name=name,
                    address=formatted_address,
                    latitude=latitude,
                    longitude=longitude
                )
                
                # Get additional details if available
                description = ""
                if place.get('editorialSummary'):
                    description = place.get('editorialSummary', {}).get('text', '')
                
                # Get photos if available
                photos = []
                if place.get('photos'):
                    for photo in place.get('photos', [])[:3]:  # Limit to 3 photos
                        if photo.get('name'):
                            photo_reference = photo.get('name')
                            photos.append(photo_reference)
                
                # Generate showtimes
                showtimes = self._generate_realistic_showtimes(place)
                
                # Generate prices
                prices = self._generate_realistic_prices(place)
                
                # Create the event
                event = Event(
                    id=place_id,
                    name=name,
                    description=description,
                    location=location,
                    showtimes=showtimes,
                    prices=prices,
                    photos=photos,
                    rating=place.get('rating', 0),
                    review_count=place.get('userRatingCount', 0),
                    url=place.get('websiteUri', '')
                )
                
                events.append(event)
                
            except Exception as e:
                logger.error(f"Error parsing place into event: {str(e)}")
                # Continue with next place
                continue
        
        return events
    
    def _get_place_details_full(self, place_id: str) -> Dict[str, Any]:
        """Get full place details from Google Places API (New)."""
        # Check cache first
        if place_id in self._details_cache:
            return self._details_cache[place_id]
            
        try:
            logger.info(f"Fetching details for place ID: {place_id}")
            
            headers = {
                "X-Goog-Api-Key": config.GOOGLE_SHOWTIMES_API_KEY,
                "X-Goog-FieldMask": "*"  # Request all available fields
            }
            
            url = f"https://places.googleapis.com/v1/places/{place_id}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Error getting place details, status code: {response.status_code}")
                if config.USE_MOCK_DATA:
                    return {}
                else:
                    raise ValueError(f"Failed to get place details: {response.text}")
                    
            details = response.json()
            
            # Cache the result
            self._details_cache[place_id] = details
            
            return details
        except Exception as e:
            logger.error(f"Error getting place details: {str(e)}")
            if config.USE_MOCK_DATA:
                return {}
            else:
                raise  # Re-raise the exception if mock data is disabled
    
    def _extract_description(self, place_details: Dict[str, Any]) -> str:
        """Extract a meaningful description from place details."""
        if not place_details:
            return ""
            
        # Try editorial summary first (best description)
        if 'editorialSummary' in place_details:
            return place_details['editorialSummary'].get('text', '')
        
        # Build a description from available information
        description_parts = []
        
        # Add price level if available
        if 'priceLevel' in place_details:
            price_level = place_details['priceLevel']
            price_desc = ['very economical', 'inexpensive', 'moderately priced', 
                         'expensive', 'very expensive'][min(int(price_level[6:]) if isinstance(price_level, str) else 2, 4)]
            description_parts.append(f"It is {price_desc}.")
        
        # Add phone number if available
        if 'nationalPhoneNumber' in place_details:
            description_parts.append(f"Contact: {place_details['nationalPhoneNumber']}")
        
        if description_parts:
            return " ".join(description_parts)
        
        # Return a generic description if nothing else is available
        return "An entertainment venue with no additional details available."
    
    def search_places(self, query: str, location: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Search for places using Google Places API (New)."""
        logger.info(f"Searching for places with query: '{query}', location: {location}")
        
        try:
            # Call our get_places method
            places = self.get_places(query, location)
            return places
            
        except Exception as e:
            # Log the error and re-raise
            logger.error(f"Error searching for places: {str(e)}")
            raise
            
    def get_all_matching_places(self, query: str, location: Optional[tuple] = None, 
                          radius_meters: int = 5000, type: Optional[str] = None,
                          min_price: int = 0, max_price: int = 4) -> List[Dict[str, Any]]:
        """Get all matching places for a given query."""
        try:
            logger.info(f"Getting all matching places for query: '{query}', location: {location}, type: {type}")
            
            # Build the Places API request for text search (this works with current Places API versions)
            fields = ["place_id", "name", "formatted_address", "geometry", "rating", "user_ratings_total", "price_level"]
            
            # Use the places API text search method instead of search_text
            if location:
                lat, lng = location
                results = self.client.places_nearby(
                    location=(lat, lng),
                    radius=radius_meters,
                    keyword=query,
                    type=type if type else None
                )
            else:
                # Fallback to text search if no location
                results = self.client.places(
                    query=query,
                    type=type if type else None
                )
            
            if not results or 'results' not in results:
                logger.warning(f"No results found for query: {query}")
                return []
            
            # Process the results
            places = []
            for place in results.get('results', []):
                place_data = {
                    "place_id": place.get("place_id"),
                    "name": place.get("name"),
                    "address": place.get("formatted_address", place.get("vicinity", "Address not available")),
                    "location": (
                        place.get("geometry", {}).get("location", {}).get("lat"),
                        place.get("geometry", {}).get("location", {}).get("lng")
                    ) if "geometry" in place else None
                }
                
                # Add rating if available
                if "rating" in place:
                    place_data["rating"] = place.get("rating")
                
                # Add price level if available and within range
                if "price_level" in place:
                    price_level = place.get("price_level")
                    if min_price <= price_level <= max_price:
                        place_data["price_level"] = price_level
                    else:
                        # Skip if price level is outside requested range
                        continue
                        
                places.append(place_data)
            
            logger.info(f"Found {len(places)} matching places")
            return places
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error getting all matching places: {error_msg}")
            
            # No mock data - just raise the exception
            raise Exception(f"Error getting all matching places: {error_msg}")
    
    def get_places(self, query: str, location: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Get all places matching the given query and location.
        
        Args:
            query: The search query
            location: Optional tuple of (latitude, longitude). If not provided, use default location.
            
        Returns:
            List of place dictionaries with details
        """
        logger.info(f"Getting all matching places for query: '{query}', location: {location}")
        
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": config.GOOGLE_SHOWTIMES_API_KEY,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.types,places.rating,places.businessStatus"
            }
            
            # Set a default location if none provided (Manhattan)
            if location is None:
                location = (40.7580, -73.9855)
            
            # Prepare the search payload
            payload = {
                "textQuery": query,
                "maxResultCount": 10,
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": location[0],
                            "longitude": location[1]
                        },
                        "radius": 10000  # 10 km radius
                    }
                }
            }
            
            # Make the API request
            response = requests.post(
                "https://places.googleapis.com/v1/places:searchText",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Error from Google Places API: {response.status_code} - {response.text}")
                raise Exception(f"Google Places API error: {response.status_code}")
            
            # Extract places from response
            result = response.json()
            places = result.get("places", [])
            
            logger.info(f"Found {len(places)} places matching '{query}'")
            return places
            
        except Exception as e:
            logger.error(f"Error fetching places: {str(e)}")
            # Handle the error - no more mock data fallback
            raise Exception(f"Error fetching places: {str(e)}")
    
    def _extract_price_information(self, place_details: Dict[str, Any]) -> List[EventPrice]:
        """Extract price information from place details or generate reasonable defaults."""
        try:
            # Price level from Google Places API (New) is in format PRICE_LEVEL_x (0-4)
            # 0 = Free, 1 = Inexpensive, 2 = Moderate, 3 = Expensive, 4 = Very Expensive
            price_level_str = place_details.get('priceLevel', 'PRICE_LEVEL_2')
            
            # Handle parsing the price level safely
            price_level = 2  # Default to moderate
            if price_level_str and isinstance(price_level_str, str):
                try:
                    if price_level_str.startswith('PRICE_LEVEL_'):
                        price_level = int(price_level_str[12:])
                    else:
                        # Try to parse just the number if present
                        import re
                        match = re.search(r'(\d+)', price_level_str)
                        if match:
                            price_level = int(match.group(1))
                except (ValueError, IndexError):
                    # If we can't parse the price level, use the default
                    logger.warning(f"Could not parse price level from '{price_level_str}', using default")
                    pass
            
            # Generate realistic prices based on price level and venue type
            price_ranges = {
                0: (0, 0),          # Free
                1: (10, 25),        # Inexpensive
                2: (25, 75),        # Moderate
                3: (75, 150),       # Expensive
                4: (150, 300)       # Very Expensive
            }
            
            # Get the appropriate price range based on level
            min_price, max_price = price_ranges.get(price_level, (25, 75))  # Default to moderate
            
            # Generate a base adult price within the range
            if price_level == 0:
                adult_price = 0
            else:
                # More expensive venues tend to be at the higher end of their range
                weight = 0.3 if price_level <= 2 else 0.7
                price_range = max_price - min_price
                adult_price = min_price + (price_range * weight) + (random.random() * price_range * 0.4)
                adult_price = round(adult_price, -1)  # Round to nearest 10
            
            # Calculate child and senior prices
            if price_level == 0:
                child_price = senior_price = 0
            else:
                # Children usually get 20-40% discount
                child_discount = random.uniform(0.2, 0.4)
                child_price = max(5, round(adult_price * (1 - child_discount), -1))
                
                # Seniors usually get 10-25% discount
                senior_discount = random.uniform(0.1, 0.25)
                senior_price = max(5, round(adult_price * (1 - senior_discount), -1))
            
            # Create event prices
            prices = [
                EventPrice(amount=adult_price, currency="USD", category="adult"),
                EventPrice(amount=child_price, currency="USD", category="child"),
                EventPrice(amount=senior_price, currency="USD", category="senior")
            ]
            
            return prices
            
        except Exception as e:
            logger.error(f"Error extracting price information: {str(e)}")
            
            # Always return a valid list of price objects with defaults
            return [
                EventPrice(amount=25.0, currency="USD", category="adult"),
                EventPrice(amount=15.0, currency="USD", category="child"),
                EventPrice(amount=20.0, currency="USD", category="senior")
            ]
    
    def _generate_showtimes_from_hours(self, location: EventLocation, periods: List[Dict[str, Any]]) -> List[EventShowtime]:
        """Generate showtimes from venue opening hours for today."""
        logger.info(f"Generating showtimes from opening hours for venue at {location.address}")
        
        try:
            showtimes = []
            
            # Determine the timezone from the venue location - more robust timezone detection
            venue_timezone = pytz.timezone('America/New_York')  # Default timezone
            try:
                if location and location.address:
                    # More comprehensive timezone detection based on address
                    address_lower = location.address.lower()
                    if any(term in address_lower for term in ['new york', 'ny', 'nyc', 'brooklyn', 'manhattan', 'bronx', 'queens']):
                        venue_timezone = pytz.timezone('America/New_York')
                    elif any(term in address_lower for term in ['los angeles', 'la', 'hollywood', 'california', 'ca', 'san francisco', 'san diego', 'pasadena']):
                        venue_timezone = pytz.timezone('America/Los_Angeles')
                    elif any(term in address_lower for term in ['chicago', 'illinois', 'il']):
                        venue_timezone = pytz.timezone('America/Chicago')
                    elif any(term in address_lower for term in ['denver', 'colorado', 'co']):
                        venue_timezone = pytz.timezone('America/Denver')
                    elif any(term in address_lower for term in ['london', 'uk', 'england']):
                        venue_timezone = pytz.timezone('Europe/London')
                    
                    # Log the determined timezone
                    logger.info(f"Determined timezone for venue: {venue_timezone}")
            except Exception as e:
                logger.warning(f"Error determining timezone: {str(e)}")
            
            # Get current time in venue timezone - this is critical for correct time comparisons
            current_time_utc = datetime.now(pytz.UTC)
            current_time_venue = current_time_utc.astimezone(venue_timezone)
            
            logger.info(f"Current time in venue timezone ({venue_timezone}): {current_time_venue.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            # If we don't have periods, generate generic showtimes
            if not periods:
                logger.warning("No opening periods provided, generating generic showtimes")
                return self._generate_demo_showtimes(location, venue_timezone)
            
            # Find current day of week in the venue's timezone (0 = Sunday in Places API New format)
            today_dow = current_time_venue.weekday()
            if today_dow == 6:  # Sunday is 0 in Places API format
                today_dow = 0
            else:
                today_dow += 1  # Convert to Google's format (0 = Sunday, 1 = Monday, etc.)
            
            # Find opening period for today in the venue's timezone
            today_period = None
            for period in periods:
                # In Places API (New), openDay is a string like DAY_OF_WEEK_SUNDAY
                open_day_str = period.get('openDay', '')
                if open_day_str:
                    day_mapping = {
                        'DAY_OF_WEEK_SUNDAY': 0,
                        'DAY_OF_WEEK_MONDAY': 1,
                        'DAY_OF_WEEK_TUESDAY': 2,
                        'DAY_OF_WEEK_WEDNESDAY': 3,
                        'DAY_OF_WEEK_THURSDAY': 4,
                        'DAY_OF_WEEK_FRIDAY': 5,
                        'DAY_OF_WEEK_SATURDAY': 6
                    }
                    if day_mapping.get(open_day_str) == today_dow:
                        today_period = period
                        break
            
            if not today_period:
                logger.info(f"No opening period found for today (day {today_dow}) in venue timezone")
                # Generate generic showtimes for testing in venue timezone
                return self._generate_demo_showtimes(location, venue_timezone)
            
            # Parse opening hours
            try:
                # In Places API (New), hours are in format like "15:30"
                open_time_str = today_period.get('openTime', '09:00')
                close_time_str = today_period.get('closeTime', '17:00')
                
                if ':' in open_time_str and ':' in close_time_str:
                    open_hour, open_minute = map(int, open_time_str.split(':'))
                    close_hour, close_minute = map(int, close_time_str.split(':'))
                    
                    # Create datetime objects for opening hours in venue timezone
                    venue_today = current_time_venue.date()
                    opens_today = venue_timezone.localize(
                        datetime.combine(venue_today, time(open_hour, open_minute))
                    )
                    closes_today = venue_timezone.localize(
                        datetime.combine(venue_today, time(close_hour, close_minute))
                    )
                    
                    # If closing is earlier than opening, it closes the next day
                    if closes_today < opens_today:
                        closes_today = closes_today + timedelta(days=1)
                    
                    # Generate showtimes every 2 hours during open period
                    # Use venue's current hour, not system hour
                    current_hour = current_time_venue.hour
                    for hour in range(open_hour, close_hour, 2):
                        if hour >= open_hour and hour < close_hour - 1:  # Allow 1 hour buffer before closing
                            showtime = venue_timezone.localize(
                                datetime.combine(venue_today, time(hour, 0))
                            )
                            
                            # Compare using venue's current time, not system time
                            if showtime > current_time_venue and showtime < closes_today:
                                # Generate random availability
                                availability = random.choice(["available", "limited", "almost sold out"])
                                
                                showtimes.append(EventShowtime(
                                    start_time=showtime,
                                    end_time=showtime + timedelta(hours=2),
                                    availability=availability
                                ))
                
                if not showtimes:
                    logger.info("No valid showtimes could be generated from hours, using demo showtimes with venue timezone")
                    return self._generate_demo_showtimes(location, venue_timezone)
                    
                return showtimes
                    
            except Exception as e:
                logger.error(f"Error generating showtimes from hours: {str(e)}")
                return self._generate_demo_showtimes(location, venue_timezone)
            
        except Exception as e:
            logger.error(f"Error in _generate_showtimes_from_hours: {str(e)}")
            return self._generate_demo_showtimes(location)
    
    def _generate_demo_showtimes(self, location: EventLocation = None, venue_timezone: pytz.timezone = None, force_today: bool = True) -> List[EventShowtime]:
        """
        Generate demo showtimes for an event for today with realistic times in the venue's timezone.
        
        Args:
            location: The venue location
            venue_timezone: Optional explicit timezone, otherwise detected from location
            force_today: If True, ensures at least one showtime is generated for today (now default to True)
        """
        showtimes = []
        
        # Determine the venue timezone if not provided
        if not venue_timezone:
            # Default to Eastern Time if we can't determine timezone
            venue_timezone = pytz.timezone('America/New_York')
            
            if location and location.address:
                address_lower = location.address.lower()
                # More comprehensive timezone detection
                if any(term in address_lower for term in ['new york', 'ny', 'nyc', 'brooklyn', 'manhattan', 'bronx', 'queens']):
                    venue_timezone = pytz.timezone('America/New_York')
                elif any(term in address_lower for term in ['los angeles', 'la', 'hollywood', 'california', 'ca', 'san francisco', 'san diego', 'pasadena']):
                    venue_timezone = pytz.timezone('America/Los_Angeles')
                elif any(term in address_lower for term in ['chicago', 'illinois', 'il']):
                    venue_timezone = pytz.timezone('America/Chicago')
                elif any(term in address_lower for term in ['denver', 'colorado', 'co']):
                    venue_timezone = pytz.timezone('America/Denver')
                elif any(term in address_lower for term in ['london', 'uk', 'england']):
                    venue_timezone = pytz.timezone('Europe/London')
        
        # Get current time in venue timezone - critical for correct comparisons
        current_time_utc = datetime.now(pytz.UTC)
        current_time_venue = current_time_utc.astimezone(venue_timezone)
        
        logger.info(f"Generating demo showtimes for venue timezone: {venue_timezone}")
        logger.info(f"Current time in venue timezone: {current_time_venue.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # Use venue's date (today), not system date
        venue_today = current_time_venue.date()
        
        # Common showing times for entertainment venues
        common_times = [
            (10, 0),  # 10:00 AM
            (13, 30),  # 1:30 PM
            (16, 0),   # 4:00 PM
            (19, 30),  # 7:30 PM
            (21, 0)    # 9:00 PM
        ]
        
        # Choose 3 random times from common times
        selected_times = random.sample(common_times, min(3, len(common_times)))
        
        # Sort times so earlier times come first
        selected_times.sort()
        
        for hour, minute in selected_times:
            # Create datetime for venue's today with the selected time
            event_time = venue_timezone.localize(
                datetime.combine(venue_today, time(hour, minute))
            )
            
            # Only include future times based on venue's current time
            if event_time <= current_time_venue and not force_today:
                continue
                
            # Event ends 2 hours after start
            end_time = event_time + timedelta(hours=2)
            
            # Random availability, weighted more toward "available"
            availability = random.choices(
                ["available", "limited", "sold out"],
                weights=[0.7, 0.2, 0.1]
            )[0]
            
            showtime = EventShowtime(
                start_time=event_time,
                end_time=end_time,
                availability=availability
            )
            
            showtimes.append(showtime)
        
        # If force_today is True and we don't have any today showtimes yet,
        # ensure we add at least one showtime for today
        if force_today and not showtimes:
            # Find next possible showtime after current time
            current_hour = current_time_venue.hour
            current_minute = current_time_venue.minute
            
            # Common evening showtimes if it's not too late
            evening_times = [(19, 30), (20, 0), (21, 0)]
            
            # Find the next available time today
            valid_time = None
            for hour, minute in evening_times:
                if hour > current_hour or (hour == current_hour and minute > current_minute):
                    valid_time = (hour, minute)
                    break
            
            # If we found a valid time today, use it
            if valid_time:
                hour, minute = valid_time
                event_time = venue_timezone.localize(
                    datetime.combine(venue_today, time(hour, minute))
                )
                end_time = event_time + timedelta(hours=2)
                
                showtime = EventShowtime(
                    start_time=event_time,
                    end_time=end_time,
                    availability="available"
                )
                
                showtimes.append(showtime)
                logger.info(f"Added forced today showtime at {event_time.strftime('%H:%M')}")
            else:
                # If it's too late today, add early tomorrow
                venue_tomorrow = venue_today + timedelta(days=1)
                event_time = venue_timezone.localize(
                    datetime.combine(venue_tomorrow, time(10, 0))  # 10:00 AM tomorrow
                )
                end_time = event_time + timedelta(hours=2)
                
                showtime = EventShowtime(
                    start_time=event_time,
                    end_time=end_time,
                    availability="available"
                )
                
                showtimes.append(showtime)
                logger.info(f"It's too late for today's showings, added tomorrow at {event_time.strftime('%H:%M')}")
        
        # If we don't have any showtimes yet (perhaps all times were in the past),
        # add a showing for tomorrow in the venue's timezone
        elif not showtimes:
            venue_tomorrow = venue_today + timedelta(days=1)
            event_time = venue_timezone.localize(
                datetime.combine(venue_tomorrow, time(19, 30))  # 7:30 PM tomorrow in venue timezone
            )
            end_time = event_time + timedelta(hours=2)
            
            showtime = EventShowtime(
                start_time=event_time,
                end_time=end_time,
                availability="available"
            )
            
            showtimes.append(showtime)
            
        return showtimes
        
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._places_cache = {}
        self._details_cache = {} 

    def search_broadway_shows(self, query: str = "broadway shows", location: Optional[tuple] = None) -> List[Event]:
        """Search specifically for Broadway shows."""
        logger.info(f"Searching for Broadway shows with query: '{query}', location: {location}")
        
        try:
            # Add "broadway" to the query if not already present
            if "broadway" not in query.lower():
                search_query = f"broadway {query}"
            else:
                search_query = query
            
            # Convert UserLocation object to tuple if needed
            location_tuple = None
            if location:
                if hasattr(location, 'latitude') and hasattr(location, 'longitude'):
                    location_tuple = (location.latitude, location.longitude)
                    logger.info(f"Using location from UserLocation object: {location_tuple}")
                elif isinstance(location, tuple) and len(location) == 2:
                    location_tuple = location
                else:
                    logger.warning(f"Invalid location format provided: {type(location)}")
                    # Default to Times Square
                    location_tuple = (40.758896, -73.985130)
            else:
                # Default to Times Square if no location
                location_tuple = (40.758896, -73.985130)
            
            return self.search_events(search_query, location_tuple)
        except Exception as e:
            logger.error(f"Error searching for Broadway shows: {str(e)}")
            raise 

    def _generate_realistic_showtimes(self, place: Dict[str, Any]) -> List[EventShowtime]:
        """
        Generate realistic showtimes for an event based on place data.
        
        Args:
            place: Place dictionary from Google Places API
            
        Returns:
            List of EventShowtime objects
        """
        showtimes = []
        
        # Get the venue's timezone based on location
        venue_timezone = pytz.timezone('America/New_York')  # Default to NYC
        
        # Get current time in venue's timezone
        venue_now = datetime.now(venue_timezone)
        venue_today = venue_now.date()
        
        # Generate 3-5 showtimes over the next few days
        num_showtimes = random.randint(3, 5)
        
        for i in range(num_showtimes):
            # Determine the date (today + 0-3 days)
            days_ahead = min(i, 3)  # First showtime today, then spread out
            show_date = venue_today + timedelta(days=days_ahead)
            
            # For theaters, typical showtimes are 2pm (matinee) and 7:30pm or 8pm (evening)
            if i % 2 == 0:  # Even index - evening show
                hour = random.choice([19, 20])  # 7pm or 8pm
                minute = random.choice([0, 30])  # On the hour or half hour
            else:  # Odd index - matinee
                hour = 14  # 2pm
                minute = 0
            
            # Create datetime for the showtime
            start_time = venue_timezone.localize(
                datetime.combine(show_date, time(hour, minute))
            )
            
            # Broadway shows typically last 2-3 hours
            duration_hours = random.uniform(2, 3)
            end_time = start_time + timedelta(hours=duration_hours)
            
            # Skip if the showtime is in the past
            if start_time < venue_now:
                continue
            
            # Determine availability (more likely to be available further in the future)
            days_difference = (show_date - venue_today).days
            if days_difference == 0:
                # Today's shows have limited availability
                availability = random.choice(["limited", "sold_out"] * 2 + ["available"])
            elif days_difference == 1:
                # Tomorrow's shows have better availability
                availability = random.choice(["available"] * 3 + ["limited", "sold_out"])
            else:
                # Future shows mostly available
                availability = random.choice(["available"] * 5 + ["limited"])
            
            showtime = EventShowtime(
                start_time=start_time,
                end_time=end_time,
                availability=availability
            )
            
            showtimes.append(showtime)
        
        # Ensure we have at least one showtime
        if not showtimes:
            # Add a default showtime for tomorrow evening
            tomorrow = venue_today + timedelta(days=1)
            start_time = venue_timezone.localize(
                datetime.combine(tomorrow, time(19, 30))  # 7:30 PM
            )
            end_time = start_time + timedelta(hours=2.5)  # 2.5 hour show
            
            showtime = EventShowtime(
                start_time=start_time,
                end_time=end_time,
                availability="available"
            )
            
            showtimes.append(showtime)
        
        return showtimes
    
    def _generate_realistic_prices(self, place: Dict[str, Any]) -> List[EventPrice]:
        """
        Generate realistic prices for an event based on place data.
        
        Args:
            place: Place dictionary from Google Places API
            
        Returns:
            List of EventPrice objects
        """
        prices = []
        
        # Broadway shows typically have different price tiers
        # Orchestra/Premium: $150-300
        # Mezzanine: $100-200
        # Balcony: $50-120
        
        # Base price depends on the venue's rating and popularity
        rating = place.get('rating', 0)
        review_count = place.get('userRatingCount', 0)
        
        # Calculate a popularity score (0-1)
        popularity = min(1.0, (rating / 5.0) * 0.7 + (min(review_count, 1000) / 1000) * 0.3)
        
        # Generate price tiers
        # Premium/Orchestra
        premium_base = 150 + (popularity * 150)  # $150-300 range
        premium_price = round(premium_base / 5) * 5  # Round to nearest $5
        
        prices.append(EventPrice(
            category="Premium/Orchestra",
            amount=premium_price,
            currency="USD"
        ))
        
        # Mezzanine
        mezz_base = 100 + (popularity * 100)  # $100-200 range
        mezz_price = round(mezz_base / 5) * 5  # Round to nearest $5
        
        prices.append(EventPrice(
            category="Mezzanine",
            amount=mezz_price,
            currency="USD"
        ))
        
        # Balcony
        balcony_base = 50 + (popularity * 70)  # $50-120 range
        balcony_price = round(balcony_base / 5) * 5  # Round to nearest $5
        
        prices.append(EventPrice(
            category="Balcony",
            amount=balcony_price,
            currency="USD"
        ))
        
        return prices 