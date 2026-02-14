# scraping/scrapy.py
import csv
import json
import os

from scraping.model import GroqModel
from scraping.highest_chunk_id import get_highest_chunk_id

BASE_DIR = r"D:\projects\taakra hackathon\chatbot\flask_server"

CSV_INPUT_PATH = os.path.join(BASE_DIR, "raw.csv")
CHUNKS_PATH = os.path.join(BASE_DIR, "scraping", "chunks.json")
PROCESSED_PATH = os.path.join(BASE_DIR, "scriptsmsg", "processed", "chunks.json")
LOG_PATH = os.path.join(BASE_DIR, "scraping", "log.json")


def run_scraper():
    if not os.path.exists(CSV_INPUT_PATH):
        raise FileNotFoundError(f"raw.csv not found at {CSV_INPUT_PATH}")

    model = GroqModel()

    start_id = get_highest_chunk_id() + 1
    current_id = start_id

    chunks = []

    with open(CSV_INPUT_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row_index, row in enumerate(reader, start=1):
            text = row.get("DATA", "").strip()
            if not text:
                continue

            # 🔁 Generate 3 Q/A pairs per DATA row
            for i in range(3):
                q_prompt = (
                    f"Based on this data:\n{text}\n\n"
                    f"Generate a concise, unique question. "
                    f"Return strictly in this format: ` {{question}} `"
                )

                question = model.extract_content(
                    model.get_response(q_prompt)
                )

                a_prompt = (
                    f"Based on this data:\n{text}\n\n"
                    f"Provide a detailed answer to this question:\n"
                    f"'{question}'\n\n"
                    f"Return strictly in this format: ` {{answer}} `"
                )

                answer = model.extract_content(
                    model.get_response(a_prompt)
                )

                chunks.append({
                    "chunk_id": current_id,
                    "question": question,
                    "description": answer,
                    "source": "database",
                    "row_index": row_index,
                    "variation": i + 1
                })

                current_id += 1

    # Save fresh chunks.json
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4, ensure_ascii=False)

    # Append to processed chunks
    if os.path.exists(PROCESSED_PATH):
        with open(PROCESSED_PATH, "r", encoding="utf-8") as f:
            processed = json.load(f)
    else:
        processed = []

    processed.extend(chunks)

    with open(PROCESSED_PATH, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=4, ensure_ascii=False)

    # Log
    log = {
        "start_chunk_id": start_id,
        "end_chunk_id": current_id - 1,
        "total_chunks_added": len(chunks),
        "rows_processed": len(set(c["row_index"] for c in chunks))
    }

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=4)
