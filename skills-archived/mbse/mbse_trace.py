import yaml
import json
import csv
import sys
from tabulate import tabulate

def read_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error reading YAML file: {e}")
        sys.exit(1)


def trace_requirements(data, output_format):
    results = []
    for req in data.get('requirements', []):
        traces = {
            'REQ ID': req.get('id'),
            'Title': req.get('title'),
            'Traces to': [],
            'Gaps': []
        }
        arch_traces = set(req.get('architecture', []))
        test_traces = set(req.get('tests', []))

        # Identify what each requirement traces to
        traces['Traces to'] = list(arch_traces.union(test_traces))

        # Record untraced items
        traces['Gaps'] = list(set(data['architecture']) - arch_traces) + \
                         list(set(data['tests']) - test_traces)

        results.append(traces)

    # Output results
    if output_format == 'json':
        print(json.dumps(results, indent=2))
    elif output_format == 'csv':
        keys = results[0].keys()
        with open('mbse_trace_output.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
    elif output_format == 'table':
        print(tabulate(results, headers='keys'))
    else:
        print("Unsupported format. Use --format json|csv|table.")


def main():
    if len(sys.argv) < 3:
        print("Usage: mbse_trace <yaml_file> --format <json|csv|table>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    output_format = sys.argv[3]
    data = read_yaml(yaml_file)
    trace_requirements(data, output_format)


if __name__ == "__main__":
    main()
