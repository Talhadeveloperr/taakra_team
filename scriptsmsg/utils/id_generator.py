#/root/whatspush/airflow-infra/dags/scriptsmsg/utils/id_generator.py
import json
import os

class IDGenerator:
    def __init__(self, processed_file_path):
        self.processed_file_path = processed_file_path

    def get_last_id(self):
        """Finds the maximum chunk_id in the existing processed file."""
        if not os.path.exists(self.processed_file_path):
            return 0
        
        try:
            with open(self.processed_file_path, 'r') as f:
                data = json.load(f)
                
            if not data:
                return 0
            
            # If it's a list, find the max chunk_id
            if isinstance(data, list):
                ids = [item.get('chunk_id', 0) for item in data]
                return max(ids) if ids else 0
            # If it's a single dict
            return data.get('chunk_id', 0)
        
        except (json.JSONDecodeError, ValueError, IOError):
            return 0