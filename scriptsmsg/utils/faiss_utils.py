#/root/whatspush/airflow-infra/dags/scriptsmsg/utils/faiss_utils.py
import json
import os

def append_to_json_list(data_list, file_path):
    """Loads existing list from file and appends new items."""
    existing_data = []
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            except json.JSONDecodeError:
                existing_data = []
    
    combined_data = existing_data + data_list
    
    with open(file_path, 'w') as f:
        json.dump(combined_data, f, indent=4)