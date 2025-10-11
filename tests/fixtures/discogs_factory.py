"""
Factory for generating mock Discogs API responses.

This module provides utilities for creating realistic test data
that mimics the structure of Discogs API responses.
"""

import random
from faker import Faker
from typing import Dict, List, Optional

class DiscogsDataFactory:
    """Factory for generating mock Discogs listing data."""
    
    def __init__(self, seed: Optional[int] = 42):
        """
        Initialize the factory with a Faker instance.
        
        Args:
            seed: Random seed for reproducible test data
        """
        self.fake = Faker()
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)
    
    def create_listing(self, **overrides) -> Dict:
        """
        Create a mock Discogs listing.
        
        Args:
            **overrides: Fields to override in the generated listing
            
        Returns:
            Dictionary representing a Discogs listing
        """
        listing_id = overrides.get('id', self.fake.random_int(min=100000, max=999999999))
        
        listing = {
            'id': listing_id,
            'status': overrides.get('status', 'For Sale'),
            'condition': overrides.get('condition', random.choice([
                'Mint (M)', 'Near Mint (NM or M-)', 'Very Good Plus (VG+)',
                'Very Good (VG)', 'Good Plus (G+)', 'Good (G)'
            ])),
            'sleeve_condition': overrides.get('sleeve_condition', random.choice([
                'Mint (M)', 'Near Mint (NM or M-)', 'Very Good Plus (VG+)',
                'Very Good (VG)', 'Good Plus (G+)', 'Good (G)'
            ])),
            'posted': overrides.get('posted', self.fake.iso8601()),
            'uri': overrides.get('uri', f'/sell/item/{listing_id}'),
            'resource_url': overrides.get('resource_url', 
                f'https://api.discogs.com/marketplace/listings/{listing_id}'),
            'price': {
                'value': overrides.get('price_value', round(random.uniform(5.0, 150.0), 2)),
                'currency': overrides.get('price_currency', 'USD')
            }, 
            'shipping_price': {
                'value': overrides.get('shipping_price', round(random.uniform(3.0, 10.0), 2)),
                'currency': overrides.get('shipping_currency', 'USD')
            },
            'weight': overrides.get('weight', round(random.uniform(150, 250), 1)),
            'format_quantity': overrides.get('format_quantity', 1),
            'external_id': overrides.get('external_id', ''),
            'location': overrides.get('location', self.fake.city()),
            'comments': overrides.get('comments', ''),
            'release': self._create_release(**overrides.get('release', {}))
        }
        # Apply any additional overrides
        for key, value in overrides.items():
            if key not in listing and key != 'release':
                listing[key] = value
        
        return listing
    
    def _create_release(self, **overrides) -> Dict:
        """Create a mock release object."""
        release_id = overrides.get('id', self.fake.random_int(min=1000, max=9999999))
        
        artist_name = overrides.get('artist', self.fake.name())
        label_name = overrides.get('label', f'{self.fake.company()} Records')
        format_name = overrides.get('format', random.choice([
            'Vinyl', 'LP', '12"', '7"', 'CD', 'Cassette'
        ]))
        
        # Generate genre and style
        genres = overrides.get('genres', random.sample([
            'Rock', 'Electronic', 'Jazz', 'Funk / Soul', 'Pop',
            'Hip Hop', 'Classical', 'Reggae', 'Blues', 'Folk, World, & Country'
        ], k=random.randint(1, 2)))
        
        styles = overrides.get('styles', random.sample([
            'Alternative Rock', 'Indie Rock', 'House', 'Techno', 'Disco',
            'Funk', 'Soul', 'Punk', 'Post-Punk', 'Experimental'
        ], k=random.randint(0, 2)))  # Styles can be empty
        
        # Generate image data
        images = overrides.get('images', [{
            'type': 'primary',
            'uri': self.fake.image_url(),
            'resource_url': self.fake.image_url(),
            'uri150': self.fake.image_url(width=150),
            'width': 600,
            'height': 600
        }])
        
        release = {
            'id': release_id,
            'title': overrides.get('title', self.fake.catch_phrase()),
            'year': overrides.get('year', random.randint(1960, 2024)),
            'resource_url': overrides.get('resource_url',
                f'https://api.discogs.com/releases/{release_id}'),
            'uri': overrides.get('uri', f'/release/{release_id}'),
            'artist': artist_name,
            'label': label_name,
            'format': format_name,
            'genres': genres,
            'styles': styles,
            'country': overrides.get('country', random.choice([
                'US', 'UK', 'Germany', 'Japan', 'France', 'Canada', 'Italy'
            ])),
            'catalog_number': overrides.get('catalog_number', 
                self.fake.bothify(text='???-####')),
            'barcode': overrides.get('barcode', ''),
            'master_id': overrides.get('master_id', self.fake.random_int(min=1000, max=999999)),
            'master_url': overrides.get('master_url',
                f'https://api.discogs.com/masters/{self.fake.random_int(min=1000, max=999999)}'),
            'images': images,
            'stats': {
                'community': {
                    'have': random.randint(10, 5000),
                    'want': random.randint(5, 2000)
                }
            }
        }
        
        # Apply any additional overrides
        for key, value in overrides.items():
            if key not in release:
                release[key] = value
        
        return release
    
    def create_listings_page(
        self, 
        page: int = 1, 
        per_page: int = 100, 
        total_items: int = 250,
        **listing_overrides
    ) -> Dict:
        """
        Create a paginated response of listings.
        
        Args:
            page: Current page number
            per_page: Items per page
            total_items: Total number of items across all pages
            **listing_overrides: Overrides for individual listings
            
        Returns:
            Dictionary representing a Discogs API page response
        """
        total_pages = (total_items + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_items)
        num_listings = max(0, end_idx - start_idx)
        
        listings = [
            self.create_listing(**listing_overrides)
            for _ in range(num_listings)
        ]
        
        return {
            'pagination': {
                'page': page,
                'pages': total_pages,
                'per_page': per_page,
                'items': total_items,
                'urls': {
                    'last': f'https://api.discogs.com/users/test/inventory?page={total_pages}',
                    'next': f'https://api.discogs.com/users/test/inventory?page={page + 1}' 
                        if page < total_pages else None
                }
            },
            'listings': listings
        }
    
    def create_bulk_listings(self, count: int = 10, **overrides) -> List[Dict]:
        """
        Create multiple listings.
        
        Args:
            count: Number of listings to create
            **overrides: Common overrides for all listings
            
        Returns:
            List of listing dictionaries
        """
        return [self.create_listing(**overrides) for _ in range(count)]
