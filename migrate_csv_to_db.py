#!/usr/bin/env python3
"""
CSV to Database Migration Script

This script migrates existing CSV data from the ingest directory
to the SQLite database used by the application.

Usage:
    python3 migrate_csv_to_db.py
    python3 migrate_csv_to_db.py --csv-file path/to/custom.csv
"""

import csv
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.extensions import db
from app.models.listing import Listing


def find_csv_file(base_dir: Path, pattern: str) -> Path:
    """
    Find the most recent CSV file matching the pattern.
    
    Args:
        base_dir: Directory to search in
        pattern: File pattern to match
        
    Returns:
        Path to the most recent CSV file
    """
    csv_files = list(base_dir.glob(pattern))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found matching '{pattern}' in {base_dir}")
    
    # Return the most recently modified file
    return max(csv_files, key=lambda p: p.stat().st_mtime)


def convert_to_float(value):
    """Convert a value to float, returning None if invalid."""
    if not value or value.strip() == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def convert_to_int(value):
    """Convert a value to int, returning None if invalid."""
    if not value or value.strip() == '':
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def clean_string(value):
    """Clean a string value, returning None for empty strings."""
    if not value or value.strip() == '':
        return None
    return value.strip()


def import_csv_to_database(csv_file: Path, app) -> dict:
    """
    Import CSV data into the database.
    
    Args:
        csv_file: Path to CSV file
        app: Flask application instance
        
    Returns:
        Dictionary with import statistics
    """
    stats = {
        'total_rows': 0,
        'imported': 0,
        'updated': 0,
        'errors': 0,
        'skipped': 0
    }
    
    with app.app_context():
        print(f"📂 Reading CSV file: {csv_file}")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            stats['total_rows'] = len(rows)
            
            print(f"📊 Found {stats['total_rows']} rows in CSV")
            print("🔄 Processing rows...")
            
            for i, row in enumerate(rows, 1):
                try:
                    # Get or create listing by listing_id
                    listing_id = clean_string(row.get('listing_id'))
                    
                    if not listing_id:
                        print(f"⚠️  Row {i}: Skipping row with no listing_id")
                        stats['skipped'] += 1
                        continue
                    
                    listing = Listing.query.filter_by(listing_id=listing_id).first()
                    
                    if listing:
                        # Update existing listing
                        is_new = False
                        stats['updated'] += 1
                    else:
                        # Create new listing
                        listing = Listing(listing_id=listing_id)
                        is_new = True
                        stats['imported'] += 1
                    
                    # Map CSV fields to model attributes
                    listing.status = clean_string(row.get('status'))
                    listing.condition = clean_string(row.get('condition'))
                    listing.sleeve_condition = clean_string(row.get('sleeve_condition'))
                    listing.posted = clean_string(row.get('posted'))
                    listing.uri = clean_string(row.get('uri'))
                    listing.resource_url = clean_string(row.get('resource_url'))
                    
                    # Price information
                    listing.price_value = convert_to_float(row.get('price_value'))
                    listing.price_currency = clean_string(row.get('price_currency'))
                    
                    # Shipping information
                    listing.shipping_price = convert_to_float(row.get('shipping_price'))
                    listing.shipping_currency = clean_string(row.get('shipping_currency'))
                    
                    # Additional details
                    listing.weight = convert_to_float(row.get('weight'))
                    listing.format_quantity = convert_to_int(row.get('format_quantity'))
                    listing.external_id = clean_string(row.get('external_id'))
                    listing.location = clean_string(row.get('location'))
                    listing.comments = clean_string(row.get('comments'))
                    
                    # Release information
                    listing.release_id = clean_string(row.get('release_id'))
                    listing.release_title = clean_string(row.get('release_title'))
                    listing.release_year = clean_string(row.get('release_year'))
                    listing.release_resource_url = clean_string(row.get('release_resource_url'))
                    listing.release_uri = clean_string(row.get('release_uri'))
                    
                    # Artist information
                    listing.artist_names = clean_string(row.get('artist_names'))
                    listing.primary_artist = clean_string(row.get('primary_artist'))
                    
                    # Label information
                    listing.label_names = clean_string(row.get('label_names'))
                    listing.primary_label = clean_string(row.get('primary_label'))
                    
                    # Format information
                    listing.format_names = clean_string(row.get('format_names'))
                    listing.primary_format = clean_string(row.get('primary_format'))
                    
                    # Genre and style
                    listing.genres = clean_string(row.get('genres'))
                    listing.styles = clean_string(row.get('styles'))
                    
                    # Country
                    listing.country = clean_string(row.get('country'))
                    
                    # Additional release details
                    listing.catalog_number = clean_string(row.get('catalog_number'))
                    listing.barcode = clean_string(row.get('barcode'))
                    listing.master_id = clean_string(row.get('master_id'))
                    listing.master_url = clean_string(row.get('master_url'))
                    
                    # Images
                    listing.image_uri = clean_string(row.get('image_uri'))
                    listing.image_resource_url = clean_string(row.get('image_resource_url'))
                    
                    # Statistics
                    listing.release_community_have = convert_to_int(row.get('release_community_have'))
                    listing.release_community_want = convert_to_int(row.get('release_community_want'))
                    
                    # Timestamps
                    listing.export_timestamp = clean_string(row.get('export_timestamp'))
                    
                    if is_new:
                        db.session.add(listing)
                    
                    # Commit every 100 rows
                    if i % 100 == 0:
                        db.session.commit()
                        print(f"  ✓ Processed {i}/{stats['total_rows']} rows...")
                
                except Exception as e:
                    print(f"❌ Error processing row {i}: {e}")
                    stats['errors'] += 1
                    db.session.rollback()
                    continue
            
            # Final commit
            try:
                db.session.commit()
                print(f"  ✓ Processed {stats['total_rows']}/{stats['total_rows']} rows")
            except Exception as e:
                print(f"❌ Error committing final changes: {e}")
                db.session.rollback()
    
    return stats


def main():
    """Main function to run the migration."""
    parser = argparse.ArgumentParser(
        description="Migrate CSV data to SQLite database",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--csv-file",
        help="Path to CSV file (defaults to most recent file in ingest/)"
    )
    
    parser.add_argument(
        "--clear-db",
        action="store_true",
        help="Clear existing database before import"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎵 Freakinbeats CSV to Database Migration")
    print("=" * 60)
    
    # Create Flask app
    app = create_app()
    
    # Determine CSV file to use
    if args.csv_file:
        csv_file = Path(args.csv_file)
        if not csv_file.exists():
            print(f"❌ Error: CSV file not found: {csv_file}")
            sys.exit(1)
    else:
        try:
            base_dir = app.config['BASE_DIR']
            pattern = app.config['CSV_FILE_PATTERN']
            csv_file = find_csv_file(base_dir, pattern)
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    # Clear database if requested
    if args.clear_db:
        print("⚠️  Clearing existing database...")
        with app.app_context():
            Listing.query.delete()
            db.session.commit()
        print("✓ Database cleared")
    
    # Import CSV data
    start_time = datetime.now()
    stats = import_csv_to_database(csv_file, app)
    duration = (datetime.now() - start_time).total_seconds()
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 Migration Results")
    print("=" * 60)
    print(f"Total rows in CSV:     {stats['total_rows']}")
    print(f"New listings imported: {stats['imported']}")
    print(f"Existing updated:      {stats['updated']}")
    print(f"Skipped:               {stats['skipped']}")
    print(f"Errors:                {stats['errors']}")
    print(f"Duration:              {duration:.2f} seconds")
    print("=" * 60)
    
    if stats['errors'] > 0:
        print("⚠️  Migration completed with errors")
        sys.exit(1)
    else:
        print("✅ Migration completed successfully!")
        
        # Show database stats
        with app.app_context():
            total = Listing.query.count()
            print(f"\n📦 Total listings in database: {total}")


if __name__ == "__main__":
    main()

