# scraping/db_to_raw.py
import csv
from scraping.connection import DatabaseConnection

RAW_CSV_PATH = "raw.csv"

QUERY = """
SELECT
    c.category_id,
    c.name AS category_name,
    c.description AS category_description,
    c.created_at AS category_created_at,

    cp.competition_id,
    cp.title AS competition_title,
    cp.tagline AS competition_tagline,
    cp.description AS competition_description,
    cp.rules AS competition_rules,
    cp.prizes AS competition_prizes,
    cp.min_team_size,
    cp.max_team_size,
    cp.start_date,
    cp.end_date,
    cp.registration_deadline,
    cp.status AS competition_status,
    cp.created_at AS competition_created_at
FROM categories c
LEFT JOIN competitions cp ON c.category_id = cp.category_id
"""

def fetch_and_save_raw():
    conn = DatabaseConnection("taakra_db").get_connection()
    cursor = conn.cursor()
    cursor.execute(QUERY)

    with open(RAW_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["DATA"])
        writer.writeheader()

        for row in cursor.fetchall():
            merged_text = " | ".join([str(col) for col in row if col is not None])
            writer.writerow({"DATA": merged_text})

    cursor.close()
    conn.close()
