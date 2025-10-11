"""
Inventory service for managing Discogs listings.

This service provides methods to query and retrieve listings from the database.
"""

import requests
from datetime import datetime
from typing import List, Optional, Dict
from flask import current_app
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
        Get a single listing by its Discogs listing ID.
        
        Args:
            listing_id: The Discogs listing ID
            
        Returns:
            Listing dictionary or None if not found
        """
        listing = Listing.query.filter_by(listing_id=listing_id).first()
        return listing.to_dict() if listing else None
    
    def get_item_by_id(self, id: int) -> Optional[dict]:
        """
        Get a single listing by its database ID.
        
        Args:
            id: The database ID
            
        Returns:
            Listing dictionary or None if not found
        """
        listing = Listing.query.get(id)
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

    def get_item_with_videos(self, listing_id: str) -> Optional[Dict]:
        """
        Get a listing with detailed release information including videos by Discogs listing ID.
        
        Args:
            listing_id: The Discogs listing ID
            
        Returns:
            Dictionary with listing data and videos, or None if not found
        """
        listing = Listing.query.filter_by(listing_id=listing_id).first()
        if not listing:
            return None
            
        # Start with basic listing data
        result = listing.to_dict()
        
        # Fetch release details from Discogs API if we have a release_id
        if listing.release_id:
            videos = self._fetch_release_videos(listing.release_id)
            result['videos'] = videos
        else:
            result['videos'] = []
            
        return result
    
    def get_item_with_videos_by_id(self, id: int) -> Optional[Dict]:
        """
        Get a listing with detailed release information including videos by database ID.
        
        Args:
            id: The database ID
            
        Returns:
            Dictionary with listing data and videos, or None if not found
        """
        listing = Listing.query.get(id)
        if not listing:
            return None
            
        # Start with basic listing data
        result = listing.to_dict()
        
        # Fetch release details from Discogs API if we have a release_id
        if listing.release_id:
            videos = self._fetch_release_videos(listing.release_id)
            result['videos'] = videos
        else:
            result['videos'] = []
            
        return result
    
    def _fetch_release_videos(self, release_id: str) -> List[Dict]:
        """
        Fetch video information for a release from Discogs API.
        
        Args:
            release_id: The Discogs release ID
            
        Returns:
            List of video dictionaries
        """
        headers = {
            'User-Agent': current_app.config.get('DISCOGS_USER_AGENT', 'FreakinbeatsWebApp/1.0'),
        }
        
        # Add token if available (for better rate limits)
        token = current_app.config.get('DISCOGS_TOKEN')
        if token:
            headers['Authorization'] = f'Discogs token={token}'
        
        try:
            url = f'https://api.discogs.com/releases/{release_id}'
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get('videos', [])
                
                # Process videos to extract YouTube ID and add thumbnail
                processed_videos = []
                for video in videos:
                    uri = video.get('uri', '')
                    if 'youtube.com/watch?v=' in uri:
                        # Extract YouTube ID
                        youtube_id = uri.split('watch?v=')[1].split('&')[0]
                        processed_video = {
                            'title': video.get('title', ''),
                            'description': video.get('description', ''),
                            'duration': video.get('duration', 0),
                            'embed': video.get('embed', False),
                            'uri': uri,
                            'youtube_id': youtube_id,
                            'thumbnail': f'https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg'
                        }
                        processed_videos.append(processed_video)
                
                return processed_videos
            else:
                current_app.logger.warning(f'Failed to fetch release {release_id}: {response.status_code}')
                return []
                
        except Exception as e:
            current_app.logger.error(f'Error fetching videos for release {release_id}: {e}')
            return []
