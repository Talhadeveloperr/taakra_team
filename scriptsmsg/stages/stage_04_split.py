#/root/whatspush/airflow-infra/dags/scriptsmsg/stages/stage_04_split.py
import json
import os
import sys

# Dynamic path resolution to avoid Permission Errors
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

CLEAN_DATA_PATH = os.path.join(BASE_DIR, "clean", "clean_messages.json")
CHUNKS_PATH = os.path.join(BASE_DIR, "processed", "chunks.json")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "intermediate", "processed.json")

def write_to_json_file(source_data, target_path, clear_first=False):
    """
    Helper to manage JSON files.
    """
    existing_data = []
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # Only load existing data if we are NOT clearing the file
    if not clear_first and os.path.exists(target_path):
        with open(target_path, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            except json.JSONDecodeError:
                existing_data = []
    
    combined_data = existing_data + source_data
    
    with open(target_path, 'w') as f:
        json.dump(combined_data, f, indent=4)
    
    action = "overwritten" if clear_first else "appended to"
    print(f"Successfully {action} {target_path} with {len(source_data)} records.")

def run_stage_04():
    # --- MANDATORY WIPE OF EMBEDDINGS FILE ---
    # We clear this at the start so it is empty in ALL cases
    os.makedirs(os.path.dirname(EMBEDDINGS_PATH), exist_ok=True)
    with open(EMBEDDINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump([], f)
    print(f"Initialized/Cleared: {EMBEDDINGS_PATH}")

    # 1. Check if the clean data path exists
    if not os.path.exists(CLEAN_DATA_PATH):
        print(f"Notice: {CLEAN_DATA_PATH} not found. Embeddings remains empty.")
        return

    # 2. Load the ID-assigned clean messages
    with open(CLEAN_DATA_PATH, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            
            # --- ROBUST CHECK: If data is empty, we exit here ---
            # The EMBEDDINGS_PATH is already cleared from the step above
            if not data:
                print("Notice: No new records in clean_messages.json. Master append skipped.")
                return 
            
            new_data = data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            print("Error: clean_messages.json is invalid/corrupt.")
            return

    # 3. Append to cloudpos_chunks.json (Master Log)
    # This only runs if new_data is NOT empty
    write_to_json_file(new_data, CHUNKS_PATH, clear_first=False)

    # 4. Update processed.json (Embeddings File)
    # We use clear_first=True, though it was already cleared above, 
    # this writes the fresh data into the empty file.
    write_to_json_file(new_data, EMBEDDINGS_PATH, clear_first=True)

if __name__ == "__main__":
    run_stage_04()