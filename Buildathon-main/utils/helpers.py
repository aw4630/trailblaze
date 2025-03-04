from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import re


def parse_time_string(time_str: str) -> Optional[datetime]:
    """Parse a time string into a datetime object."""
    formats = [
        "%H:%M",  # 24-hour format (e.g., "14:30")
        "%I:%M %p",  # 12-hour format with AM/PM (e.g., "2:30 PM")
        "%I:%M%p",  # 12-hour format without space (e.g., "2:30PM")
        "%I %p"  # Hour only (e.g., "2 PM")
    ]
    
    for fmt in formats:
        try:
            # Parse the time string
            time_obj = datetime.strptime(time_str, fmt)
            
            # Set the date to today
            now = datetime.now()
            time_obj = time_obj.replace(
                year=now.year,
                month=now.month,
                day=now.day
            )
            
            return time_obj
        except ValueError:
            continue
    
    return None


def extract_budget(text: str) -> Optional[float]:
    """Extract budget amount from text."""
    # Look for patterns like "$50", "50 dollars", etc.
    dollar_pattern = r'\$(\d+(?:\.\d+)?)'
    number_pattern = r'(\d+(?:\.\d+)?)\s*(?:dollars|USD)'
    
    dollar_match = re.search(dollar_pattern, text)
    if dollar_match:
        return float(dollar_match.group(1))
    
    number_match = re.search(number_pattern, text)
    if number_match:
        return float(number_match.group(1))
    
    return None


def format_duration(seconds: int) -> str:
    """Format duration in seconds to a human-readable string."""
    if seconds < 60:
        return f"{seconds} seconds"
    
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minutes"
    
    hours = minutes // 60
    minutes = minutes % 60
    
    if minutes == 0:
        return f"{hours} hours"
    else:
        return f"{hours} hours {minutes} minutes"


def format_distance(meters: float) -> str:
    """Format distance in meters to a human-readable string."""
    if meters < 1000:
        return f"{int(meters)} meters"
    
    kilometers = meters / 1000
    return f"{kilometers:.1f} kilometers"


def format_price(amount: float, currency: str = "USD") -> str:
    """Format price to a human-readable string."""
    if currency == "USD":
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"


def format_datetime(dt: datetime) -> str:
    """Format datetime to a human-readable string."""
    return dt.strftime("%A, %B %d, %Y at %I:%M %p")


def html_to_text(html: str) -> str:
    """Convert HTML to plain text."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html)
    # Replace HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text 