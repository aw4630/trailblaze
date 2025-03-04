from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any


class UserLocation(BaseModel):
    """Model for user's current location."""
    latitude: float
    longitude: float
    address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the location to a dictionary."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address
        }


class UserProfile(BaseModel):
    """Model for user profile information."""
    email: Optional[str] = None
    accessibility_needs: Optional[List[str]] = Field(default_factory=list)
    walking_capability: Optional[str] = None  # e.g., "high", "medium", "low"
    location: Optional[UserLocation] = None


class UserPreferences(BaseModel):
    """Model for user preferences gathered during chat."""
    event_theme: Optional[str] = None
    available_time_start: Optional[str] = None
    available_time_end: Optional[str] = None
    budget: Optional[float] = None
    transport_preferences: Optional[List[str]] = Field(default_factory=list)


class UserContext(BaseModel):
    """Combined model for all user context information."""
    profile: UserProfile = Field(default_factory=UserProfile)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    messages: List[Dict[str, str]] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary for embedding."""
        return {
            "profile": self.profile.model_dump(exclude_none=True),
            "preferences": self.preferences.model_dump(exclude_none=True)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserContext':
        """Create a UserContext instance from a dictionary."""
        if isinstance(data, cls):
            return data
            
        if not isinstance(data, dict):
            return cls()
            
        # Extract profile data
        profile_data = data.get('profile', {})
        if profile_data and 'location' in profile_data and isinstance(profile_data['location'], dict):
            # Convert location dict to UserLocation
            location_data = profile_data['location']
            profile_data['location'] = UserLocation(**location_data)
        
        profile = UserProfile(**profile_data) if profile_data else UserProfile()
        
        # Extract preferences data
        preferences_data = data.get('preferences', {})
        preferences = UserPreferences(**preferences_data) if preferences_data else UserPreferences()
        
        # Extract messages
        messages = data.get('messages', [])
        
        return cls(
            profile=profile,
            preferences=preferences,
            messages=messages
        )
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.messages.append({
            "role": role,
            "content": content
        })
    
    def update_from_chat(self, chat_data: Dict[str, Any]) -> None:
        """Update user context from chat interaction."""
        if "event_theme" in chat_data:
            self.preferences.event_theme = chat_data["event_theme"]
        
        if "available_time_start" in chat_data:
            self.preferences.available_time_start = chat_data["available_time_start"]
            
        if "available_time_end" in chat_data:
            self.preferences.available_time_end = chat_data["available_time_end"]
            
        if "budget" in chat_data:
            self.preferences.budget = chat_data["budget"]
            
        if "transport_preferences" in chat_data:
            self.preferences.transport_preferences = chat_data["transport_preferences"] 