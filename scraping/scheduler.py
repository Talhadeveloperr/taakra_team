# scraping/scheduler.py

from scraping.db_to_raw import fetch_and_save_raw
from scraping.scrapy import run_scraper


def run_sync_pipeline():
    """
    One-click sync:
    DB → raw.csv → 3x Q/A per row → chunks
    """
    fetch_and_save_raw()
    run_scraper()
