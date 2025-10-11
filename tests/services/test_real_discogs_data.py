"""
Tests using real Discogs API data.

These tests use actual data fetched from the Discogs API to ensure
our code handles real-world responses correctly.

To enable these tests:
1. Set ENABLE_REAL_DATA_TESTS=true in your environment or .env
2. Run: python3 tests/fetch_real_discogs_data.py
3. Run tests normally: pytest tests/services/

The real data file (real_discogs_data.json) is git-ignored and contains
a minimal sample of actual API responses for validation.
"""

import pytest
import json
import os
from pathlib import Path
from app.services.discogs_sync_service import DiscogsSyncService
from app.models.listing import Listing


def should_run_real_data_tests():
    """Check if real data tests should run based on environment."""
    return os.getenv('ENABLE_REAL_DATA_TESTS', 'false').lower() == 'true'


@pytest.fixture
def real_discogs_data():
    """Load real Discogs API response data."""
    if not should_run_real_data_tests():
        pytest.skip("Real data tests disabled. Set ENABLE_REAL_DATA_TESTS=true to enable.")
    
    data_file = Path(__file__).parent.parent / 'fixtures' / 'real_discogs_data.json'
    
    if not data_file.exists():
        pytest.skip(
            "Real Discogs data not available. "
            "Run: python3 tests/fetch_real_discogs_data.py"
        )
    
    with open(data_file, 'r') as f:
        return json.load(f)


class TestRealDiscogsData:
    """Test with real Discogs API responses."""
    
    def test_real_data_structure(self, real_discogs_data):
        """Verify the real data has expected structure."""
        assert 'pagination' in real_discogs_data
        assert 'listings' in real_discogs_data
        assert len(real_discogs_data['listings']) > 0
        
        # Check pagination structure
        pagination = real_discogs_data['pagination']
        assert 'page' in pagination
        assert 'pages' in pagination
        assert 'items' in pagination
    
    def test_flatten_real_listing(self, sync_service, real_discogs_data):
        """Test flattening a real Discogs listing."""
        real_listing = real_discogs_data['listings'][0]
        
        flattened = sync_service._flatten_listing(real_listing)
        
        # Verify all required fields are present
        assert flattened['listing_id'] == str(real_listing['id'])
        assert flattened['status'] == real_listing['status']
        assert flattened['condition'] == real_listing['condition']
        assert flattened['sleeve_condition'] == real_listing['sleeve_condition']
        
        # Verify price fields
        assert flattened['price_value'] == real_listing['price']['value']
        assert flattened['price_currency'] == real_listing['price']['currency']
        
        # Verify release fields
        assert flattened['release_id'] == str(real_listing['release']['id'])
        assert flattened['release_title'] == real_listing['release']['title']
        assert flattened['release_year'] == str(real_listing['release']['year'])
        
        # Verify artist handling (real API uses 'artist' string, not 'artists' array)
        assert flattened['artist_names'] == real_listing['release']['artist']
        assert flattened['primary_artist'] == real_listing['release']['artist']
        
        # Verify label handling
        assert flattened['label_names'] == real_listing['release']['label']
        assert flattened['primary_label'] == real_listing['release']['label']
    
    def test_flatten_all_real_listings(self, sync_service, real_discogs_data):
        """Test that all real listings can be flattened without errors."""
        for listing in real_discogs_data['listings']:
            flattened = sync_service._flatten_listing(listing)
            
            # Basic sanity checks
            assert flattened['listing_id']
            assert flattened['status']
            assert flattened['price_value'] is not None
            assert flattened['export_timestamp']
    
    def test_real_shipping_structure(self, sync_service, real_discogs_data):
        """Test that real shipping data structure is handled correctly."""
        real_listing = real_discogs_data['listings'][0]
        flattened = sync_service._flatten_listing(real_listing)
        
        # Real API has 'shipping_price' as a dict, not 'shipping'
        if 'shipping_price' in real_listing:
            assert flattened['shipping_price'] == real_listing['shipping_price']['value']
            assert flattened['shipping_currency'] == real_listing['shipping_price']['currency']
    
    def test_real_data_db_insertion(self, sync_service, db, real_discogs_data):
        """Test that real listings can be inserted into database."""
        real_listing = real_discogs_data['listings'][0]
        flattened = sync_service._flatten_listing(real_listing)
        
        # Create and save listing
        listing = Listing(**flattened)
        db.session.add(listing)
        db.session.commit()
        
        # Verify it was saved
        saved = Listing.query.filter_by(listing_id=flattened['listing_id']).first()
        assert saved is not None
        assert saved.release_title == flattened['release_title']
        assert saved.price_value == flattened['price_value']
    
    def test_real_format_handling(self, sync_service, real_discogs_data):
        """Test handling of format field from real API."""
        real_listing = real_discogs_data['listings'][0]
        flattened = sync_service._flatten_listing(real_listing)
        
        # Real API has 'format' string, not 'formats' array
        # Our code should handle both cases
        assert flattened['format_names'] is not None
        assert flattened['primary_format'] is not None
    
    def test_real_image_handling(self, sync_service, real_discogs_data):
        """Test that real image data is extracted correctly."""
        real_listing = real_discogs_data['listings'][0]
        flattened = sync_service._flatten_listing(real_listing)
        
        if real_listing['release'].get('images'):
            assert flattened['image_uri'] != ''
            assert flattened['image_resource_url'] != ''
        else:
            assert flattened['image_uri'] == ''
            assert flattened['image_resource_url'] == ''
