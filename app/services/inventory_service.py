"""
Inventory service for managing Discogs listings.

This service provides methods to query and retrieve listings from the database.
"""

from datetime import datetime
from typing import List, Optional
from app.models.listing import Listing


class InventoryService:
    """Service for accessing inventory listings from database."""
    
    def get_all_items(self) -> List[dict]:
        """
        Get all listings from database, sorted by posted date (newest first).
        
        Returns:
            List of listing dictionaries
        """
        listings = Listing.query.order_by(Listing.posted.desc()).all()
        return [listing.to_dict() for listing in listings]
    
    def get_item_by_listing_id(self, listing_id: str) -> Optional[dict]:
        """
        Get a single listing by its listing ID.
        
        Args:
            listing_id: The Discogs listing ID
            
        Returns:
            Listing dictionary or None if not found
        """
        listing = Listing.query.filter_by(listing_id=listing_id).first()
        return listing.to_dict() if listing else None
    
    def search_items(self, query: str = None, artist: str = None, 
                    genre: str = None, format_type: str = None) -> List[dict]:
        """
        Search listings with optional filters.
        
        Args:
            query: Search query for title or artist
            artist: Filter by artist name
            genre: Filter by genre
            format_type: Filter by format
            
        Returns:
            List of matching listing dictionaries
        """
        q = Listing.query
        
        if query:
            q = q.filter(
                (Listing.release_title.ilike(f'%{query}%')) |
                (Listing.artist_names.ilike(f'%{query}%'))
            )
        
        if artist:
            q = q.filter(Listing.artist_names.ilike(f'%{artist}%'))
        
        if genre:
            q = q.filter(Listing.genres.ilike(f'%{genre}%'))
        
        if format_type:
            q = q.filter(Listing.format_names.ilike(f'%{format_type}%'))
        
        listings = q.order_by(Listing.posted.desc()).all()
        return [listing.to_dict() for listing in listings]
    
    def get_stats(self) -> dict:
        """
        Get inventory statistics.
        
        Returns:
            Dictionary with inventory statistics
        """
        total = Listing.query.count()
        
        return {
            'total_listings': total,
            'last_updated': Listing.query.order_by(
                Listing.updated_at.desc()
            ).first().updated_at.isoformat() if total > 0 else None
        }
