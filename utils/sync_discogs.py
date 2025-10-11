#!/usr/bin/env python3
"""
Sync Discogs Listings to Database

This utility syncs listings from Discogs API to the local database.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.services.discogs_sync_service import DiscogsSyncService
from app.models.listing import Listing

def main():
    app = create_app()
    
    with app.app_context():
        token = app.config.get('DISCOGS_TOKEN')
        username = app.config.get('DISCOGS_SELLER_USERNAME')
        
        if not token:
            print("❌ DISCOGS_TOKEN not found in config")
            print("   Set it in .env file")
            sys.exit(1)
        
        print("="*70)
        print("🔄 Discogs Sync")
        print("="*70)
        print(f"Token: {token[:15]}...{token[-5:]}")
        print(f"Username: {username}")
        print("")
        print("Fetching listings from Discogs API...")
        print("This may take 2-3 minutes for large inventories...")
        print("")
        
        sync_service = DiscogsSyncService(
            token=token,
            seller_username=username,
            user_agent=app.config.get('DISCOGS_USER_AGENT', 'FreakinbeatsWebApp/1.0')
        )
        
        stats = sync_service.sync_all_listings()
        
        # Verify database
        count = Listing.query.count()
        
        print("\n" + "="*70)
        print("✅ Sync Complete!")
        print("="*70)
        print(f"Database listings: {count}")
        print(f"Added: {stats.get('added', 0)}")
        print(f"Updated: {stats.get('updated', 0)}")
        print(f"Removed: {stats.get('removed', 0)}")
        
        if count > 0:
            sample = Listing.query.first()
            print(f"\n📀 Sample: {sample.release_title} by {sample.artist_names}")
            print(f"   Price: ${sample.price_value}")
        
        print("\n🌐 Start server with: python3 run.py")

if __name__ == '__main__':
    main()

