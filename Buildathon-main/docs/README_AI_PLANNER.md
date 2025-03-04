# AI-Driven Planner

## Overview

The AI-Driven Planner is a new feature that leverages OpenAI to create comprehensive plans for users, incorporating real-world venues, events, showtimes, and navigation routes. This system uses a verification loop to ensure that AI-generated plans align with real-world data from Google APIs.

## Key Components

1. **OpenAI Service (Enhanced)**
   - `create_initial_plan`: Generates an initial plan using OpenAI's web browsing capabilities
   - `refine_plan`: Refines plans based on verification feedback

2. **Plan Verification Service**
   - `PlanVerifier`: Validates venues, events, routes, and timing logic using Google APIs
   - Identifies issues that need correction

3. **AI Planner API**
   - `/api/plan` endpoint: Orchestrates the planning process
   - Implements a verification loop that refines plans until they are accurate

4. **Frontend Interface**
   - Web form for user input
   - Interactive display of generated plans
   - Visualization of routes, venues, and events

## How It Works

1. **User Query Processing**
   - The user submits a query about what they want to do
   - The system extracts intent and context from the query

2. **Initial Plan Generation**
   - OpenAI creates an initial plan with venues, events, and routes
   - Plans are structured in a consistent JSON format

3. **Verification Loop**
   - The plan is verified against Google APIs
   - Issues are identified (invalid venues, incorrect showtimes, unrealistic routes)

4. **Plan Refinement**
   - OpenAI refines the plan based on identified issues
   - The process repeats until the plan is error-free or max iterations reached

5. **Results Presentation**
   - The system generates a natural language summary of the plan
   - Detailed information is presented in an organized, visual format

## Usage

### API Endpoint

```json
POST /api/plan
{
  "query": "Broadway shows and dinner in New York tonight",
  "transport_mode": "walking",
  "max_iterations": 3
}
```

**Response Format:**

```json
{
  "success": true,
  "plan": {
    "summary": "Your evening in New York includes dinner at Carmine's at 6:00 PM followed by 'The Lion King' at Minskoff Theatre at 8:00 PM...",
    "venues": [...],
    "events": [...],
    "routes": [...],
    "total_duration": "4 hours 30 minutes",
    "total_cost": "$$-$$$",
    "issues": []
  },
  "query": "Broadway shows and dinner in New York tonight",
  "transport_mode": "walking",
  "iterations": 2
}
```

### Web Interface

Access the planner at `/ai-planner` in your browser.

## Testing

Run the test script to verify functionality:

```
python tests/test_ai_planner.py "Dinner and a Broadway show in New York"
```

## Implementation Details

### Plan JSON Structure

```json
{
  "venues": [
    {
      "id": "venue_1",
      "name": "Restaurant Name",
      "address": "123 Broadway, New York, NY",
      "place_id": "Google Place ID",
      "location": {"lat": 40.123, "lng": -73.456},
      "verified": true,
      "phone": "+1 212-555-1234",
      "website": "https://example.com",
      "price_level": 2
    }
  ],
  "events": [
    {
      "id": "event_1",
      "venue_id": "venue_1",
      "name": "Dinner",
      "start_time": "2023-04-15T18:00:00",
      "end_time": "2023-04-15T19:30:00",
      "duration": 90,
      "verified": true
    }
  ],
  "routes": [
    {
      "id": "route_1",
      "origin_id": "event_1",
      "destination_id": "event_2",
      "mode": "walking",
      "distance": 500,
      "duration": 600,
      "verified": true,
      "steps": [...]
    }
  ],
  "total_duration": 14400,
  "total_cost": 3,
  "issues": []
}
```

## Requirements

- OpenAI API key configured in `.env` file
- Google Maps API key with Places, Directions, and Geocoding enabled
- `openai` Python package version 0.27.8 or higher
- Flask web framework

## Future Enhancements

1. Support for filtering by price range and accessibility requirements
2. Calendar integration for event scheduling
3. User preference learning based on feedback
4. Multi-day itinerary planning
5. Mobile-optimized interface with real-time updates 