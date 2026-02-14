#/root/whatspush/airflow-infra/dags/scriptsmsg/stages/stage_06_faiss.py
import os
import sys
import json
import faiss
from datetime import datetime

# Path Hack
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from models.embedder import MessageEmbedder

# File Paths
EMBEDDINGS_JSON = os.path.join(BASE_DIR, "intermediate", "embeddings.json")
FAISS_DIR = os.path.join(BASE_DIR, "embeddings")
FAISS_FILE = os.path.join(FAISS_DIR, "faiss_index.bin")

def archive_existing_index(file_path):
    """Renames existing index to include a timestamp."""
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        # Create name like: faiss_index_20260205_1625.bin
        name_parts = os.path.splitext(base_name)
        new_name = f"{name_parts[0]}_{timestamp}{name_parts[1]}"
        new_path = os.path.join(dir_name, new_name)
        
        os.rename(file_path, new_path)
        print(f"Archived old index to: {new_name}")

def run_stage_06():
    # 1. Load the text data
    if not os.path.exists(EMBEDDINGS_JSON):
        print("Error: embeddings.json not found.")
        return

    with open(EMBEDDINGS_JSON, 'r') as f:
        try:
            texts = json.load(f)
            if not texts:
                print("Notice: No text data found for indexing. Skipping.")
                return
        except json.JSONDecodeError:
            print("Error: Failed to decode embeddings.json")
            return

    # 2. Generate Embeddings
    embedder = MessageEmbedder()
    vectors = embedder.generate_embeddings(texts)

    if vectors is None:
        return

    # 3. Create FAISS Index
    dimension = vectors.shape[1]
    # IndexFlatIP = Inner Product, used for normalized Cosine Similarity
    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)
    print(f"Created FAISS index with {index.ntotal} vectors.")

    # 4. Save and Archive
    os.makedirs(FAISS_DIR, exist_ok=True)
    archive_existing_index(FAISS_FILE)
    
    faiss.write_index(index, FAISS_FILE)
    print(f"Success: New index saved at {FAISS_FILE}")

if __name__ == "__main__":
    run_stage_06()