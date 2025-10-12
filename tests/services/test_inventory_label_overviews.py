"""
Unit tests for InventoryService label overview features.

This module tests the label overview and caching functionality in InventoryService:
- Label overview fetching with cache checks
- AI overview generation integration
- Database caching of generated overviews
- Multi-label support with deduplication
"""

import pytest
from unittest.mock import Mock, patch, call
from datetime import datetime

from app.services.inventory_service import InventoryService
from app.models.listing import Listing
from app.models.label_info import LabelInfo
from app.extensions import db


class TestGenerateLabelUrls:
    """Test the _generate_label_urls method."""
    
    def test_single_label_generates_three_urls(self, app_context):
        """Test that single label generates 3 URLs."""
        service = InventoryService()
        urls = service._generate_label_urls("Blue Note Records", "Blue Note Records")
        
        assert len(urls) == 3
        assert any('Discogs' in url['title'] for url in urls)
        assert any('Bandcamp' in url['title'] for url in urls)
        assert any('Google' in url['title'] for url in urls)
    
    def test_multiple_labels_generate_multiple_urls(self, app_context):
        """Test that multiple labels generate URLs for each."""
        service = InventoryService()
        urls = service._generate_label_urls("Label A, Label B", "Label A")
        
        # 2 labels × 3 URLs each = 6 total
        assert len(urls) == 6
        
        # Check that both labels are present
        titles = [url['title'] for url in urls]
        assert any('Label A' in title for title in titles)
        assert any('Label B' in title for title in titles)
    
    def test_duplicate_labels_deduplicated(self, app_context):
        """Test that duplicate labels are deduplicated."""
        service = InventoryService()
        urls = service._generate_label_urls("Label A, Label B, Label A", "Label A")
        
        # Should only generate 6 URLs (2 unique labels), not 9
        assert len(urls) == 6
    
    def test_empty_label_returns_empty_list(self, app_context):
        """Test that empty label returns empty list."""
        service = InventoryService()
        
        urls1 = service._generate_label_urls("", "")
        urls2 = service._generate_label_urls("Unknown", "Unknown")
        urls3 = service._generate_label_urls(None, None)
        
        assert urls1 == []
        assert urls2 == []
        assert urls3 == []
    
    def test_url_encoding_special_characters(self, app_context):
        """Test that special characters in labels are properly encoded."""
        service = InventoryService()
        urls = service._generate_label_urls("Label & Records", "Label & Records")
        
        # Check that URLs are properly encoded
        for url_info in urls:
            if 'Discogs' in url_info['title']:
                assert 'Label%20%26%20Records' in url_info['url'] or 'Label+%26+Records' in url_info['url']
    
    def test_bandcamp_uses_plus_encoding(self, app_context):
        """Test that Bandcamp URLs use + for spaces."""
        service = InventoryService()
        urls = service._generate_label_urls("Test Label", "Test Label")
        
        bandcamp_url = [url for url in urls if 'Bandcamp' in url['title']][0]
        assert 'Test+Label' in bandcamp_url['url']
        assert 'item_type=b' in bandcamp_url['url']
    
    def test_single_label_no_prefix(self, app_context):
        """Test that single labels don't have name prefix in title."""
        service = InventoryService()
        urls = service._generate_label_urls("Single Label", "Single Label")
        
        # Titles should not include label name prefix
        for url_info in urls:
            assert not url_info['title'].startswith("Single Label -")
    
    def test_multiple_labels_have_prefix(self, app_context):
        """Test that multiple labels have name prefix in title."""
        service = InventoryService()
        urls = service._generate_label_urls("Label A, Label B", "Label A")
        
        # Titles should include label name prefix
        label_a_urls = [url for url in urls if 'Label A' in url['title']]
        assert len(label_a_urls) == 3
        assert all(url['title'].startswith("Label A -") for url in label_a_urls)


class TestGetLabelOverviews:
    """Test the _get_label_overviews method."""
    
    def test_returns_empty_for_no_labels(self, app_context):
        """Test returns empty dict when no labels provided."""
        service = InventoryService()
        
        result1 = service._get_label_overviews("")
        result2 = service._get_label_overviews("Unknown")
        result3 = service._get_label_overviews(None)
        
        assert result1 == {}
        assert result2 == {}
        assert result3 == {}
    
    def test_returns_empty_when_disabled(self, app_context):
        """Test returns empty dict when AI overviews are disabled."""
        app_context.config['ENABLE_AI_OVERVIEWS'] = False
        
        service = InventoryService()
        result = service._get_label_overviews("Test Label")
        
        assert result == {}
    
    def test_uses_cached_overview_when_available(self, app_context, db, session):
        """Test that cached overviews are used instead of generating new ones."""
        app_context.config['ENABLE_AI_OVERVIEWS'] = True
        
        # Create cached label info
        cached_info = LabelInfo(
            label_name="Cached Label Unique1",
            overview="This is a cached overview",
            cache_valid=True
        )
        session.add(cached_info)
        session.commit()
        
        service = InventoryService()
        result = service._get_label_overviews("Cached Label Unique1")
        assert true = false;
        assert result == {"Cached Label Unique1": "This is a cached overview"}
    
    def test_ignores_invalid_cache(self, app_context, db, session):
        """Test that invalid cache entries are not used."""
        app_context.config['ENABLE_AI_OVERVIEWS'] = True
        app_context.config['GEMINI_API_KEY'] = None  # Disable Gemini
        
        # Create invalid cached label info
        cached_info = LabelInfo(
            label_name="Invalid Cache Unique",
            overview="Old overview",
            cache_valid=False  # Invalid
        )
        session.add(cached_info)
        session.commit()
        
        service = InventoryService()
        result = service._get_label_overviews("Invalid Cache Unique")
        
        # Should return empty when cache is invalid and Gemini unavailable
        assert result == {}
    
    def test_generates_for_uncached_labels(self, app_context, db):
        """Test that uncached labels return empty when Gemini is not configured."""
        app_context.config['ENABLE_AI_OVERVIEWS'] = True
        app_context.config['GEMINI_API_KEY'] = None  # No API key
        
        service = InventoryService()
        result = service._get_label_overviews("New Label")
        
        # Without API key, should return empty
        assert result == {}
    
    def test_handles_multiple_labels(self, app_context, db, session):
        """Test handling multiple comma-separated labels from cache."""
        app_context.config['ENABLE_AI_OVERVIEWS'] = True
        
        # Cache two labels
        for i, label in enumerate(["Cached Label Multi 1", "Cached Label Multi 2"]):
            cached_info = LabelInfo(
                label_name=label,
                overview=f"Cached overview {i}",
                cache_valid=True
            )
            session.add(cached_info)
        session.commit()
        
        service = InventoryService()
        result = service._get_label_overviews("Cached Label Multi 1, Cached Label Multi 2")
        
        # Should retrieve both from cache
        assert len(result) == 2
        assert result["Cached Label Multi 1"] == "Cached overview 0"
        assert result["Cached Label Multi 2"] == "Cached overview 1"
    
    def test_deduplicates_labels(self, app_context, db, session):
        """Test that duplicate labels in list are deduplicated."""
        app_context.config['ENABLE_AI_OVERVIEWS'] = True
        
        # Cache two unique labels
        for label in ["Dedup Label A", "Dedup Label B"]:
            cached_info = LabelInfo(
                label_name=label,
                overview=f"Overview for {label}",
                cache_valid=True
            )
            session.add(cached_info)
        session.commit()
        
        service = InventoryService()
        result = service._get_label_overviews("Dedup Label A, Dedup Label B, Dedup Label A")
        
        # Should only have 2 unique labels (A is duplicated)
        assert len(result) == 2
        assert "Dedup Label A" in result
        assert "Dedup Label B" in result
    
    def test_handles_gemini_not_available(self, app_context, db):
        """Test graceful handling when Gemini is not available."""
        app_context.config['ENABLE_AI_OVERVIEWS'] = True
        
        with patch('app.services.gemini_service.GeminiService') as mock_gemini_class:
            mock_gemini = Mock()
            mock_gemini.is_available.return_value = False
            mock_gemini_class.return_value = mock_gemini
            
            service = InventoryService()
            result = service._get_label_overviews("Test Label Not Available")
            
            # Should return empty dict, not crash
            assert result == {}
    
    def test_handles_generation_failure(self, app_context, db):
        """Test handling when AI generation fails."""
        app_context.config['ENABLE_AI_OVERVIEWS'] = True
        
        with patch('app.services.gemini_service.GeminiService') as mock_gemini_class:
            mock_gemini = Mock()
            mock_gemini.is_available.return_value = True
            mock_gemini.generate_label_overview.return_value = None  # Failed
            mock_gemini_class.return_value = mock_gemini
            
            service = InventoryService()
            result = service._get_label_overviews("Test Label Failure")
            
            # Should handle gracefully
            assert result == {}


class TestCacheLabelOverview:
    """Test the _cache_label_overview method."""
    
    def test_caches_new_overview(self, app_context, db):
        """Test caching a new label overview."""
        service = InventoryService()
        service._cache_label_overview("New Label Unique Cache", "Test overview")
        
        # Verify it was saved to database
        cached = LabelInfo.query.filter_by(label_name="New Label Unique Cache").first()
        assert cached is not None
        assert cached.overview == "Test overview"
        assert cached.cache_valid is True
        assert cached.generated_by == "gemini-1.5-flash"
    
    def test_updates_existing_overview(self, app_context, db, session):
        """Test updating an existing cached overview."""
        # Create initial cache
        old_info = LabelInfo(
            label_name="Update Label Unique",
            overview="Old overview",
            cache_valid=False
        )
        session.add(old_info)
        session.commit()
        old_id = old_info.id
        
        # Update with new overview
        service = InventoryService()
        service._cache_label_overview("Update Label Unique", "New overview")
        
        # Verify update
        updated = LabelInfo.query.filter_by(id=old_id).first()
        assert updated.overview == "New overview"
        assert updated.cache_valid is True
        assert updated.generation_error is None
    
    def test_cache_handles_special_characters(self, app_context, db):
        """Test caching labels with special characters."""
        service = InventoryService()
        
        special_labels = [
            "Label & Records Unique",
            "Label's Music Unique",
            "Label (Europe) Unique",
            "Label/Sublabel Unique"
        ]
        
        for label in special_labels:
            service._cache_label_overview(label, f"Overview for {label}")
            cached = LabelInfo.query.filter_by(label_name=label).first()
            assert cached is not None
            assert cached.overview == f"Overview for {label}"
    
    @patch('app.services.inventory_service.current_app')
    @patch('app.services.inventory_service.db.session')
    def test_cache_handles_database_error(self, mock_session, mock_app, app_context):
        """Test that caching handles database errors gracefully."""
        mock_session.commit.side_effect = Exception("Database error")
        
        service = InventoryService()
        
        # Should not raise exception
        try:
            service._cache_label_overview("Test Label", "Overview")
        except Exception:
            pytest.fail("Should handle database errors gracefully")
        
        mock_session.rollback.assert_called()


class TestGetItemWithVideosAndOverviews:
    """Test that get_item_with_videos_by_id includes label overviews."""
    
    def test_includes_label_overviews_in_response(self, app_context, db, session):
        """Test that detail response includes label_overviews."""
        listing = Listing(
            listing_id='overview_test_unique',
            label_names='Overview Test Label',
            primary_label='Overview Test Label',
            release_id='12345',
            release_title='Test Album',
            artist_names='Test Artist',
            price_value=15.99,
            condition='Near Mint (NM)',
            status='For Sale'
        )
        session.add(listing)
        session.commit()
        
        with patch.object(InventoryService, '_get_label_overviews') as mock_get_overviews:
            mock_get_overviews.return_value = {"Test Label": "Test overview"}
            
            service = InventoryService()
            result = service.get_item_with_videos_by_id(listing.id)
            
            assert result is not None
            assert 'label_overviews' in result
            assert result['label_overviews'] == {"Test Label": "Test overview"}
    
    def test_includes_label_urls_in_response(self, app_context, db, session):
        """Test that detail response includes label_urls."""
        listing = Listing(
            listing_id='urls_test_456_unique',
            label_names='URL Test Label',
            primary_label='URL Test Label',
            release_id='12345',
            release_title='URL Test Album',
            artist_names='Test Artist',
            price_value=15.99,
            condition='Near Mint (NM)',
            status='For Sale'
        )
        session.add(listing)
        session.commit()
        
        service = InventoryService()
        result = service.get_item_with_videos_by_id(listing.id)
        
        assert result is not None
        assert 'label_urls' in result
        assert isinstance(result['label_urls'], list)


class TestLabelOverviewIntegration:
    """Integration tests for complete label overview workflow."""
    
    def test_complete_workflow_with_cache(self, app_context, db, session):
        """Test complete workflow: generate, cache, retrieve."""
        listing = Listing(
            listing_id='workflow_test_789_unique',
            label_names='Workflow Test Label',
            primary_label='Workflow Test Label',
            release_id='12345',
            release_title='Workflow Test Album',
            artist_names='Test Artist',
            price_value=15.99,
            condition='Near Mint (NM)',
            status='For Sale'
        )
        session.add(listing)
        session.commit()
        
        with patch('app.services.gemini_service.GeminiService') as mock_gemini_class:
            mock_gemini = Mock()
            mock_gemini.is_available.return_value = True
            mock_gemini.generate_label_overview.return_value = "AI generated overview"
            mock_gemini_class.return_value = mock_gemini
            
            service = InventoryService()
            
            # First call - should generate and cache
            result1 = service.get_item_with_videos_by_id(listing.id)
            assert result1['label_overviews'] == {"Workflow Test Label": "AI generated overview"}
            
            # Verify cached in database
            cached = LabelInfo.query.filter_by(label_name="Workflow Test Label").first()
            assert cached is not None
            assert cached.overview == "AI generated overview"
            
            # Second call - should use cache
            result2 = service.get_item_with_videos_by_id(listing.id)
            assert result2['label_overviews'] == {"Workflow Test Label": "AI generated overview"}
            
            # AI should only be called once (cached on second call)
            assert mock_gemini.generate_label_overview.call_count == 1
    
    def test_multi_label_listing(self, app_context, db, session):
        """Test listing with multiple labels."""
        listing = Listing(
            listing_id='multi123_unique',
            label_names='Label A, Label B, Label C',
            primary_label='Label A',
            release_id='12345',
            release_title='Test Release',
            artist_names='Test Artist',
            price_value=10.0
        )
        session.add(listing)
        session.commit()
        
        with patch('app.services.gemini_service.GeminiService') as mock_gemini_class:
            mock_gemini = Mock()
            mock_gemini.is_available.return_value = True
            
            # Return different overviews based on label name
            def mock_generate(label_name):
                if label_name == "Label A":
                    return "Overview for Label A"
                elif label_name == "Label B":
                    return "Overview for Label B"
                elif label_name == "Label C":
                    return "Overview for Label C"
                return f"Overview for {label_name}"
            
            mock_gemini.generate_label_overview.side_effect = mock_generate
            mock_gemini_class.return_value = mock_gemini
            
            service = InventoryService()
            result = service.get_item_with_videos_by_id(listing.id)
            
            # Should have overviews for all 3 labels
            assert len(result['label_overviews']) == 3
            assert result['label_overviews']['Label A'] == "Overview for Label A"
            assert result['label_overviews']['Label B'] == "Overview for Label B"
            assert result['label_overviews']['Label C'] == "Overview for Label C"
            
            # Should have 9 URLs (3 labels × 3 URLs)
            assert len(result['label_urls']) == 9


# Fixtures specific to this test module
@pytest.fixture
def sample_listing():
    """Create a sample listing for testing."""
    return Listing(
        listing_id='test123',
        label_names='Test Label',
        primary_label='Test Label',
        release_id='12345',
        release_title='Test Album',
        artist_names='Test Artist',
        primary_artist='Test Artist',
        price_value=15.99,
        condition='Near Mint (NM)',
        sleeve_condition='Very Good Plus (VG+)',
        status='For Sale'
    )


@pytest.fixture
def multi_label_listing():
    """Create a listing with multiple labels for testing."""
    return Listing(
        listing_id='multi456',
        label_names='Blue Note, Atlantic Records, Motown',
        primary_label='Blue Note',
        release_id='67890',
        release_title='Multi Label Album',
        artist_names='Various Artists',
        price_value=25.00,
        condition='Mint (M)',
        status='For Sale'
    )

