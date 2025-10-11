"""
Unit tests for DiscogsSyncService.

This module tests the Discogs API synchronization service, including:
- Fetching single pages from the API
- Fetching all listings across multiple pages
- Syncing listings with the database (add, update, remove)
- Error handling and rate limiting
"""

import pytest
import responses
import requests
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
        """Test successfully fetching a page of listings."""
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
        assert len(result['listings']) > 0
        assert result['pagination']['page'] == 1
    
    @responses.activate
    def test_fetch_page_with_params(self, sync_service, mock_listings_page):
        """Test that correct query parameters are sent."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        responses.add(
            responses.GET,
            url,
            json=mock_listings_page,
            status=200
        )
        
        sync_service._fetch_page(2)
        
        # Check the request was made with correct params
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert 'page=2' in request.url
        assert 'per_page=100' in request.url
        assert 'status=For+Sale' in request.url
        assert 'sort=listed' in request.url
    
    @responses.activate
    def test_fetch_page_401_authentication_error(self, sync_service):
        """Test handling of authentication error (401)."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        responses.add(
            responses.GET,
            url,
            json={'message': 'Invalid token'},
            status=401
        )
        
        result = sync_service._fetch_page(1)
        
        assert result is None
    
    @responses.activate
    def test_fetch_page_404_seller_not_found(self, sync_service):
        """Test handling of seller not found (404)."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        responses.add(
            responses.GET,
            url,
            json={'message': 'Seller not found'},
            status=404
        )
        
        result = sync_service._fetch_page(1)
        
        assert result is None
    
    @responses.activate
    @patch('time.sleep')
    def test_fetch_page_429_rate_limit_retry(self, mock_sleep, sync_service, mock_listings_page):
        """Test handling of rate limit (429) with retry."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # First request: rate limited
        # Second request: success
        responses.add(
            responses.GET,
            url,
            json={'message': 'Rate limit exceeded'},
            status=429
        )
        responses.add(
            responses.GET,
            url,
            json=mock_listings_page,
            status=200
        )
        
        result = sync_service._fetch_page(1)
        
        assert result is not None
        assert len(responses.calls) == 2
        mock_sleep.assert_any_call(60)  # Should wait 60 seconds
    
    @patch('requests.get')
    def test_fetch_page_network_error(self, mock_get, sync_service):
        """Test handling of network errors."""
        # Mock requests.get to raise a connection error
        mock_get.side_effect = requests.exceptions.ConnectionError('Network error')
        
        result = sync_service._fetch_page(1)
        
        assert result is None


class TestFetchAllListings:
    """Test the _fetch_all_listings method."""
    
    @responses.activate
    @patch('time.sleep')
    def test_fetch_all_listings_single_page(self, mock_sleep, sync_service, discogs_factory):
        """Test fetching all listings when there's only one page."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        page_data = discogs_factory.create_listings_page(
            page=1,
            per_page=100,
            total_items=50  # Less than one page
        )
        
        responses.add(
            responses.GET,
            url,
            json=page_data,
            status=200
        )
        
        result = sync_service._fetch_all_listings()
        
        assert len(result) == 50
        assert len(responses.calls) == 1
    
    @responses.activate
    @patch('time.sleep')
    def test_fetch_all_listings_multiple_pages(self, mock_sleep, sync_service, discogs_factory):
        """Test fetching all listings across multiple pages."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # Page 1: 100 listings
        page1 = discogs_factory.create_listings_page(page=1, per_page=100, total_items=250)
        # Page 2: 100 listings
        page2 = discogs_factory.create_listings_page(page=2, per_page=100, total_items=250)
        # Page 3: 50 listings
        page3 = discogs_factory.create_listings_page(page=3, per_page=100, total_items=250)
        
        responses.add(responses.GET, url, json=page1, status=200)
        responses.add(responses.GET, url, json=page2, status=200)
        responses.add(responses.GET, url, json=page3, status=200)
        
        result = sync_service._fetch_all_listings()
        
        assert len(result) == 250
        assert len(responses.calls) == 3
        # Verify rate limiting sleep was called between pages
        assert mock_sleep.call_count >= 2
    
    @responses.activate
    @patch('time.sleep')
    def test_fetch_all_listings_empty_response(self, mock_sleep, sync_service):
        """Test fetching when API returns no listings."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        responses.add(
            responses.GET,
            url,
            json={'pagination': {'page': 1, 'pages': 1}, 'listings': []},
            status=200
        )
        
        result = sync_service._fetch_all_listings()
        
        assert len(result) == 0
    
    @responses.activate
    def test_fetch_all_listings_page_error_stops_iteration(self, sync_service, discogs_factory):
        """Test that errors during page fetch stop the iteration."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # First page succeeds
        page1 = discogs_factory.create_listings_page(page=1, per_page=100, total_items=200)
        responses.add(responses.GET, url, json=page1, status=200)
        
        # Second page fails
        responses.add(responses.GET, url, json={'message': 'Error'}, status=500)
        
        result = sync_service._fetch_all_listings()
        
        # Should only get listings from first page
        assert len(result) == 100


class TestSyncAllListings:
    """Test the sync_all_listings method."""
    
    @responses.activate
    @patch('time.sleep')
    def test_sync_adds_new_listings(self, mock_sleep, sync_service, db, discogs_factory):
        """Test syncing when all listings are new."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # Create 5 new listings
        page_data = discogs_factory.create_listings_page(
            page=1,
            per_page=100,
            total_items=5
        )
        
        responses.add(responses.GET, url, json=page_data, status=200)
        
        # Database should be empty
        assert Listing.query.count() == 0
        
        stats = sync_service.sync_all_listings()
        
        assert stats['added'] == 5
        assert stats['updated'] == 0
        assert stats['removed'] == 0
        assert stats['total'] == 5
        assert Listing.query.count() == 5
    
    @responses.activate
    @patch('time.sleep')
    def test_sync_updates_existing_listings(self, mock_sleep, sync_service, db, discogs_factory):
        """Test syncing when listings already exist and need updating."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # Create an existing listing in the database
        existing_listing = Listing(
            listing_id='123456',
            price_value=10.0,
            release_title='Old Title'
        )
        db.session.add(existing_listing)
        db.session.commit()
        
        # API returns the same listing with updated info
        api_listing = discogs_factory.create_listing(
            id=123456,
            price_value=15.0
        )
        api_listing['release']['title'] = 'New Title'
        
        page_data = {
            'pagination': {'page': 1, 'pages': 1},
            'listings': [api_listing]
        }
        
        responses.add(responses.GET, url, json=page_data, status=200)
        
        stats = sync_service.sync_all_listings()
        
        assert stats['added'] == 0
        assert stats['updated'] == 1
        assert stats['removed'] == 0
        assert Listing.query.count() == 1
        
        # Check that the listing was updated
        updated = Listing.query.filter_by(listing_id='123456').first()
        assert updated.price_value == 15.0
        assert updated.release_title == 'New Title'
    
    @responses.activate
    @patch('time.sleep')
    def test_sync_removes_delisted_items(self, mock_sleep, sync_service, db, discogs_factory):
        """Test syncing removes listings that are no longer in API response."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # Create two listings in the database
        listing1 = Listing(listing_id='111111', price_value=10.0)
        listing2 = Listing(listing_id='222222', price_value=20.0)
        db.session.add_all([listing1, listing2])
        db.session.commit()
        
        # API only returns listing1
        api_listing = discogs_factory.create_listing(id=111111)
        page_data = {
            'pagination': {'page': 1, 'pages': 1},
            'listings': [api_listing]
        }
        
        responses.add(responses.GET, url, json=page_data, status=200)
        
        stats = sync_service.sync_all_listings()
        
        assert stats['added'] == 0
        assert stats['updated'] == 1
        assert stats['removed'] == 1
        assert Listing.query.count() == 1
        
        # Verify listing2 was removed
        assert Listing.query.filter_by(listing_id='222222').first() is None
        assert Listing.query.filter_by(listing_id='111111').first() is not None
    
    @responses.activate
    @patch('time.sleep')
    def test_sync_mixed_operations(self, mock_sleep, sync_service, db, discogs_factory):
        """Test syncing with add, update, and remove operations."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # Database has 2 listings
        existing1 = Listing(listing_id='111111', price_value=10.0)  # Will be updated
        existing2 = Listing(listing_id='222222', price_value=20.0)  # Will be removed
        db.session.add_all([existing1, existing2])
        db.session.commit()
        
        # API returns: updated listing1 + new listing3
        api_listing1 = discogs_factory.create_listing(id=111111, price_value=15.0)
        api_listing3 = discogs_factory.create_listing(id=333333, price_value=30.0)
        
        page_data = {
            'pagination': {'page': 1, 'pages': 1},
            'listings': [api_listing1, api_listing3]
        }
        
        responses.add(responses.GET, url, json=page_data, status=200)
        
        stats = sync_service.sync_all_listings()
        
        assert stats['added'] == 1  # listing3
        assert stats['updated'] == 1  # listing1
        assert stats['removed'] == 1  # listing2
        assert stats['total'] == 2
        assert Listing.query.count() == 2
    
    @responses.activate
    def test_sync_no_listings_from_api(self, sync_service, db):
        """Test syncing when API returns no listings."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        responses.add(
            responses.GET,
            url,
            json={'message': 'Error'},
            status=500
        )
        
        stats = sync_service.sync_all_listings()
        
        assert stats['added'] == 0
        assert stats['updated'] == 0
        assert stats['removed'] == 0
        assert stats['total'] == 0
    
    @responses.activate
    @patch('time.sleep')
    def test_sync_skips_listings_without_id(self, mock_sleep, sync_service, db, discogs_factory):
        """Test that listings without IDs are skipped."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        # Create a listing with missing 'id' field entirely
        bad_listing = discogs_factory.create_listing()
        del bad_listing['id']  # Remove the ID field entirely
        
        good_listing = discogs_factory.create_listing(id=123456)
        
        page_data = {
            'pagination': {'page': 1, 'pages': 1},
            'listings': [bad_listing, good_listing]
        }
        
        responses.add(responses.GET, url, json=page_data, status=200)
        
        stats = sync_service.sync_all_listings()
        
        # Only the good listing should be added
        assert stats['added'] == 1
        assert Listing.query.count() == 1
    
    @responses.activate
    @patch('time.sleep')
    def test_sync_database_rollback_on_error(self, mock_sleep, sync_service, db, discogs_factory):
        """Test that database changes are rolled back on error."""
        url = f"{sync_service.base_url}/users/{sync_service.seller_username}/inventory"
        
        page_data = discogs_factory.create_listings_page(page=1, per_page=100, total_items=5)
        responses.add(responses.GET, url, json=page_data, status=200)
        
        # Mock db.session.commit to raise an exception
        with patch.object(db.session, 'commit', side_effect=Exception('DB Error')):
            with pytest.raises(Exception, match='DB Error'):
                sync_service.sync_all_listings()
        
        # Verify rollback was called
        assert Listing.query.count() == 0


class TestFlattenListing:
    """Test the _flatten_listing method."""
    
    def test_flatten_basic_fields(self, sync_service, mock_listing):
        """Test flattening basic listing fields."""
        result = sync_service._flatten_listing(mock_listing)
        
        assert result['listing_id'] == str(mock_listing['id'])
        assert result['status'] == mock_listing['status']
        assert result['condition'] == mock_listing['condition']
        assert result['sleeve_condition'] == mock_listing['sleeve_condition']
    
    def test_flatten_price_fields(self, sync_service, mock_listing):
        """Test flattening price information."""
        result = sync_service._flatten_listing(mock_listing)
        
        assert result['price_value'] == mock_listing['price']['value']
        assert result['price_currency'] == mock_listing['price']['currency']
        assert result['shipping_price'] == mock_listing['shipping']['price']
        assert result['shipping_currency'] == mock_listing['shipping']['currency']
    
    def test_flatten_release_fields(self, sync_service, mock_listing):
        """Test flattening release information."""
        result = sync_service._flatten_listing(mock_listing)
        
        release = mock_listing['release']
        assert result['release_id'] == str(release['id'])
        assert result['release_title'] == release['title']
        assert result['release_year'] == str(release['year'])
    
    def test_flatten_artist_fields(self, sync_service, mock_listing):
        """Test flattening artist information."""
        result = sync_service._flatten_listing(mock_listing)
        
        assert result['artist_names'] is not None
        assert result['primary_artist'] is not None
        assert len(result['primary_artist']) > 0
    
    def test_flatten_with_missing_fields(self, sync_service, discogs_factory):
        """Test flattening handles missing optional fields."""
        # Create a minimal listing
        minimal_listing = {
            'id': 123456,
            'status': 'For Sale',
            'condition': 'VG',
            'price': {'value': 10.0, 'currency': 'USD'},
            'shipping': {'price': 3.0, 'currency': 'USD'},
            'release': {
                'id': 789,
                'title': 'Test Album'
            }
        }
        
        result = sync_service._flatten_listing(minimal_listing)
        
        assert result['listing_id'] == '123456'
        assert result['artist_names'] == ''
        assert result['genres'] == ''
        assert result['styles'] == ''
    
    @freeze_time("2024-01-15 12:00:00")
    def test_flatten_adds_timestamp(self, sync_service, mock_listing):
        """Test that flattening adds export timestamp."""
        result = sync_service._flatten_listing(mock_listing)
        
        assert 'export_timestamp' in result
        assert '2024-01-15' in result['export_timestamp']


class TestUpdateListingFromDict:
    """Test the _update_listing_from_dict method."""
    
    def test_update_existing_fields(self, sync_service, db):
        """Test updating existing listing fields."""
        listing = Listing(
            listing_id='123456',
            price_value=10.0,
            release_title='Old Title'
        )
        db.session.add(listing)
        db.session.commit()
        
        update_data = {
            'price_value': 15.0,
            'release_title': 'New Title',
            'condition': 'Mint (M)'
        }
        
        sync_service._update_listing_from_dict(listing, update_data)
        
        assert listing.price_value == 15.0
        assert listing.release_title == 'New Title'
        assert listing.condition == 'Mint (M)'
    
    def test_update_ignores_invalid_fields(self, sync_service, db):
        """Test that invalid field names are ignored."""
        listing = Listing(listing_id='123456', price_value=10.0)
        db.session.add(listing)
        db.session.commit()
        
        update_data = {
            'price_value': 15.0,
            'invalid_field': 'should be ignored',
            'another_fake_field': 123
        }
        
        # Should not raise an error
        sync_service._update_listing_from_dict(listing, update_data)
        
        assert listing.price_value == 15.0
        assert not hasattr(listing, 'invalid_field')
