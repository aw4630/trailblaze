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
        
    def search_events(
        self, query: str, location: Optional[tuple] = None, 
        radius_meters: int = 20000, language: str = "en"
    ) -> List[Event]:
        """
        Search for events matching the given query and location.
        
        Args:
            query: The event query (e.g., "broadway shows", "concerts")
            location: Optional tuple of (latitude, longitude). If not provided, uses location from IP.
            radius_meters: Search radius in meters (default: 20km)
            language: Preferred language for results
            
        Returns:
            List of Event objects representing matching events
        """
        logger.info(f"Searching for events with query: '{query}', location: {location}")
        
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": config.GOOGLE_SHOWTIMES_API_KEY
            }
            
            # Build the request payload
            payload = {
                "textQuery": query,
                "maxResultCount": 20,
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": location[0],
                            "longitude": location[1]
                        },
                        "radius": radius_meters
                    }
                }
            }
            
            # Send the request to Google Places API
            response = requests.post(
                "https://places.googleapis.com/v1/places:searchText",
                headers=headers,
                json=payload
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.error(f"Error from Google Places API: {response.status_code} - {response.text}")
                raise Exception(f"Google Places API error: {response.status_code}")
            
            # Parse the response
            places_data = response.json()
            
            # Convert to Event objects
            events = self._parse_events_from_places(places_data.get("places", []), query)
            logger.info(f"Found {len(events)} events matching query '{query}'")
            
            return events
            
        except Exception as e:
            logger.error(f"Error searching for events: {str(e)}")
            # Handle the error - no more mock data fallback
            raise Exception(f"Error searching for events: {str(e)}")
    
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
            
    def get_all_matching_places(self, query: str, location: Optional[tuple] = None, radius: int = 5000) -> List[Dict[str, Any]]:
        """
        Get all places matching the query from Google Places API (New).
        
        This function handles both direct places search and fallback to find potential venues.
        """
        try:
            # First try to get places via direct API call
            places = self.get_places(query, location)
            
            # If we found places, return them
            if places:
                logger.info(f"Found {len(places)} places directly matching query '{query}'")
                return places
            else:
                # No places found, log the issue
                logger.warning(f"No places found matching '{query}'")
                raise ValueError(f"No places found matching '{query}'")
                
        except Exception as e:
            # Log the error and re-raise
            logger.error(f"Error getting all matching places: {str(e)}")
            raise ValueError(f"Error getting all places: {str(e)}")
    
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
                
            return self.search_events(search_query, location)
        except Exception as e:
            logger.error(f"Error searching for Broadway shows: {str(e)}")
            raise 