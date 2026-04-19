import yaml
import sys
import json
import csv
from tabulate import tabulate

def read_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error reading YAML file: {e}")
        sys.exit(1)


def analyze_coverage(data, output_format):
    coverage_data = []
    coverage_by_priority = {}

    for req in data.get('requirements', []):
        tested = len(req.get('tests', [])) > 0
        entry = {
            'REQ ID': req.get('id'),
            'Title': req.get('title'),
            'Tested': 'Yes' if tested else 'No',
            'Priority': req.get('priority', 'Undefined'),
            'Missing Tests': [] if tested else req.get('tests', [])
        }
        coverage_data.append(entry)

        # Calculate coverage by priority
        priority = entry['Priority']
        if priority not in coverage_by_priority:
            coverage_by_priority[priority] = {'total': 0, 'tested': 0}
        coverage_by_priority[priority]['total'] += 1
        if tested:
            coverage_by_priority[priority]['tested'] += 1

    # Print coverage recommendation by priority
    recommendations = []
    for priority, counts in coverage_by_priority.items():
        coverage_percent = (counts['tested'] / counts['total']) * 100
        recommendations.append(
            {
                'Priority': priority,
                'Coverage %': f'{coverage_percent:.2f}',
                'Recommendations': 'Add tests' if coverage_percent < 100 else 'None'
            }
        )

    if output_format == 'json':
        print(json.dumps({'coverage_data': coverage_data, 'recommendations': recommendations}, indent=2))
    elif output_format == 'csv':
        with open('mbse_coverage_output.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=coverage_data[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(coverage_data)

        with open('mbse_recommendations_output.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=recommendations[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(recommendations)

    elif output_format == 'table':
        print("Coverage Data:")
        print(tabulate(coverage_data, headers='keys'))
        print("\nRecommendations:")
        print(tabulate(recommendations, headers='keys'))
    else:
        print("Unsupported format. Use --format json|csv|table.")


def main():
    if len(sys.argv) < 3:
        print("Usage: mbse_coverage <yaml_file> --format <json|csv|table>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    output_format = sys.argv[3]
    data = read_yaml(yaml_file)
    analyze_coverage(data, output_format)


if __name__ == "__main__":
    main()
