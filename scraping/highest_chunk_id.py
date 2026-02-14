#scraping/highest_chunk_id.py
import json
import os

PROCESSED_PATH = r"D:\projects\taakra hackathon\chatbot\flask_server\scriptsmsg\processed\chunks.json"

def get_highest_chunk_id():
    if not os.path.exists(PROCESSED_PATH):
        return 0

    with open(PROCESSED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        if not data:
            return 0
        return max(item.get("chunk_id", 0) for item in data)
