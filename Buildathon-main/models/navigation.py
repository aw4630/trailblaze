from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum

# Conditional import to avoid circular imports at runtime
if TYPE_CHECKING:
    from models.event import EventSchedule


class TransportMode(str, Enum):
    """Enum for transport modes."""
    DRIVING = "driving"
    WALKING = "walking"
    BICYCLING = "bicycling"
    TRANSIT = "transit"


class RouteStep(BaseModel):
    """Model for a step in a route."""
    instruction: str
    distance: float  # in meters
    duration: int  # in seconds
    start_location: Dict[str, float]  # lat, lng
    end_location: Dict[str, float]  # lat, lng
    travel_mode: TransportMode
    html_instructions: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "instruction": self.instruction,
            "distance": self.distance,
            "duration": self.duration,
            "start_location": self.start_location,
            "end_location": self.end_location,
            "travel_mode": self.travel_mode.value,
            "html_instructions": self.html_instructions
        }


class Route(BaseModel):
    """Model for a route between two locations."""
    origin: Dict[str, float]  # lat, lng
    destination: Dict[str, float]  # lat, lng
    distance: float  # in meters
    duration: int  # in seconds
    steps: List[RouteStep] = Field(default_factory=list)
    travel_mode: TransportMode
    polyline: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "origin": self.origin,
            "destination": self.destination,
            "distance": self.distance,
            "duration": self.duration,
            "steps": [step.to_dict() for step in self.steps],
            "travel_mode": self.travel_mode.value,
            "polyline": self.polyline
        }


class NavigationPlan(BaseModel):
    """Model for a navigation plan between multiple locations."""
    routes: List[Route] = Field(default_factory=list)
    total_distance: float = 0  # in meters
    total_duration: int = 0  # in seconds
    
    def add_route(self, route: Route) -> None:
        """Add a route to the navigation plan."""
        self.routes.append(route)
        self.total_distance += route.distance
        self.total_duration += route.duration
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "routes": [route.to_dict() for route in self.routes],
            "total_distance": self.total_distance,
            "total_duration": self.total_duration
        } 