"""
Pytest configuration and shared fixtures.

This module provides reusable fixtures for testing the Freakinbeats application,
including Flask app context, database setup, and mock Discogs API utilities.
"""

import pytest
from app import create_app
from app.extensions import db as _db
from tests.fixtures.discogs_factory import DiscogsDataFactory


@pytest.fixture(scope='session')
def app():
    """
    Create and configure a Flask application for testing.
    
    This fixture creates a Flask app instance with test configuration
    and yields it for use in tests.
    """
    import os
    # Set environment variables before creating app
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    os.environ['ENABLE_AUTO_SYNC'] = 'false'
    os.environ['DISCOGS_TOKEN'] = 'test_token_12345'
    os.environ['DISCOGS_SELLER_USERNAME'] = 'test_seller'
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'ENABLE_AUTO_SYNC': False,  # Disable scheduler in tests
        'DISCOGS_TOKEN': 'test_token_12345',
        'DISCOGS_SELLER_USERNAME': 'test_seller',
        'DISCOGS_USER_AGENT': 'FreakinBeatsTest/1.0'
    })
    
    yield app


@pytest.fixture(scope='function')
def app_context(app):
    """
    Provide an application context for tests.
    
    This fixture pushes an app context and pops it after the test.
    """
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db(app_context):
    """
    Provide a clean database for each test.
    
    This fixture creates all tables before the test and drops them after.
    Each test gets a fresh database state.
    """
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """
    Provide a database session for tests.
    
    This fixture provides access to the database session and ensures
    proper cleanup after each test.
    """
    yield db.session
    db.session.rollback()


@pytest.fixture
def discogs_factory():
    """
    Provide a DiscogsDataFactory instance for generating mock data.
    
    Returns:
        DiscogsDataFactory: Factory for creating mock Discogs API responses
    """
    return DiscogsDataFactory(seed=42)


@pytest.fixture
def mock_listing(discogs_factory):
    """
    Provide a single mock Discogs listing.
    
    Returns:
        Dict: A mock listing dictionary
    """
    return discogs_factory.create_listing()


@pytest.fixture
def mock_listings(discogs_factory):
    """
    Provide multiple mock Discogs listings.
    
    Returns:
        List[Dict]: List of mock listing dictionaries
    """
    return discogs_factory.create_bulk_listings(count=10)


@pytest.fixture
def mock_listings_page(discogs_factory):
    """
    Provide a paginated response of mock listings.
    
    Returns:
        Dict: A mock paginated API response
    """
    return discogs_factory.create_listings_page(page=1, per_page=100, total_items=250)


@pytest.fixture
def sync_service(app_context):
    """
    Provide a DiscogsSyncService instance for testing.
    
    Returns:
        DiscogsSyncService: Configured sync service instance
    """
    from app.services.discogs_sync_service import DiscogsSyncService
    from flask import current_app
    
    return DiscogsSyncService(
        token=current_app.config['DISCOGS_TOKEN'],
        seller_username=current_app.config['DISCOGS_SELLER_USERNAME'],
        user_agent=current_app.config['DISCOGS_USER_AGENT']
    )
