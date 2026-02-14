#scriptsmsg/stages/stage_02_clean.py
import json
import os
import sys
import re
from datetime import datetime

# Dynamic path resolution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

RAW_DATA_PATH = os.path.join(BASE_DIR, "raw", "messages.json")
CLEAN_DATA_PATH = os.path.join(BASE_DIR, "clean", "clean_messages.json")
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "pipeline_log.json")

def get_last_extraction_limit():
    """Extracts the 'up to' timestamp from the last log entry."""
    if not os.path.exists(LOG_FILE_PATH):
        return None

    try:
        with open(LOG_FILE_PATH, 'r') as f:
            logs = json.load(f)
            if not logs or not isinstance(logs, list):
                return None
            
            last_log = logs[-1]
            log_msg = last_log.get("message", "")

            # Look for the timestamp in the message: "Processed records up to ..."
            timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?', log_msg)
            
            if timestamp_match:
                return timestamp_match.group(0)
    except Exception as e:
        print(f"Error reading log: {e}")
    
    return None

def run_stage_02():
    # 1. Initialize/Clear Clean File
    os.makedirs(os.path.dirname(CLEAN_DATA_PATH), exist_ok=True)
    with open(CLEAN_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump([], f)
    
    # 2. Get the limit from Stage 01
    end_limit = get_last_extraction_limit()
    
    if not end_limit:
        print("Notice: No valid 'up to' timestamp found in logs. Skipping.")
        return

    print(f"Filtering records up to: {end_limit}")

    # 3. Load Raw Data
    if not os.path.exists(RAW_DATA_PATH):
        print(f"Raw data file {RAW_DATA_PATH} not found.")
        return

    try:
        with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
            all_messages = json.load(f)
            if not all_messages:
                return
    except (json.JSONDecodeError, IOError):
        return

    # 4. Corrected Filter Logic
    # We take the last N records based on the timestamp limit provided by Stage 01
    # Since Stage 01 just logged the count it processed, we should match that.
    target_messages = [
        m for m in all_messages 
        if m.get('timestamp', '') <= end_limit
    ]

    # Optimization: If Stage 1 said it processed 81, let's ensure we are getting the latest ones
    # Sort by timestamp and take the top ones if necessary, but <= end_limit is usually enough.
    target_messages.sort(key=lambda x: x.get('timestamp', ''))
    
    # If you only want the specific batch from the last run:
    # We take the last records matching the count from the log
    try:
        with open(LOG_FILE_PATH, 'r') as f:
            last_count = json.load(f)[-1].get("records_count", len(target_messages))
            target_messages = target_messages[-last_count:]
    except:
        pass

    # 5. Format and Save
    cleaned_data = []
    for msg in target_messages:
        cleaned_data.append({
            "user_message": msg.get("user_message", ""),
            "model_response": msg.get("model_response", ""),
            "timestamp": msg.get("timestamp", "") # Keep timestamp for ID generation consistency
        })

    with open(CLEAN_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

    print(f"Stage 02 Complete: {len(cleaned_data)} records processed (Matched with Stage 01 count).")

if __name__ == "__main__":
    run_stage_02()