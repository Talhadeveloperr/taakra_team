#/root/whatspush/airflow-infra/dags/scriptsmsg/utils/file_tracker.py
import json
import os

class FileTracker:
    def __init__(self, tracker_path):
        self.tracker_path = tracker_path

    def get_last_state(self):
        """Returns the last processed timestamp from the tracker file."""
        if not os.path.exists(self.tracker_path):
            return None
        try:
            with open(self.tracker_path, 'r') as f:
                data = json.load(f)
                return data.get("last_processed_timestamp")
        except (json.JSONDecodeError, IOError):
            return None

    def update_state(self, last_timestamp):
        """Updates the tracker file with the newest timestamp processed."""
        os.makedirs(os.path.dirname(self.tracker_path), exist_ok=True)
        with open(self.tracker_path, 'w') as f:
            json.dump({"last_processed_timestamp": last_timestamp}, f, indent=4)