# Utility Scripts

This directory contains various utility scripts for managing the Broadway Show & Event Planner application.

## API Key Management

- **set_openai_key.py** - Command-line tool to set the OpenAI API key in the .env file
- **set_key_from_clipboard.py** - Utility to set the OpenAI API key from clipboard content

## Application Management

- **use_openai_first.py** - Script to switch to the OpenAI-first implementation
- **organize_tests.py** - Script to organize test files into the tests directory

## Usage

All scripts should be run from the project root directory:

```bash
# Set OpenAI API key
python scripts/set_openai_key.py --key YOUR_API_KEY

# Switch to OpenAI-first implementation
python scripts/use_openai_first.py

# Organize test files
python scripts/organize_tests.py
``` 