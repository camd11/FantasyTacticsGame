import yaml
import json
import os

def convert_yaml_to_json(file_path):
    """Convert a YAML file to JSON format."""
    try:
        # Read YAML file
        with open(file_path, 'r') as yaml_file:
            yaml_content = yaml.safe_load(yaml_file)
        
        # Write JSON file
        with open(file_path, 'w') as json_file:
            json.dump(yaml_content, json_file, indent=2)
        
        print(f"Successfully converted {file_path} to JSON format")
    except Exception as e:
        print(f"Error converting {file_path}: {str(e)}")

# Convert all three files
files_to_convert = [
    "data/chapters/test_chapter/map.json",
    "data/chapters/test_chapter/placements.json",
    "data/chapters/test_chapter/events.json"
]

for file_path in files_to_convert:
    convert_yaml_to_json(file_path)