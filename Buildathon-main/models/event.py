from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime

# Using string literal annotation for forward reference
# No need for explicit ForwardRef


class EventLocation(BaseModel):
    """Model for event location."""
    name: str
    address: str
    latitude: float
    longitude: float
    place_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "name": self.name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "place_id": self.place_id
        }


class EventShowtime(BaseModel):
    """Model for event showtimes."""
    start_time: datetime
    end_time: Optional[datetime] = None
    availability: Optional[str] = None  # e.g., "available", "limited", "sold out"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "availability": self.availability
        }


class EventPrice(BaseModel):
    """Model for event pricing."""
    amount: float
    currency: str = "USD"
    category: Optional[str] = None  # e.g., "adult", "child", "senior"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "amount": self.amount,
            "currency": self.currency,
            "category": self.category
        }


class Event(BaseModel):
    """Model for event information."""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    location: EventLocation
    showtimes: List[EventShowtime] = Field(default_factory=list)
    prices: List[EventPrice] = Field(default_factory=list)
    image_url: Optional[str] = None
    website_url: Optional[str] = None
    rating: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "location": self.location.to_dict(),
            "showtimes": [showtime.to_dict() for showtime in self.showtimes],
            "prices": [price.to_dict() for price in self.prices],
            "image_url": self.image_url,
            "website_url": self.website_url,
            "rating": self.rating
        }


class EventSchedule(BaseModel):
    """Model for a schedule of events."""
    events: List[Event] = Field(default_factory=list)
    total_cost: float = 0
    total_duration: int = 0  # in minutes
    navigation_plan: Optional["NavigationPlan"] = None
    
    def add_event(self, event: Event) -> None:
        """Add an event to the schedule."""
        self.events.append(event)
        
        # Update total cost (using the lowest price if multiple are available)
        if event.prices:
            min_price = min(event.prices, key=lambda x: x.amount)
            self.total_cost += min_price.amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        result = {
            "events": [event.to_dict() for event in self.events],
            "total_cost": self.total_cost,
            "total_duration": self.total_duration
        }
        
        if self.navigation_plan:
            result["navigation_plan"] = self.navigation_plan.to_dict()
            
        return result 

# Import NavigationPlan for type checking only, after all classes are defined
from models.navigation import NavigationPlan

# Update forward references - in Pydantic v2, this should be automatic in most cases
# but we'll keep it to be sure
EventSchedule.model_rebuild() 