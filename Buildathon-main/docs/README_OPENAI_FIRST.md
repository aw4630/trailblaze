# OpenAI-First Implementation

## Overview

This is an enhanced implementation of the Broadway Show & Event Planner that uses an OpenAI-first approach. Instead of relying primarily on Google APIs for event search, this implementation uses OpenAI to:

1. Generate complete plans directly from user queries
2. Verify these plans against real-world data via Google APIs
3. Refine the plans based on verification results

## Key Benefits

- More conversational and natural responses to user queries
- Complete plans generated based on user intent rather than just keyword matching
- Verification loop ensures accurate, real-world information
- Comprehensive itineraries that include venues, events, routes, and timing

## How to Switch to OpenAI-First Mode

### Option 1: Using the Helper Script

We've provided a helper script to make switching easy:

```bash
python use_openai_first.py
```

This script will:
1. Check if your OpenAI API key is configured
2. Backup your current `app.py`
3. Replace it with the OpenAI-first implementation

### Option 2: Manual Switch

If you prefer to switch manually:

1. Make a backup of your current `app.py`
2. Copy `app_openai_first.py` to `app.py`:
   ```bash
   cp app_openai_first.py app.py
   ```

## Requirements

- OpenAI API key (version 0.27.8)
- Google Maps API key with Places, Directions, and Geocoding enabled
- Python 3.7 or higher
- Flask framework

## Configuration

### API Keys Setup

Make sure your `.env` file contains:

```
OPENAI_API_KEY=your_openai_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GOOGLE_SHOWTIMES_API_KEY=your_google_places_api_key
OPENAI_MODEL=gpt-3.5-turbo  # or other supported model
```

### Google API Configuration

You need to enable specific APIs in your Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to "APIs & Services" > "Library"
4. Enable the following APIs:
   - Places API
   - Geocoding API
   - Directions API
   - Routes API (Important: This is required for detailed navigation)
   - Distance Matrix API

Without enabling these APIs, your verification will fail with authorization errors.

## Testing the Implementation

After switching, you can test the implementation by:

1. Running the Flask app:
   ```bash
   python app.py
   ```

2. Using the chat interface at `/` or the AI planner at `/ai-planner`

3. Running the test script:
   ```bash
   python tests/test_openai_first.py "Broadway shows and dinner in New York tonight"
   ```

## How It Works

### Chat Endpoint (`/api/chat`)

When a user sends a message to the chat endpoint:

1. The message is sent directly to OpenAI to create an initial plan
2. The plan is verified against Google APIs
3. If issues are found, the plan is refined by OpenAI
4. A natural language summary is generated
5. The response includes both the conversational summary and structured data

### AI Planner Endpoint (`/api/plan`)

This dedicated endpoint follows the same flow but exposes more details about the verification process.

## Restoring the Original Implementation

If you want to restore the original implementation, rename your backup file:

```bash
cp app_backup_TIMESTAMP.py app.py
```

Replace `TIMESTAMP` with the actual timestamp in your backup filename.

## Troubleshooting

- **Error: OpenAI service is not available**
  Make sure your OpenAI API key is properly set in the `.env` file.

- **Error: Plan verification service is not available**
  Check that your Google API keys are properly configured.

- **Google API Authorization Errors**
  If you see "This API key is not authorized to use this service or API", you need to enable the specific API in your Google Cloud Console.

- **Slow responses**
  The OpenAI-first approach may take longer to generate responses as it involves multiple API calls for verification.

## Contact

If you encounter any issues or have questions, please contact the development team. 