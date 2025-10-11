"""
Unit tests for DiscogsSyncService.

This module tests the Discogs API synchronization service, including:
- Fetching single pages from the API
- Fetching all listings across multiple pages
- Syncing listings with the database (add, update, remove)
- Error handling and rate limiting
"""
import os
import json
import pytest
import responses
from unittest.mock import Mock, patch, call
from datetime import datetime
from freezegun import freeze_time

from app.services.discogs_sync_service import DiscogsSyncService
from app.models.listing import Listing


class TestDiscogsSyncServiceInit:
    """Test DiscogsSyncService initialization."""
    
    def test_init_sets_attributes(self, app_context):
        """Test that initialization sets correct attributes."""
        service = DiscogsSyncService(
            token='test_token',
            seller_username='test_user',
            user_agent='TestAgent/1.0'
        )
        
        assert service.base_url == 'https://api.discogs.com'
        assert service.seller_username == 'test_user'
        assert 'TestAgent/1.0' in service.headers['User-Agent']
        assert 'Discogs token=test_token' in service.headers['Authorization']
        assert service.headers['Accept'] == 'application/vnd.discogs.v2.discogs+json'


class TestFetchPage:
    """Test the _fetch_page method."""
    
    @responses.activate
    def test_fetch_page_success(self, sync_service, mock_listings_page):
        """Test successful page fetch."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        responses.add(
            responses.GET,
            url,
            json=mock_listings_page,
            status=200
        )
        
        result = sync_service._fetch_page(1)
        
        assert result is not None
        assert 'listings' in result
        assert 'pagination' in result
    
    @responses.activate
    def test_fetch_page_with_params(self, sync_service, mock_listings_page):
        """Test page fetch includes correct parameters."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        def check_params(request):
            assert request.params['status'] == 'For Sale'
            assert request.params['per_page'] == '100'
            assert request.params['page'] == '1'
            return (200, {}, json.dumps(mock_listings_page))
        
        responses.add_callback(
            responses.GET,
            url,
            callback=check_params
        )
        
        sync_service._fetch_page(1)
    
    @responses.activate
    def test_fetch_page_401_authentication_error(self, sync_service):
        """Test handling of authentication errors."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        responses.add(responses.GET, url, status=401)
        
        result = sync_service._fetch_page(1)
        
        assert result is None
    
    @responses.activate
    def test_fetch_page_404_seller_not_found(self, sync_service):
        """Test handling of seller not found errors."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        responses.add(responses.GET, url, status=404)
        
        result = sync_service._fetch_page(1)
        
        assert result is None
    
    @responses.activate
    @patch('time.sleep')
    def test_fetch_page_429_rate_limit_retry(self, mock_sleep, sync_service, mock_listings_page):
        """Test retry logic for rate limit errors."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # First call returns 429, second succeeds
        responses.add(responses.GET, url, status=429)
        responses.add(responses.GET, url, json=mock_listings_page, status=200)
        
        result = sync_service._fetch_page(1)
        
        assert result is not None
        assert len(responses.calls) == 2
        mock_sleep.assert_any_call(60)  # Should wait 60 seconds

class TestFetchAllListings:
    """Test the _fetch_all_listings method."""
    
    @responses.activate
    @patch('time.sleep')
    def test_fetch_all_listings_single_page(self, mock_sleep, sync_service, discogs_factory):
        """Test fetching all listings when only one page exists."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        page_data = discogs_factory.create_listings_page(
            page=1,
            per_page=100,
            total_items=50
        )
        
        responses.add(responses.GET, url, json=page_data, status=200)
        
        results = sync_service._fetch_all_listings()
        
        assert len(results) == 50
    
    @responses.activate
    @patch('time.sleep')
    def test_fetch_all_listings_multiple_pages(self, mock_sleep, sync_service, discogs_factory):
        """Test fetching all listings across multiple pages."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # Page 1
        page1_data = discogs_factory.create_listings_page(
            page=1,
            per_page=100,
            total_items=250
        )
        responses.add(responses.GET, url, json=page1_data, status=200)
        
        # Page 2
        page2_data = discogs_factory.create_listings_page(
            page=2,
            per_page=100,
            total_items=250
        )
        responses.add(responses.GET, url, json=page2_data, status=200)
        
        # Page 3 (last page, partial)
        page3_data = discogs_factory.create_listings_page(
            page=3,
            per_page=100,
            total_items=250
        )
        responses.add(responses.GET, url, json=page3_data, status=200)
        
        results = sync_service._fetch_all_listings()
        
        assert len(results) == 250
    
    @responses.activate
    @patch('time.sleep')
    def test_fetch_all_listings_empty_response(self, mock_sleep, sync_service):
        """Test handling of empty API response."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        empty_response = {
            'pagination': {'page': 1, 'pages': 1, 'items': 0},
            'listings': []
        }
        responses.add(responses.GET, url, json=empty_response, status=200)
        
        results = sync_service._fetch_all_listings()
        
        assert len(results) == 0
    
    @responses.activate
    def test_fetch_all_listings_api_error(self, sync_service):
        """Test handling of API errors during fetch."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        responses.add(responses.GET, url, status=500)
        
        results = sync_service._fetch_all_listings()
        
        assert len(results) == 0


class TestSyncAllListings:
    """Test the sync_all_listings method."""
    
    @responses.activate
    @patch('time.sleep')
    def test_sync_adds_new_listings(self, mock_sleep, sync_service, db, discogs_factory):
        """Test that new listings are added to database."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        page_data = discogs_factory.create_listings_page(
            page=1,
            per_page=100,
            total_items=3
        )
        responses.add(responses.GET, url, json=page_data, status=200)
        
        stats = sync_service.sync_all_listings()
        
        assert stats['added'] == 3
        assert stats['updated'] == 0
        assert stats['removed'] == 0
        assert Listing.query.count() == 3
    
    @responses.activate
    @patch('time.sleep')
    def test_sync_updates_existing_listings(self, mock_sleep, sync_service, db, discogs_factory):
        """Test that existing listings are updated."""
        # Create existing listing in database
        existing = Listing(
            listing_id='12345',
            artist_names='Old Artist',
            release_title='Old Title',
            price_value=10.0
        )
        db.session.add(existing)
        db.session.commit()
        
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # API returns updated listing
        page_data = discogs_factory.create_listings_page(
            page=1,
            per_page=100,
            total_items=1,
            id=12345,
            price_value=15.0,
            release={'artist': 'New Artist', 'title': 'New Title'}
        )
        responses.add(responses.GET, url, json=page_data, status=200)
        
        stats = sync_service.sync_all_listings()
        
        assert stats['added'] == 0
        assert stats['updated'] == 1
        assert stats['removed'] == 0
        
        updated = Listing.query.filter_by(listing_id='12345').first()
        assert updated.price_value == 15.0
        assert updated.artist_names == 'New Artist'
    
    @responses.activate
    @patch('time.sleep')
    def test_sync_removes_delisted_items(self, mock_sleep, sync_service, db, discogs_factory):
        """Test that listings not in API response are removed."""
        # Create listings in database
        listing1 = Listing(listing_id='11111', artist_names='Artist 1', release_title='Title 1')
        listing2 = Listing(listing_id='22222', artist_names='Artist 2', release_title='Title 2')
        db.session.add_all([listing1, listing2])
        db.session.commit()
        
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # API only returns one listing
        page_data = discogs_factory.create_listings_page(
            page=1,
            per_page=100,
            total_items=1,
            id=11111
        )
        responses.add(responses.GET, url, json=page_data, status=200)
        
        stats = sync_service.sync_all_listings()
        
        assert stats['added'] == 0
        assert stats['updated'] == 1
        assert stats['removed'] == 1
        assert Listing.query.count() == 1
    
    @responses.activate
    @patch('time.sleep')
    def test_sync_handles_mixed_operations(self, mock_sleep, sync_service, db, discogs_factory):
        """Test sync with add, update, and remove operations."""
        # Existing listings
        existing1 = Listing(listing_id='11111', artist_names='Artist 1', release_title='Title 1')
        existing2 = Listing(listing_id='22222', artist_names='Artist 2', release_title='Title 2')
        db.session.add_all([existing1, existing2])
        db.session.commit()
        
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # API returns: updated 11111, new 33333, removes 22222
        listings = [
            discogs_factory.create_listing(id=11111),
            discogs_factory.create_listing(id=33333)
        ]
        page_data = {
            'pagination': {'page': 1, 'pages': 1, 'items': 2, 'per_page': 100},
            'listings': listings
        }
        responses.add(responses.GET, url, json=page_data, status=200)
        
        stats = sync_service.sync_all_listings()
        
        assert stats['added'] == 1
        assert stats['updated'] == 1
        assert stats['removed'] == 1
        assert Listing.query.count() == 2
    
    @responses.activate
    def test_sync_empty_api_response(self, sync_service, db):
        """Test sync with empty API response."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        responses.add(responses.GET, url, status=500)
        
        stats = sync_service.sync_all_listings()
        
        assert stats['added'] == 0
        assert stats['updated'] == 0
        assert stats['removed'] == 0
        assert stats['total'] == 0
    
    @responses.activate
    @patch('time.sleep')
    def test_sync_database_error_rollback(self, mock_sleep, sync_service, db, discogs_factory):
        """Test that database errors trigger rollback."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        page_data = discogs_factory.create_listings_page(page=1, total_items=1)
        responses.add(responses.GET, url, json=page_data, status=200)
        
        with patch.object(db.session, 'commit', side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                sync_service.sync_all_listings()


class TestFlattenListing:
    """Test the _flatten_listing method."""
    
    def test_flatten_basic_fields(self, sync_service, mock_listing):
        """Test flattening basic listing fields."""
        result = sync_service._flatten_listing(mock_listing)
        
        assert result['listing_id'] == str(mock_listing['id'])
        assert result['status'] == mock_listing['status']
        assert result['condition'] == mock_listing['condition']
        assert result['sleeve_condition'] == mock_listing['sleeve_condition']
        assert result['posted'] == mock_listing['posted']
        assert result['uri'] == mock_listing['uri']
        assert result['resource_url'] == mock_listing['resource_url']
    
    def test_flatten_price_fields(self, sync_service, mock_listing):
        """Test flattening price information."""
        result = sync_service._flatten_listing(mock_listing)
        
        assert result['price_value'] == mock_listing['price']['value']
        assert result['price_currency'] == mock_listing['price']['currency']
        # Real API uses 'shipping_price', not 'shipping'
        assert result['shipping_price'] == mock_listing['shipping_price']['value']
        assert result['shipping_currency'] == mock_listing['shipping_price']['currency']
    
    def test_flatten_release_fields(self, sync_service, mock_listing):
        """Test flattening release information."""
        result = sync_service._flatten_listing(mock_listing)
        release = mock_listing['release']
        
        assert result['release_id'] == str(release['id'])
        assert result['release_title'] == release['title']
        assert result['release_year'] == str(release['year'])
        assert result['release_resource_url'] == release['resource_url']
        assert result['release_uri'] == release['uri']
    
    def test_flatten_artist_fields(self, sync_service, mock_listing):
        """Test flattening artist information."""
        result = sync_service._flatten_listing(mock_listing)
        release = mock_listing['release']
        
        # Real API uses single 'artist' string
        assert result['artist_names'] == release['artist']
        assert result['primary_artist'] == release['artist']
    
    def test_flatten_with_missing_fields(self, sync_service, discogs_factory):
        """Test flattening handles missing optional fields gracefully."""
        minimal_listing = discogs_factory.create_listing(
            comments='',
            external_id='',
            release={
                'barcode': '',
                'styles': []
            }
        )
        
        result = sync_service._flatten_listing(minimal_listing)
        
        assert result['comments'] == ''
        assert result['external_id'] == ''
        assert result['barcode'] == ''
        assert result['styles'] == ''
    
    @freeze_time("2024-01-15 12:00:00")
    def test_flatten_timestamp(self, sync_service, mock_listing):
        """Test that export timestamp is added."""
        result = sync_service._flatten_listing(mock_listing)
        
        assert 'export_timestamp' in result
        assert result['export_timestamp'] == "2024-01-15T12:00:00"


class TestUpdateListingFromDict:
    """Test the _update_listing_from_dict method."""
    
    def test_update_existing_fields(self, sync_service, db):
        """Test updating existing listing fields."""
        listing = Listing(
            listing_id='12345',
            artist_names='Old Artist',
            price_value=10.0
        )
        db.session.add(listing)
        db.session.commit()
        
        update_data = {
            'artist_names': 'New Artist',
            'price_value': 15.0,
            'release_title': 'New Title'
        }
        
        sync_service._update_listing_from_dict(listing, update_data)
        
        assert listing.artist_names == 'New Artist'
        assert listing.price_value == 15.0
        assert listing.release_title == 'New Title'
    
    def test_update_ignores_invalid_fields(self, sync_service, db):
        """Test that invalid field names are ignored."""
        listing = Listing(
            listing_id='12345',
            artist_names='Artist'
        )
        db.session.add(listing)
        db.session.commit()
        
        update_data = {
            'artist_names': 'New Artist',
            'invalid_field': 'Should be ignored',
            'another_fake_field': 123
        }
        
        sync_service._update_listing_from_dict(listing, update_data)
        
        assert listing.artist_names == 'New Artist'
        assert not hasattr(listing, 'invalid_field')
        assert not hasattr(listing, 'another_fake_field')
