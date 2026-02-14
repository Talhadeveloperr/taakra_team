#/scriptsmsg/stages/stage_03_assign_ids.py
import json
import os
import sys

# Path Hack
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from scriptsmsg.utils.id_generator import IDGenerator

# File Paths
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
CLEAN_DATA_PATH = os.path.join(BASE_DIR, "clean", "clean_messages.json")
REFERENCE_FILE_PATH = os.path.join(BASE_DIR, "processed", "chunks.json")

def run_stage_03():
    gen = IDGenerator(REFERENCE_FILE_PATH)
    last_id = gen.get_last_id()
    
    if not os.path.exists(CLEAN_DATA_PATH):
        print(f"Error: {CLEAN_DATA_PATH} not found.")
        return

    with open(CLEAN_DATA_PATH, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            # --- NEW ROBUST CHECK ---
            if not data:
                print("Notice: clean_messages.json is empty. Nothing to assign IDs to. Skipping.")
                return 
            
            # Support list of lists or single list
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                messages_to_id = data[0]
            else:
                messages_to_id = data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            print("Error: clean_messages.json is invalid.")
            return

    updated_messages = []
    current_id = last_id
    
    for msg in messages_to_id:
        current_id += 1
        
        question = msg.get("user_message") or msg.get("question") or ""
        description = msg.get("model_response") or msg.get("description") or ""
        
        new_entry = {
            "chunk_id": current_id,
            "question": question,
            "description": description,
            "source": ""
        }
        updated_messages.append(new_entry)

    with open(CLEAN_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(updated_messages, f, indent=4, ensure_ascii=False)
    
    print(f"Success: Assigned IDs {last_id + 1} to {current_id}")

if __name__ == "__main__":
    run_stage_03()