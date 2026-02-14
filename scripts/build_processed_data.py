import json
from pathlib import Path
from utils.text_cleaner import clean_text

RAW_PATH = Path("data/raw/cloudpos_raw.json")
PROCESSED_PATH = Path("data/processed/cloudpos_chunks.json")

def main():
    print(f" Reading from: {RAW_PATH}")
    
    if not RAW_PATH.exists():
        print(f" Error: {RAW_PATH} not found.")
        return

    with open(RAW_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    processed_data = []
    
    for i, row in enumerate(raw_data):
        
        raw_title = row.get("title", "")
        raw_desc = row.get("description", "")
        raw_link = row.get("link", "")

        
        clean_title = clean_text(raw_title)
        clean_desc = clean_text(raw_desc)

       
        final_link = raw_link if raw_link and raw_link.lower() != "none" else ""

        
        processed_data.append({
            "chunk_id": i,
            "question": clean_title,
            "description": clean_desc,
            "source": final_link  
        })

   
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(PROCESSED_PATH, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)

    print(f" Success! Created {len(processed_data)} items with separate questions and links.")

if __name__ == "__main__":
    main()