import os
import json
import logging
import sys
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("openai_test")

# Try to import OpenAI
try:
    import openai
except ImportError:
    logger.error("OpenAI package not installed. Run: pip install openai")
    sys.exit(1)

# Import configuration
try:
    import config
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    logger.error("Missing configuration or .env file")
    sys.exit(1)

def test_openai_api():
    """Test OpenAI API call"""
    logger.info("Testing OpenAI API call")
    logger.info(f"OpenAI API Key present: {bool(config.OPENAI_API_KEY)}")
    
    # Set up the prompt
    system_message = "You are a helpful travel assistant."
    user_prompt = "Create a short itinerary for New York City focused on art museums and restaurants."
    
    try:
        # Call OpenAI API
        logger.info("About to initialize OpenAI client")
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
        
        logger.info("Calling OpenAI API with chat.completions.create")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        logger.info("OpenAI API call completed successfully")
        
        # Extract response content
        ai_response = response.choices[0].message.content
        logger.info(f"Raw OpenAI response: {ai_response}")
        
        logger.info("OpenAI API test completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception details: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_openai_api() 