# Broadway Show & Event Planner

A web application that helps users find entertainment events, including Broadway shows, movies, and concerts with accurate timezone handling for showtimes, and now featuring an AI-driven planner for comprehensive itineraries.

## Features

- Search for Broadway shows, movies, concerts, and other entertainment events
- Find events based on location (e.g., New York, Los Angeles)
- View accurate showtimes in the venue's local timezone
- Search for specific shows like "The Great Gatsby Musical"
- Get event pricing and venue information
- **NEW: AI-Driven Planner** - Create complete itineraries with verified venues, events, and routing

## Project Structure

```
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── models/                 # Data models
│   ├── embedding.py        # Embedding model for text processing
│   ├── event.py            # Event data models
│   ├── navigation.py       # Navigation and routing models
│   └── user.py             # User context and preferences
├── services/               # Service integrations
│   ├── openai_service.py   # OpenAI integration for planning and chat
│   ├── google_maps_service.py # Google Maps integration
│   ├── google_showtimes_service.py # Google Places API for events
│   └── plan_verification.py # Verification service for AI-generated plans
├── static/                 # Static assets (CSS, JS, images)
│   ├── js/
│   │   └── ai_planner.js   # Frontend for AI planner
│   └── ...
├── templates/              # HTML templates
│   ├── ai_planner.html     # AI planner interface
│   └── ...
├── tests/                  # Test modules
│   ├── test_app.py         # Application tests
│   └── test_ai_planner.py  # Tests for AI planner feature
├── utils/                  # Utility functions
│   └── helpers.py          # Helper functions
└── README_AI_PLANNER.md    # Detailed documentation for AI planner
```

## Testing Scripts

The repository includes several test scripts to verify functionality:

- `test_gatsby_search.py` - Tests searching for "The Great Gatsby Musical"
- `test_specific_show.py` - Tests finding specific shows
- `test_timezone.py` - Tests timezone handling
- `test_timezone_events.py` - Tests timezone handling for events
- `test_with_openai.py` - Tests OpenAI integration
- `test_ai_planner.py` - Tests the AI-driven planning feature

## Configuration

1. Create a `.env` file in the project root with the following API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   GOOGLE_SHOWTIMES_API_KEY=your_google_places_api_key
   USE_MOCK_DATA=False  # Set to True for testing without API calls
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

## API Endpoints

- `/` - Main web interface
- `/ai-planner` - AI-driven planning interface
- `/api/chat` - Chat interface for event queries
- `/api/plan` - Generate comprehensive plans with venue and route verification
- `/api/profile` - Update user profile information
- `/api/preferences` - Update user preferences
- `/api/service-status` - Check service availability

## AI-Driven Planner

The new AI-driven planner feature uses OpenAI to generate comprehensive itineraries with:

- Real venue information verified against Google Places API
- Accurate showtimes and event details
- Realistic routing with walking times between venues
- Cost estimates and timing considerations

See [README_AI_PLANNER.md](README_AI_PLANNER.md) for full documentation.

## Debugging

The application includes a debug mode that can be enabled by setting `DEBUG=True` in the `.env` file. When enabled, additional debugging information is available at the `/api/debug` endpoint. 