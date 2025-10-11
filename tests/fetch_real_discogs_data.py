"""
Script to fetch real Discogs API data for test validation.

This script queries the Discogs API with real credentials and saves
the response data to a JSON file. This data can then be used to:
1. Validate our mock data factory structure
2. Create realistic test fixtures
3. Ensure our data flattening logic handles all real-world cases
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv


def fetch_real_discogs_data():
    """Fetch real data from Discogs API and save to file."""
    
    # Get credentials from environment
    token = os.getenv('DISCOGS_TOKEN')
    seller_username = os.getenv('DISCOGS_SELLER_USERNAME')
    
    if not token or not seller_username:
        print("ERROR: Missing DISCOGS_TOKEN or DISCOGS_SELLER_USERNAME environment variables")
        print("Please set them in your .env file or environment")
        return
    
    # Setup API request
    base_url = "https://api.discogs.com"
    headers = {
        "User-Agent": "FreakinBeatsTest/1.0",
        "Accept": "application/vnd.discogs.v2.discogs+json",
        "Authorization": f"Discogs token={token}"
    }
    
    url = f"{base_url}/users/{seller_username}/inventory"
    params = {
        "status": "For Sale",
        "per_page": 3,  # Minimal sample - just need a few for validation
        "page": 1,
        "sort": "listed",
        "sort_order": "desc"
    }
    
    print(f"Fetching listings from Discogs for seller: {seller_username}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 401:
            print("ERROR: Authentication failed. Check your DISCOGS_TOKEN")
            return
        elif response.status_code == 404:
            print(f"ERROR: Seller '{seller_username}' not found")
            return
        elif response.status_code == 429:
            print("ERROR: Rate limit exceeded. Wait a moment and try again")
            return
        
        response.raise_for_status()
        data = response.json()
        
        # Save the raw response
        output_dir = Path(__file__).parent / 'fixtures'
        output_file = output_dir / 'real_discogs_data.json'
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✓ Successfully fetched {len(data.get('listings', []))} listings")
        print(f"✓ Saved to: {output_file}")
        
        # Print summary
        print("\n=== Data Structure Summary ===")
        print(f"Pagination keys: {list(data.get('pagination', {}).keys())}")
        print(f"Number of listings: {len(data.get('listings', []))}")
        
        if data.get('listings'):
            first_listing = data['listings'][0]
            print(f"\n=== First Listing Structure ===")
            print(f"Top-level keys: {list(first_listing.keys())}")
            
            if 'release' in first_listing:
                release = first_listing['release']
                print(f"\nRelease keys: {list(release.keys())}")
                
                # Check for artists
                if 'artists' in release:
                    print(f"  - Artists: {len(release['artists'])} artist(s)")
                    if release['artists']:
                        print(f"    First artist keys: {list(release['artists'][0].keys())}")
                
                # Check for labels
                if 'labels' in release:
                    print(f"  - Labels: {len(release['labels'])} label(s)")
                    if release['labels']:
                        print(f"    First label keys: {list(release['labels'][0].keys())}")
                
                # Check for formats
                if 'formats' in release:
                    print(f"  - Formats: {len(release['formats'])} format(s)")
                    if release['formats']:
                        print(f"    First format keys: {list(release['formats'][0].keys())}")
                
                # Check for images
                if 'images' in release:
                    print(f"  - Images: {len(release['images'])} image(s)")
                    if release['images']:
                        print(f"    First image keys: {list(release['images'][0].keys())}")
        
        # Analyze all listings for field coverage
        print("\n=== Field Coverage Analysis ===")
        analyze_field_coverage(data.get('listings', []))
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed: {e}")
        return
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return


def analyze_field_coverage(listings):
    """Analyze which fields are present across all listings."""
    if not listings:
        return
    
    # Track which fields appear in listings
    listing_fields = {}
    release_fields = {}
    
    for listing in listings:
        # Listing-level fields
        for key in listing.keys():
            listing_fields[key] = listing_fields.get(key, 0) + 1
        
        # Release-level fields
        if 'release' in listing:
            for key in listing['release'].keys():
                release_fields[key] = release_fields.get(key, 0) + 1
    
    total = len(listings)
    
    print(f"Analyzed {total} listings")
    print("\nListing-level fields (present in X/{total} listings):")
    for key, count in sorted(listing_fields.items()):
        percentage = (count / total) * 100
        marker = "✓" if count == total else "⚠"
        print(f"  {marker} {key}: {count}/{total} ({percentage:.0f}%)")
    
    print("\nRelease-level fields (present in X/{total} listings):")
    for key, count in sorted(release_fields.items()):
        percentage = (count / total) * 100
        marker = "✓" if count == total else "⚠"
        print(f"  {marker} {key}: {count}/{total} ({percentage:.0f}%)")


def compare_with_mock_factory():
    """Compare real data structure with our mock factory."""
    print("\n=== Comparing with Mock Factory ===")
    
    # Try to load real data
    real_data_file = Path(__file__).parent / 'fixtures' / 'real_discogs_data.json'
    
    if not real_data_file.exists():
        print("No real data file found. Run fetch first.")
        return
    
    with open(real_data_file, 'r') as f:
        real_data = json.load(f)
    
    if not real_data.get('listings'):
        print("No listings in real data")
        return
    
    # Import our factory
    try:
        from tests.fixtures.discogs_factory import DiscogsDataFactory
        factory = DiscogsDataFactory(seed=42)
        mock_listing = factory.create_listing()
        
        real_listing = real_data['listings'][0]
        
        # Compare top-level keys
        real_keys = set(real_listing.keys())
        mock_keys = set(mock_listing.keys())
        
        print("\nTop-level listing keys:")
        print(f"  Real keys: {len(real_keys)}")
        print(f"  Mock keys: {len(mock_keys)}")
        
        missing_in_mock = real_keys - mock_keys
        extra_in_mock = mock_keys - real_keys
        
        if missing_in_mock:
            print(f"  ⚠ Missing in mock: {missing_in_mock}")
        if extra_in_mock:
            print(f"  ℹ Extra in mock: {extra_in_mock}")
        if not missing_in_mock and not extra_in_mock:
            print("  ✓ Perfect match!")
        
        # Compare release keys
        if 'release' in real_listing and 'release' in mock_listing:
            real_release_keys = set(real_listing['release'].keys())
            mock_release_keys = set(mock_listing['release'].keys())
            
            print("\nRelease keys:")
            print(f"  Real keys: {len(real_release_keys)}")
            print(f"  Mock keys: {len(mock_release_keys)}")
            
            missing_in_mock_release = real_release_keys - mock_release_keys
            extra_in_mock_release = mock_release_keys - real_release_keys
            
            if missing_in_mock_release:
                print(f"  ⚠ Missing in mock release: {missing_in_mock_release}")
            if extra_in_mock_release:
                print(f"  ℹ Extra in mock release: {extra_in_mock_release}")
            if not missing_in_mock_release and not extra_in_mock_release:
                print("  ✓ Perfect match!")
        
    except ImportError as e:
        print(f"Could not import mock factory: {e}")


if __name__ == '__main__':
    print("=" * 70)
    print("Discogs API Real Data Fetcher")
    print("=" * 70)
    
    # Load environment variables from .env file
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        print(f"Loading environment from: {env_file}")
        load_dotenv(env_file)
    else:
        print("No .env file found, using system environment variables")
    
    fetch_real_discogs_data()
    compare_with_mock_factory()
    
    print("\n" + "=" * 70)
    print("Done! Check tests/fixtures/real_discogs_data.json for the raw data")
    print("=" * 70)
