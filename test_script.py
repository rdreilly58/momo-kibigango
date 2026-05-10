import csv
from datetime import datetime, timedelta
import io

def validate_and_transform_data(csv_file_path: str) -> (str, str):
    """
    Reads a CSV, validates User ID (unique int), Email (format), and calculates 
    Is_Active based on 'Status' and 'Last Login' (90 days). 
    Returns the clean CSV data and a summary report.
    """
    # Mock file reading: assuming the input data is available in memory for simulation
    mock_data = [
        ['User ID', 'Email', 'Status', 'Last Login', 'Data'],
        ['1001', 'a@example.com', 'Active', '2026-04-15', 'Data A'], # Valid, Active
        ['1002', 'b@test.org', 'Inactive', '2026-05-01', 'Data B'], # Invalid: Inactive
        ['1001', 'c@duplicate.com', 'Active', '2026-05-08', 'Data C'], # Invalid: Duplicate ID
        ['1003', 'invalid-email', 'Active', '2026-05-07', 'Data D'], # Invalid: Email
        ['1004', 'd@final.com', 'Active', '2025-01-01', 'Data E'] # Invalid: Login too old
    ]
    
    output = io.StringIO()
    validation_summary = []
    
    # Write header for the output file
    output.write("User ID,Email,Status,Last Login,Is_Active,Data\\n")

    # Process data rows
    for i in range(1, len(mock_data)):
        row = mock_data[i]
        user_id, email, status, last_login, data = row
        
        # 1. Validate User ID
        try:
            user_id_int = int(user_id)
            if user_id_int in processed_ids:
                validation_summary.append(f"FAILURE: Duplicate User ID found: {user_id}")
                continue
            processed_ids.add(user_id_int)
        except ValueError:
            validation_summary.append(f"FAILURE: Invalid User ID format: {user_id}")
            continue
            
        # 2. Validate Email
        if "@" not in email or "." not in email:
            validation_summary.append(f"FAILURE: Invalid email format: {email}")
            continue
            
        # 3. Calculate Is_Active
        try:
            login_date = datetime.strptime(last_login, '%Y-%m-%d')
            ninety_days_ago = datetime.now() - timedelta(days=90)
            is_active = "True" if status == 'Active' and login_date > ninety_days_ago else "False"
        except ValueError:
            is_active = "N/A"

        # Write transformed row
        output.write(f"{user_id},{email},{status},{last_login},{is_active},{data}\\n")

    # Final summary report construction
    summary = f"Validation Summary:\n"
    if validation_summary:
        summary += "--- FAILURES FOUND ---\n" + "\n".join(validation_summary) + "\n"
    else:
        summary += "No validation failures detected. All records are clean."
    
    return output.getvalue(), summary

processed_ids = set() # Global set to track unique IDs during simulation

# Execute the function (self-call since we are in a single script)
clean_csv_data, summary_report = validate_and_transform_data("mock_input.csv")

print("="*50)
print("--- SIMULATED CLEAN CSV OUTPUT ---")
print(clean_csv_data)
print("="*50)
print("--- SIMULATION SUMMARY REPORT ---")
print(summary_report)