#/scriptsmsg/stages/stage_01_log.py
import json
import os
from datetime import datetime
from utils.file_tracker import FileTracker

# Determine path relative to this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level to reach 'scriptsmsg'
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

RAW_DATA_PATH = os.path.join(BASE_DIR, "raw", "messages.json")
TRACKER_PATH = os.path.join(BASE_DIR, "utils", "tracker_state.json")
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "pipeline_log.json")

def log_pipeline_run(status, message, records_processed):
    """Appends a run summary to the central log file."""
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    log_entry = {
        "run_time": datetime.now().isoformat(),
        "status": status,
        "message": message,
        "records_count": records_processed
    }
    
    logs = []
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError: logs = []

    logs.append(log_entry)
    with open(LOG_FILE_PATH, 'w') as f:
        json.dump(logs, f, indent=4)

def run_stage_01():
    tracker = FileTracker(TRACKER_PATH)
    last_processed_ts = tracker.get_last_state()
    
    if not os.path.exists(RAW_DATA_PATH):
        print(f"File not found: {RAW_DATA_PATH}")
        log_pipeline_run("Error", "messages.json not found", 0)
        return

    with open(RAW_DATA_PATH, 'r') as f:
        try:
            data = json.load(f)
            all_messages = data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            log_pipeline_run("Error", "Invalid JSON format in messages.json", 0)
            return

    new_messages = []
    if last_processed_ts:
        last_ts_dt = datetime.fromisoformat(last_processed_ts)
        new_messages = [
            m for m in all_messages 
            if datetime.fromisoformat(m['timestamp']) > last_ts_dt
        ]
    else:
        new_messages = all_messages

    if not new_messages:
        log_pipeline_run("Success", "No new data to process", 0)
        print("Pipeline up to date.")
        return

    new_messages.sort(key=lambda x: x['timestamp'])
    print(f"Processing {len(new_messages)} new messages...")

    # Finalize Tracker
    latest_ts = new_messages[-1]['timestamp']
    tracker.update_state(latest_ts)
    
    msg = f"Processed records up to {latest_ts}"
    log_pipeline_run("Success", msg, len(new_messages))
    print(f"Run complete: {msg}")