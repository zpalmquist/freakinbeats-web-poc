"""
Discogs API interface for converting Discogs data to our database schema.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime


class DiscogsInterface:
    """Interface for converting Discogs API data to our database format."""
    
    # Discogs to our condition mapping
    CONDITION_MAPPING = {
        'Mint (M)': 'Mint',
        'Near Mint (NM)': 'Near Mint', 
        'Very Good Plus (VG+)': 'Very Good +',
        'Very Good (VG)': 'Very Good',
        'Good Plus (G+)': 'Good +',
        'Good (G)': 'Good',
        'Fair (F)': 'Fair',
        'Poor (P)': 'Poor'
    }
    
    # Valid status values
    VALID_STATUSES = {'For Sale', 'Sold', 'Removed', 'Hold'}
    
    # Valid condition values
    VALID_CONDITIONS = {'Mint', 'Near Mint', 'Very Good +', 'Very Good', 'Good +', 'Good', 'Fair', 'Poor'}
    
    @classmethod
    def convert_listing(cls, discogs_listing: Dict) -> Dict:
        """
        Convert a Discogs listing to our database format.
        
        Args:
            discogs_listing: Raw listing from Discogs API
            
        Returns:
            Dictionary matching our Listing model fields
        """
        release = discogs_listing.get('release', {})
        price = discogs_listing.get('price', {})
        
        return {
            'listing_id': str(discogs_listing.get('id', '')),
            'status': cls._map_status(discogs_listing.get('status', '')),
            'media_condition': cls._map_condition(discogs_listing.get('condition', '')),
            'sleeve_condition': cls._map_condition(discogs_listing.get('sleeve_condition', '')),
            'posted_at': cls._parse_datetime(discogs_listing.get('posted', '')),
            'price': float(price.get('value', 0)) if price.get('value') else 0.0,
            'resource_url': discogs_listing.get('resource_url', ''),
            'quantity': int(discogs_listing.get('format_quantity', 1)),
            'release_title': release.get('title', ''),
            'release_year': cls._parse_year(release.get('year')),
            'image_uri': cls._extract_image_uri(release.get('images', [])),
            'artist_name': release.get('artist', ''),
            'label_name': cls._extract_primary_label(release.get('label', ''))
        }
    
    @classmethod
    def _map_status(cls, discogs_status: str) -> str:
        """Map Discogs status to our valid statuses."""
        if discogs_status in cls.VALID_STATUSES:
            return discogs_status
        return 'For Sale'  # Default
    
    @classmethod
    def _map_condition(cls, discogs_condition: str) -> str:
        """Map Discogs condition format to our format."""
        mapped = cls.CONDITION_MAPPING.get(discogs_condition)
        if mapped and mapped in cls.VALID_CONDITIONS:
            return mapped
        return 'Very Good'  # Default
    
    @classmethod
    def _parse_datetime(cls, date_string: str) -> Optional[datetime]:
        """Parse Discogs datetime string."""
        if not date_string:
            return None
        
        try:
            # Discogs format: "2024-01-15T10:30:00-08:00"
            if 'T' in date_string:
                date_part = date_string.split('T')[0]
                return datetime.strptime(date_part, '%Y-%m-%d')
            return datetime.strptime(date_string, '%Y-%m-%d')
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _parse_year(cls, year_value) -> Optional[int]:
        """Parse release year from various formats."""
        if not year_value:
            return None
        
        try:
            year = int(year_value)
            if 1900 <= year <= 2030:  # Reasonable range
                return year
        except (ValueError, TypeError):
            pass
        
        return None
    
    @classmethod
    def _extract_image_uri(cls, images: List[Dict]) -> str:
        """Extract primary image URI from images list."""
        if not images or not isinstance(images, list):
            return ''
        
        # Find primary image or use first available
        for image in images:
            if image.get('type') == 'primary':
                return image.get('uri', '')
        
        # Use first image if no primary
        return images[0].get('uri', '') if images else ''
    
    @classmethod
    def _extract_primary_label(cls, label_data) -> str:
        """Extract primary label name from label data."""
        if isinstance(label_data, str):
            return label_data
        elif isinstance(label_data, list) and label_data:
            return label_data[0]
        return 'Not On Label'
