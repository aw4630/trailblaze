# Testing Guide for OpenAI-First Implementation

This guide outlines how to test the new OpenAI-first implementation of the Broadway Show & Event Planner.

## Prerequisites

Before testing, ensure you have:

1. Installed all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables in a `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   GOOGLE_SHOWTIMES_API_KEY=your_google_places_api_key
   ```

3. Switched to the OpenAI-first implementation:
   ```bash
   python use_openai_first.py
   ```

## Test Methods

### 1. Using the Test Script

The quickest way to test the OpenAI-first implementation is using the provided test script:

```bash
python tests/test_openai_first.py "Broadway shows and dinner in New York tonight"
```

You can customize the query, transport mode, and maximum iterations:

```bash
python tests/test_openai_first.py "Museums and lunch in Manhattan" "TRANSIT" 2
```

The script will:
- Send your query to the planning endpoint
- Print a detailed report of the generated plan
- Save the complete plan as a JSON file for reference

### 2. Using the Web Interface

To test the application through the user interface:

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser to:
   - http://localhost:5000/ for the chat interface
   - http://localhost:5000/ai-planner for the dedicated planner UI

3. Enter your query in the input field and submit

The web interface will display the generated plan with a conversational summary and details about venues, events, and routes.

### 3. Testing the API Directly

You can test the API endpoints directly using tools like `curl` or Postman:

#### Testing the Plan Endpoint

```bash
curl -X POST http://localhost:5000/api/plan \
  -H "Content-Type: application/json" \
  -d '{"query":"Broadway shows and dinner in New York tonight","transport_mode":"WALKING","max_iterations":3}'
```

#### Testing the Chat Endpoint

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I want to see Broadway shows and have dinner in New York tonight"}'
```

## Expected Results

A successful response from the OpenAI-first implementation should include:

1. A conversational summary of the plan
2. Structured data including:
   - Venues with names, addresses, and types
   - Events with names, venues, and times
   - Routes between venues with distances and durations
   - Verification status for each item
   - Total duration and cost estimates

## Troubleshooting

### API Keys

If you see errors related to OpenAI or Google services, verify your API keys are correctly set in the `.env` file.

### Missing Dependencies

If you encounter import errors, ensure you've installed all required packages:

```bash
pip install -r requirements.txt
```

### OpenAI Version Conflicts

This implementation requires the OpenAI package version 0.27.8. If you experience issues with the OpenAI API, check your installed version:

```bash
pip show openai
```

If needed, install the correct version:

```bash
pip install openai==0.27.8
```

### Port Already in Use

If port 5000 is already in use, you can modify the port in `app.py` by changing:

```python
if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Changed from 5000 to 5001
```

## Contact

If you encounter any issues or have questions, please contact the development team. 