#/root/whatspush/airflow-infra/dags/scriptsmsg/stages/stage_05_embed.py
import json
import os
import sys

# Path Hack
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from utils.faiss_utils import append_to_json_list

# File Paths
PROCESSED_PATH = os.path.join(BASE_DIR, "intermediate", "processed.json")
TEXTS_OUT_PATH = os.path.join(BASE_DIR, "intermediate", "embeddings.json")
META_OUT_PATH = os.path.join(BASE_DIR, "embeddings", "faiss_metadata.json")

def run_stage_05():
    # 1. Load and Validate the current batch
    if not os.path.exists(PROCESSED_PATH):
        print(f"Notice: {PROCESSED_PATH} not found. Skipping Stage 05.")
        return

    try:
        with open(PROCESSED_PATH, 'r') as f:
            data = json.load(f)
            
            # --- ROBUST CHECK: Handle empty list or None ---
            if not data or (isinstance(data, list) and len(data) == 0):
                print("Notice: No records found in processed.json. Nothing to embed. Skipping.")
                return 
            
            # Ensure data is a list for the loop
            items_to_process = data if isinstance(data, list) else [data]
            
    except json.JSONDecodeError:
        print("Error: processed.json is empty or contains invalid JSON.")
        return
    except Exception as e:
        print(f"An unexpected error occurred reading processed.json: {e}")
        return

    # 2. Transform Data
    texts = []
    metadata = []

    for item in items_to_process:
        # Check if required keys exist to prevent KeyErrors
        question = item.get('question', 'N/A')
        description = item.get('description', 'N/A')
        chunk_id = item.get('chunk_id', 'Unknown')
        source = item.get('source', '')

        # Format the text for the embedding model
        text_content = f"Q: {question}\nA: {description}"
        texts.append(text_content)

        # Prepare metadata for FAISS mapping
        metadata.append({
            "chunk_id": chunk_id,
            "question": question,
            "source": source
        })

    # 3. Append to target files
    if texts and metadata:
        # texts go to intermediate/embeddings.json
        append_to_json_list(texts, TEXTS_OUT_PATH)
        
        # metadata goes to embeddings/faiss_metadata.json
        append_to_json_list(metadata, META_OUT_PATH)

        print(f"Stage 05 Success: Processed {len(texts)} items for embedding.")
    else:
        print("Notice: No valid text/metadata generated. Skipping file update.")

if __name__ == "__main__":
    run_stage_05()