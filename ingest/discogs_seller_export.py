#!/usr/bin/env python3
"""
Discogs Seller Profile Export Tool

This script fetches all items for sale from a Discogs seller profile
and exports them to a CSV file with all available data fields.

Usage:
    python3 discogs_seller_export.py --seller freakin_beats --token YOUR_TOKEN
    python3 discogs_seller_export.py --seller freakin_beats --token YOUR_TOKEN --output my_listings.csv
"""

import requests
import json
import csv
import sys
import argparse
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime


class DiscogsSellerExporter:
    """Class to handle Discogs seller profile data export."""
    
    def __init__(self, token: Optional[str] = None, user_agent: str = "DiscogsSellerExport/1.0"):
        """
        Initialize the Discogs seller exporter.
        
        Args:
            token: Discogs API token (required)
            user_agent: User agent string for API requests
        """
        self.base_url = "https://api.discogs.com"
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "application/vnd.discogs.v2.discogs+json"
        }
        
        if token:
            self.headers["Authorization"] = f"Discogs token={token}"
        else:
            raise ValueError("Discogs API token is required")
    
    def get_seller_listings(self, seller_username: str, per_page: int = 100, 
                           page: int = 1, sort: str = "price", 
                           sort_order: str = "asc") -> Optional[Dict]:
        """
        Get all listings for a specific seller using the user inventory endpoint.
        
        Args:
            seller_username: Discogs seller username
            per_page: Number of results per page (max 100)
            page: Page number to retrieve
            sort: Sort field (price, listed, condition, etc.)
            sort_order: Sort order (asc or desc)
            
        Returns:
            Dictionary containing seller listings or None if error
        """
        url = f"{self.base_url}/users/{seller_username}/inventory"
        params = {
            "status": "For Sale",  # Only get items for sale
            "per_page": min(per_page, 100),
            "page": page,
            "sort": sort,
            "sort_order": sort_order
        }
        
        return self._make_api_request(url, params)
    
    def get_all_seller_listings(self, seller_username: str, max_pages: int = None) -> List[Dict]:
        """
        Get all listings for a seller across multiple pages.
        
        Args:
            seller_username: Discogs seller username
            max_pages: Maximum number of pages to fetch (None for all)
            
        Returns:
            List of all listing dictionaries
        """
        all_listings = []
        page = 1
        
        print(f"🔍 Fetching listings for seller: {seller_username}")
        
        while True:
            if max_pages and page > max_pages:
                break
                
            print(f"📄 Fetching page {page}...")
            
            listings_data = self.get_seller_listings(seller_username, per_page=100, page=page)
            
            if not listings_data:
                print(f"❌ Failed to fetch page {page}")
                break
            
            results = listings_data.get("listings", [])
            if not results:
                print(f"✅ No more listings found on page {page}")
                break
            
            all_listings.extend(results)
            print(f"📦 Found {len(results)} listings on page {page} (Total: {len(all_listings)})")
            
            # Check if there are more pages
            pagination = listings_data.get("pagination", {})
            if page >= pagination.get("pages", 1):
                break
            
            page += 1
            time.sleep(1)  # Rate limiting
        
        print(f"🎯 Total listings fetched: {len(all_listings)}")
        return all_listings
    
    def _make_api_request(self, url: str, params: Dict) -> Optional[Dict]:
        """
        Make an API request with error handling and rate limiting.
        
        Args:
            url: API endpoint URL
            params: Request parameters
            
        Returns:
            JSON response or None if error
        """
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 401:
                print("\n❌ Authentication Error (401 Unauthorized)")
                print("The Discogs API requires authentication for marketplace requests.")
                print("\nTo fix this:")
                print("1. Get a personal access token from: https://www.discogs.com/settings/developers")
                print("2. Set it as an environment variable: export DISCOGS_TOKEN=your_token_here")
                print("3. Or use the --token option when running the script")
                return None
            elif response.status_code == 429:
                print("⚠️ Rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
                return self._make_api_request(url, params)  # Retry
            elif response.status_code == 404:
                print(f"❌ Seller '{params.get('seller', 'Unknown')}' not found")
                return None
            
            response.raise_for_status()
            
            # Basic rate limiting - sleep between requests
            time.sleep(1)
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request to {url}: {e}", file=sys.stderr)
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}", file=sys.stderr)
            return None
    
    def flatten_listing_data(self, listing: Dict) -> Dict:
        """
        Flatten a listing dictionary to extract all available fields.
        
        Args:
            listing: Single listing dictionary from API response
            
        Returns:
            Flattened dictionary with all available fields
        """
        flattened = {}
        
        # Basic listing information
        flattened['listing_id'] = listing.get('id', '')
        flattened['status'] = listing.get('status', '')
        flattened['condition'] = listing.get('condition', '')
        flattened['sleeve_condition'] = listing.get('sleeve_condition', '')
        flattened['posted'] = listing.get('posted', '')
        flattened['uri'] = listing.get('uri', '')
        flattened['resource_url'] = listing.get('resource_url', '')
        
        # Price information
        price = listing.get('price', {})
        flattened['price_value'] = price.get('value', '')
        flattened['price_currency'] = price.get('currency', '')
        
        # Shipping information
        shipping = listing.get('shipping', {})
        flattened['shipping_price'] = shipping.get('price', '')
        flattened['shipping_currency'] = shipping.get('currency', '')
        
        # Additional listing details
        flattened['weight'] = listing.get('weight', '')
        flattened['format_quantity'] = listing.get('format_quantity', '')
        flattened['external_id'] = listing.get('external_id', '')
        flattened['location'] = listing.get('location', '')
        flattened['comments'] = listing.get('comments', '')
        
        # Release information
        release = listing.get('release', {})
        flattened['release_id'] = release.get('id', '')
        flattened['release_title'] = release.get('title', '')
        flattened['release_year'] = release.get('year', '')
        flattened['release_resource_url'] = release.get('resource_url', '')
        flattened['release_uri'] = release.get('uri', '')
        
        # Artist information (inventory API uses 'artist' as string, not 'artists' array)
        artist = release.get('artist', '')
        if artist:
            flattened['artist_names'] = artist
            flattened['primary_artist'] = artist
        else:
            # Fallback for search API format (artists array)
            artists = release.get('artists', [])
            if artists:
                artist_names = [artist.get('name', '') for artist in artists]
                flattened['artist_names'] = '; '.join(artist_names)
                flattened['primary_artist'] = artists[0].get('name', '') if artists else ''
            else:
                flattened['artist_names'] = ''
                flattened['primary_artist'] = ''
        
        # Label information (inventory API uses 'label' as string, not 'labels' array)
        label = release.get('label', '')
        if label:
            flattened['label_names'] = label
            flattened['primary_label'] = label
        else:
            # Fallback for search API format (labels array)
            labels = release.get('labels', [])
            if labels:
                label_names = [label.get('name', '') for label in labels]
                flattened['label_names'] = '; '.join(label_names)
                flattened['primary_label'] = labels[0].get('name', '') if labels else ''
            else:
                flattened['label_names'] = ''
                flattened['primary_label'] = ''
        
        # Format information
        formats = release.get('formats', [])
        if formats:
            format_names = [fmt.get('name', '') for fmt in formats]
            flattened['format_names'] = '; '.join(format_names)
            flattened['primary_format'] = formats[0].get('name', '') if formats else ''
        else:
            flattened['format_names'] = ''
            flattened['primary_format'] = ''
        
        # Genre and style information
        genres = release.get('genres', [])
        flattened['genres'] = '; '.join(genres) if genres else ''
        
        styles = release.get('styles', [])
        flattened['styles'] = '; '.join(styles) if styles else ''
        
        # Country information
        flattened['country'] = release.get('country', '')
        
        # Additional release details
        flattened['catalog_number'] = release.get('catalog_number', '')
        flattened['barcode'] = release.get('barcode', '')
        flattened['master_id'] = release.get('master_id', '')
        flattened['master_url'] = release.get('master_url', '')
        
        # Images
        images = release.get('images', [])
        if images:
            flattened['image_uri'] = images[0].get('uri', '') if images else ''
            flattened['image_resource_url'] = images[0].get('resource_url', '') if images else ''
        else:
            flattened['image_uri'] = ''
            flattened['image_resource_url'] = ''
        
        # Statistics
        stats = release.get('stats', {})
        flattened['release_community_have'] = stats.get('community', {}).get('have', '')
        flattened['release_community_want'] = stats.get('community', {}).get('want', '')
        
        # Add timestamp of export
        flattened['export_timestamp'] = datetime.now().isoformat()
        
        return flattened
    
    def export_to_csv(self, listings: List[Dict], filename: str) -> bool:
        """
        Export listings to CSV file.
        
        Args:
            listings: List of listing dictionaries
            filename: Output CSV filename
            
        Returns:
            True if successful, False otherwise
        """
        if not listings:
            print("❌ No listings to export")
            return False
        
        try:
            # Flatten all listings
            flattened_listings = [self.flatten_listing_data(listing) for listing in listings]
            
            # Get all unique field names
            all_fields = set()
            for listing in flattened_listings:
                all_fields.update(listing.keys())
            
            # Sort fields for consistent column order
            fieldnames = sorted(list(all_fields))
            
            # Write to CSV with CRLF line endings to preserve Windows-style formatting
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\r\n')
                writer.writeheader()
                writer.writerows(flattened_listings)
            
            print(f"✅ Successfully exported {len(flattened_listings)} listings to {filename}")
            print(f"📊 CSV contains {len(fieldnames)} columns")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return False


def main():
    """Main function to run the seller export tool."""
    parser = argparse.ArgumentParser(
        description="Export all Discogs seller listings to CSV",
        epilog="""
Authentication:
The Discogs API requires a personal access token for marketplace requests.
Get your token from: https://www.discogs.com/settings/developers

Examples:
  %(prog)s --seller freakin_beats --token YOUR_TOKEN
  %(prog)s --seller freakin_beats --token YOUR_TOKEN --output my_listings.csv
  %(prog)s --seller freakin_beats --max-pages 5
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--seller",
        required=True,
        help="Discogs seller username"
    )
    parser.add_argument(
        "--token",
        help="Discogs API token (can also be set via DISCOGS_TOKEN env var)"
    )
    parser.add_argument(
        "--output",
        default="discogs_seller_listings.csv",
        help="Output CSV filename (default: discogs_seller_listings.csv)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Maximum number of pages to fetch (default: all pages)"
    )
    parser.add_argument(
        "--user-agent",
        default="DiscogsSellerExport/1.0",
        help="User agent string for API requests"
    )
    
    args = parser.parse_args()
    
    # Get token from argument or environment variable
    token = args.token or os.getenv("DISCOGS_TOKEN")
    
    if not token:
        print("❌ Error: Discogs API token is required.")
        print("Get a token from: https://www.discogs.com/settings/developers")
        print("Then set DISCOGS_TOKEN environment variable or use --token option")
        sys.exit(1)
    
    # Create exporter instance
    try:
        exporter = DiscogsSellerExporter(token=token, user_agent=args.user_agent)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    print(f"🎯 Starting export for seller: {args.seller}")
    if args.max_pages:
        print(f"📄 Limiting to {args.max_pages} pages")
    print(f"💾 Output file: {args.output}")
    print("=" * 50)
    
    # Fetch all listings
    listings = exporter.get_all_seller_listings(
        seller_username=args.seller,
        max_pages=args.max_pages
    )
    
    if not listings:
        print("❌ No listings found or failed to fetch data")
        sys.exit(1)
    
    # Export to CSV
    success = exporter.export_to_csv(listings, args.output)
    
    if success:
        print("🎉 Export completed successfully!")
        print(f"📁 File saved as: {args.output}")
    else:
        print("❌ Export failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
