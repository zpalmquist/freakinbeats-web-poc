import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Legacy CSV settings (for migration script)
    BASE_DIR = Path(__file__).parent / "ingest"
    CSV_FILE_PATTERN = "discogs_seller_listings*.csv"
    PORT = 3000
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f'sqlite:///{Path(__file__).parent / "freakinbeats.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Discogs API settings
    DISCOGS_TOKEN = os.getenv('DISCOGS_TOKEN')
    DISCOGS_SELLER_USERNAME = os.getenv('DISCOGS_SELLER_USERNAME', 'freakin_beats')
    DISCOGS_USER_AGENT = "FreakinbeatsWebApp/1.0"
    
    # Google Gemini API settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    ENABLE_AI_OVERVIEWS = os.getenv('ENABLE_AI_OVERVIEWS', 'true').lower() == 'true'
    
    # Scheduler settings
    SCHEDULER_API_ENABLED = False  # Disable APScheduler API
    SYNC_INTERVAL_HOURS = 1  # Sync every hour
    ENABLE_AUTO_SYNC = os.getenv('ENABLE_AUTO_SYNC', 'true').lower() == 'true'

