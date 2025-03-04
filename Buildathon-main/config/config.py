import os
from dotenv import load_dotenv
import logging

# Set up logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    logger.warning("Missing ANTHROPIC_API_KEY in environment variables")
else:
    logger.info(f"ANTHROPIC_API_KEY: {'*' * (len(ANTHROPIC_API_KEY) - 8)}{ANTHROPIC_API_KEY[-8:] if ANTHROPIC_API_KEY else ''}")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("Missing OPENAI_API_KEY in environment variables")
else:
    logger.info(f"OPENAI_API_KEY: {'*' * (len(OPENAI_API_KEY) - 8)}{OPENAI_API_KEY[-8:] if OPENAI_API_KEY else ''}")

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    logger.warning("Missing GOOGLE_MAPS_API_KEY in environment variables")
else:
    logger.info(f"GOOGLE_MAPS_API_KEY: {'*' * (len(GOOGLE_MAPS_API_KEY) - 8)}{GOOGLE_MAPS_API_KEY[-8:] if GOOGLE_MAPS_API_KEY else ''}")

GOOGLE_SHOWTIMES_API_KEY = os.getenv("GOOGLE_SHOWTIMES_API_KEY")
if not GOOGLE_SHOWTIMES_API_KEY:
    logger.warning("Missing GOOGLE_SHOWTIMES_API_KEY in environment variables")
else:
    logger.info(f"GOOGLE_SHOWTIMES_API_KEY: {'*' * (len(GOOGLE_SHOWTIMES_API_KEY) - 8)}{GOOGLE_SHOWTIMES_API_KEY[-8:] if GOOGLE_SHOWTIMES_API_KEY else ''}")

# Data Handling Configuration
USE_MOCK_DATA = False  # Mock data is NOT SUPPORTED and should NEVER be enabled
logger.info(f"Mock data is DISABLED - the application requires actual API responses")

# Claude AI Model Configuration
CLAUDE_MODEL = "claude-3-haiku-20240307"
MAX_TOKENS = 4000

# OpenAI Model Configuration
OPENAI_MODEL = "gpt-4o"  # Default model, can also use "gpt-4" for better results
OPENAI_MAX_TOKENS = 2000

# Embedding Model Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# API Endpoints
GOOGLE_DIRECTIONS_API_URL = "https://maps.googleapis.com/maps/api/directions/json"
GOOGLE_SHOWTIMES_API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("PORT", 5000))
HOST = os.getenv("HOST", "0.0.0.0") 