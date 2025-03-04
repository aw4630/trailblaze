import os
import sys
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('openai_test.log')
    ]
)
logger = logging.getLogger("openai_simple_test")

# Try to load environment variables directly
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Loaded .env file using python-dotenv")
except ImportError:
    logger.error("python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

# Check if OpenAI API key exists in environment
openai_key = os.environ.get("OPENAI_API_KEY")
if not openai_key:
    logger.error("OPENAI_API_KEY not found in environment variables")
    logger.info("Checking current working directory...")
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Check if .env file exists
    if os.path.exists(".env"):
        logger.info(".env file exists. Content preview (without showing full key):")
        with open(".env", "r") as f:
            for line in f:
                if "OPENAI_API_KEY" in line:
                    key_value = line.strip().split("=", 1)
                    if len(key_value) > 1 and key_value[1]:
                        masked_key = key_value[1][:5] + "..." + key_value[1][-5:] if len(key_value[1]) > 10 else "[EMPTY]"
                        logger.info(f"Found OPENAI_API_KEY in .env file: {masked_key}")
                    else:
                        logger.error("OPENAI_API_KEY exists in .env but has no value")
                else:
                    logger.debug(f"Other env variable: {line.split('=')[0] if '=' in line else line.strip()}")
    else:
        logger.error(".env file not found in current directory")
        sys.exit(1)
else:
    masked_key = openai_key[:5] + "..." + openai_key[-5:] if len(openai_key) > 10 else "[EMPTY]"
    logger.info(f"OPENAI_API_KEY found in environment: {masked_key}")

# Try to import and initialize OpenAI
try:
    import openai
    logger.info("OpenAI package imported successfully")
    
    # Print OpenAI version
    logger.info(f"OpenAI package version: {openai.__version__}")
    
    # Set API key directly (older style)
    openai.api_key = openai_key
    logger.info("OpenAI API key set")
    
    # Make a simple API call using older API style (for version 0.27.x)
    logger.info("Attempting a simple completion call...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ],
        max_tokens=10
    )
    
    # Log the response
    logger.info(f"OpenAI API responded successfully: {response.choices[0].message.content}")
    logger.info("OpenAI API test PASSED!")
    print("OpenAI API test PASSED! Check openai_test.log for details.")
    
except ImportError:
    logger.error("OpenAI package not installed. Run: pip install openai")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error testing OpenAI API: {str(e)}")
    logger.error("OpenAI API test FAILED! Check openai_test.log for details.")
    print("OpenAI API test FAILED! Check openai_test.log for details.")
    sys.exit(1) 