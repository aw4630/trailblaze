# OpenAI Integration for Broadway Shows Application

This document explains the changes made to switch the application from using Claude to OpenAI for AI-powered features.

## Overview of Changes

The application has been updated to use OpenAI's API instead of Anthropic's Claude for the following features:
- Processing user queries for event preferences
- Generating natural language responses to users
- Validating event data against user preferences

## New Files

1. `services/openai_service.py` - A new service class that replaces the Claude service
2. `set_key_from_clipboard.py` - A utility script to set the OpenAI API key
3. `run_with_openai.py` - A script to run the application with OpenAI enabled
4. `tests/test_with_openai.py` - A modified test script for OpenAI integration
5. `README_OPENAI.md` - This documentation file

## Modified Files

1. `app.py` - Updated to use OpenAIService instead of ClaudeService
2. `config.py` - Added OpenAI API key and model configuration
3. `requirements.txt` - Added OpenAI package dependency

## How to Use

### Setup

1. First, set up your OpenAI API key by running:
   ```
   python set_key_from_clipboard.py
   ```
   This will set the key in the `.env` file and enable mock data for testing.

2. Alternatively, you can set the key manually by adding it to your `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   USE_MOCK_DATA=True
   ```

### Running the Application

1. Run the application with OpenAI integration:
   ```
   python run_with_openai.py
   ```

2. Or, run the application normally after setting the API key:
   ```
   python app.py
   ```

### Testing

1. Run the OpenAI-specific tests:
   ```
   python tests/test_with_openai.py
   ```

## API Models

The default OpenAI model is set to `gpt-3.5-turbo` in the configuration. You can change this to a different model like `gpt-4` for potentially better results by updating the `OPENAI_MODEL` value in `config.py`.

## Fallback Behavior

The application maintains backward compatibility with Claude. If the OpenAI service fails to initialize but Claude is available, the service status endpoint will indicate this.

## Mock Data

For testing without active API keys, mock data is enabled by default when using the scripts provided. This can be toggled by changing the `USE_MOCK_DATA` setting in the `.env` file or in `config.py`.

## Troubleshooting

- **Missing API Key**: Make sure your OpenAI API key is correctly set in the `.env` file.
- **API Key Format**: OpenAI API keys typically start with `sk-`.
- **Missing Dependencies**: Run `pip install -r requirements.txt` to ensure all dependencies are installed.
- **API Rate Limits**: The OpenAI API has rate limits. If you encounter errors related to rate limits, consider implementing retry logic or requesting increased limits.

## Next Steps

1. Refine prompt engineering for better results with OpenAI models
2. Implement streaming responses for a more interactive user experience
3. Add support for more advanced OpenAI features like function calling 