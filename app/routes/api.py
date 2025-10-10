from flask import Blueprint, jsonify, request
from app.services.inventory_service import InventoryService

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/data')
def get_data():
    """Get all listings."""
    service = InventoryService()
    data = service.get_all_items()
    return jsonify(data)

@bp.route('/data/<listing_id>')
def get_listing(listing_id):
    """Get a specific listing by ID."""
    service = InventoryService()
    listing = service.get_item_by_listing_id(listing_id)
    if listing:
        return jsonify(listing)
    return jsonify({'error': 'Listing not found'}), 404

@bp.route('/search')
def search_listings():
    """Search listings with optional filters."""
    service = InventoryService()
    
    query = request.args.get('q')
    artist = request.args.get('artist')
    genre = request.args.get('genre')
    format_type = request.args.get('format')
    
    data = service.search_items(
        query=query,
        artist=artist,
        genre=genre,
        format_type=format_type
    )
    return jsonify(data)

@bp.route('/stats')
def get_stats():
    """Get inventory statistics."""
    service = InventoryService()
    stats = service.get_stats()
    return jsonify(stats)
