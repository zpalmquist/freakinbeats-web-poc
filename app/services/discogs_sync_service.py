"""
Discogs API synchronization service.

This service handles fetching listings from the Discogs API and updating
the local database. It includes rate limiting and error handling.
"""

import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
from flask import current_app
from app.extensions import db
from app.models.listing import Listing


class DiscogsSyncService:
    """Service for synchronizing Discogs listings with local database."""
    
    def __init__(self, token: str, seller_username: str, user_agent: str):
        """
        Initialize the Discogs sync service.
        
        Args:
            token: Discogs API token
            seller_username: Discogs seller username
            user_agent: User agent string for API requests
        """
        self.base_url = "https://api.discogs.com"
        self.seller_username = seller_username
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "application/vnd.discogs.v2.discogs+json",
            "Authorization": f"Discogs token={token}"
        }
    
    def sync_all_listings(self) -> Dict[str, int]:
        """
        Fetch all listings from Discogs API and sync with database.
        
        Returns:
            Dictionary with sync statistics (added, updated, removed)
        """
        current_app.logger.info(f"Starting sync for seller: {self.seller_username}")
        
        # Fetch all listings from API
        api_listings = self._fetch_all_listings()
        
        if not api_listings:
            current_app.logger.warning("No listings fetched from API")
            return {'added': 0, 'updated': 0, 'removed': 0, 'total': 0}
        
        # Get current listing IDs from database
        existing_listings = {listing.listing_id: listing for listing in Listing.query.all()}
        api_listing_ids = set()
        
        stats = {'added': 0, 'updated': 0, 'removed': 0, 'total': len(api_listings)}
        
        # Process each API listing
        for api_listing in api_listings:
            flattened = self._flatten_listing(api_listing)
            listing_id = flattened.get('listing_id')
            
            if not listing_id:
                continue
            
            api_listing_ids.add(listing_id)
            
            if listing_id in existing_listings:
                # Update existing listing
                listing = existing_listings[listing_id]
                self._update_listing_from_dict(listing, flattened)
                stats['updated'] += 1
            else:
                # Create new listing
                listing = Listing(**flattened)
                db.session.add(listing)
                stats['added'] += 1
        
        # Remove listings that are no longer in API response
        for listing_id, listing in existing_listings.items():
            if listing_id not in api_listing_ids:
                db.session.delete(listing)
                stats['removed'] += 1
        
        # Commit all changes
        try:
            db.session.commit()
            current_app.logger.info(
                f"Sync completed: {stats['added']} added, "
                f"{stats['updated']} updated, {stats['removed']} removed"
            )
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error committing sync: {e}")
            raise
        
        return stats
    
    def _fetch_all_listings(self) -> List[Dict]:
        """
        Fetch all listings from Discogs API across multiple pages.
        
        Returns:
            List of all listing dictionaries
        """
        all_listings = []
        page = 1
        
        while True:
            current_app.logger.debug(f"Fetching page {page}...")
            
            listings_data = self._fetch_page(page)
            
            if not listings_data:
                break
            
            results = listings_data.get("listings", [])
            if not results:
                break
            
            all_listings.extend(results)
            current_app.logger.debug(
                f"Page {page}: {len(results)} listings (Total: {len(all_listings)})"
            )
            
            # Check if there are more pages
            pagination = listings_data.get("pagination", {})
            if page >= pagination.get("pages", 1):
                break
            
            page += 1
            time.sleep(1)  # Rate limiting
        
        current_app.logger.info(f"Total listings fetched: {len(all_listings)}")
        return all_listings
    
    def _fetch_page(self, page: int) -> Optional[Dict]:
        """
        Fetch a single page of listings from the API.
        
        Args:
            page: Page number to fetch
            
        Returns:
            JSON response or None if error
        """
        url = f"{self.base_url}/users/{self.seller_username}/inventory"
        params = {
            "status": "For Sale",
            "per_page": 100,
            "page": page,
            "sort": "listed",
            "sort_order": "desc"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 401:
                current_app.logger.error("Authentication error: Invalid Discogs token")
                return None
            elif response.status_code == 429:
                current_app.logger.warning("Rate limit exceeded, waiting 60 seconds...")
                time.sleep(60)
                return self._fetch_page(page)  # Retry
            elif response.status_code == 404:
                current_app.logger.error(f"Seller '{self.seller_username}' not found")
                return None
            
            response.raise_for_status()
            time.sleep(1)  # Basic rate limiting
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error fetching page {page}: {e}")
            return None
    
    def _flatten_listing(self, listing: Dict) -> Dict:
        """
        Flatten a listing dictionary to match database schema.
        
        Args:
            listing: Single listing dictionary from API response
            
        Returns:
            Flattened dictionary matching Listing model fields
        """
        flattened = {}
        
        # Basic listing information
        flattened['listing_id'] = str(listing.get('id', ''))
        flattened['status'] = listing.get('status', '')
        flattened['condition'] = listing.get('condition', '')
        flattened['sleeve_condition'] = listing.get('sleeve_condition', '')
        flattened['posted'] = listing.get('posted', '')
        flattened['uri'] = listing.get('uri', '')
        flattened['resource_url'] = listing.get('resource_url', '')
        
        # Price information
        price = listing.get('price', {})
        flattened['price_value'] = float(price.get('value', 0)) if price.get('value') else None
        flattened['price_currency'] = price.get('currency', '')
        
        # Shipping information
        shipping = listing.get('shipping', {})
        flattened['shipping_price'] = float(shipping.get('price', 0)) if shipping.get('price') else None
        flattened['shipping_currency'] = shipping.get('currency', '')
        
        # Additional listing details
        flattened['weight'] = float(listing.get('weight', 0)) if listing.get('weight') else None
        flattened['format_quantity'] = int(listing.get('format_quantity', 0)) if listing.get('format_quantity') else None
        flattened['external_id'] = listing.get('external_id', '')
        flattened['location'] = listing.get('location', '')
        flattened['comments'] = listing.get('comments', '')
        
        # Release information
        release = listing.get('release', {})
        flattened['release_id'] = str(release.get('id', ''))
        flattened['release_title'] = release.get('title', '')
        flattened['release_year'] = str(release.get('year', ''))
        flattened['release_resource_url'] = release.get('resource_url', '')
        flattened['release_uri'] = release.get('uri', '')
        
        # Artist information
        artist = release.get('artist', '')
        if artist:
            flattened['artist_names'] = artist
            flattened['primary_artist'] = artist
        else:
            artists = release.get('artists', [])
            if artists:
                artist_names = [a.get('name', '') for a in artists]
                flattened['artist_names'] = '; '.join(artist_names)
                flattened['primary_artist'] = artists[0].get('name', '') if artists else ''
            else:
                flattened['artist_names'] = ''
                flattened['primary_artist'] = ''
        
        # Label information
        label = release.get('label', '')
        if label:
            flattened['label_names'] = label
            flattened['primary_label'] = label
        else:
            labels = release.get('labels', [])
            if labels:
                label_names = [lbl.get('name', '') for lbl in labels]
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
        flattened['master_id'] = str(release.get('master_id', ''))
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
        community = stats.get('community', {})
        flattened['release_community_have'] = int(community.get('have', 0)) if community.get('have') else None
        flattened['release_community_want'] = int(community.get('want', 0)) if community.get('want') else None
        
        # Timestamp
        flattened['export_timestamp'] = datetime.now().isoformat()
        
        return flattened
    
    def _update_listing_from_dict(self, listing: Listing, data: Dict):
        """
        Update a Listing object with data from dictionary.
        
        Args:
            listing: Listing object to update
            data: Dictionary with new data
        """
        for key, value in data.items():
            if hasattr(listing, key):
                setattr(listing, key, value)

