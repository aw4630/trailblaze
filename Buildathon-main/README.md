# Broadway Show & Event Planner Application

## Overview

This application helps users plan Broadway show visits and related events using a combination of AI (OpenAI) and Google APIs. It provides a chat interface and automated planning capabilities.

## Project Structure

The project has been organized into a clean directory structure:

```
.
├── app.py                 # Main Flask application
├── run_with_openai.py     # Entry point script
├── app_openai_first.py    # Alternative OpenAI-first implementation
├── backups/               # Backup files and logs
├── config/                # Configuration files
│   ├── .env               # Environment variables (copied)
│   └── config.py          # Configuration module
├── docs/                  # Documentation
│   ├── README_*.md        # Various README files
│   ├── RECOVERY_GUIDE.md  # Recovery instructions
│   └── API_FIXES.md       # API implementation notes
├── models/                # Data models
├── scripts/               # Utility scripts
│   ├── set_openai_key.py  # API key management
│   └── use_openai_first.py  # Switch to OpenAI-first implementation
├── services/              # External API services
│   ├── google_maps_service.py
│   ├── google_showtimes_service.py
│   ├── openai_service.py
│   └── plan_verification.py
├── static/                # Frontend assets
├── templates/             # HTML templates
├── tests/                 # Test suite
└── utils/                 # Utility functions
```

## Getting Started

1. Set up your environment:
   ```
   python -m pip install -r requirements.txt
   ```

2. Configure API keys in `.env` file:
   ```
   OPENAI_API_KEY=your_key_here
   GOOGLE_MAPS_API_KEY=your_key_here
   GOOGLE_SHOWTIMES_API_KEY=your_key_here
   ```

3. Run the application:
   ```
   python run_with_openai.py
   ```

## Documentation

For more detailed documentation, see the files in the `docs/` directory:

- API implementations and changes: `docs/API_FIXES*.md`
- Recovery procedures: `docs/RECOVERY_GUIDE*.md`
- OpenAI implementation details: `docs/README_OPENAI*.md`

## API Integrations

- **OpenAI API**: Used for generating plans and chat responses
- **Google Maps API**: Uses Routes API for directions and travel times
- **Google Places API**: For showtimes and venue information 