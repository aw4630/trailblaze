# Manual Itinerary Testing

This README provides instructions on how to use the manual itinerary testing scripts to experiment with different JSON inputs for the itinerary generator.

## Files

- `manual_itinerary_test.py`: Script for testing with hardcoded JSON itinerary request data
- `validate_modified_itinerary.py`: Script for validating and fixing existing itineraries
- `custom_itinerary_request.json`: A reference JSON request file (not used by the script)

## 1. Generating Itineraries from Scratch

### Basic Usage

Run the script with an output file parameter:

```bash
python manual_itinerary_test.py --output custom_result.json
```

### Additional Options

- `--max-attempts <number>`: Set the maximum number of attempts for generating a valid itinerary (default: 3)
- `--use-real-api`: Use real API calls instead of mock data
- `--skip-modify`: Skip the modification step in the script

Example with all options:

```bash
python manual_itinerary_test.py --output custom_result.json --max-attempts 5 --use-real-api --skip-modify
```

### Modifying the Request

You can modify the hardcoded request in two ways:

1. **Edit the ExampleJSON directly in the script**: Open `manual_itinerary_test.py` and modify the `ExampleJSON` dictionary at the top of the file.

2. **Programmatic modifications**: Edit the `modify_request()` function in `manual_itinerary_test.py` to make programmatic changes to the request data.

#### Example Modifications

In the `modify_request()` function, you can uncomment and customize the example modifications:

```python
# Change route name
request_data["route_name"] = "Modified Historical Manhattan Tour"

# Change distance
request_data["distance"] = 5

# Change budget
request_data["budget"] = 200

# Add or modify specific requirements
if "requirements" in request_data:
    request_data["requirements"].append("Include at least one museum")
```

## 2. Validating and Fixing Existing Itineraries

If you already have an itinerary result file (like `historical_manhattan_result.json`) and want to modify it directly and re-validate it without regenerating from scratch, use the validation script.

### Basic Usage

```bash
python validate_modified_itinerary.py --input historical_manhattan_result.json --output modified_result.json
```

### Additional Options

- `--use-real-api`: Use real API calls instead of mock data
- `--skip-modify`: Skip the modification step in the script
- `--fix-issues`: Attempt to automatically fix any issues found during validation

Example with all options:

```bash
python validate_modified_itinerary.py --input historical_manhattan_result.json --output modified_result.json --use-real-api --fix-issues
```

### Modifying the Itinerary

You can modify the itinerary by editing the `modify_itinerary()` function in `validate_modified_itinerary.py`. Example modifications include:

```python
# Change itinerary name
itinerary["name"] = "Modified Historical Manhattan Tour"

# Adjust event times
if "events" in itinerary and len(itinerary["events"]) > 0:
    # Adjust the first event to end 30 minutes earlier
    event = itinerary["events"][0]
    end_time = event["end_time"]
    # Parse the time, subtract 30 minutes, and format back
    from datetime import datetime, timedelta
    dt = datetime.fromisoformat(end_time)
    new_dt = dt - timedelta(minutes=30)
    event["end_time"] = new_dt.isoformat()

# Add a new venue
if "venues" in itinerary:
    itinerary["venues"].append({
        "name": "New Museum",
        "address": "123 Example St, New York, NY 10001",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "opening_hours": "09:00-17:00"
    })
```

## Understanding the Output

After running either script, it will:

1. Print the modified request/itinerary (if modifications were made)
2. Generate or validate the itinerary
3. Save the results to the specified output file
4. Print a summary of the process, including whether the itinerary is valid and any issues found

You can then examine the output JSON file for the complete results. 