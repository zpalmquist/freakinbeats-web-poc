"""
Unit tests for soft delete functionality in InventoryService.

This module tests the soft delete features including:
- Soft delete (mark as removed)
- Restore soft-deleted listings
- Mark as sold
- Filtering active listings
"""
import pytest
from datetime import datetime, timezone
from app.models.listing import Listing
from app.services.inventory_service import InventoryService


class TestSoftDelete:
    """Test soft delete functionality."""
    
    def test_soft_delete_marks_listing_inactive(self, app_context, db):
        """Test that soft delete marks a listing as inactive."""
        # Create a listing
        listing = Listing(
            listing_id='12345',
            release_id='100',
            artist_names='Test Artist',
            release_title='Test Album',
            price_value=10.0,
            is_active=True
        )
        db.session.add(listing)
        db.session.commit()
        
        # Soft delete the listing
        service = InventoryService()
        result = service.soft_delete('12345')
        
        assert result is True
        
        # Verify listing is marked inactive
        updated = Listing.query.filter_by(listing_id='12345').first()
        assert updated.is_active is False
        assert updated.removed_at is not None
        assert updated.sold_at is None
    
    def test_soft_delete_nonexistent_listing_returns_false(self, app_context, db):
        """Test that soft deleting a non-existent listing returns False."""
        service = InventoryService()
        result = service.soft_delete('nonexistent')
        
        assert result is False
    
    def test_restore_listing_reactivates(self, app_context, db):
        """Test that restore_listing reactivates a soft-deleted listing."""
        # Create a soft-deleted listing
        listing = Listing(
            listing_id='12345',
            release_id='100',
            artist_names='Test Artist',
            release_title='Test Album',
            price_value=10.0,
            is_active=False,
            removed_at=datetime.now(timezone.utc)
        )
        db.session.add(listing)
        db.session.commit()
        
        # Restore the listing
        service = InventoryService()
        result = service.restore_listing('12345')
        
        assert result is True
        
        # Verify listing is active again
        updated = Listing.query.filter_by(listing_id='12345').first()
        assert updated.is_active is True
        assert updated.removed_at is None
    
    def test_restore_listing_nonexistent_returns_false(self, app_context, db):
        """Test that restoring a non-existent listing returns False."""
        service = InventoryService()
        result = service.restore_listing('nonexistent')
        
        assert result is False
    
    def test_mark_as_sold(self, app_context, db):
        """Test that mark_as_sold marks a listing as sold."""
        # Create a listing
        listing = Listing(
            listing_id='12345',
            release_id='100',
            artist_names='Test Artist',
            release_title='Test Album',
            price_value=10.0,
            is_active=True
        )
        db.session.add(listing)
        db.session.commit()
        
        # Mark as sold
        service = InventoryService()
        result = service.mark_as_sold('12345')
        
        assert result is True
        
        # Verify listing is marked sold
        updated = Listing.query.filter_by(listing_id='12345').first()
        assert updated.is_active is False
        assert updated.sold_at is not None
        assert updated.removed_at is None
    
    def test_mark_as_sold_nonexistent_returns_false(self, app_context, db):
        """Test that marking non-existent listing as sold returns False."""
        service = InventoryService()
        result = service.mark_as_sold('nonexistent')
        
        assert result is False


class TestActiveListingFiltering:
    """Test that listing queries filter by is_active."""
    
    def test_get_all_items_excludes_inactive(self, app_context, db):
        """Test that get_all_items only returns active listings."""
        # Create active and inactive listings
        active = Listing(
            listing_id='active1',
            release_id='100',
            artist_names='Active Artist',
            release_title='Active Album',
            price_value=10.0,
            is_active=True
        )
        inactive = Listing(
            listing_id='inactive1',
            release_id='101',
            artist_names='Inactive Artist',
            release_title='Inactive Album',
            price_value=15.0,
            is_active=False
        )
        db.session.add_all([active, inactive])
        db.session.commit()
        
        service = InventoryService()
        items = service.get_all_items()
        
        assert len(items) == 1
        assert items[0]['listing_id'] == 'active1'
    
    def test_search_items_excludes_inactive(self, app_context, db):
        """Test that search_items only returns active listings."""
        # Create active and inactive listings
        active = Listing(
            listing_id='active1',
            release_id='100',
            artist_names='Test Artist',
            release_title='Test Album',
            price_value=10.0,
            is_active=True
        )
        inactive = Listing(
            listing_id='inactive1',
            release_id='101',
            artist_names='Test Artist',
            release_title='Test Album 2',
            price_value=15.0,
            is_active=False
        )
        db.session.add_all([active, inactive])
        db.session.commit()
        
        service = InventoryService()
        items = service.search_items(artist='Test Artist')
        
        assert len(items) == 1
        assert items[0]['listing_id'] == 'active1'
    
    def test_get_item_by_listing_id_returns_none_for_inactive(self, app_context, db):
        """Test that get_item_by_listing_id returns None for inactive listings."""
        # Create inactive listing
        inactive = Listing(
            listing_id='inactive1',
            release_id='101',
            artist_names='Test Artist',
            release_title='Test Album',
            price_value=15.0,
            is_active=False
        )
        db.session.add(inactive)
        db.session.commit()
        
        service = InventoryService()
        item = service.get_item_by_listing_id('inactive1')
        
        assert item is None
    
    def test_get_stats_counts_only_active(self, app_context, db):
        """Test that get_stats only counts active listings."""
        # Create active and inactive listings
        active1 = Listing(
            listing_id='active1',
            release_id='100',
            artist_names='Active Artist 1',
            release_title='Active Album 1',
            price_value=10.0,
            is_active=True
        )
        active2 = Listing(
            listing_id='active2',
            release_id='102',
            artist_names='Active Artist 2',
            release_title='Active Album 2',
            price_value=12.0,
            is_active=True
        )
        inactive = Listing(
            listing_id='inactive1',
            release_id='101',
            artist_names='Inactive Artist',
            release_title='Inactive Album',
            price_value=15.0,
            is_active=False
        )
        db.session.add_all([active1, active2, inactive])
        db.session.commit()
        
        service = InventoryService()
        stats = service.get_stats()
        
        assert stats['total_listings'] == 2


class TestListingDefaults:
    """Test default values for new listings."""
    
    def test_new_listing_is_active_by_default(self, app_context, db):
        """Test that new listings are active by default."""
        listing = Listing(
            listing_id='12345',
            release_id='100',
            artist_names='Test Artist',
            release_title='Test Album',
            price_value=10.0
        )
        db.session.add(listing)
        db.session.commit()
        
        assert listing.is_active is True
        assert listing.removed_at is None
        assert listing.sold_at is None
        assert listing.custom_metadata is None
    
    def test_custom_metadata_can_store_json(self, app_context, db):
        """Test that custom_metadata field can store JSON data."""
        metadata = {
            'location': 'CB1',
            'external_id': 'ext-12345',
            'custom_notes': 'Limited edition pressing'
        }
        
        listing = Listing(
            listing_id='12345',
            release_id='100',
            artist_names='Test Artist',
            release_title='Test Album',
            price_value=10.0,
            custom_metadata=metadata
        )
        db.session.add(listing)
        db.session.commit()
        
        # Retrieve and verify
        retrieved = Listing.query.filter_by(listing_id='12345').first()
        assert retrieved.custom_metadata == metadata
        assert retrieved.custom_metadata['location'] == 'CB1'


class TestToDict:
    """Test that to_dict includes new fields."""
    
    def test_to_dict_includes_soft_delete_fields(self, app_context, db):
        """Test that to_dict includes is_active, removed_at, sold_at."""
        listing = Listing(
            listing_id='12345',
            release_id='100',
            artist_names='Test Artist',
            release_title='Test Album',
            price_value=10.0,
            is_active=True,
            removed_at=None,
            sold_at=None,
            custom_metadata={'key': 'value'}
        )
        db.session.add(listing)
        db.session.commit()
        
        data = listing.to_dict()
        
        assert 'is_active' in data
        assert 'removed_at' in data
        assert 'sold_at' in data
        assert 'custom_metadata' in data
        assert data['is_active'] is True
        assert data['removed_at'] is None
        assert data['sold_at'] is None
        assert data['custom_metadata'] == {'key': 'value'}
