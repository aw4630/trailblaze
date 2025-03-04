# Configuration

This directory contains configuration files for the Broadway Show & Event Planner application.

## Files

- **config.py** - Main configuration module with settings for API endpoints, credentials, and application settings
- **.env** - Environment variables file (copy of the root .env file)
- **temp_config.py** - Temporary configuration used during development

## Environment Variables

The application requires the following environment variables to be set in the `.env` file:

```
# API Keys
OPENAI_API_KEY=your_openai_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
GOOGLE_SHOWTIMES_API_KEY=your_google_places_key

# Application Settings
DEBUG=False  # Set to True for debug mode
PORT=5000    # Application port
HOST=0.0.0.0 # Application host

# API Model Configuration
OPENAI_MODEL=gpt-3.5-turbo  # OpenAI model to use
```

## Important Notes

- Do not commit `.env` files with real API keys to version control
- The application will check for required API keys on startup
- Mock data is no longer supported; all API keys are required 