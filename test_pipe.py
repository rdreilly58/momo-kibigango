import sys
import json

def process_input(input_data):
    try:
        # Simulate JSON parsing step
        data = json.loads(input_data)
        if 'key' in data:
            return f"Success: Processed data key: {data['key']}"
        return "Failure: 'key' not found in data."
    except json.JSONDecodeError:
        return "Failure: Invalid JSON input."
    except Exception as e:
        return f"Failure: An unexpected error occurred: {e}"

if __name__ == "__main__":
    # We expect the input data to be passed as the first argument (sys.argv[1])
    if len(sys.argv) > 1:
        input_string = sys.argv[1]
        print(process_input(input_string))
    else:
        print("Error: No input provided.")