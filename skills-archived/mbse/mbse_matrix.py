import yaml
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


def generate_rtm(data):
    matrix = []
    for req in data.get('requirements', []):
        entry = {
            'REQ ID': req.get('id'),
            'Title': req.get('title'),
            'Status': req.get('status', 'Unknown'),
            'ARCH Components': ', '.join(req.get('architecture', [])),
            'Tests': ', '.join(req.get('tests', [])),
            'Coverage %': "{:.2f}".format(100 * len(req.get('tests', [])) / max(1, len(data['tests'])))
        }
        matrix.append(entry)

    return matrix


def output_matrix(matrix, output_format):
    if output_format == 'csv':
        keys = matrix[0].keys()
        with open('mbse_matrix_output.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(matrix)
    elif output_format == 'table':
        print(tabulate(matrix, headers='keys'))
    else:
        print("Unsupported format. Use --format csv|table.")


def main():
    if len(sys.argv) < 3:
        print("Usage: mbse_matrix <yaml_file> --format <csv|table>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    output_format = sys.argv[3]
    data = read_yaml(yaml_file)
    matrix = generate_rtm(data)
    output_matrix(matrix, output_format)


if __name__ == "__main__":
    main()
