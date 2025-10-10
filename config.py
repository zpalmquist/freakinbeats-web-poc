import os
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).parent / "ingest"
    CSV_FILE_PATTERN = "discogs_seller_listings*.csv"
    PORT = 3000

