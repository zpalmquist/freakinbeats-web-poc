"""
Inventory service for managing Discogs listings.

This service provides methods to query and retrieve listings from the database.
"""

import requests
from datetime import datetime, timezone
from typing import List, Optional, Dict
from flask import current_app
from app.models.listing import Listing
from app.models.label_info import LabelInfo
from app.extensions import db


class InventoryService:
    """Service for accessing inventory listings from database."""
    
    def get_all_items(self) -> List[dict]:
        """
        Get all active listings from database, sorted by posted date (newest first).
        
        Returns:
            List of listing dictionaries
        """
        listings = Listing.query.filter_by(is_active=True).order_by(Listing.posted.desc()).all()
        return [listing.to_dict() for listing in listings]
    
    def get_item_by_listing_id(self, listing_id: str) -> Optional[dict]:
        """
        Get a single active listing by its Discogs listing ID.
        
        Args:
            listing_id: The Discogs listing ID
            
        Returns:
            Listing dictionary or None if not found or inactive
        """
        listing = Listing.query.filter_by(listing_id=listing_id, is_active=True).first()
        return listing.to_dict() if listing else None
    
    def get_item_by_id(self, id: int) -> Optional[dict]:
        """
        Get a single active listing by its database ID.
        
        Args:
            id: The database ID
            
        Returns:
            Listing dictionary or None if not found or inactive
        """
        listing = Listing.query.filter_by(id=id, is_active=True).first()
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
        q = Listing.query.filter_by(is_active=True)
        
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
        total = Listing.query.filter_by(is_active=True).count()
        
        return {
            'total_listings': total,
            'last_updated': Listing.query.filter_by(is_active=True).order_by(
                Listing.updated_at.desc()
            ).first().updated_at.isoformat() if total > 0 else None
        }
    
    def get_filter_facets(self) -> dict:
        """
        Get all unique values for filterable fields with counts.
        
        Returns:
            Dictionary with filter facets and their counts
        """
        from sqlalchemy import func
        
        # Get unique artists with counts
        artists = Listing.query.filter_by(is_active=True).with_entities(
            Listing.primary_artist,
            func.count(Listing.id).label('count')
        ).filter(
            Listing.primary_artist.isnot(None),
            Listing.primary_artist != ''
        ).group_by(Listing.primary_artist).order_by(
            func.count(Listing.id).desc()
        ).all()
        
        # Get unique labels with counts
        labels = Listing.query.filter_by(is_active=True).with_entities(
            Listing.primary_label,
            func.count(Listing.id).label('count')
        ).filter(
            Listing.primary_label.isnot(None),
            Listing.primary_label != ''
        ).group_by(Listing.primary_label).order_by(
            func.count(Listing.id).desc()
        ).all()
        
        # Get unique years with counts
        years = Listing.query.filter_by(is_active=True).with_entities(
            Listing.release_year,
            func.count(Listing.id).label('count')
        ).filter(
            Listing.release_year.isnot(None),
            Listing.release_year != ''
        ).group_by(Listing.release_year).order_by(
            Listing.release_year.desc()
        ).all()
        
        # Get unique conditions with counts
        conditions = Listing.query.filter_by(is_active=True).with_entities(
            Listing.condition,
            func.count(Listing.id).label('count')
        ).filter(
            Listing.condition.isnot(None),
            Listing.condition != ''
        ).group_by(Listing.condition).order_by(
            func.count(Listing.id).desc()
        ).all()
        
        # Get unique sleeve conditions with counts
        sleeve_conditions = Listing.query.filter_by(is_active=True).with_entities(
            Listing.sleeve_condition,
            func.count(Listing.id).label('count')
        ).filter(
            Listing.sleeve_condition.isnot(None),
            Listing.sleeve_condition != ''
        ).group_by(Listing.sleeve_condition).order_by(
            func.count(Listing.id).desc()
        ).all()
        
        return {
            'artists': [{'value': artist, 'count': count} for artist, count in artists if artist],
            'labels': [{'value': label, 'count': count} for label, count in labels if label],
            'years': [{'value': year, 'count': count} for year, count in years if year],
            'conditions': [{'value': condition, 'count': count} for condition, count in conditions if condition],
            'sleeve_conditions': [{'value': sleeve, 'count': count} for sleeve, count in sleeve_conditions if sleeve]
        }
    
    def filter_items(self, query: str = None, artist: str = None, 
                    label: str = None, year: str = None, 
                    condition: str = None, sleeve_condition: str = None) -> List[dict]:
        """
        Filter listings with multiple criteria.
        
        Args:
            query: Search query for title or artist
            artist: Filter by artist name
            label: Filter by label name
            year: Filter by release year
            condition: Filter by condition
            sleeve_condition: Filter by sleeve condition
            
        Returns:
            List of matching listing dictionaries
        """
        q = Listing.query.filter_by(is_active=True)
        
        if query:
            q = q.filter(
                (Listing.release_title.ilike(f'%{query}%')) |
                (Listing.artist_names.ilike(f'%{query}%')) |
                (Listing.label_names.ilike(f'%{query}%'))
            )
        
        if artist:
            q = q.filter(Listing.primary_artist == artist)
        
        if label:
            q = q.filter(Listing.primary_label == label)
        
        if year:
            q = q.filter(Listing.release_year == year)
        
        if condition:
            q = q.filter(Listing.condition == condition)
        
        if sleeve_condition:
            q = q.filter(Listing.sleeve_condition == sleeve_condition)
        
        listings = q.order_by(Listing.posted.desc()).all()
        return [listing.to_dict() for listing in listings]

    def get_item_with_videos(self, listing_id: str) -> Optional[Dict]:
        """
        Get an active listing with detailed release information including videos by Discogs listing ID.
        
        Args:
            listing_id: The Discogs listing ID
            
        Returns:
            Dictionary with listing data and videos, or None if not found or inactive
        """
        listing = Listing.query.filter_by(listing_id=listing_id, is_active=True).first()
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
        
        # Add label reference URLs
        result['label_urls'] = self._generate_label_urls(listing.label_names, listing.primary_label)
        
        # Add AI-generated label overviews
        result['label_overviews'] = self._get_label_overviews(listing.label_names)
            
        return result
    
    def get_item_with_videos_by_id(self, id: int) -> Optional[Dict]:
        """
        Get an active listing with detailed release information including videos by database ID.
        
        Args:
            id: The database ID
            
        Returns:
            Dictionary with listing data and videos, or None if not found or inactive
        """
        listing = Listing.query.filter_by(id=id, is_active=True).first()
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
        
        # Add label reference URLs
        result['label_urls'] = self._generate_label_urls(listing.label_names, listing.primary_label)
        
        # Add AI-generated label overviews
        result['label_overviews'] = self._get_label_overviews(listing.label_names)
            
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
    
    def _generate_label_urls(self, label_names: str, primary_label: str) -> List[Dict]:
        """
        Generate reference URLs for labels. If multiple labels are present (comma-separated),
        generates URLs for each label.
        
        Args:
            label_names: Full label names string (comma-separated if multiple)
            primary_label: Primary label name (used as fallback)
            
        Returns:
            List of reference URL dictionaries (3 URLs per label)
        """
        import urllib.parse
        
        if not label_names or label_names == 'Unknown':
            return []
        
        # Parse comma-separated labels and remove duplicates while preserving order
        labels = []
        seen = set()
        for label in label_names.split(','):
            label_clean = label.strip()
            if label_clean and label_clean not in seen:
                labels.append(label_clean)
                seen.add(label_clean)
        
        if not labels:
            return []
        
        urls = []
        
        # Generate 3 URLs for each unique label
        for label_clean in labels:
            label_encoded = urllib.parse.quote(label_clean)
            label_encoded_plus = urllib.parse.quote_plus(label_clean)
            
            # Add label name prefix if there are multiple labels
            label_prefix = f"{label_clean} - " if len(labels) > 1 else ""
            
            urls.extend([
                {
                    'title': f'{label_prefix}Discogs Label Page',
                    'url': f'https://www.discogs.com/search/?q={label_encoded}&type=label',
                    'description': f'Search for {label_clean} on Discogs'
                },
                {
                    'title': f'{label_prefix}Bandcamp Search',
                    'url': f'https://bandcamp.com/search?q={label_encoded_plus}&item_type=b',
                    'description': f'Find {label_clean} on Bandcamp'
                },
                {
                    'title': f'{label_prefix}Google Search',
                    'url': f'https://www.google.com/search?q={label_encoded}+record+label',
                    'description': f'Search for {label_clean} information'
                }
            ])
        
        return urls
    
    def _get_label_overviews(self, label_names: str) -> Dict[str, str]:
        """
        Get AI-generated overviews for labels, using cache when available.
        
        Args:
            label_names: Comma-separated label names
            
        Returns:
            Dictionary mapping label names to their AI-generated overviews
        """
        if not label_names or label_names == 'Unknown':
            return {}
        
        # Check if AI overviews are enabled
        if not current_app.config.get('ENABLE_AI_OVERVIEWS', True):
            return {}
        
        # Parse unique labels
        labels = []
        seen = set()
        for label in label_names.split(','):
            label_clean = label.strip()
            if label_clean and label_clean not in seen:
                labels.append(label_clean)
                seen.add(label_clean)
        
        if not labels:
            return {}
        
        overviews = {}
        labels_to_generate = []
        
        # Check cache for each label
        for label_name in labels:
            cached_info = LabelInfo.query.filter_by(
                label_name=label_name,
                cache_valid=True
            ).first()
            
            if cached_info and cached_info.overview:
                overviews[label_name] = cached_info.overview
            else:
                labels_to_generate.append(label_name)
        
        # Generate overviews for uncached labels
        if labels_to_generate:
            from app.services.gemini_service import GeminiService
            gemini = GeminiService()
            
            if gemini.is_available():
                for label_name in labels_to_generate:
                    try:
                        overview = gemini.generate_label_overview(label_name)
                        
                        if overview:
                            overviews[label_name] = overview
                            
                            # Cache the result
                            self._cache_label_overview(label_name, overview)
                        else:
                            current_app.logger.warning(f"Failed to generate overview for: {label_name}")
                            
                    except Exception as e:
                        current_app.logger.error(f"Error generating overview for {label_name}: {e}")
            else:
                current_app.logger.warning("Gemini service not available. Skipping AI overviews.")
        
        return overviews
    
    def _cache_label_overview(self, label_name: str, overview: str) -> None:
        """
        Cache a label overview in the database.
        
        Args:
            label_name: Name of the label
            overview: Generated overview text
        """
        try:
            # Check if entry exists
            label_info = LabelInfo.query.filter_by(label_name=label_name).first()
            
            if label_info:
                # Update existing
                label_info.overview = overview
                label_info.cache_valid = True
                label_info.generation_error = None
                label_info.updated_at = datetime.utcnow()
            else:
                # Create new
                label_info = LabelInfo(
                    label_name=label_name,
                    overview=overview,
                    generated_by='gemini-1.5-flash',
                    cache_valid=True
                )
                db.session.add(label_info)
            
            db.session.commit()
            current_app.logger.info(f"Cached overview for label: {label_name}")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error caching overview for {label_name}: {e}")
    
    def _update_listing_status(self, listing_id: str, updates: Dict) -> bool:
        """
        Private helper to update listing status fields.
        
        Args:
            listing_id: The Discogs listing ID
            updates: Dictionary of field names and values to update
            
        Returns:
            True if successful, False if listing not found
        """
        listing = Listing.query.filter_by(listing_id=listing_id).first()
        if listing:
            for field, value in updates.items():
                setattr(listing, field, value)
            db.session.commit()
            return True
        return False
    
    def soft_delete(self, listing_id: str) -> bool:
        """
        Mark a listing as removed (soft delete) instead of deleting from database.
        
        Args:
            listing_id: The Discogs listing ID to mark as removed
            
        Returns:
            True if successful, False if listing not found
        """
        return self._update_listing_status(listing_id, {
            'is_active': False,
            'removed_at': datetime.now(timezone.utc)
        })
    
    def restore_listing(self, listing_id: str) -> bool:
        """
        Restore a soft-deleted listing.
        
        Args:
            listing_id: The Discogs listing ID to restore
            
        Returns:
            True if successful, False if listing not found
        """
        return self._update_listing_status(listing_id, {
            'is_active': True,
            'removed_at': None
        })
    
    def mark_as_sold(self, listing_id: str) -> bool:
        """
        Mark a listing as sold.
        
        Args:
            listing_id: The Discogs listing ID to mark as sold
            
        Returns:
            True if successful, False if listing not found
        """
        return self._update_listing_status(listing_id, {
            'is_active': False,
            'sold_at': datetime.now(timezone.utc)
        })
